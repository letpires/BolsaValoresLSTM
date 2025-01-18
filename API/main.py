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
import pandas as pd

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
    """
    prices: List[float]  # Lista de preços históricos fornecidos pelo usuário

# Lista para armazenar os tempos de resposta das requisições
performance_data: List[Dict[str, float]] = []

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """
    Middleware para calcular o tempo de processamento de cada requisição e armazená-lo.
    Adiciona um cabeçalho `X-Process-Time` à resposta.
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)

    # Log do tempo de resposta
    logging.info(f"Path: {request.url.path}, Method: {request.method}, Process Time: {process_time:.4f}s")

    # Armazena o tempo de resposta no monitoramento, se for uma requisição ao /predict
    if request.url.path == "/predict":
        performance_data.append({"path": request.url.path, "process_time": process_time})

    return response

@app.post("/predict")
def predict_prices(data: HistoricalData):
    """
    Endpoint para realizar previsões de preços com base nos dados históricos fornecidos.
    - Entrada (JSON):
        {
            "prices": [100, 105, 110, 120]
        }
    - Saída (JSON):
        {
            "future_price": 125.0
        }
    """
    try:
        if len(data.prices) < 60:
            raise ValueError("É necessário fornecer pelo menos 60 preços históricos para realizar a previsão.")

        if model is None:
            raise ValueError("Modelo não carregado. Verifique se o arquivo do modelo está disponível.")

        # Normalizando os dados fornecidos
        historical_prices = np.array(data.prices).reshape(-1, 1)
        scaled_prices = scaler.fit_transform(historical_prices)

        # Criando a sequência de entrada para o modelo LSTM
        input_sequence = scaled_prices[-60:].reshape(1, 60, 1)  # Formato [samples, time_steps, features]

        # Fazendo a previsão
        prediction = model.predict(input_sequence)
        predicted_price = scaler.inverse_transform(prediction)[0, 0]

        return {"future_price": float(predicted_price)}
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
                {"path": "/predict", "process_time": 0.1234},
                {"path": "/predict", "process_time": 0.0987}
            ]
        }
    """
    return {"performance": performance_data}

@app.get("/performance/plot", response_class=HTMLResponse)
def plot_performance():
    """
    Endpoint para gerar e exibir um gráfico visual dos tempos de resposta registrados.
    - Saída: Gráfico exibido como uma imagem no navegador.
    """
    if not performance_data:
        return HTMLResponse("<h3>Não há dados de performance registrados ainda.</h3>")

    # Extrai os tempos de resposta
    times = [entry["process_time"] for entry in performance_data]
    requests_ids = list(range(1, len(times) + 1))

    # Cria o gráfico
    plt.figure(figsize=(10, 6))
    plt.plot(requests_ids, times, marker="o")
    plt.title("Monitoramento de Tempo de Resposta da API")
    plt.xlabel("Número da Requisição")
    plt.ylabel("Tempo de Resposta (s)")
    plt.grid(True)

    # Salva o gráfico em memória
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    buffer.close()

    # Retorna o gráfico embutido em HTML
    return HTMLResponse(f"""
    <html>
        <head><title>Monitoramento de Performance</title></head>
        <body>
            <h3>Gráfico de Tempo de Resposta</h3>
            <img src="data:image/png;base64,{image_base64}" alt="Gráfico de Performance">
        </body>
    </html>
    """)

@app.get("/predicaoPrecos", response_class=HTMLResponse)
def render_interface():
    """
    Interface gráfica para enviar dados ao endpoint /predict.
    """
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Previsão de Preços</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f9; }
            h1 { color: #333; }
            .container { max-width: 600px; margin: auto; background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); }
            textarea { width: 100%; height: 150px; margin-bottom: 15px; padding: 10px; border: 1px solid #ccc; border-radius: 5px; }
            button { background-color: #007BFF; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
            button:hover { background-color: #0056b3; }
            .output { margin-top: 20px; padding: 10px; background-color: #e9ecef; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Previsão de Preços</h1>
            <p>Insira uma lista de preços históricos (mínimo de 60 valores) separados por vírgulas:</p>
            <textarea id="pricesInput" placeholder="100, 105, 110, 120, ..."></textarea>
            <button onclick="predict()">Enviar</button>
            <div id="output" class="output"></div>
        </div>
        <script>
            async function predict() {
                // Pega os valores do textarea e tenta convertê-los para números
                const prices = document.getElementById("pricesInput").value.split(",").map(v => parseFloat(v.trim()));

                // Verifica se todos os valores são números válidos
                if (prices.some(isNaN)) {
                    document.getElementById("output").innerText = "Por favor, insira apenas números separados por vírgulas.";
                    return;
                }

                // Verifica se há pelo menos 60 valores
                if (prices.length < 60) {
                    document.getElementById("output").innerText = "Por favor, insira pelo menos 60 valores.";
                    return;
                }

                // Envia a requisição ao endpoint /predict
                const response = await fetch("/predict", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ prices })
                });

                // Processa a resposta
                if (response.ok) {
                    const data = await response.json();
                    document.getElementById("output").innerText = `Preço Previsto: ${data.future_price}`;
                } else {
                    const error = await response.json();
                    document.getElementById("output").innerText = `Erro: ${error.detail}`;
                }
            }
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