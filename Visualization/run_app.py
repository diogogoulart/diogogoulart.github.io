###############################################
# File: plot_app.py
# A self-contained Streamlit app for
# uploading multiple files (CSV/XLS/XLSX)
# and creating various interactive plots,
# with expanded scale options for 
# Scatter and Line plots (Exponential, Log10, etc.),
# a "moving average" option for Line plots,
# optional error bars for Line plots,
# preset saving/loading/deleting across sessions,
# and multiple-file support for Scatter/Line.
###############################################

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from sklearn.impute import KNNImputer  # for KNN option in NaN handling
from scipy.stats import zscore

import json
import os

# Named colors for color dropdown
NAMED_COLORS = [
    'blue','red','green','orange','purple','cyan','black','gray',
    'pink','brown','lime','olive','navy','teal','maroon'
]

# Optional colormaps for Boxplot/Violin hue usage
CMAPS = ['None','viridis','plasma','inferno','magma','cividis','Pastel1','Set3']

# For violin 'scale' param
VIOLIN_SCALE_OPTIONS = {
    'Proportional area': 'area',
    'Proportional length': 'count',
    'Fixed width': 'width'
}

###########################################
# Preset loading/saving logic
###########################################
PRESET_FILE = "plot_presets.json"

def load_presets():
    """Load presets from JSON file, return dict."""
    if os.path.exists(PRESET_FILE):
        with open(PRESET_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return {}

def save_presets(presets):
    """Save presets to JSON file."""
    with open(PRESET_FILE, 'w', encoding='utf-8') as f:
        json.dump(presets, f, indent=2)

# Initialize or load presets into session_state
if 'presets' not in st.session_state:
    st.session_state['presets'] = load_presets()

###########################################
# 1) Title and Intro
###########################################
st.title("Interactive Plotting Interface")
st.write("""
Upload one **or more** files (CSV/XLS/XLSX). If Excel with multiple sheets, 
pick which sheet. Then choose a graph type and parameters to visualize your data.
You can re-upload new files any time to replace the existing ones.
""")

st.write("---")

###########################################
# 2) File Upload
###########################################
# -- ACCEPT MULTIPLE FILES -- 
uploaded_files = st.file_uploader(
    "Upload one or more files (CSV/XLS/XLSX)",
    type=["csv","xlsx","xls"],
    accept_multiple_files=True
)

# Dictionary for fileName -> DataFrame
df_dict = {}

def load_data(file, sheet_name=None):
    """
    Reads from a file-like object:
    - If CSV => pd.read_csv
    - If Excel => pd.read_excel
    sheet_name is used only if Excel.
    """
    if sheet_name is None:
        # Attempt CSV first
        try:
            return pd.read_csv(file)
        except:
            # If that fails, assume Excel
            file.seek(0)
            return pd.read_excel(file)
    else:
        # Specifically read Excel with given sheet
        return pd.read_excel(file, sheet_name=sheet_name)

# We'll keep a container for "sheet selection" if the file is Excel
# but for simplicity, always read the first sheet:
if uploaded_files:
    for file_obj in uploaded_files:
        file_name = file_obj.name.lower()
        try:
            if file_name.endswith(".csv"):
                df_temp = pd.read_csv(file_obj)
                st.write(f"Loaded CSV '{file_obj.name}' with shape: {df_temp.shape}")
                df_dict[file_obj.name] = df_temp
            elif file_name.endswith(".xlsx") or file_name.endswith(".xls"):
                xls = pd.ExcelFile(file_obj)
                first_sheet = xls.sheet_names[0]
                st.write(f"Loading Excel '{file_obj.name}' first sheet '{first_sheet}'")
                file_obj.seek(0)
                df_temp = pd.read_excel(file_obj, sheet_name=first_sheet)
                st.write(f"Loaded Excel '{file_obj.name}' sheet '{first_sheet}' with shape: {df_temp.shape}")
                df_dict[file_obj.name] = df_temp
            else:
                st.error(f"Unsupported file type: {file_obj.name}")
        except Exception as e:
            st.error(f"File {file_obj.name} is not valid: {e}")
else:
    st.info("No file(s) uploaded yet. Please upload one or more above.")

st.write("---")

##########################################################################
# Helper Functions
##########################################################################

def check_columns_for_nans_and_length(df, columns):
    """
    Check if chosen columns have NaN values or differing counts of valid data.
    Returns (bool_has_nans, bool_mismatch, valid_counts_dict).
    """
    has_nans = False
    mismatch = False
    valid_counts = {}
    counts = []
    for col in columns:
        if col not in df.columns:
            # If the user typed or selected a non-existent column, skip checks
            continue
        col_nans = df[col].isna().sum()
        if col_nans > 0:
            has_nans = True
        valid_count = df[col].dropna().shape[0]
        valid_counts[col] = valid_count
        counts.append(valid_count)
    if len(set(counts)) > 1:
        mismatch = True
    return has_nans, mismatch, valid_counts

def handle_nans(df_in, columns_in_use, method):
    """
    Return a copy of df_in where NaNs in columns_in_use are handled 
    according to the chosen method (for plotting only).
    """
    df_out = df_in.copy()
    for c in columns_in_use:
        if c not in df_out.columns:
            # If the col doesn't exist, skip
            continue

    if method == "Ignore":
        return df_out  # do nothing

    if method == "Drop rows":
        df_out = df_out.dropna(subset=columns_in_use)

    elif method == "Fill with mean":
        for c in columns_in_use:
            if c in df_out.columns and pd.api.types.is_numeric_dtype(df_out[c]):
                mean_val = df_out[c].mean()
                df_out[c] = df_out[c].fillna(mean_val)

    elif method == "Fill with most common value":
        for c in columns_in_use:
            if c in df_out.columns and df_out[c].dropna().size > 0:
                mode_val = df_out[c].mode(dropna=True)[0]
                df_out[c] = df_out[c].fillna(mode_val)

    elif method == "Replace with 0":
        df_out[columns_in_use] = df_out[columns_in_use].fillna(0)

    elif method == "Interpolate":
        df_out[columns_in_use] = df_out[columns_in_use].interpolate(method='linear')

    elif method == "KNN (nearest 4 points)":
        # We'll apply KNN only on numeric columns_in_use
        numeric_cols = [c for c in columns_in_use if c in df_out.columns and pd.api.types.is_numeric_dtype(df_out[c])]
        if len(numeric_cols) > 0:
            imputer = KNNImputer(n_neighbors=4)
            df_numeric = df_out[numeric_cols]
            df_imputed = imputer.fit_transform(df_numeric)
            df_out[numeric_cols] = df_imputed

    elif method == "Replace with nearest point":
        for c in columns_in_use:
            if c not in df_out.columns:
                continue
            if pd.api.types.is_numeric_dtype(df_out[c]):
                df_out[c] = df_out[c].interpolate(method='nearest')
            else:
                # fallback to ffill then bfill for strings
                df_out[c] = df_out[c].ffill().bfill()

    return df_out

def handle_outliers(df_in, columns_in_use, method):
    """
    Return a copy of df_in with outliers handled in numeric columns_in_use 
    according to the chosen method (for plotting only).
    """
    df_out = df_in.copy()
    numeric_cols = [c for c in columns_in_use if c in df_out.columns and pd.api.types.is_numeric_dtype(df_out[c])]

    if method == "Ignore":
        return df_out  # do nothing

    if len(numeric_cols) == 0:
        return df_out  # No numeric columns to process

    if method in ["Cap 0.1%", "Cap 1%", "Cap 5%"]:
        if method == "Cap 0.1%":
            lower_q, upper_q = 0.001, 0.999
        elif method == "Cap 1%":
            lower_q, upper_q = 0.01, 0.99
        else:  # "Cap 5%"
            lower_q, upper_q = 0.05, 0.95

        for c in numeric_cols:
            lower_val = df_out[c].quantile(lower_q)
            upper_val = df_out[c].quantile(upper_q)
            df_out[c] = df_out[c].clip(lower=lower_val, upper=upper_val)

    elif method == "Outside 1.5×IQR":
        for c in numeric_cols:
            Q1 = df_out[c].quantile(0.25)
            Q3 = df_out[c].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            df_out = df_out[(df_out[c] >= lower_bound) & (df_out[c] <= upper_bound)]

    elif method == "Remove rows (|z-score|>3)":
        z_scores = np.abs(zscore(df_out[numeric_cols], nan_policy='omit'))
        mask = (z_scores < 3).all(axis=1)
        df_out = df_out[mask]

    return df_out

def transform_series(series, scale_type, label=""):
    """
    Apply a custom scale transformation to a numeric Series.
    - Negative or zero values are dropped for log/sqrt as invalid.
    - Non-numeric or invalid entries are dropped as well.
    Returns a new Series (with potentially fewer rows).
    """
    s = pd.to_numeric(series, errors='coerce').dropna()

    if scale_type == "Linear":
        return s  # no transform
    elif scale_type == "Exponential":
        return np.exp(s)
    elif scale_type == "Log10":
        s = s[s > 0]
        return np.log10(s)
    elif scale_type == "Log2":
        s = s[s > 0]
        return np.log2(s)
    elif scale_type == "Natural Log (ln)":
        s = s[s > 0]
        return np.log(s)
    elif scale_type == "^2":
        return s**2
    elif scale_type == "sqrt":
        s = s[s >= 0]
        return np.sqrt(s)
    else:
        return s  # fallback no transform


import matplotlib.patches as patches

def add_axis_arrows(ax):
    """
    Remove the default spines, then draw arrowheads 
    on the X and Y axes using ax.annotate().
    
    By default, this will place arrows at the 
    existing axis limits (ax.get_xlim/ylim).
    """
    # 1) Hide the existing spines
    for spine in ["left","right","top","bottom"]:
        ax.spines[spine].set_visible(False)

    # 2) Get the current data range
    x_min, x_max = ax.get_xlim()
    y_min, y_max = ax.get_ylim()

    # 3) Draw an arrow for the X axis
    ax.annotate(
        "", 
        xy=(x_max, 0),              # arrow tail at the right side
        xycoords="data",
        xytext=(x_min, 0),          # arrow head at the left side
        textcoords="data",
        arrowprops=dict(
            arrowstyle="->", 
            linewidth=1.2, 
            color="black"
        )
    )

    # 4) Draw an arrow for the Y axis
    ax.annotate(
        "", 
        xy=(0, y_max),             # arrow tail at the top
        xycoords="data",
        xytext=(0, y_min),         # arrow head at the bottom
        textcoords="data",
        arrowprops=dict(
            arrowstyle="->", 
            linewidth=1.2, 
            color="black"
        )
    )

##########################################################################
# MAIN APP
##########################################################################

# If no files, we skip everything
if not df_dict:
    st.stop()

file_names = list(df_dict.keys())
primary_file_name = file_names[0]  
df_primary = df_dict[primary_file_name]
all_columns_primary = list(df_primary.columns)

# Create a combined list "fileName||colName" for *every* column of *every* file
multi_file_columns = []
for f_name in file_names:
    df_temp = df_dict[f_name]
    for c in df_temp.columns:
        multi_file_columns.append(f"{f_name}||{c}")

###########################################
# 3) Common Plot Parameters
###########################################
st.write("### Select Rows to Use")

row_cols = st.columns(2)
with row_cols[0]:
    row_start = st.number_input("Row start index", min_value=0, max_value=None, value=0, step=1)
with row_cols[1]:
    row_end = st.number_input("Row end index (exclusive)", min_value=1, value=len(df_primary), step=1)

st.write("---")
st.write("### Figure Size")
size_cols = st.columns(2)
with size_cols[0]:
    fig_width = st.slider("Fig width", min_value=1.0, max_value=20.0, value=8.0, step=0.5)
with size_cols[1]:
    fig_height = st.slider("Fig height", min_value=1.0, max_value=20.0, value=5.0, step=0.5)

st.write("---")
st.write("### Font Sizes")
font_cols = st.columns(4)
with font_cols[0]:
    title_font = st.slider("Title Font", min_value=6, max_value=30, value=12, step=1)
with font_cols[1]:
    label_font = st.slider("Label Font", min_value=6, max_value=30, value=10, step=1)
with font_cols[2]:
    tick_font = st.slider("Tick Font", min_value=6, max_value=30, value=9, step=1)
with font_cols[3]:
    legend_font = st.slider("Legend Font", min_value=6, max_value=30, value=9, step=1)

st.write("---")
st.write("### Title / Axis Labels (leave blank for auto)")

title_cols = st.columns(3)
with title_cols[0]:
    custom_title = st.text_input("Title override", "")
with title_cols[1]:
    custom_xlabel = st.text_input("X Label override", "")
with title_cols[2]:
    custom_ylabel = st.text_input("Y Label override", "")

st.write("---")
###########################################
# 4) Graph Type & Options
###########################################
st.markdown("<h2 style='font-size:50px;'>Pick a Graph Type</h2>", unsafe_allow_html=True)
graph_type = st.selectbox(
    "Graph Type",
    [
        "Histogram",
        "Scatter",
        "Line",
        "Bar",
        "Pie",
        "Distribution",
        "Boxplot",
        "Violin Plot"
    ]
)

# Utility for color selection
def get_chosen_color(named, custom):
    c = custom.strip()
    return c if c else named

fig, ax = plt.subplots(figsize=(fig_width, fig_height))
ax.tick_params(labelsize=tick_font)

default_title = ""
default_xlabel = ""
default_ylabel = ""

########################################################################
# HELPER: Handle loading a saved preset for the current graph_type
########################################################################
current_graph_presets = st.session_state.presets.get(graph_type, {})
preset_names = ["None"] + list(current_graph_presets.keys())

st.write(f"#### Saved {graph_type} Presets")
selected_preset_name = st.selectbox(
    "Load a preset (optional)",
    preset_names,
    index=0,
    key=f"{graph_type}_preset_selectbox"
)

############################################################################
# HISTOGRAM  (only uses primary file)
############################################################################
if graph_type == "Histogram":
    hist_default = {
        "col": all_columns_primary[0] if all_columns_primary else "",
        "bins_val": 0,
        "color_named": "blue",
        "color_custom": "",
        "show_grid": False,
        "nan_method": "Ignore",
        "outlier_method": "Ignore"
    }
    if selected_preset_name != "None":
        loaded = current_graph_presets[selected_preset_name]
        for k, v in loaded.items():
            if k in hist_default:
                hist_default[k] = v

    col = st.selectbox(
        "Select column for histogram (primary file only)",
        all_columns_primary,
        index=all_columns_primary.index(hist_default["col"]) if hist_default["col"] in all_columns_primary else 0
    )
    hist_cols = st.columns(2)
    with hist_cols[0]:
        bins_val = st.slider(
            "Number of bins (0 = 'fd')",
            min_value=0, max_value=50, value=hist_default["bins_val"]
        )
    with hist_cols[1]:
        color_named = st.selectbox(
            "Named Color",
            NAMED_COLORS,
            index=NAMED_COLORS.index(hist_default["color_named"]) 
            if hist_default["color_named"] in NAMED_COLORS else 0
        )
        color_custom = st.text_input(
            "Custom color (hex or rgb)",
            hist_default["color_custom"]
        )

    show_grid = st.checkbox("Turn grid on", hist_default["show_grid"])

    columns_in_use = [col]
    subset_primary = df_primary.iloc[row_start:row_end].copy()

    has_nans, mismatch, valid_counts = check_columns_for_nans_and_length(subset_primary, columns_in_use)
    if has_nans:
        st.warning("The chosen column has NaN values.")
    if mismatch:
        st.warning("The chosen column has a different number of valid points than expected.")

    nan_method = st.selectbox(
        "How to treat NaN values (for plot only)",
        [
            "Ignore",
            "Drop rows",
            "Fill with mean",
            "Fill with most common value",
            "Replace with 0",
            "Interpolate",
            "KNN (nearest 4 points)",
            "Replace with nearest point"
        ],
        index=[
            "Ignore",
            "Drop rows",
            "Fill with mean",
            "Fill with most common value",
            "Replace with 0",
            "Interpolate",
            "KNN (nearest 4 points)",
            "Replace with nearest point"
        ].index(hist_default["nan_method"]) if hist_default["nan_method"] in [
            "Ignore",
            "Drop rows",
            "Fill with mean",
            "Fill with most common value",
            "Replace with 0",
            "Interpolate",
            "KNN (nearest 4 points)",
            "Replace with nearest point"
        ] else 0
    )

    outlier_method = st.selectbox(
        "How to treat outliers (for plot only)",
        [
            "Ignore",
            "Cap 0.1%",
            "Cap 1%",
            "Cap 5%",
            "Outside 1.5×IQR",
            "Remove rows (|z-score|>3)"
        ],
        index=[
            "Ignore",
            "Cap 0.1%",
            "Cap 1%",
            "Cap 5%",
            "Outside 1.5×IQR",
            "Remove rows (|z-score|>3)"
        ].index(hist_default["outlier_method"]) if hist_default["outlier_method"] in [
            "Ignore",
            "Cap 0.1%",
            "Cap 1%",
            "Cap 5%",
            "Outside 1.5×IQR",
            "Remove rows (|z-score|>3)"
        ] else 0
    )

    final_color = get_chosen_color(color_named, color_custom)
    final_bins = "fd" if bins_val == 0 else bins_val

    default_title = f"Histogram of {col}"
    default_xlabel = col
    default_ylabel = "Frequency"

    subset_for_plot = handle_nans(subset_primary.copy(), columns_in_use, nan_method)
    subset_for_plot = handle_outliers(subset_for_plot, columns_in_use, outlier_method)

    sns.histplot(subset_for_plot[col], bins=final_bins, color=final_color, ax=ax, label=col)
    ax.grid(show_grid)
    ax.legend(fontsize=legend_font)

    # Preset saving
    st.write("#### Save / Delete Histogram Preset")
    preset_name_input = st.text_input(
        "Preset name",
        value=selected_preset_name if selected_preset_name != "None" else "",
        key=f"{graph_type}_preset_name_input"
    )

    if st.button("Save this preset", key=f"{graph_type}_save_preset_btn"):
        new_preset_data = {
            "col": col,
            "bins_val": bins_val,
            "color_named": color_named,
            "color_custom": color_custom,
            "show_grid": show_grid,
            "nan_method": nan_method,
            "outlier_method": outlier_method
        }
        if not preset_name_input.strip():
            st.error("Please provide a valid preset name.")
        else:
            st.session_state.presets.setdefault(graph_type, {})[preset_name_input] = new_preset_data
            save_presets(st.session_state.presets)
            st.success(f"Preset '{preset_name_input}' saved!")

    if selected_preset_name != "None":
        if st.button("Delete this preset", key=f"{graph_type}_delete_preset_btn"):
            if preset_name_input in st.session_state.presets[graph_type]:
                del st.session_state.presets[graph_type][preset_name_input]
                save_presets(st.session_state.presets)
                st.success(f"Preset '{preset_name_input}' deleted!")


############################################################################
# SCATTER (SUPPORT MULTI-FILE)
############################################################################
elif graph_type == "Scatter":
    scatter_default = {
        "series_count": 1,
        "show_grid": False,
        "x_scale": "Linear",
        "y_scale": "Linear",
        "series_params": [
            {
                "col_choice": multi_file_columns[0] if multi_file_columns else "",
                "color_named": "blue",
                "color_custom": "",
                "marker_size": 20,
                "legend_name": ""
            }
        ],
        "nan_method": "Ignore",
        "outlier_method": "Ignore"
    }
    if selected_preset_name != "None":
        loaded = current_graph_presets[selected_preset_name]
        for k, v in loaded.items():
            scatter_default[k] = v

    series_count = st.slider(
        "Number of series", 
        min_value=1, max_value=5, 
        value=scatter_default["series_count"], 
        step=1
    )
    show_grid = st.checkbox("Turn grid on", scatter_default["show_grid"])

    scale_options = [
        "Linear",
        "Exponential",
        "Log10",
        "Log2",
        "Natural Log (ln)",
        "^2",
        "sqrt"
    ]
    scale_cols = st.columns(2)
    with scale_cols[0]:
        x_scale = st.selectbox(
            "X Scale", 
            scale_options, 
            index=scale_options.index(scatter_default["x_scale"])
            if scatter_default["x_scale"] in scale_options else 0
        )
    with scale_cols[1]:
        y_scale = st.selectbox(
            "Y Scale", 
            scale_options,
            index=scale_options.index(scatter_default["y_scale"])
            if scatter_default["y_scale"] in scale_options else 0
        )

    scatter_params = []
    existing_series = scatter_default["series_params"]
    while len(existing_series) < series_count:
        existing_series.append({
            "col_choice": multi_file_columns[0] if multi_file_columns else "",
            "color_named": "blue",
            "color_custom": "",
            "marker_size": 20,
            "legend_name": ""
        })

    columns_in_use_for_nans = []

    for i in range(series_count):
        st.write(f"**Series {i+1}:**")
        col_choice_value = existing_series[i]["col_choice"] if i < len(existing_series) else (multi_file_columns[0] if multi_file_columns else "")
        color_named_value = existing_series[i]["color_named"]
        color_custom_value = existing_series[i]["color_custom"]
        marker_size_value = existing_series[i]["marker_size"]
        legend_name_value = existing_series[i]["legend_name"]

        scatter_col_1 = st.columns(3)
        with scatter_col_1[0]:
            col_choice = st.selectbox(
                f"Column (Series {i+1}) [file||column]",
                multi_file_columns,
                index=multi_file_columns.index(col_choice_value) 
                if col_choice_value in multi_file_columns else 0,
                key=f"scatter_col_{i}"
            )
        with scatter_col_1[1]:
            color_named = st.selectbox(
                f"Named Color (Series {i+1})",
                NAMED_COLORS,
                index=NAMED_COLORS.index(color_named_value) 
                if color_named_value in NAMED_COLORS else 0,
                key=f"scatter_color_named_{i}"
            )
        with scatter_col_1[2]:
            color_custom = st.text_input(
                f"Custom color (Series {i+1})",
                value=color_custom_value,
                key=f"scatter_color_custom_{i}"
            )

        scatter_col_2 = st.columns(2)
        with scatter_col_2[0]:
            marker_size = st.slider(
                f"Marker size (Series {i+1})", 
                min_value=1, 
                max_value=200, 
                value=marker_size_value, 
                step=1, 
                key=f"scatter_size_{i}"
            )
        with scatter_col_2[1]:
            legend_name = st.text_input(
                f"Legend Name (Series {i+1})",
                value=legend_name_value,
                key=f"scatter_legend_{i}"
            )

        scatter_params.append({
            "col_choice": col_choice,
            "color_named": color_named,
            "color_custom": color_custom,
            "marker_size": marker_size,
            "legend_name": legend_name
        })
        columns_in_use_for_nans.append(col_choice)

    # Check for NaNs
    nan_flags = []
    for col_combo in columns_in_use_for_nans:
        fname, real_col = col_combo.split("||", 1)
        this_df = df_dict[fname].iloc[row_start:row_end].copy()
        if real_col not in this_df.columns:
            continue
        if this_df[real_col].isna().any():
            nan_flags.append(col_combo)
    if nan_flags:
        st.warning(f"Some chosen columns contain NaN values: {nan_flags}")

    nan_method = st.selectbox(
        "How to treat NaN values (for plot only)",
        [
            "Ignore",
            "Drop rows",
            "Fill with mean",
            "Fill with most common value",
            "Replace with 0",
            "Interpolate",
            "KNN (nearest 4 points)",
            "Replace with nearest point"
        ],
        index=[
            "Ignore",
            "Drop rows",
            "Fill with mean",
            "Fill with most common value",
            "Replace with 0",
            "Interpolate",
            "KNN (nearest 4 points)",
            "Replace with nearest point"
        ].index(scatter_default["nan_method"]) 
        if scatter_default["nan_method"] in [
            "Ignore",
            "Drop rows",
            "Fill with mean",
            "Fill with most common value",
            "Replace with 0",
            "Interpolate",
            "KNN (nearest 4 points)",
            "Replace with nearest point"
        ] else 0
    )

    outlier_method = st.selectbox(
        "How to treat outliers (for plot only)",
        [
            "Ignore",
            "Cap 0.1%",
            "Cap 1%",
            "Cap 5%",
            "Outside 1.5×IQR",
            "Remove rows (|z-score|>3)"
        ],
        index=[
            "Ignore",
            "Cap 0.1%",
            "Cap 1%",
            "Cap 5%",
            "Outside 1.5×IQR",
            "Remove rows (|z-score|>3)"
        ].index(scatter_default["outlier_method"]) 
        if scatter_default["outlier_method"] in [
            "Ignore",
            "Cap 0.1%",
            "Cap 1%",
            "Cap 5%",
            "Outside 1.5×IQR",
            "Remove rows (|z-score|>3)"
        ] else 0
    )

    legend_used = False

    for sp in scatter_params:
        file_and_col = sp["col_choice"]
        fname, real_col = file_and_col.split("||", 1)
        df_subset = df_dict[fname].iloc[row_start:row_end].copy()

        df_subset = handle_nans(df_subset, [real_col], nan_method)
        df_subset = handle_outliers(df_subset, [real_col], outlier_method)

        original_x = pd.Series(df_subset.index, index=df_subset.index)
        x_transformed = transform_series(original_x, x_scale, label="X")

        if real_col not in df_subset.columns:
            # Just skip if somehow the column doesn't exist
            continue

        y_original = df_subset[real_col]
        y_transformed = transform_series(y_original, y_scale, label=real_col)

        common_idx = x_transformed.index.intersection(y_transformed.index)
        x_plot = x_transformed.loc[common_idx]
        y_plot = y_transformed.loc[common_idx]

        c_final = get_chosen_color(sp["color_named"], sp["color_custom"])
        lbl = sp["legend_name"] if sp["legend_name"] else file_and_col
        ax.scatter(x_plot, y_plot, color=c_final, s=sp["marker_size"], label=lbl)
        legend_used = True

    if series_count > 1:
        default_title = "Multiple columns across multiple files"
        default_ylabel = "values"
    else:
        if scatter_params:
            default_title = f"{scatter_params[0]['col_choice']} depending on index"
            default_ylabel = scatter_params[0]['col_choice']
    default_xlabel = "index"

    ax.grid(show_grid)
    if legend_used:
        ax.legend(fontsize=legend_font)

    # Preset saving
    st.write("#### Save / Delete Scatter Preset")
    preset_name_input = st.text_input(
        "Preset name",
        value=selected_preset_name if selected_preset_name != "None" else "",
        key=f"{graph_type}_preset_name_input"
    )
    if st.button("Save this preset", key=f"{graph_type}_save_preset_btn"):
        new_preset_data = {
            "series_count": series_count,
            "show_grid": show_grid,
            "x_scale": x_scale,
            "y_scale": y_scale,
            "series_params": scatter_params,
            "nan_method": nan_method,
            "outlier_method": outlier_method
        }
        if not preset_name_input.strip():
            st.error("Please provide a valid preset name.")
        else:
            st.session_state.presets.setdefault(graph_type, {})[preset_name_input] = new_preset_data
            save_presets(st.session_state.presets)
            st.success(f"Preset '{preset_name_input}' saved!")

    if selected_preset_name != "None":
        if st.button("Delete this preset", key=f"{graph_type}_delete_preset_btn"):
            if preset_name_input in st.session_state.presets[graph_type]:
                del st.session_state.presets[graph_type][preset_name_input]
                save_presets(st.session_state.presets)
                st.success(f"Preset '{preset_name_input}' deleted!")


############################################################################
# LINE (SUPPORT MULTI-FILE + PER-LINE ERROR COLUMNS)
############################################################################
elif graph_type == "Line":
    line_default = {
        "series_count": 1,
        "show_grid": False,
        "add_marker": False,
        "x_scale": "Linear",
        "y_scale": "Linear",
        "line_params": [
            {
                "column": multi_file_columns[0] if multi_file_columns else "",
                "color": "blue",
                "color_named": "blue",
                "color_custom": "",
                "linewidth": 2.0,
                "label": "",
                "plot_ma": False,
                "ma_window": 5,
                "ma_color": "red",
                "ma_color_named": "red",
                "ma_color_custom": "",
                "ma_label": "Moving Avg",
                # For error columns:
                "error_mode": "Use global numeric",  # or "None", "Column-based"
                "yerr_column": "",
                "xerr_column": ""
            }
        ],
        "nan_method": "Ignore",
        "outlier_method": "Ignore",
        "add_error_bars": False,
        "yerr_val": 0.1,
        "xerr_val": 0.0,
        "ecolor_named": "blue",
        "ecolor_custom": "",
        "elinewidth_val": 1.0,
        "capsize_val": 3,
        "capthick_val": 1.0
    }
    if selected_preset_name != "None":
        loaded = current_graph_presets[selected_preset_name]
        for k, v in loaded.items():
            line_default[k] = v

    line_top_cols = st.columns(2)
    with line_top_cols[0]:
        show_grid = st.checkbox("Turn grid on", line_default["show_grid"])
    with line_top_cols[1]:
        add_marker = st.checkbox("Turn on Marker (o)", line_default["add_marker"])
    marker_style = 'o' if add_marker else None

    scale_options = [
        "Linear",
        "Exponential",
        "Log10",
        "Log2",
        "Natural Log (ln)",
        "^2",
        "sqrt"
    ]
    scale_cols = st.columns(2)
    with scale_cols[0]:
        x_scale = st.selectbox(
            "X Scale", 
            scale_options, 
            index=scale_options.index(line_default["x_scale"]) 
            if line_default["x_scale"] in scale_options else 0
        )
    with scale_cols[1]:
        y_scale = st.selectbox(
            "Y Scale", 
            scale_options, 
            index=scale_options.index(line_default["y_scale"]) 
            if line_default["y_scale"] in scale_options else 0
        )

    series_count = st.slider(
        "Number of series",
        min_value=1,
        max_value=5,
        value=line_default["series_count"],
        step=1
    )

    existing_line_series = line_default["line_params"]
    while len(existing_line_series) < series_count:
        existing_line_series.append({
            "column": multi_file_columns[0] if multi_file_columns else "",
            "color": "blue",
            "color_named": "blue",
            "color_custom": "",
            "linewidth": 2.0,
            "label": "",
            "plot_ma": False,
            "ma_window": 5,
            "ma_color": "red",
            "ma_color_named": "red",
            "ma_color_custom": "",
            "ma_label": "Moving Avg",
            "error_mode": "Use global numeric",
            "yerr_column": "",
            "xerr_column": ""
        })

    line_params_list = []
    columns_in_use_for_nans = []

    for i in range(series_count):
        st.write(f"**Series {i+1}:**")

        sdata = existing_line_series[i]
        col_choice_value = sdata["column"]
        color_value = sdata.get("color_named","blue")
        color_custom_value = sdata.get("color_custom","")
        lw_value = sdata.get("linewidth",2.0)
        lbl_value = sdata.get("label","")
        plot_ma_value = sdata.get("plot_ma",False)
        ma_window_value = sdata.get("ma_window",5)
        ma_color_value = sdata.get("ma_color_named","red")
        ma_color_custom_value = sdata.get("ma_color_custom","")
        ma_legend_value = sdata.get("ma_label","Moving Avg")

        error_mode_value = sdata.get("error_mode","Use global numeric")
        yerr_col_value = sdata.get("yerr_column","")
        xerr_col_value = sdata.get("xerr_column","")

        line_col_1 = st.columns(3)
        with line_col_1[0]:
            col_choice = st.selectbox(
                f"Column (Series {i+1}) [file||column]",
                multi_file_columns,
                index=multi_file_columns.index(col_choice_value) 
                if col_choice_value in multi_file_columns else 0,
                key=f"line_col_{i}"
            )
        with line_col_1[1]:
            color_named = st.selectbox(
                f"Named Color (Series {i+1})",
                NAMED_COLORS,
                index=NAMED_COLORS.index(color_value) 
                if color_value in NAMED_COLORS else 0,
                key=f"line_color_named_{i}"
            )
        with line_col_1[2]:
            color_custom = st.text_input(
                f"Custom color (Series {i+1})",
                value=color_custom_value,
                key=f"line_color_custom_{i}"
            )

        line_col_2 = st.columns(2)
        with line_col_2[0]:
            lw_val = st.slider(
                f"Line width (Series {i+1})",
                min_value=0.1, max_value=10.0, 
                value=lw_value, step=0.1,
                key=f"line_lw_{i}"
            )
        with line_col_2[1]:
            legend_name = st.text_input(
                f"Legend Name (Series {i+1})", 
                value=lbl_value,
                key=f"line_legend_{i}"
            )

        ma_cols = st.columns(2)
        with ma_cols[0]:
            plot_moving_avg = st.checkbox(
                f"Plot moving average (Series {i+1})", 
                value=plot_ma_value,
                key=f"line_ma_toggle_{i}"
            )
        if plot_moving_avg:
            with ma_cols[1]:
                ma_n = st.slider(
                    f"MA Window (Series {i+1})", 
                    min_value=2, 
                    max_value=200, 
                    value=ma_window_value, 
                    step=1, 
                    key=f"line_ma_n_{i}"
                )
            ma_color_cols = st.columns(2)
            with ma_color_cols[0]:
                ma_color_named = st.selectbox(
                    f"MA Named Color (Series {i+1})",
                    NAMED_COLORS,
                    index=NAMED_COLORS.index(ma_color_value) 
                    if ma_color_value in NAMED_COLORS else 0,
                    key=f"line_ma_color_named_{i}"
                )
            with ma_color_cols[1]:
                ma_color_custom = st.text_input(
                    f"MA Custom Color (Series {i+1})",
                    value=ma_color_custom_value,
                    key=f"line_ma_color_custom_{i}"
                )
            ma_legend = st.text_input(
                f"MA Legend (Series {i+1})",
                value=ma_legend_value,
                key=f"line_ma_legend_{i}"
            )
        else:
            ma_n = 1
            ma_color_named = "red"
            ma_color_custom = ""
            ma_legend = ""

        # Error mode for this line
        if "add_error_bars" not in line_default:
            line_default["add_error_bars"] = False
        error_mode = error_mode_value

        line_params_list.append({
            'column': col_choice,
            'color': get_chosen_color(color_named, color_custom),
            'color_named': color_named,
            'color_custom': color_custom,
            'linewidth': lw_val,
            'label': legend_name,
            'plot_ma': plot_moving_avg,
            'ma_window': ma_n,
            'ma_color': get_chosen_color(ma_color_named, ma_color_custom),
            'ma_color_named': ma_color_named,
            'ma_color_custom': ma_color_custom,
            'ma_label': ma_legend,
            'error_mode': error_mode,
            'yerr_column': yerr_col_value,
            'xerr_column': xerr_col_value
        })
        columns_in_use_for_nans.append(col_choice)  # main data col

    add_error_bars = st.checkbox("Add error bars", line_default["add_error_bars"])
    if add_error_bars:
        st.write("#### Global Numeric Error (if a line uses 'Use global numeric')")
        err_cols1 = st.columns(2)
        with err_cols1[0]:
            yerr_val = st.number_input(
                "Global magnitude of error (Y)",
                min_value=0.0, 
                value=line_default["yerr_val"], 
                step=0.1
            )
        with err_cols1[1]:
            xerr_val = st.number_input(
                "Global magnitude of error (X)",
                min_value=0.0, 
                value=line_default["xerr_val"], 
                step=0.1
            )
        err_cols2 = st.columns(2)
        with err_cols2[0]:
            ecolor_named = st.selectbox(
                "Error bar color (named)",
                NAMED_COLORS,
                index=NAMED_COLORS.index(line_default["ecolor_named"]) 
                if line_default["ecolor_named"] in NAMED_COLORS else 0
            )
            ecolor_custom = st.text_input(
                "Error bar custom color",
                line_default["ecolor_custom"]
            )
            ecolor_final = get_chosen_color(ecolor_named, ecolor_custom)
        with err_cols2[1]:
            elinewidth_val = st.slider(
                "Error bar line width",
                min_value=0.1, 
                max_value=5.0, 
                value=line_default["elinewidth_val"], 
                step=0.1
            )
        err_cols3 = st.columns(2)
        with err_cols3[0]:
            capsize_val = st.slider(
                "Cap size",
                min_value=0, 
                max_value=10, 
                value=line_default["capsize_val"], 
                step=1
            )
        with err_cols3[1]:
            capthick_val = st.slider(
                "Cap thickness",
                min_value=0.1, 
                max_value=5.0, 
                value=line_default["capthick_val"], 
                step=0.1
            )

        st.write("##### Per-line Error Mode:")
        for i in range(series_count):
            emode_cols = st.columns(3)
            current_emode = line_params_list[i]["error_mode"]
            with emode_cols[0]:
                new_emode = st.selectbox(
                    f"Line {i+1} error mode:",
                    ["None","Use global numeric","Column-based"],
                    index=["None","Use global numeric","Column-based"].index(current_emode)
                    if current_emode in ["None","Use global numeric","Column-based"] else 1,
                    key=f"line_err_mode_{i}"
                )
            line_params_list[i]["error_mode"] = new_emode

            if new_emode == "Column-based":
                # Choose Y-err column
                with emode_cols[1]:
                    yerr_col_choice = line_params_list[i]["yerr_column"]
                    yerr_col = st.selectbox(
                        f"Line {i+1} Y-err column",
                        [""] + multi_file_columns,
                        index=([""] + multi_file_columns).index(yerr_col_choice) 
                        if yerr_col_choice in multi_file_columns else 0,
                        key=f"line_err_ycol_{i}"
                    )
                line_params_list[i]["yerr_column"] = yerr_col

                # Choose X-err column
                with emode_cols[2]:
                    xerr_col_choice = line_params_list[i]["xerr_column"]
                    xerr_col = st.selectbox(
                        f"Line {i+1} X-err column",
                        [""] + multi_file_columns,
                        index=([""] + multi_file_columns).index(xerr_col_choice) 
                        if xerr_col_choice in multi_file_columns else 0,
                        key=f"line_err_xcol_{i}"
                    )
                line_params_list[i]["xerr_column"] = xerr_col
    else:
        yerr_val = line_default["yerr_val"]
        xerr_val = line_default["xerr_val"]
        ecolor_named = line_default["ecolor_named"]
        ecolor_custom = line_default["ecolor_custom"]
        ecolor_final = get_chosen_color(ecolor_named, ecolor_custom)
        elinewidth_val = line_default["elinewidth_val"]
        capsize_val = line_default["capsize_val"]
        capthick_val = line_default["capthick_val"]

    nan_method = st.selectbox(
        "How to treat NaN values (for plot only)",
        [
            "Ignore",
            "Drop rows",
            "Fill with mean",
            "Fill with most common value",
            "Replace with 0",
            "Interpolate",
            "KNN (nearest 4 points)",
            "Replace with nearest point"
        ],
        index=[
            "Ignore",
            "Drop rows",
            "Fill with mean",
            "Fill with most common value",
            "Replace with 0",
            "Interpolate",
            "KNN (nearest 4 points)",
            "Replace with nearest point"
        ].index(line_default["nan_method"]) 
        if line_default["nan_method"] in [
            "Ignore",
            "Drop rows",
            "Fill with mean",
            "Fill with most common value",
            "Replace with 0",
            "Interpolate",
            "KNN (nearest 4 points)",
            "Replace with nearest point"
        ] else 0
    )

    outlier_method = st.selectbox(
        "How to treat outliers (for plot only)",
        [
            "Ignore",
            "Cap 0.1%",
            "Cap 1%",
            "Cap 5%",
            "Outside 1.5×IQR",
            "Remove rows (|z-score|>3)"
        ],
        index=[
            "Ignore",
            "Cap 0.1%",
            "Cap 1%",
            "Cap 5%",
            "Outside 1.5×IQR",
            "Remove rows (|z-score|>3)"
        ].index(line_default["outlier_method"]) 
        if line_default["outlier_method"] in [
            "Ignore",
            "Cap 0.1%",
            "Cap 1%",
            "Cap 5%",
            "Outside 1.5×IQR",
            "Remove rows (|z-score|>3)"
        ] else 0
    )

    # Check for NaNs in each chosen column
    nan_flags = []
    for lp in line_params_list:
        file_and_col = lp["column"]
        fname, real_col = file_and_col.split("||", 1)
        df_check = df_dict[fname].iloc[row_start:row_end].copy()
        if real_col in df_check.columns and df_check[real_col].isna().any():
            nan_flags.append(file_and_col)

        # Also check error columns if used
        if add_error_bars and lp["error_mode"] == "Column-based":
            if lp["yerr_column"]:
                f_yerr, r_yerr = lp["yerr_column"].split("||",1)
                df_check_err = df_dict[f_yerr].iloc[row_start:row_end].copy()
                if r_yerr in df_check_err.columns and df_check_err[r_yerr].isna().any():
                    nan_flags.append(lp["yerr_column"])
            if lp["xerr_column"]:
                f_xerr, r_xerr = lp["xerr_column"].split("||",1)
                df_check_err = df_dict[f_xerr].iloc[row_start:row_end].copy()
                if r_xerr in df_check_err.columns and df_check_err[r_xerr].isna().any():
                    nan_flags.append(lp["xerr_column"])

    if nan_flags:
        st.warning(f"Some chosen columns contain NaN values: {nan_flags}")

    legend_used = False

    for lp in line_params_list:
        file_and_col = lp["column"]
        fname, real_col = file_and_col.split("||", 1)
        df_subset = df_dict[fname].iloc[row_start:row_end].copy()

        df_subset = handle_nans(df_subset, [real_col], nan_method)
        df_subset = handle_outliers(df_subset, [real_col], outlier_method)

        original_x = pd.Series(df_subset.index, index=df_subset.index)
        x_transformed = transform_series(original_x, x_scale, label="X")

        if real_col not in df_subset.columns:
            continue
        y_original = df_subset[real_col]
        y_transformed = transform_series(y_original, y_scale, label=real_col)

        common_idx = x_transformed.index.intersection(y_transformed.index)

        local_xerr = None
        local_yerr = None

        if add_error_bars and lp["error_mode"] != "None":
            if lp["error_mode"] == "Use global numeric":
                local_xerr = xerr_val if xerr_val > 0 else None
                local_yerr = yerr_val if yerr_val > 0 else None

            elif lp["error_mode"] == "Column-based":
                if lp["yerr_column"]:
                    fy, ry = lp["yerr_column"].split("||",1)
                    df_err_y = df_dict[fy].iloc[row_start:row_end].copy()
                    df_err_y = handle_nans(df_err_y, [ry], nan_method)
                    df_err_y = handle_outliers(df_err_y, [ry], outlier_method)
                    # transform error column with same scale as Y
                    err_y_series = transform_series(df_err_y[ry], y_scale, label=f"{ry}_err")
                    err_y_series = err_y_series.abs()  # <-- NEW: take absolute value
                    common_idx = common_idx.intersection(err_y_series.index)
                    local_yerr = err_y_series.loc[common_idx]

                if lp["xerr_column"]:
                    fx, rx = lp["xerr_column"].split("||",1)
                    df_err_x = df_dict[fx].iloc[row_start:row_end].copy()
                    df_err_x = handle_nans(df_err_x, [rx], nan_method)
                    df_err_x = handle_outliers(df_err_x, [rx], outlier_method)
                    # transform error column with same scale as X
                    err_x_series = transform_series(df_err_x[rx], x_scale, label=f"{rx}_err")
                    err_x_series = err_x_series.abs()  # <-- NEW: take absolute value
                    common_idx = common_idx.intersection(err_x_series.index)
                    local_xerr = err_x_series.loc[common_idx]

        x_plot = x_transformed.loc[common_idx]
        y_plot = y_transformed.loc[common_idx]

        fmt_string = '-o' if marker_style else '-'
        if add_error_bars and lp["error_mode"] != "None":
            ax.errorbar(
                x_plot,
                y_plot,
                xerr=local_xerr,
                yerr=local_yerr,
                fmt=fmt_string,
                color=lp["color"],
                ecolor=ecolor_final if ecolor_final else lp["color"],
                linewidth=lp['linewidth'],
                elinewidth=elinewidth_val if elinewidth_val else lp['linewidth'],
                capsize=capsize_val,
                capthick=capthick_val,
                label=lp["label"]
            )
        else:
            ax.plot(
                x_plot,
                y_plot,
                color=lp["color"],
                linestyle='-',
                marker=marker_style,
                linewidth=lp['linewidth'],
                label=lp["label"]
            )

        if series_count > 1 or lp["label"]:
            legend_used = True

        if lp['plot_ma']:
            y_ma = y_original.rolling(window=lp['ma_window'], min_periods=1).mean()
            y_ma_transformed = transform_series(y_ma, y_scale, label=f"{real_col}_ma")
            ma_common_idx = x_transformed.index.intersection(y_ma_transformed.index)
            x_plot_ma = x_transformed.loc[ma_common_idx]
            y_plot_ma = y_ma_transformed.loc[ma_common_idx]

            ax.plot(
                x_plot_ma,
                y_plot_ma,
                color=lp['ma_color'],
                linestyle='--',
                marker=None,
                linewidth=lp['linewidth'],
                label=lp['ma_label'] if lp['ma_label'] else f"{real_col} (MA)"
            )
            legend_used = True

    if series_count > 1:
        default_title = "Multiple columns across multiple files"
        default_ylabel = "values"
    else:
        if line_params_list:
            default_title = f"{line_params_list[0]['column']} depending on index"
            default_ylabel = line_params_list[0]['column']
    default_xlabel = "index"

    ax.grid(show_grid)
    if legend_used:
        ax.legend(fontsize=legend_font)

    st.write("#### Save / Delete Line Preset")
    preset_name_input = st.text_input(
        "Preset name",
        value=selected_preset_name if selected_preset_name != "None" else "",
        key=f"{graph_type}_preset_name_input"
    )
    if st.button("Save this preset", key=f"{graph_type}_save_preset_btn"):
        new_preset_data = {
            "show_grid": show_grid,
            "add_marker": add_marker,
            "x_scale": x_scale,
            "y_scale": y_scale,
            "series_count": series_count,
            "line_params": line_params_list,
            "nan_method": nan_method,
            "outlier_method": outlier_method,
            "add_error_bars": add_error_bars,
            "yerr_val": yerr_val if add_error_bars else line_default["yerr_val"],
            "xerr_val": xerr_val if add_error_bars else line_default["xerr_val"],
            "ecolor_named": ecolor_named,
            "ecolor_custom": ecolor_custom,
            "elinewidth_val": elinewidth_val,
            "capsize_val": capsize_val,
            "capthick_val": capthick_val
        }
        if not preset_name_input.strip():
            st.error("Please provide a valid preset name.")
        else:
            st.session_state.presets.setdefault(graph_type, {})[preset_name_input] = new_preset_data
            save_presets(st.session_state.presets)
            st.success(f"Preset '{preset_name_input}' saved!")

    if selected_preset_name != "None":
        if st.button("Delete this preset", key=f"{graph_type}_delete_preset_btn"):
            if preset_name_input in st.session_state.presets[graph_type]:
                del st.session_state.presets[graph_type][preset_name_input]
                save_presets(st.session_state.presets)
                st.success(f"Preset '{preset_name_input}' deleted!")


############################################################################
# BAR (only uses primary file)
############################################################################
elif graph_type == "Bar":
    bar_default = {
        "col": all_columns_primary[0] if all_columns_primary else "",
        "color_named": "blue",
        "color_custom": "",
        "order_opt": "No sorting",
        "show_grid": False,
        "show_vals": False,
        "vals_font": 10,
        "nan_method": "Ignore",
        "outlier_method": "Ignore"
    }
    if selected_preset_name != "None":
        loaded = current_graph_presets[selected_preset_name]
        for k, v in loaded.items():
            if k in bar_default:
                bar_default[k] = v

    col = st.selectbox(
        "Select column for Bar chart (primary file only)",
        all_columns_primary,
        index=all_columns_primary.index(bar_default["col"]) if bar_default["col"] in all_columns_primary else 0
    )
    bar_cols_1 = st.columns(2)
    with bar_cols_1[0]:
        color_named = st.selectbox(
            "Named Color", 
            NAMED_COLORS, 
            index=NAMED_COLORS.index(bar_default["color_named"]) 
            if bar_default["color_named"] in NAMED_COLORS else 0
        )
        color_custom = st.text_input("Custom color (overrides)", bar_default["color_custom"])
    with bar_cols_1[1]:
        order_opt = st.selectbox(
            "Order bars", 
            ["No sorting","Smallest→largest","Largest→smallest","Alphabetical (A→Z)","Alphabetical (Z→A)"],
            index=["No sorting","Smallest→largest","Largest→smallest","Alphabetical (A→Z)","Alphabetical (Z→A)"].index(bar_default["order_opt"]) 
            if bar_default["order_opt"] in ["No sorting","Smallest→largest","Largest→smallest","Alphabetical (A→Z)","Alphabetical (Z→A)"] 
            else 0
        )

    bar_cols_2 = st.columns(2)
    with bar_cols_2[0]:
        show_grid = st.checkbox("Turn grid on", bar_default["show_grid"])
    with bar_cols_2[1]:
        show_vals = st.checkbox("Show values on top", bar_default["show_vals"])

    vals_font = st.slider("Values Font size", min_value=6, max_value=30, value=bar_default["vals_font"], step=1)

    c_final = get_chosen_color(color_named, color_custom)

    subset_primary = df_primary.iloc[row_start:row_end].copy()
    columns_in_use = [col]
    has_nans, mismatch, _ = check_columns_for_nans_and_length(subset_primary, columns_in_use)
    if has_nans:
        st.warning("The chosen column has NaN values.")
    if mismatch:
        st.warning("The chosen column has a different number of valid points than expected.")

    nan_method = st.selectbox(
        "How to treat NaN values (for plot only)",
        [
            "Ignore",
            "Drop rows",
            "Fill with mean",
            "Fill with most common value",
            "Replace with 0",
            "Interpolate",
            "KNN (nearest 4 points)",
            "Replace with nearest point"
        ],
        index=[
            "Ignore",
            "Drop rows",
            "Fill with mean",
            "Fill with most common value",
            "Replace with 0",
            "Interpolate",
            "KNN (nearest 4 points)",
            "Replace with nearest point"
        ].index(bar_default["nan_method"]) 
        if bar_default["nan_method"] in [
            "Ignore",
            "Drop rows",
            "Fill with mean",
            "Fill with most common value",
            "Replace with 0",
            "Interpolate",
            "KNN (nearest 4 points)",
            "Replace with nearest point"
        ] else 0
    )

    outlier_method = st.selectbox(
        "How to treat outliers (for plot only)",
        [
            "Ignore",
            "Cap 0.1%",
            "Cap 1%",
            "Cap 5%",
            "Outside 1.5×IQR",
            "Remove rows (|z-score|>3)"
        ],
        index=[
            "Ignore",
            "Cap 0.1%",
            "Cap 1%",
            "Cap 5%",
            "Outside 1.5×IQR",
            "Remove rows (|z-score|>3)"
        ].index(bar_default["outlier_method"]) 
        if bar_default["outlier_method"] in [
            "Ignore",
            "Cap 0.1%",
            "Cap 1%",
            "Cap 5%",
            "Outside 1.5×IQR",
            "Remove rows (|z-score|>3)"
        ] else 0
    )

    subset_for_plot = handle_nans(subset_primary.copy(), columns_in_use, nan_method)
    subset_for_plot = handle_outliers(subset_for_plot, columns_in_use, outlier_method)

    if pd.api.types.is_numeric_dtype(subset_for_plot[col]):
        default_title = f"{col} depending on index"
        xvals = subset_for_plot.index
        yvals = subset_for_plot[col]
        bars = ax.bar(xvals, yvals, color=c_final)
        default_xlabel = "index"
        default_ylabel = col
        if show_vals:
            ax.bar_label(bars, fontsize=vals_font)
    else:
        counts = subset_for_plot[col].value_counts(dropna=False)
        if order_opt == 'Smallest→largest':
            counts = counts.sort_values(ascending=True)
        elif order_opt == 'Largest→smallest':
            counts = counts.sort_values(ascending=False)
        elif order_opt == 'Alphabetical (A→Z)':
            counts = counts.sort_index(ascending=True)
        elif order_opt == 'Alphabetical (Z→A)':
            counts = counts.sort_index(ascending=False)

        default_title = f"Count of {col}"
        bars = ax.bar(counts.index.astype(str), counts.values, color=c_final)
        default_xlabel = col
        default_ylabel = "Count"
        if show_vals:
            ax.bar_label(bars, fontsize=vals_font)

    ax.grid(show_grid)

    st.write("#### Save / Delete Bar Preset")
    preset_name_input = st.text_input(
        "Preset name",
        value=selected_preset_name if selected_preset_name != "None" else "",
        key=f"{graph_type}_preset_name_input"
    )
    if st.button("Save this preset", key=f"{graph_type}_save_preset_btn"):
        new_preset_data = {
            "col": col,
            "color_named": color_named,
            "color_custom": color_custom,
            "order_opt": order_opt,
            "show_grid": show_grid,
            "show_vals": show_vals,
            "vals_font": vals_font,
            "nan_method": nan_method,
            "outlier_method": outlier_method
        }
        if not preset_name_input.strip():
            st.error("Please provide a valid preset name.")
        else:
            st.session_state.presets.setdefault(graph_type, {})[preset_name_input] = new_preset_data
            save_presets(st.session_state.presets)
            st.success(f"Preset '{preset_name_input}' saved!")

    if selected_preset_name != "None":
        if st.button("Delete this preset", key=f"{graph_type}_delete_preset_btn"):
            if preset_name_input in st.session_state.presets[graph_type]:
                del st.session_state.presets[graph_type][preset_name_input]
                save_presets(st.session_state.presets)
                st.success(f"Preset '{preset_name_input}' deleted!")


############################################################################
# PIE (only uses primary file)
############################################################################
elif graph_type == "Pie":
    pie_default = {
        "col": all_columns_primary[0] if all_columns_primary else "",
        "autopct_choice": "1 decimal",
        "angle": 0,
        "nan_method": "Ignore",
        "outlier_method": "Ignore"
    }
    if selected_preset_name != "None":
        loaded = current_graph_presets[selected_preset_name]
        for k, v in loaded.items():
            if k in pie_default:
                pie_default[k] = v

    col = st.selectbox(
        "Select column for Pie chart (primary file only)",
        all_columns_primary,
        index=all_columns_primary.index(pie_default["col"]) if pie_default["col"] in all_columns_primary else 0
    )
    pie_cols = st.columns(2)
    with pie_cols[0]:
        autopct_choice = st.selectbox(
            "Autopct", 
            ["none","no decimals","1 decimal","2 decimals"], 
            index=["none","no decimals","1 decimal","2 decimals"].index(pie_default["autopct_choice"]) 
            if pie_default["autopct_choice"] in ["none","no decimals","1 decimal","2 decimals"] else 2
        )
    with pie_cols[1]:
        angle = st.slider("Rotation angle", min_value=0, max_value=360, step=10, value=pie_default["angle"])

    if autopct_choice == 'none':
        autopct_val = None
    elif autopct_choice == 'no decimals':
        autopct_val = '%1.0f%%'
    elif autopct_choice == '1 decimal':
        autopct_val = '%1.1f%%'
    elif autopct_choice == '2 decimals':
        autopct_val = '%1.2f%%'
    else:
        autopct_val = None

    default_title = f"Pie of {col}"

    subset_primary = df_primary.iloc[row_start:row_end].copy()
    columns_in_use = [col]
    has_nans, mismatch, _ = check_columns_for_nans_and_length(subset_primary, columns_in_use)
    if has_nans:
        st.warning("The chosen column has NaN values.")
    if mismatch:
        st.warning("The chosen column has a different number of valid points than expected.")

    nan_method = st.selectbox(
        "How to treat NaN values (for plot only)",
        [
            "Ignore",
            "Drop rows",
            "Fill with mean",
            "Fill with most common value",
            "Replace with 0",
            "Interpolate",
            "KNN (nearest 4 points)",
            "Replace with nearest point"
        ],
        index=[
            "Ignore",
            "Drop rows",
            "Fill with mean",
            "Fill with most common value",
            "Replace with 0",
            "Interpolate",
            "KNN (nearest 4 points)",
            "Replace with nearest point"
        ].index(pie_default["nan_method"]) 
        if pie_default["nan_method"] in [
            "Ignore",
            "Drop rows",
            "Fill with mean",
            "Fill with most common value",
            "Replace with 0",
            "Interpolate",
            "KNN (nearest 4 points)",
            "Replace with nearest point"
        ] else 0
    )

    outlier_method = st.selectbox(
        "How to treat outliers (for plot only)",
        [
            "Ignore",
            "Cap 0.1%",
            "Cap 1%",
            "Cap 5%",
            "Outside 1.5×IQR",
            "Remove rows (|z-score|>3)"
        ],
        index=[
            "Ignore",
            "Cap 0.1%",
            "Cap 1%",
            "Cap 5%",
            "Outside 1.5×IQR",
            "Remove rows (|z-score|>3)"
        ].index(pie_default["outlier_method"]) 
        if pie_default["outlier_method"] in [
            "Ignore",
            "Cap 0.1%",
            "Cap 1%",
            "Cap 5%",
            "Outside 1.5×IQR",
            "Remove rows (|z-score|>3)"
        ] else 0
    )

    subset_for_plot = handle_nans(subset_primary.copy(), columns_in_use, nan_method)
    subset_for_plot = handle_outliers(subset_for_plot, columns_in_use, outlier_method)

    if pd.api.types.is_numeric_dtype(subset_for_plot[col]):
        data = subset_for_plot[col].dropna()
        if data.empty:
            st.warning("No valid numeric data for Pie.")
        else:
            labels = data.index
            values = data.values
            patches, texts, autotexts = ax.pie(
                values,
                labels=labels,
                autopct=autopct_val,
                startangle=angle
            )
            for t in texts:
                t.set_fontsize(tick_font)
            if autotexts:
                for t in autotexts:
                    t.set_fontsize(legend_font)
    else:
        counts = subset_for_plot[col].value_counts(dropna=False)
        labels = counts.index.astype(str)
        values = counts.values
        patches, texts, autotexts = ax.pie(
            values,
            labels=labels,
            autopct=autopct_val,
            startangle=angle
        )
        for t in texts:
            t.set_fontsize(tick_font)
        if autotexts:
            for t in autotexts:
                t.set_fontsize(legend_font)

    st.write("#### Save / Delete Pie Preset")
    preset_name_input = st.text_input(
        "Preset name",
        value=selected_preset_name if selected_preset_name != "None" else "",
        key=f"{graph_type}_preset_name_input"
    )
    if st.button("Save this preset", key=f"{graph_type}_save_preset_btn"):
        new_preset_data = {
            "col": col,
            "autopct_choice": autopct_choice,
            "angle": angle,
            "nan_method": nan_method,
            "outlier_method": outlier_method
        }
        if not preset_name_input.strip():
            st.error("Please provide a valid preset name.")
        else:
            st.session_state.presets.setdefault(graph_type, {})[preset_name_input] = new_preset_data
            save_presets(st.session_state.presets)
            st.success(f"Preset '{preset_name_input}' saved!")

    if selected_preset_name != "None":
        if st.button("Delete this preset", key=f"{graph_type}_delete_preset_btn"):
            if preset_name_input in st.session_state.presets[graph_type]:
                del st.session_state.presets[graph_type][preset_name_input]
                save_presets(st.session_state.presets)
                st.success(f"Preset '{preset_name_input}' deleted!")


############################################################################
# DISTRIBUTION (KDE) (only uses primary file)
############################################################################
elif graph_type == "Distribution":
    dist_default = {
        "col": all_columns_primary[0] if all_columns_primary else "",
        "color_named": "blue",
        "color_custom": "",
        "fill_val": True,
        "nan_method": "Ignore",
        "outlier_method": "Ignore"
    }
    if selected_preset_name != "None":
        loaded = current_graph_presets[selected_preset_name]
        for k, v in loaded.items():
            if k in dist_default:
                dist_default[k] = v

    col = st.selectbox(
        "Select column for Distribution (KDE) (primary file only)",
        all_columns_primary,
        index=all_columns_primary.index(dist_default["col"]) if dist_default["col"] in all_columns_primary else 0
    )
    dist_cols = st.columns(2)
    with dist_cols[0]:
        color_named = st.selectbox(
            "Named Color", 
            NAMED_COLORS, 
            index=NAMED_COLORS.index(dist_default["color_named"]) 
            if dist_default["color_named"] in NAMED_COLORS else 0
        )
    with dist_cols[1]:
        color_custom = st.text_input("Custom color (overrides)", dist_default["color_custom"])
    fill_val = st.checkbox("Fill", dist_default["fill_val"])

    c_final = get_chosen_color(color_named, color_custom)

    default_title = f"Distribution of {col}"
    default_xlabel = col
    default_ylabel = "Density"

    subset_primary = df_primary.iloc[row_start:row_end].copy()
    columns_in_use = [col]
    has_nans, mismatch, _ = check_columns_for_nans_and_length(subset_primary, columns_in_use)
    if has_nans:
        st.warning("The chosen column has NaN values.")
    if mismatch:
        st.warning("The chosen column has a different number of valid points than expected.")

    nan_method = st.selectbox(
        "How to treat NaN values (for plot only)",
        [
            "Ignore",
            "Drop rows",
            "Fill with mean",
            "Fill with most common value",
            "Replace with 0",
            "Interpolate",
            "KNN (nearest 4 points)",
            "Replace with nearest point"
        ],
        index=[
            "Ignore",
            "Drop rows",
            "Fill with mean",
            "Fill with most common value",
            "Replace with 0",
            "Interpolate",
            "KNN (nearest 4 points)",
            "Replace with nearest point"
        ].index(dist_default["nan_method"]) 
        if dist_default["nan_method"] in [
            "Ignore",
            "Drop rows",
            "Fill with mean",
            "Fill with most common value",
            "Replace with 0",
            "Interpolate",
            "KNN (nearest 4 points)",
            "Replace with nearest point"
        ] else 0
    )

    outlier_method = st.selectbox(
        "How to treat outliers (for plot only)",
        [
            "Ignore",
            "Cap 0.1%",
            "Cap 1%",
            "Cap 5%",
            "Outside 1.5×IQR",
            "Remove rows (|z-score|>3)"
        ],
        index=[
            "Ignore",
            "Cap 0.1%",
            "Cap 1%",
            "Cap 5%",
            "Outside 1.5×IQR",
            "Remove rows (|z-score|>3)"
        ].index(dist_default["outlier_method"]) 
        if dist_default["outlier_method"] in [
            "Ignore",
            "Cap 0.1%",
            "Cap 1%",
            "Cap 5%",
            "Outside 1.5×IQR",
            "Remove rows (|z-score|>3)"
        ] else 0
    )

    subset_for_plot = handle_nans(subset_primary.copy(), columns_in_use, nan_method)
    subset_for_plot = handle_outliers(subset_for_plot, columns_in_use, outlier_method)

    if not pd.api.types.is_numeric_dtype(subset_for_plot[col]):
        st.warning("Selected column is not numeric. Distribution may fail.")
    else:
        data_ = subset_for_plot[col].dropna()
        if data_.empty:
            st.warning("No valid data to plot distribution.")
        else:
            sns.kdeplot(data_, fill=fill_val, color=c_final, label=col, ax=ax)
            leg = ax.legend()
            if leg:
                for txt in leg.get_texts():
                    txt.set_fontsize(legend_font)

    st.write("#### Save / Delete Distribution Preset")
    preset_name_input = st.text_input(
        "Preset name",
        value=selected_preset_name if selected_preset_name != "None" else "",
        key=f"{graph_type}_preset_name_input"
    )
    if st.button("Save this preset", key=f"{graph_type}_save_preset_btn"):
        new_preset_data = {
            "col": col,
            "color_named": color_named,
            "color_custom": color_custom,
            "fill_val": fill_val,
            "nan_method": nan_method,
            "outlier_method": outlier_method
        }
        if not preset_name_input.strip():
            st.error("Please provide a valid preset name.")
        else:
            st.session_state.presets.setdefault(graph_type, {})[preset_name_input] = new_preset_data
            save_presets(st.session_state.presets)
            st.success(f"Preset '{preset_name_input}' saved!")

    if selected_preset_name != "None":
        if st.button("Delete this preset", key=f"{graph_type}_delete_preset_btn"):
            if preset_name_input in st.session_state.presets[graph_type]:
                del st.session_state.presets[graph_type][preset_name_input]
                save_presets(st.session_state.presets)
                st.success(f"Preset '{preset_name_input}' deleted!")


############################################################################
# BOXPLOT (only uses primary file)
############################################################################
elif graph_type == "Boxplot":
    box_default = {
        "ycol": all_columns_primary[0] if all_columns_primary else "",
        "hue_col": "None",
        "orientation": "vertical",
        "cmap_choice": "None",
        "color_named": "blue",
        "color_custom": "",
        "show_grid": False,
        "nan_method": "Ignore",
        "outlier_method": "Ignore"
    }
    if selected_preset_name != "None":
        loaded = current_graph_presets[selected_preset_name]
        for k, v in loaded.items():
            if k in box_default:
                box_default[k] = v

    st.write("Boxplot: uses only primary file. Choose 1 numeric Y column. Optionally pick a 'Hue'.")
    ycol = st.selectbox(
        "Y Column",
        all_columns_primary,
        index=all_columns_primary.index(box_default["ycol"]) if box_default["ycol"] in all_columns_primary else 0
    )
    hue_opt = ["None"] + all_columns_primary
    hue_col = st.selectbox(
        "Hue (or None)",
        hue_opt,
        index=hue_opt.index(box_default["hue_col"]) if box_default["hue_col"] in hue_opt else 0
    )
    orientation = st.selectbox(
        "Orientation", 
        ["vertical","horizontal"], 
        index=["vertical","horizontal"].index(box_default["orientation"]) 
        if box_default["orientation"] in ["vertical","horizontal"] else 0
    )
    cmap_choice = st.selectbox(
        "Colormap", 
        CMAPS, 
        index=CMAPS.index(box_default["cmap_choice"]) if box_default["cmap_choice"] in CMAPS else 0
    )

    box_cols_1 = st.columns(2)
    with box_cols_1[0]:
        color_named = st.selectbox(
            "Named Color", 
            NAMED_COLORS, 
            index=NAMED_COLORS.index(box_default["color_named"]) 
            if box_default["color_named"] in NAMED_COLORS else 0
        )
    with box_cols_1[1]:
        color_custom = st.text_input("Custom color (overrides)", box_default["color_custom"])

    show_grid = st.checkbox("Turn grid on", box_default["show_grid"])

    if hue_col == "None":
        hue_col = None

    color_final = get_chosen_color(color_named, color_custom)

    default_title = f"Boxplot of {ycol}"
    subset_primary = df_primary.iloc[row_start:row_end].copy()
    columns_in_use = [ycol]
    has_nans, mismatch, _ = check_columns_for_nans_and_length(subset_primary, columns_in_use)
    if has_nans:
        st.warning("The chosen Y column has NaN values.")
    if mismatch:
        st.warning("The chosen column has a different number of valid points than expected.")

    nan_method = st.selectbox(
        "How to treat NaN values (for plot only)",
        [
            "Ignore",
            "Drop rows",
            "Fill with mean",
            "Fill with most common value",
            "Replace with 0",
            "Interpolate",
            "KNN (nearest 4 points)",
            "Replace with nearest point"
        ],
        index=[
            "Ignore",
            "Drop rows",
            "Fill with mean",
            "Fill with most common value",
            "Replace with 0",
            "Interpolate",
            "KNN (nearest 4 points)",
            "Replace with nearest point"
        ].index(box_default["nan_method"]) 
        if box_default["nan_method"] in [
            "Ignore",
            "Drop rows",
            "Fill with mean",
            "Fill with most common value",
            "Replace with 0",
            "Interpolate",
            "KNN (nearest 4 points)",
            "Replace with nearest point"
        ] else 0
    )

    outlier_method = st.selectbox(
        "How to treat outliers (for plot only)",
        [
            "Ignore",
            "Cap 0.1%",
            "Cap 1%",
            "Cap 5%",
            "Outside 1.5×IQR",
            "Remove rows (|z-score|>3)"
        ],
        index=[
            "Ignore",
            "Cap 0.1%",
            "Cap 1%",
            "Cap 5%",
            "Outside 1.5×IQR",
            "Remove rows (|z-score|>3)"
        ].index(box_default["outlier_method"]) 
        if box_default["outlier_method"] in [
            "Ignore",
            "Cap 0.1%",
            "Cap 1%",
            "Cap 5%",
            "Outside 1.5×IQR",
            "Remove rows (|z-score|>3)"
        ] else 0
    )

    subset_for_plot = handle_nans(subset_primary.copy(), columns_in_use, nan_method)
    subset_for_plot = handle_outliers(subset_for_plot, columns_in_use, outlier_method)

    if not pd.api.types.is_numeric_dtype(subset_for_plot[ycol]):
        st.warning("Y column must be numeric for Boxplot.")
    else:
        palette = None
        if hue_col and cmap_choice != 'None':
            palette = sns.color_palette(cmap_choice)

        if orientation == 'vertical':
            x_var = hue_col
            y_var = ycol
            orient = None
        else:
            x_var = ycol
            y_var = hue_col
            orient = 'h'

        sns.boxplot(
            data=subset_for_plot,
            x=x_var,
            y=y_var,
            palette=palette if hue_col else None,
            color=color_final if (not hue_col or not palette) else None,
            orient=orient,
            ax=ax
        )
        if orientation == 'vertical':
            default_xlabel = hue_col if hue_col else ""
            default_ylabel = ycol
        else:
            default_xlabel = ycol
            default_ylabel = hue_col if hue_col else ""
        ax.grid(show_grid)

    st.write("#### Save / Delete Boxplot Preset")
    preset_name_input = st.text_input(
        "Preset name",
        value=selected_preset_name if selected_preset_name != "None" else "",
        key=f"{graph_type}_preset_name_input"
    )
    if st.button("Save this preset", key=f"{graph_type}_save_preset_btn"):
        new_preset_data = {
            "ycol": ycol,
            "hue_col": hue_col if hue_col else "None",
            "orientation": orientation,
            "cmap_choice": cmap_choice,
            "color_named": color_named,
            "color_custom": color_custom,
            "show_grid": show_grid,
            "nan_method": nan_method,
            "outlier_method": outlier_method
        }
        if not preset_name_input.strip():
            st.error("Please provide a valid preset name.")
        else:
            st.session_state.presets.setdefault(graph_type, {})[preset_name_input] = new_preset_data
            save_presets(st.session_state.presets)
            st.success(f"Preset '{preset_name_input}' saved!")

    if selected_preset_name != "None":
        if st.button("Delete this preset", key=f"{graph_type}_delete_preset_btn"):
            if preset_name_input in st.session_state.presets[graph_type]:
                del st.session_state.presets[graph_type][preset_name_input]
                save_presets(st.session_state.presets)
                st.success(f"Preset '{preset_name_input}' deleted!")


############################################################################
# VIOLIN PLOT (only uses primary file)
############################################################################
elif graph_type == "Violin Plot":
    violin_default = {
        "ycol": all_columns_primary[0] if all_columns_primary else "",
        "hue_col": "None",
        "side_choice": "1-sided",
        "scale_ui": "Proportional area",
        "sensitivity": 1.0,
        "cmap_choice": "None",
        "color_named": "blue",
        "color_custom": "",
        "show_grid": False,
        "nan_method": "Ignore",
        "outlier_method": "Ignore"
    }
    if selected_preset_name != "None":
        loaded = current_graph_presets[selected_preset_name]
        for k, v in loaded.items():
            if k in violin_default:
                violin_default[k] = v

    st.write("Violin Plot: uses only primary file. Pick a numeric Y column. Optionally pick Hue.")
    ycol = st.selectbox(
        "Y Column",
        all_columns_primary,
        index=all_columns_primary.index(violin_default["ycol"]) if violin_default["ycol"] in all_columns_primary else 0
    )
    hue_opt = ["None"] + all_columns_primary
    hue_col = st.selectbox(
        "Hue (or None)",
        hue_opt,
        index=hue_opt.index(violin_default["hue_col"]) if violin_default["hue_col"] in hue_opt else 0
    )
    side_choice = st.selectbox(
        "Violin sides", 
        ["1-sided","2-sided"], 
        index=["1-sided","2-sided"].index(violin_default["side_choice"]) 
        if violin_default["side_choice"] in ["1-sided","2-sided"] else 0
    )
    scale_ui = st.selectbox(
        "Scale",
        ["Proportional area","Proportional length","Fixed width"],
        index=["Proportional area","Proportional length","Fixed width"].index(violin_default["scale_ui"]) 
        if violin_default["scale_ui"] in ["Proportional area","Proportional length","Fixed width"] else 0
    )
    sensitivity = st.slider(
        "Sensitivity (bigger => more detail => smaller bandwidth)", 
        min_value=0.2, 
        max_value=5.0, 
        value=violin_default["sensitivity"], 
        step=0.2
    )
    cmap_choice = st.selectbox(
        "Colormap", 
        CMAPS, 
        index=CMAPS.index(violin_default["cmap_choice"]) 
        if violin_default["cmap_choice"] in CMAPS else 0
    )

    viol_cols_1 = st.columns(2)
    with viol_cols_1[0]:
        color_named = st.selectbox(
            "Named Color", 
            NAMED_COLORS,
            index=NAMED_COLORS.index(violin_default["color_named"]) 
            if violin_default["color_named"] in NAMED_COLORS else 0
        )
    with viol_cols_1[1]:
        color_custom = st.text_input("Custom color (overrides)", violin_default["color_custom"])

    show_grid = st.checkbox("Turn grid on", violin_default["show_grid"])

    if side_choice == "1-sided":
        split_val = True
    else:
        split_val = False

    if hue_col == "None":
        hue_col = None

    bw_val = 1.0 / sensitivity
    color_final = get_chosen_color(color_named, color_custom)

    default_title = f"Violin plot of {ycol}"
    default_xlabel = hue_col if hue_col else ""
    default_ylabel = ycol

    subset_primary = df_primary.iloc[row_start:row_end].copy()
    columns_in_use = [ycol]
    has_nans, mismatch, _ = check_columns_for_nans_and_length(subset_primary, columns_in_use)
    if has_nans:
        st.warning("The chosen Y column has NaN values.")
    if mismatch:
        st.warning("The chosen column has a different number of valid points than expected.")

    nan_method = st.selectbox(
        "How to treat NaN values (for plot only)",
        [
            "Ignore",
            "Drop rows",
            "Fill with mean",
            "Fill with most common value",
            "Replace with 0",
            "Interpolate",
            "KNN (nearest 4 points)",
            "Replace with nearest point"
        ],
        index=[
            "Ignore",
            "Drop rows",
            "Fill with mean",
            "Fill with most common value",
            "Replace with 0",
            "Interpolate",
            "KNN (nearest 4 points)",
            "Replace with nearest point"
        ].index(violin_default["nan_method"]) 
        if violin_default["nan_method"] in [
            "Ignore",
            "Drop rows",
            "Fill with mean",
            "Fill with most common value",
            "Replace with 0",
            "Interpolate",
            "KNN (nearest 4 points)",
            "Replace with nearest point"
        ] else 0
    )

    outlier_method = st.selectbox(
        "How to treat outliers (for plot only)",
        [
            "Ignore",
            "Cap 0.1%",
            "Cap 1%",
            "Cap 5%",
            "Outside 1.5×IQR",
            "Remove rows (|z-score|>3)"
        ],
        index=[
            "Ignore",
            "Cap 0.1%",
            "Cap 1%",
            "Cap 5%",
            "Outside 1.5×IQR",
            "Remove rows (|z-score|>3)"
        ].index(violin_default["outlier_method"]) 
        if violin_default["outlier_method"] in [
            "Ignore",
            "Cap 0.1%",
            "Cap 1%",
            "Cap 5%",
            "Outside 1.5×IQR",
            "Remove rows (|z-score|>3)"
        ] else 0
    )

    subset_for_plot = handle_nans(subset_primary.copy(), columns_in_use, nan_method)
    subset_for_plot = handle_outliers(subset_for_plot, columns_in_use, outlier_method)

    if not pd.api.types.is_numeric_dtype(subset_for_plot[ycol]):
        st.warning("Y column must be numeric for Violin plot.")
    else:
        palette = None
        if hue_col and cmap_choice != 'None':
            palette = sns.color_palette(cmap_choice)

        sns.violinplot(
            data=subset_for_plot,
            x=hue_col if hue_col else None,
            y=ycol,
            split=(split_val if hue_col else False),
            scale=VIOLIN_SCALE_OPTIONS[scale_ui],
            bw=bw_val,
            palette=palette if hue_col else None,
            color=None if (hue_col and palette) else color_final,
            ax=ax
        )
        ax.grid(show_grid)

    st.write("#### Save / Delete Violin Preset")
    preset_name_input = st.text_input(
        "Preset name",
        value=selected_preset_name if selected_preset_name != "None" else "",
        key=f"{graph_type}_preset_name_input"
    )
    if st.button("Save this preset", key=f"{graph_type}_save_preset_btn"):
        new_preset_data = {
            "ycol": ycol,
            "hue_col": hue_col if hue_col else "None",
            "side_choice": side_choice,
            "scale_ui": scale_ui,
            "sensitivity": sensitivity,
            "cmap_choice": cmap_choice,
            "color_named": color_named,
            "color_custom": color_custom,
            "show_grid": show_grid,
            "nan_method": nan_method,
            "outlier_method": outlier_method
        }
        if not preset_name_input.strip():
            st.error("Please provide a valid preset name.")
        else:
            st.session_state.presets.setdefault(graph_type, {})[preset_name_input] = new_preset_data
            save_presets(st.session_state.presets)
            st.success(f"Preset '{preset_name_input}' saved!")

    if selected_preset_name != "None":
        if st.button("Delete this preset", key=f"{graph_type}_delete_preset_btn"):
            if preset_name_input in st.session_state.presets[graph_type]:
                del st.session_state.presets[graph_type][preset_name_input]
                save_presets(st.session_state.presets)
                st.success(f"Preset '{preset_name_input}' deleted!")

########################################
# Apply Title / Axis Overrides
########################################
final_title = custom_title.strip() or default_title
final_xlabel = custom_xlabel.strip() or default_xlabel
final_ylabel = custom_ylabel.strip() or default_ylabel

if final_title:
    ax.set_title(final_title, fontsize=title_font)
if final_xlabel:
    ax.set_xlabel(final_xlabel, fontsize=label_font)
if final_ylabel:
    ax.set_ylabel(final_ylabel, fontsize=label_font)

ax.tick_params(labelsize=tick_font)

add_axis_arrows(ax)

# Display the plot
st.pyplot(fig)

###########################################
# 8) Additional Explanation or Info
###########################################
st.write("---")
st.write("When you upload new files, the old set is replaced. For Scatter/Line, pick 'fileName||columnName'.")
st.write("Use 'Save this preset' to store your current settings for future sessions, or 'Delete this preset' if needed.")
