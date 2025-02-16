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
- [Deploy na Nuvem](#deploy-na-nuvem)

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
   - **Descrição**: Recebe dados históricos e o número de dias futuros para prever uma lista de preços.
   - **Entrada**:
     ```json
     {
         "prices": [100, 105, 110, 115, 120, ...],
         "days_ahead": 3,
         "real_values": [125, 130, 135] // Opcional
     }
     ```
   - **Saída**:
     ```json
     {
        "future_prices": [125.0, 130.0, 135.0],
        "accuracy": 95.67 // Opcional, se valores reais forem fornecidos
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

### 5. **Interface Gráfica para Previsões**
   - **Endpoint**: `GET /predicaoPrecos`
   - **Descrição**: Exibe uma interface web para que o usuário insira os preços históricos e o número de dias diretamente no navegador e visualize os resultados.
   - **Como Usar**:
     1. Acesse o endpoint no navegador: `http://127.0.0.1:8000/predicaoPrecos`
     2. Insira pelo menos **60 preços históricos** separados por vírgulas no campo de texto.
     3. Insira o número de dias futuros no campo "Número de dias futuros".
     4. Insira os valores reais correspondentes no campo "Valores reais".
     5. Clique em "Enviar" para visualizar a lista de preços futuros previstos.

### 6. **Gráfico de Acurácia**
   - **Endpoint**: `GET /accuracy/plot`
   - **Descrição**: Gera um gráfico visual mostrando a acurácia das previsões realizadas com base nos valores reais fornecidos.
   - **Saída**: Um gráfico exibido no navegador.
   - **Notas:**: O gráfico exibe os valores reais, os valores previstos e a acurácia calculada para cada previsão registrada.
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

## **Deploy na Nuvem**

### **Deploy Usando AWS Elastic Beanstalk**

1. **Pré-requisitos**:
   - Instale a AWS CLI e configure com suas credenciais.
   - Certifique-se de ter um repositório ECR (Elastic Container Registry) configurado.

2. **Push da Imagem para o ECR**:
   ```bash
   aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <account_id>.dkr.ecr.<region>.amazonaws.com
   docker tag minha-api-fastapi:latest <account_id>.dkr.ecr.<region>.amazonaws.com/minha-api-fastapi:latest
   docker push <account_id>.dkr.ecr.<region>.amazonaws.com/minha-api-fastapi:latest
   ```

3. **Criar a Aplicação no Elastic Beanstalk**:
   - Acesse o console da AWS e vá até o Elastic Beanstalk.
   - Crie uma nova aplicação com o nome desejado.
   - Escolha a plataforma Docker e forneça o URI da imagem do ECR.

4. **Configurar o Ambiente**:
   - Configure a porta 8000 no Elastic Beanstalk.
   - Faça o deploy e aguarde a inicialização.

5. **Acessar o Endpoint da Aplicação**:
   O Elastic Beanstalk fornecerá um domínio onde sua aplicação estará acessível.

### **Deploy Usando uma Conta RENDER(Gratuito)**

1. Crie uma conta no Render
   
2.Crie um novo serviço Web

3.Escolha "Docker" como opção de deploy

4.Forneça o link do repositório do seu projeto (GitHub/GitLab)

5.Configure variáveis de ambiente e publique!

**LINK da Nossa API na NUVEM**:
 ```
   https://bolsavaloreslstm.onrender.com/docs
   ```
---
