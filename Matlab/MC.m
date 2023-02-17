% Disciplina: Matem�tica Computacional
% Curso: Mestrado Integrado em Engenharia Mec�nica
% Ano Letivo: 2019/2020
% Nome: Diogo Silva N� 93240
% Nome: Eduardo Monteiro N� 93244
% Nome: Gil Simas N� 93257
% Enunciado: PA52 Integra��o num�rica regra de Simpson adaptativa n�o-iterativa

clear all

choice = menu('Escolha a fun��o a integrar', 'I -  x.*exp(2*x)' ,'II -  10.^(2*x)' , ...
    'III -  4./(x.^2 + 1)', 'IV -  exp(x).*sin(2*x)./(x.^2 + 1)', 'Outra') ;

waiting = true;
flag = false;

while waiting == true
    switch choice
        case 1
            fun = @(x) x.*exp(2*x);
            a = 0;                      % a = limite inferior de integra��o
            b = 3;                      % b = limite superior de integra��o
        case 2
            fun = @(x) 10.^(2*x);
            a = 0;
            b = 1;
        case 3
            fun = @(x) 4./((x.^2) + 1);
            a = 0;
            b = 1;
        case 4
            fun = @(x) exp(x).*sin(2*x)./((x.^2) + 1);
            a = 0;
            b = 3;
        case 5
            prompt = {'Fun��o (ex. @(x) 4./((x.^2) + 1)', 'Integrar de', 'a'};
            dlg_title = 'Input';
            num_lines = 1;
            def = {' ',' ', ' '};
            answer = inputdlg(prompt, dlg_title, num_lines, def);
            try 
                 tryexemp = str2num(answer{1}(2));
            catch
                 flag = true;
                 break
            end
            fun = str2num(answer{1});
            a = str2double(answer{2});
            b = str2double(answer{3});  
            flag = false;
    end  
    if flag == true
         waiting = true;
    else
         waiting = false;
    end
end

prompt = {'Erro absoluto pretendido', 'N�mero (inteiro maior que 1) de intervalos inciais'};
num_lines = 1;
dlg_title = 'Input';
def = {' ',' '};
answer = inputdlg(prompt, dlg_title, num_lines, def);
ErroPretendidoAbsoluto = abs(str2double(answer{1}));
N = floor(abs(str2double(answer{2})));

tic

integraltotal=0 ;

I = integral(fun,a,b) ; %ser� para comparar

FunAvaliadaDados = GetErrosEIntegrais(a, b, ErroPretendidoAbsoluto, N, fun);
ErroTotalFun = FunAvaliadaDados{1} ;  
ArrayLimitsFun = FunAvaliadaDados{2} ;     %Recorrendo �s fun��es s�o calculadas
ArrayErrosPorInt = FunAvaliadaDados{3} ;   %as seguintes vari�veis
IntegralTotalFun = FunAvaliadaDados{4} ;
ArrayErroIntESubInt = [FunAvaliadaDados{5}, 0];

%%%  Gr�fico 1: Representa��o da integral escolhida (�rea debaixo da fun��o
%%%  1D) e representa��o dos subintervalos pela regra de Simpson com
%%%  curvatura quadr�tica

figure(1)

x= linspace(a,b) ;
k=fun(x) ;
ar=area (x,k);
ar.FaceAlpha = 0.1 ;
ar.EdgeColor = 'g';
ar.FaceColor= 'g';
ar.FaceAlpha = 0.1 ;

hold on

for ii=2:length(ArrayLimitsFun)  % loop para desenhar os intervalos da regra de simpson com a curvatura (quadr�tica)
    xii = ArrayLimitsFun(ii-1);  % s� ser� vis�vel se o n�mero de subintervalos for pequeno e a toler�ncia for grande, 
    xfi= ArrayLimitsFun(ii) ;    % caso contr�rio as linhas dos dois gr�ficos v�o se sobrepor com a grande proximidade
    xmi=(xfi+xii)/2 ;            % que as suas representa��es passariam a ter
    
    x= linspace(xii,xfi) ;
    lo=@(x) (x-xmi).*(x-xfi)/((xii-xmi)*(xii-xfi));
    l1=@(x) (x-xii).*(x-xfi)/((xmi-xii)*(xmi-xfi));
    l2=@(x) (x-xii).*(x-xmi)/((xfi-xii)*(xfi-xmi));
    
    yo=fun(xii) ;
    y1=fun(xmi) ;
    y2=fun(xfi) ;
    
    z= yo * lo(x) + y1 *l1(x)+ y2 *l2(x) ;
    
    plot(x, z)
end

% clear figure
% figure(1)


title('Fun��o')

hold off
%%%

%%% gr�fico 2 representa o erro de cada subdivis�o do g�fico num gr�fico em
%%% que o valor do eixo das abcissas representa as coordenas do x do
%%% intervalo e o eixo das ordenas representa o erro associado a cada
%%% intervalo

h = (b - a)/N ;
ArrayN = [] ;

for ii = a:h:b
    ArrayN = [ArrayN, ii] ;
end

figure(2)

ArrayErrosPorInt=[ArrayErrosPorInt,0] ;
stairs(ArrayN ,ArrayErrosPorInt,'LineWidth',2,'MarkerFaceColor','c')
hold on
stairs(ArrayLimitsFun ,ArrayErroIntESubInt,'LineWidth',1,'MarkerFaceColor','r')
hold off

title('Erro de Cada Divis�o')
xlabel('x') 
ylabel('Erro') 

%%%Gr�fico 3 demonstra a varia��o do erro (Integral exata - integral
%%% calculada) em fun��o do erro pretendido

figure(3)

IntegralExato = abs(integral(fun,a, b, 'ArrayValue', true));
ErroInicial = 0.00001;
Razao = 1.25;
NRepeticoes = 70;

Graf3ArrayErroPretendido = zeros (1,NRepeticoes);           %Onde ser�o armazenados os erros maximos do integral
Graf3ArrayErroObtido = zeros(1,NRepeticoes);                %One ser�o armazendos os erros reais


for ii=1:NRepeticoes
    ErroPretendidoAbcissas = ErroInicial*Razao.^(ii-1);     %Progress�o geom�trica para gerar conjunto de erros maximos do integral
    FunsDat = GetErrosEIntegrais(a, b, ErroPretendidoAbcissas, 3, fun);
    IntegralObtido = FunsDat{4};
    ErroReal = abs(IntegralExato - IntegralObtido) ;
    Graf3ArrayErroPretendido(ii) = ErroPretendidoAbcissas;
    Graf3ArrayErroObtido(ii) = ErroReal;
end 

% plot(Graf3ArrayErroPretendido, Graf3ArrayErroObtido)
semilogx(Graf3ArrayErroPretendido, Graf3ArrayErroObtido)
ylabel('I- Integral total') 
xlabel('Erro Pretendido') 

%%%Verifica��o se o erro especificado est� ser consegido
if ErroTotalFun < ErroPretendidoAbsoluto
    disp('O erro especificado est� a ser conseguido')
    fprintf('\nErro Pretendido: %f', ErroPretendidoAbsoluto);
    fprintf('\nErro Total: %s', ErroTotalFun);
else
    disp ('Falha')
end
toc

% ai = inicio do intervalo
% bi = fim do intervalo 

function output = IntegrInterv(ai, aii, fun)        %Calcula o integral aproximado do intervalo/subintervalo
    output = (aii-ai)*(1/6).*(fun(ai) + fun(aii) + 4.*fun((aii+ai)/2));
end

function output = IntegrItervDois(ai, aii, fun)     %Calcula o integral de um intervalo subdividido em dois
    xmi = (ai + aii)/2;                     % xmi = valor m�dio de aii e bii
    output = IntegrInterv(ai, xmi, fun) + IntegrInterv(xmi, aii, fun);
end

function output = QuartaDeriv(ai, aii, fun)         %Calcula aproxima��o � quarta derivada
    output = 3072*(IntegrInterv(ai, aii, fun) - IntegrItervDois(ai, aii, fun))/((aii-ai)^5);
end

function output = getmi(ErroPretendidoAbsoluto, ai, aii, a, b, fun)     %Calcula n�mero, m, de subintervalos necess�rios
    fd = QuartaDeriv(ai, aii, fun) ;
    output = floor( (aii-ai)*((abs(fd).*(b-a)*((ErroPretendidoAbsoluto*2880)^-1))^(1./4)) ) + 1;
end

function output = ErroInt(ai, aii, fun)    %Estima o erro, associado ao calculo do integral no intervalo/subintervalo
    output = abs((1/2880)*QuartaDeriv(ai, aii, fun)*((aii-ai)^5));
end


function output = GetErrosEIntegrais(a, b, ErroPretendidoAbsoluto, N, fun)
    
    h=(b-a)/N ;
    ErroTotal = 0 ;
    ArrayLimsInterv=[a];                 %Onde se armazenam os pontos limites dos intervalos
    ArrayDosErros=[];                    %Onde se armazenam os erros dos intervalos
    IntegralTotal = 0 ;                  %Soma do integral calculado em cada intervalo
    ArrayDosErrosIntESubInt = []  ;      %Onde se armazenam os erros dos intervalos e subintervalos
    ErroMaximoPorInt = ErroPretendidoAbsoluto/N    ;
    for ii=1:N 
        ai= a + h*(ii-1) ;               %Calcula os pontos delimitadores
        aii= ai + h ;                    %dos intervalos
        ErroIntervAiAii = ErroInt(ai, aii, fun);
        
        if ErroIntervAiAii < ErroMaximoPorInt
            
            ArrayLimsInterv=[ArrayLimsInterv, aii];        
            ArrayDosErros = [ArrayDosErros, ErroIntervAiAii];
            ArrayDosErrosIntESubInt = [ArrayDosErrosIntESubInt, ErroIntervAiAii] ;
            IntegralTotal = IntegralTotal + IntegrInterv(ai, aii, fun) ;
            ErroTotal = ErroTotal + ErroIntervAiAii ;
            
        else
            mi = getmi(ErroPretendidoAbsoluto, ai, aii, a, b, fun) ;
            hi = h/mi;                          %Calculo do tamanho dos subintervalos
            ErroAcomuladoSubInts = 0;           %Acomulador dos erros nos subintervalos

            for iii=1:mi
                aSubInt = ai + hi*(iii-1);            %aSubInt = inicio do subintervalo
                bSubInt = aSubInt + hi;               %bSubInt = fim do subintervalo
                ErroSubInterv = ErroInt(aSubInt, bSubInt, fun);         %Erro associado, no subintervalo
                ErroAcomuladoSubInts = ErroAcomuladoSubInts + ErroSubInterv;
                ArrayLimsInterv=[ArrayLimsInterv, bSubInt];
                ArrayDosErrosIntESubInt = [ArrayDosErrosIntESubInt, ErroSubInterv];
                IntegralTotal = IntegralTotal + IntegrInterv(aSubInt, bSubInt, fun) ;
                
            end
            
            ArrayDosErros = [ArrayDosErros, ErroAcomuladoSubInts];
            ErroTotal = ErroTotal + ErroAcomuladoSubInts;
            
        end
    end
    
    output = {ErroTotal, ArrayLimsInterv, ArrayDosErros, IntegralTotal, ArrayDosErrosIntESubInt};
    
end