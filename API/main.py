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

app = FastAPI()

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dados do modelo treinado (fake para exemplo)
# Substitua isso com o seu modelo final quando disponível
class FakeModel:
    def predict(self, historical_prices: List[float], future_days: int) -> List[float]:
        # Gera previsões fake, apenas como exemplo
        last_price = historical_prices[-1] if historical_prices else 100
        return [last_price + i * 5 for i in range(1, future_days + 1)]

# Instancia o modelo fake
model = FakeModel()

# Define o modelo de dados para a entrada
class HistoricalData(BaseModel):
    prices: List[float]  # Lista de preços históricos fornecidos pelo usuário
    days_ahead: int  # Número de dias para prever no futuro

# Armazena os tempos de resposta
performance_data: List[Dict[str, float]] = []

# Middleware para medir o tempo de resposta
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
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
    """Retorna os tempos de resposta registrados para monitoramento."""
    return {"performance": performance_data}

@app.get("/performance/plot", response_class=HTMLResponse)
def plot_performance():
    """Gera um gráfico visual dos tempos de resposta registrados."""
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
    return {"message": "API de previsão de preços está funcionando! Envie dados históricos e o número de dias para obter previsões."}
