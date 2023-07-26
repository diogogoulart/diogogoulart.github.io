#data from https://www.kaggle.com/datasets/ofrancisco/emoji-diet-nutritional-data-sr28?select=Emoji+Diet+Nutritional+Data+%28g%29+-+EmojiFoods+%28g%29.csv

import pandas as pd

data = pd.read_excel('complete_diet.xlsx')

data = data[['name','Price','Calories (kcal)','Carbohydrates (g)','Protein (g)','Total Fat (g)','Vitamin B6 (mg)','Vitamin A (IU)',
'Vitamin B12 (ug)','Vitamin C (mg)','Vitamin E (IU)','Vitamin K (ug)','Thiamin (mg)','Riboflavin (mg)',
'Niacin (mg)','Pantothenic Acid (mg)']]

#reorder foods in an attempt to have a better schemata
foods_order = ['beef', 'chicken', 'taco', 'burrito', 'mushroom', 'ice cream', 'milk', 'cheese', 'grapes', 'melon', 'watermelon', 
'tangerine', 'lemon', 'banana', 'pineapple', 'red apple', 'green apple', 'pear', 'peach',
'cherries', 'strawberry', 'kiwifruit','potato', 'tomato', 'avocado', 'eggplant', 'corn', 'hot pepper', 'cucumber', 'carrot',
'peanuts', 'chestnut', 'bread', 'rice', 'spaghetti', 'bacon', 'hamburger', 'french fries',
'pizza', 'hotdog', 'popcorn','croissant', 'french bread', 'pancakes', 'rice crackers', 'fried shrimp', 'doughnut', 'cookie',
'cake', 'chocolate bar', 'candy', 'custard flan', 'honey', 'black tea', 'sake', 'champagne', 'red wine','beer']

data['name'] = pd.Categorical(data['name'], categories=foods_order, ordered=True)
data = data.sort_values('name')

data = data.values.tolist()

# Nutrient minimums.
min_nutrients = [
    ['Calories (kcal)', 1200], 
    ['Carbohydrates (g)', 130],
    ['Protein (g)', 70], 
    ['Total Fat (g)', 44], 
    ['Vitamin B6 (mg)', 1.3], 
    ['Vitamin A (IU)', 1000], 
    ['Vitamin B12 (ug)', 2.4], 
    ['Vitamin C (mg)', 90],  
    ['Vitamin E (IU)', 15], 
    ['Vitamin K (ug)', 120], 
    ['Thiamin (mg)', 1.2], 
    ['Riboflavin (mg)', 1.3], 
    ['Niacin (mg)', 16], 
    ['Pantothenic Acid (mg)', 5]
    ]

max_nutrients = [
    ['Calories (kcal)', 3000], 
    ['Carbohydrates (g)', 500],
    ['Protein (g)', 200], 
    ['Total Fat (g)', 70], 
    ['Vitamin B6 (mg)', 2.0], 
    ['Vitamin A (IU)', 5000], 
    ['Vitamin B12 (ug)', 3.0], 
    ['Vitamin C (mg)', 100],  
    ['Vitamin E (IU)', 30], 
    ['Vitamin K (ug)', 150], 
    ['Thiamin (mg)', 1.5], 
    ['Riboflavin (mg)', 1.7], 
    ['Niacin (mg)', 20], 
    ['Pantothenic Acid (mg)', 7]
]