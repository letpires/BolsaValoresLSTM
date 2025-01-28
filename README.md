# 💰 Predição do valor de fechamento da bolsa de valores da Disney


Este projeto tem como objetivo construir um modelo preditivo utilizando redes neurais Long Short Term Memory (LSTM) para prever o valor de fechamento das ações da empresa Disney (ticker: DIS) com base em dados históricos. O desafio envolve o desenvolvimento completo do pipeline, desde a coleta e pré-processamento dos dados até o deploy do modelo por meio de uma API RESTful.

## Objetivo do Projeto

- **Coleta e Pré-processamento dos Dados:** Obter e preparar os dados históricos de preços utilizando a biblioteca yfinance.
- **Desenvolvimento do Modelo LSTM:** Treinar o modelo para capturar padrões temporais nos dados financeiros.
- **Deploy do Modelo:** Criar uma API RESTful com Flask ou FastAPI que permita a utilização do modelo por outros usuários.
- **Escalabilidade e Monitoramento:** Configurar práticas e ferramentas para monitorar o desempenho da API e do modelo em produção.

## Estrutura do projeto

<pre>
├── API/                          # Pasta contendo a API RESTful
│   ├── .vscode/                  # Configurações do editor (opcional)
│   ├── .DS_Store                 # Arquivo de sistema (pode ser ignorado)
│   ├── Dockerfile                # Arquivo para criação de imagem Docker da API
│   ├── README.md                 # Documentação específica da API
│   ├── main.py                   # Arquivo principal da API (implementação com Flask/FastAPI)
│   ├── modelo_lstm_predicao_acoes.h5 # Modelo LSTM treinado utilizado pela API
│   └── requirements.txt          # Dependências necessárias para rodar a API
├── modelo.ipynb                  # Notebook com o desenvolvimento do modelo
├── modelo_lstm_predicao_acoes.h5 # Arquivo do modelo treinado (salvo em HDF5)
├── README.md                     # Documentação principal do projeto
├── requirements.txt              # Dependências necessárias para o projeto
└── .gitignore                    # Arquivos e pastas ignorados pelo Git
</pre>




## Decisões consideradas para um bom resultado do modelo

As seguintes escolhas foram feitas para melhorar a performance do modelo:

1. Escalonamento dos Dados: Foi utilizado o MinMaxScaler para normalizar os dados no intervalo de [0, 1].

2. Número de Steps (Janela Deslizante): O modelo utiliza os últimos 30 dias para prever o próximo valor de fechamento.

3. LSTM Units: Foi definida uma camada com 100 unidades LSTM.

4. Otimizador Adam: O otimizador escolhido foi o Adam (Adaptive Moment Estimation). Converge rapidamente e ajusta dinamicamente a taxa de aprendizado para cada peso, reduzindo o tempo de treinamento e aumentando a eficiência.

5. Épocas: O modelo foi treinado por 50 épocas. Oferece tempo suficiente para o aprendizado sem causar overfitting.

6. Dropout: Foi aplicada uma taxa de 20% de dropout. Reduz o risco de overfitting, ajudando o modelo a generalizar melhor para dados não vistos.


## Resultados do Modelo

Métricas do Conjunto de Treinamento:
MAE: 2.43
RMSE: 3.38
MAPE: 1.98%
R²: 0.99
Métricas do Conjunto de Teste:
MAE: 1.99
RMSE: 2.56
MAPE: 2.13%
R²: 0.95

Conclusão: O modelo apresentou excelente desempenho em ambas as fases (treino e teste), com erro percentual absoluto médio (MAPE) inferior a 2.5% e alta capacidade explicativa (R² acima de 0.95).

## Pontos de melhoria

Preenchimento de Lacunas nos Finais de Semana:

Atualmente, os finais de semana não possuem dados, o que pode causar inconsistências nos padrões temporais.
Estratégias possíveis:
Forward Fill: Repetir o último valor da sexta-feira.
Interpolação Linear: Calcular valores intermediários entre sexta e segunda-feira.
Média Móvel: Suavizar os valores ao longo do tempo.
Ajuste de Hiperparâmetros:

Testar combinações de:
Tamanho da janela (steps).
Número de unidades LSTM.
Possibilidade de aumentar ou reduzir o número de épocas conforme o comportamento do modelo.
Exploração de Features Adicionais:

Incorporar variáveis como volume de negociação ou indicadores técnicos (ex.: médias móveis, RSI) para enriquecer as entradas do modelo.
Validação em Dados Futuros:

Testar o modelo em dados reais futuros para validar sua capacidade de generalização.





Requisitos
Linguagem: Python 3.7+
Principais Bibliotecas:
yfinance
pandas
numpy
matplotlib
tensorflow ou pytorch


Observação
A documentação detalhada da API pode ser encontrada na pasta API/README.md.

