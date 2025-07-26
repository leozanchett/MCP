# MCP Math Server - Exposição via HTTP

Este projeto demonstra como expor um servidor MCP (Model Context Protocol) via HTTP usando FastAPI, permitindo que outros clientes consumam as funcionalidades através de uma API REST.

## Estrutura do Projeto

```
youtube/
├── client.py          # Cliente MCP original (stdio)
├── math_server.py     # Servidor MCP com operações matemáticas
├── http_server.py     # Servidor HTTP que expõe o MCP via REST API
└── example_client.py  # Exemplos de como consumir a API HTTP
```

## Instalação

1. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure as variáveis de ambiente (se necessário):**
   Crie um arquivo `.env` com suas configurações do Azure OpenAI (para o client.py original):
   ```
   AZURE_OPENAI_ENDPOINT=sua_url
   AZURE_OPENAI_API_KEY=sua_chave
   AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=seu_modelo
   OPENAI_API_VERSION=2024-02-15-preview
   ```

## Como Usar

### 1. Iniciando o Servidor HTTP

```bash
cd youtube
python http_server.py
```

O servidor será iniciado em `http://localhost:8000`

### 2. Acessando a Documentação da API

Após iniciar o servidor, acesse:
- **Documentação Swagger:** http://localhost:8000/docs
- **Documentação ReDoc:** http://localhost:8000/redoc

### 3. Endpoints Disponíveis

| Método | Endpoint | Descrição |
|--------|----------|----------|
| GET | `/` | Informações da API |
| GET | `/tools` | Lista ferramentas disponíveis |
| POST | `/add` | Soma dois números |
| POST | `/subtract` | Subtrai dois números |
| POST | `/calculate` | Endpoint genérico para cálculos |

### 4. Exemplos de Uso

#### Python (usando requests)

```python
import requests

# Somar dois números
response = requests.post('http://localhost:8000/add', 
                        json={'a': 5, 'b': 3})
result = response.json()
print(f"Resultado: {result['result']}")  # 8
```

#### JavaScript (usando fetch)

```javascript
// Somar dois números
fetch('http://localhost:8000/add', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({a: 5, b: 3})
})
.then(response => response.json())
.then(data => console.log('Resultado:', data.result));
```

#### cURL

```bash
# Somar dois números
curl -X POST http://localhost:8000/add \
  -H "Content-Type: application/json" \
  -d '{"a": 5, "b": 3}'
```

### 5. Testando com o Cliente de Exemplo

```bash
python example_client.py
```

Este script testa todos os endpoints e mostra exemplos em diferentes linguagens.

## Arquitetura

### Como Funciona

1. **math_server.py**: Servidor MCP que define as ferramentas matemáticas
2. **http_server.py**: Servidor FastAPI que:
   - Inicia uma sessão com o servidor MCP
   - Expõe as ferramentas MCP como endpoints HTTP
   - Converte requisições HTTP em chamadas MCP
3. **Clientes**: Podem consumir a API via HTTP de qualquer linguagem

### Fluxo de Dados

```
Cliente HTTP → FastAPI → MCP Client → MCP Server → Resposta
```

## Vantagens da Exposição HTTP

1. **Interoperabilidade**: Qualquer linguagem pode consumir via HTTP
2. **Escalabilidade**: Pode ser deployado em containers, load balancers, etc.
3. **Documentação**: FastAPI gera documentação automática
4. **Padrão REST**: Familiar para a maioria dos desenvolvedores
5. **Monitoramento**: Fácil de monitorar com ferramentas HTTP

## Extensões Possíveis

1. **Autenticação**: Adicionar JWT, API Keys, etc.
2. **Rate Limiting**: Controlar número de requisições
3. **Logging**: Adicionar logs detalhados
4. **Métricas**: Prometheus, Grafana, etc.
5. **Cache**: Redis para cache de respostas
6. **WebSockets**: Para comunicação em tempo real
7. **Múltiplos Servidores MCP**: Proxy para diferentes servidores

## Deployment

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY youtube/ .

EXPOSE 8000
CMD ["python", "http_server.py"]
```

### Produção

Para produção, considere:
- Usar Gunicorn ou similar
- Configurar HTTPS
- Adicionar monitoramento
- Configurar logs estruturados

## Troubleshooting

1. **Erro de conexão**: Verifique se o math_server.py está acessível
2. **Porta ocupada**: Mude a porta no http_server.py
3. **Dependências**: Certifique-se de que todas as dependências estão instaladas

## Comparação: MCP vs HTTP

| Aspecto | MCP (stdio) | HTTP API |
|---------|-------------|----------|
| Performance | Mais rápido | Overhead HTTP |
| Interoperabilidade | Limitada | Universal |
| Debugging | Mais difícil | Ferramentas HTTP |
| Escalabilidade | Limitada | Alta |
| Documentação | Manual | Automática |