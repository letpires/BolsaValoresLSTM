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

# Classe FakeModel para simular previsões de preços
class FakeModel:
    """
    Classe que simula um modelo de previsão de preços com base nos dados históricos fornecidos.
    """
    def predict(self, historical_prices: List[float], future_days: int) -> List[float]:
        # Gera previsões baseadas no último preço da lista de preços históricos
        last_price = historical_prices[-1] if historical_prices else 100
        return [last_price + i * 5 for i in range(1, future_days + 1)]

# Instancia o modelo fake
model = FakeModel()

# Classe para validar os dados de entrada fornecidos pelo usuário
class HistoricalData(BaseModel):
    """
    Representa os dados de entrada esperados pela API para previsão de preços.
    - `prices`: Lista de preços históricos.
    - `days_ahead`: Número de dias para prever no futuro.
    """
    prices: List[float]  # Lista de preços históricos fornecidos pelo usuário
    days_ahead: int  # Número de dias para prever no futuro

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
            "prices": [100, 105, 110, 120],
            "days_ahead": 3
        }
    - Saída (JSON):
        {
            "future_prices": [125, 130, 135]
        }
    """
    try:
        if len(data.prices) < 1:
            raise ValueError("É necessário fornecer pelo menos um preço histórico.")
        if data.days_ahead < 1:
            raise ValueError("O número de dias deve ser maior que zero.")
        
        start_time = time.time()
        predictions = model.predict(data.prices, data.days_ahead)
        response_time = time.time() - start_time
        
        # Log de performance
        logging.info(f"Prediction completed in {response_time:.4f}s for {data.days_ahead} days ahead.")
        return {"future_prices": predictions}
    except ValueError as e:
        logging.error(f"Error: {str(e)}")
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
