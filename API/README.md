# 💲 Documentação da API de Previsão de Preços de Ações

Esta API foi desenvolvida para realizar previsões de preços com base em dados históricos fornecidos pelo usuário. A API utiliza **FastAPI** como framework principal e pode ser executada localmente ou em um contêiner Docker.

---

## **Índice**

- [Requisitos](#requisitos)
- [Montar o Ambiente Virtual](#montar-o-ambiente-virtual)
- [Instalar as Dependências](#instalar-as-dependências)
- [Estrutura de Pastas](#estrutura-de-pastas)
- [Executar Localmente](#executar-localmente)
- [Métodos da API](#métodos-da-api)
- [Montar e Rodar com Docker](#montar-e-rodar-com-docker)

---

## **Requisitos**

- Python 3.10 ou superior
- Pip (gerenciador de pacotes do Python)
- Docker (para rodar no contêiner)

---

## **Montar o Ambiente Virtual**

Para garantir um ambiente isolado:

1. Crie o ambiente virtual:
   ```bash
   python -m venv venv
   ```
2. Ative o ambiente virtual:
   - No Linux/macOS:
     ```bash
     source venv/bin/activate
     ```
   - No Windows:
     ```bash
     venv\Scripts\activate
     ```
3. Atualize o `pip` (opcional, mas recomendado):
   ```bash
   pip install --upgrade pip
   ```

---

## **Instalar as Dependências**

1. Instale as dependências a partir do arquivo `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

---

## **Estrutura de Pastas**

A organização do projeto:

```
.
├── main.py               # Código principal da API
├── requirements.txt      # Lista de dependências
├── Dockerfile            # Configuração do Docker
└── README.md             # Documentação
```

---

## **Executar Localmente**

1. Ative o ambiente virtual:
   ```bash
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate   # Windows
   ```

2. Execute a API usando o Uvicorn:
   ```bash
   uvicorn main:app --reload
   ```

3. A API estará disponível em:
   ```
    http://127.0.0.1:8000
   ```

4. Teste os endpoints acessando o **Swagger UI**:
   ```
    http://127.0.0.1:8000/docs
   ```

---

## **Métodos da API**

### 1. **Status da API**
   - **Endpoint**: `GET /`
   - **Descrição**: Retorna uma mensagem indicando que a API está funcionando.
   - **Exemplo de Resposta**:
     ```json
     {
       "message": "API de previsão de preços está funcionando! Envie dados históricos e o número de dias para obter previsões."
     }
     ```

### 2. **Previsão de Preços**
   - **Endpoint**: `POST /predict`
   - **Descrição**: Recebe dados históricos e o número de dias para prever preços futuros.
   - **Entrada**:
     ```json
     {
       "prices": [100, 105, 110, 120],
       "days_ahead": 3
     }
     ```
   - **Saída**:
     ```json
     {
       "future_prices": [125, 130, 135]
     }
     ```

### 3. **Monitoramento de Performance**
   - **Endpoint**: `GET /performance`
   - **Descrição**: Retorna os tempos de resposta registrados durante o uso da API.
   - **Exemplo de Resposta**:
     ```json
     {
       "performance": [
         {"path": "/predict", "process_time": 0.1234},
         {"path": "/predict", "process_time": 0.0987}
       ]
     }
     ```

### 4. **Gráfico de Performance**
   - **Endpoint**: `GET /performance/plot`
   - **Descrição**: Gera um gráfico visual dos tempos de resposta registrados.
   - **Saída**: Um gráfico exibido no navegador.
   - **Exemplo de Gráfico Gerado**:

     ![Exemplo de Gráfico de Performance](data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/2wBDAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/wAARCACWAKADASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAX/xAAeEAABAwQDAAAAAAAAAAAAAAACAAQRAwQSITFBYv/EABUBAQEAAAAAAAAAAAAAAAAAAAQF/8QAGhEAAgIDAAAAAAAAAAAAAAAAABEBIgMhMf/aAAwDAQACEAMQAAAB7cXU4RJnnDKPU7nBh3uP/AJ4tdOLnEGmzDpbn60f//Z)

---

## **Montar e Rodar com Docker**

1. **Criar a Imagem Docker**:
   No diretório do projeto, execute:
   ```bash
   docker build -t minha-api-fastapi .
   ```

2. **Rodar o Contêiner**:
   ```bash
   docker run -d -p 8000:8000 minha-api-fastapi
   ```

3. **Acessar a API**:
   A API estará disponível em:
   ```
   http://127.0.0.1:8000
   ```

---

Com esta documentação, você pode montar o ambiente, entender os métodos da API e executá-la localmente ou em um contêiner Docker. 🚀
