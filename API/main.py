from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
import numpy as np
import time
import logging
from fastapi.responses import HTMLResponse
import matplotlib
matplotlib.use('Agg')  # Usa um backend sem GUI
import matplotlib.pyplot as plt
import io
import base64
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler

# Configuração do logger para monitoramento
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Inicialização do aplicativo FastAPI
app = FastAPI()

# Configuração do CORS para permitir requisições de qualquer origem
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Carregando o modelo LSTM salvo
MODEL_PATH = 'modelo_lstm_predicao_acoes.h5'
try:
    model = load_model(MODEL_PATH)
    logging.info("Modelo carregado com sucesso.")
except Exception as e:
    logging.error(f"Erro ao carregar o modelo: {e}")
    model = None

# Configurando o escalador MinMaxScaler
scaler = MinMaxScaler(feature_range=(0, 1))

# Classe para validar os dados de entrada fornecidos pelo usuário
class HistoricalData(BaseModel):
    """
    Representa os dados de entrada esperados pela API para previsão de preços.
    - `prices`: Lista de preços históricos.
    - `days_ahead`: Número de dias futuros para prever.
    - `real_values`: Lista de valores reais (opcional).
    """
    prices: List[float]
    days_ahead: int
    real_values: List[float] = None

# Lista para armazenar os tempos de resposta das requisições
performance_data: List[Dict[str, float]] = []

# Lista para armazenar os dados de acurácia
accuracy_data = []

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """
    Middleware para calcular o tempo de processamento de cada requisição e armazená-lo.
    Adiciona um cabeçalho `X-Process-Time` à resposta.
    """
    start_time = time.time()
    days_ahead = None  # Inicializa como None para não registrar valores irrelevantes

    # Verifica se a requisição é para o endpoint /predict com método POST
    if request.method == "POST" and request.url.path == "/predict":
        try:
            body = await request.json()  # Lê o corpo da requisição de forma assíncrona
            days_ahead = body.get("days_ahead", 0)  # Obtém o valor de days_ahead
        except Exception as e:
            logging.error(f"Erro ao extrair 'days_ahead': {e}")

    response = await call_next(request)  # Processa a requisição
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)

    # Log do tempo de resposta com contexto
    logging.info(f"Path: {request.url.path}, Method: {request.method}, Days Ahead: {days_ahead}, Process Time: {process_time:.4f}s")

    # Armazena o tempo de resposta somente se for do endpoint /predict
    if request.url.path == "/predict" and days_ahead is not None:
        performance_data.append({
            "path": request.url.path,
            "process_time": process_time,
            "days_ahead": days_ahead
        })

    return response

@app.post("/predict")
def predict_prices(data: HistoricalData):
    """
    Endpoint para realizar previsões de preços com base nos dados históricos fornecidos.
    Também calcula e armazena a acurácia, se os valores reais forem fornecidos.
    """
    try:
        if len(data.prices) < 60:
            raise ValueError("É necessário fornecer pelo menos 60 preços históricos para realizar a previsão.")

        if data.days_ahead < 1:
            raise ValueError("O número de dias futuros deve ser pelo menos 1.")

        if model is None:
            raise ValueError("Modelo não carregado. Verifique se o arquivo do modelo está disponível.")

        # Normalizando os dados fornecidos
        historical_prices = np.array(data.prices).reshape(-1, 1)
        scaled_prices = scaler.fit_transform(historical_prices)

        # Criando a sequência de entrada para o modelo LSTM
        input_sequence = scaled_prices[-60:].reshape(1, 60, 1)

        # Fazendo as previsões para múltiplos dias
        future_prices = []
        current_sequence = input_sequence

        for _ in range(data.days_ahead):
            prediction = model.predict(current_sequence)
            future_prices.append(prediction[0, 0])
            current_sequence = np.append(current_sequence[:, 1:, :], [[prediction[0]]], axis=1)

        # Revertendo a normalização das previsões
        future_prices = scaler.inverse_transform(np.array(future_prices).reshape(-1, 1)).flatten().tolist()

        # Calcula a acurácia se os valores reais forem fornecidos
        accuracy = None
        if data.real_values:
            real_values = np.array(data.real_values[:len(future_prices)])
            predicted_values = np.array(future_prices[:len(real_values)])
            accuracy = np.mean(1 - abs(real_values - predicted_values) / real_values) * 100

            # Armazena os dados para o gráfico
            accuracy_data.append({
                "real_values": real_values.tolist(),
                "predicted_values": predicted_values.tolist(),
                "accuracy": accuracy
            })

        return {
            "future_prices": future_prices,
            "accuracy": round(accuracy, 2) if accuracy is not None else None
        }
    except Exception as e:
        logging.error(f"Erro durante a previsão: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/performance")
def get_performance_data():
    """
    Endpoint para retornar os tempos de resposta registrados durante o uso da API.
    - Saída (JSON):
        {
            "performance": [
                {"path": "/predict", "process_time": 0.1234, "days_ahead": 3},
                {"path": "/predict", "process_time": 0.0987, "days_ahead": 5}
            ]
        }
    """
    return {"performance": performance_data}

@app.get("/performance/plot", response_class=HTMLResponse)
def plot_performance():
    """
    Endpoint para gerar e exibir um gráfico visual dos tempos de resposta registrados.
    """
    if not performance_data:
        return HTMLResponse("<h3>Não há dados de performance registrados ainda.</h3>")

    # Extrai os tempos de resposta e dias futuros
    times = [entry["process_time"] for entry in performance_data]
    days_ahead = [entry["days_ahead"] for entry in performance_data]
    requests_ids = list(range(1, len(times) + 1))

    # Cria o gráfico
    plt.figure(figsize=(12, 6))
    plt.scatter(requests_ids, times, s=100, c="blue", edgecolor="k", label="Tempo de Resposta")
    plt.plot(requests_ids, times, linestyle="--", alpha=0.7, label="Tendência")

    # Adiciona o número de dias em cada ponto
    for i, txt in enumerate(days_ahead):
        plt.annotate(f"{txt} dias", (requests_ids[i], times[i]), textcoords="offset points", xytext=(0, 10), ha="center", fontsize=9)

    # Configurações do gráfico
    plt.title("Monitoramento de Tempo de Resposta da API", fontsize=14)
    plt.xlabel("Número da Requisição", fontsize=12)
    plt.ylabel("Tempo de Resposta (segundos)", fontsize=12)
    plt.legend(loc="upper left")
    plt.grid(True)
    plt.tight_layout()

    # Salva o gráfico em memória
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    buffer.close()

    # Explicação do gráfico
    explanation = """
    <h4>Sobre o Gráfico:</h4>
    <p>
        Este gráfico exibe o tempo de resposta da API para cada requisição, considerando:
    </p>
    <ul>
        <li><strong>Eixo X:</strong> Número da requisição enviada à API.</li>
        <li><strong>Eixo Y:</strong> Tempo de resposta da API em segundos.</li>
        <li><strong>Números nos pontos:</strong> Número de dias futuros previstos pela API para cada requisição.</li>
    </ul>
    <p>
        Use este gráfico para monitorar o desempenho da API e identificar como o número de dias futuros impacta o tempo de resposta.
    </p>
    """

    # Retorna o gráfico embutido em HTML com explicação
    return HTMLResponse(f"""
    <html>
        <head><title>Monitoramento de Performance</title></head>
        <body>
            <h3>Gráfico de Tempo de Resposta</h3>
            <img src="data:image/png;base64,{image_base64}" alt="Gráfico de Performance">
            {explanation}
        </body>
    </html>
    """)

@app.get("/accuracy/plot", response_class=HTMLResponse)
def plot_accuracy():
    """
    Gera um gráfico comparando os valores reais e previstos armazenados em accuracy_data.
    """
    if not accuracy_data:
        return HTMLResponse("<h3>Não há dados de acurácia registrados ainda.</h3>")

    # Cria o gráfico
    plt.figure(figsize=(12, 6))
    for i, entry in enumerate(accuracy_data):
        real_values = entry["real_values"]
        predicted_values = entry["predicted_values"]
        accuracy = entry["accuracy"]

        # Adiciona uma linha para cada previsão
        plt.plot(range(len(real_values)), real_values, label=f"Real ({i+1})", marker="o")
        plt.plot(range(len(predicted_values)), predicted_values, label=f"Previsto ({i+1}) - {accuracy:.2f}%", marker="x")

    plt.title("Comparação de Previsão e Acurácia", fontsize=14)
    plt.xlabel("Dias Futuros", fontsize=12)
    plt.ylabel("Preço", fontsize=12)
    plt.legend()
    plt.grid()

    # Salva o gráfico em memória
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    buffer.close()

    # Retorna o gráfico como HTML
    return HTMLResponse(f"""
    <html>
        <head><title>Gráfico de Acurácia</title></head>
        <body>
            <h3>Gráfico de Comparação de Previsão</h3>
            <img src="data:image/png;base64,{image_base64}" alt="Gráfico de Acurácia">
        </body>
    </html>
    """)

@app.get("/predicaoPrecos", response_class=HTMLResponse)
def render_interface():
    """
    Interface gráfica para enviar dados ao endpoint /predict.
    Também exibe os resultados mais recentes de previsão, se existirem.
    """
    # Verifica se há dados de previsão registrados
    latest_data = accuracy_data[-1] if accuracy_data else None

    # HTML do container de resultados (inicialmente vazio ou com os últimos dados)
    results_html = """
    <div id="results" class="output">
        <h2>Últimos Resultados:</h2>
        <p>Realize uma previsão para ver os resultados aqui.</p>
    </div>
    """
    if latest_data:
        real_values = latest_data["real_values"]
        predicted_values = latest_data["predicted_values"]
        accuracy = latest_data["accuracy"]

        # Formata os preços para exibição
        formatted_predicted = [f"R$ {price:.2f}".replace('.', ',') for price in predicted_values]
        formatted_real = [f"R$ {price:.2f}".replace('.', ',') for price in real_values]

        results_html = f"""
        <div id="results" class="output">
            <h2>Últimos Resultados:</h2>
            <p><strong>Valores Previstos:</strong></p>
            <p class="price">{' | '.join(formatted_predicted)}</p>
            <p><strong>Valores Reais:</strong></p>
            <p>{' | '.join(formatted_real)}</p>
            <p><strong>Acurácia:</strong> <span class="accuracy">{accuracy:.2f}%</span></p>
        </div>
        """

    # HTML principal com formulário de entrada e resultados recentes
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Previsão de Preços</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f9; }}
            h1 {{ color: #333; text-align: center; }}
            .container {{ max-width: 600px; margin: auto; background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); }}
            textarea, input {{ width: 100%; margin-bottom: 15px; padding: 10px; border: 1px solid #ccc; border-radius: 5px; }}
            button {{ background-color: #007BFF; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; display: block; margin: auto; }}
            button:hover {{ background-color: #0056b3; }}
            .output {{ margin-top: 20px; padding: 20px; background-color: #e9ecef; border-radius: 5px; text-align: center; }}
            .price {{ font-size: 24px; font-weight: bold; color: #007BFF; }}
            .accuracy {{ color: green; font-weight: bold; }}
            .error {{ color: red; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Previsão de Preços</h1>
            <p>Insira uma lista de preços históricos (mínimo de 60 valores) separados por vírgulas:</p>
            <textarea id="pricesInput" placeholder="100, 105, 110, 120, ..."></textarea>
            <p>Insira o número de dias futuros para prever:</p>
            <input type="number" id="daysAhead" placeholder="Número de dias futuros" min="1">
            <p>Insira os valores reais (opcional, separados por vírgulas):</p>
            <textarea id="realValuesInput" placeholder="110, 115, 120, ..."></textarea>
            <button onclick="predict()">Enviar</button>
            {results_html}
        </div>
        <script>
            async function predict() {{
                const prices = document.getElementById("pricesInput").value.split(",").map(v => parseFloat(v.trim()));
                const daysAhead = parseInt(document.getElementById("daysAhead").value);
                const realValues = document.getElementById("realValuesInput").value.split(",").map(v => parseFloat(v.trim()));

                // Validação dos preços
                if (prices.some(isNaN) || prices.length < 60) {{
                    alert("Por favor, insira pelo menos 60 valores numéricos separados por vírgulas.");
                    return;
                }}

                // Validação do número de dias
                if (isNaN(daysAhead) || daysAhead < 1) {{
                    alert("Por favor, insira um número válido de dias futuros.");
                    return;
                }}

                // Enviar a requisição para o endpoint /predict
                const response = await fetch("/predict", {{
                    method: "POST",
                    headers: {{ "Content-Type": "application/json" }},
                    body: JSON.stringify({{ prices, days_ahead: daysAhead, real_values: realValues }})
                }});

                // Processar a resposta
                if (response.ok) {{
                    const data = await response.json();
                    
                    // Atualizar os resultados na página
                    const resultsDiv = document.getElementById("results");
                    resultsDiv.innerHTML = `
                        <h2>Últimos Resultados:</h2>
                        <p><strong>Valores Previstos:</strong></p>
                        <p class="price">${{data.future_prices.map(p => `R$ ${{p.toFixed(2).replace('.', ',')}}`).join(' | ')}}</p>
                        <p><strong>Acurácia:</strong> <span class="accuracy">${{data.accuracy ? data.accuracy.toFixed(2) : 'N/A'}}%</span></p>
                    `;
                }} else {{
                    const error = await response.json();
                    alert("Erro: " + error.detail);
                }}
            }}
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/")
def root():
    """
    Endpoint para verificar se a API está funcionando.
    - Saída (JSON):
        {
            "message": "API de previsão de preços está funcionando! Envie dados históricos e o número de dias para obter previsões."
        }
    """
    return {"message": "API de previsão de preços está funcionando! Envie dados históricos e o número de dias para obter previsões."}