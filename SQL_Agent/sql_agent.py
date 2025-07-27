# Instale as bibliotecas necessárias
# pip install langchain langchain-openai langgraph langchain-community sqlalchemy python-dotenv

import os
from langchain_openai import AzureChatOpenAI
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit, create_sql_agent
from pydantic import SecretStr
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# --- 1. Configuração do Ambiente (Azure OpenAI) ---
azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
azure_deployment = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME") or os.getenv("AZURE_MODEL_NAME")
azure_api_version = os.getenv("OPENAI_API_VERSION")

# Verifique se as variáveis de ambiente do Azure estão configuradas
if not all([azure_endpoint, azure_api_key, azure_deployment, azure_api_version]):
    print("Erro: Uma ou mais variáveis de ambiente do Azure OpenAI não foram definidas.")
    print("Por favor, configure AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, AZURE_OPENAI_CHAT_DEPLOYMENT_NAME, e OPENAI_API_VERSION.")
    exit()

# --- 2. Configuração do Banco de Dados ---
# Conectando ao banco de dados local Chinook.db
db = SQLDatabase.from_uri("sqlite:///Chinook.db")

# --- 3. Criação das Ferramentas e do Agente ---
# Inicialize o modelo de linguagem que o agente usará
llm = AzureChatOpenAI(
    azure_endpoint=azure_endpoint,
    azure_deployment=azure_deployment,
    api_key=SecretStr(azure_api_key) if azure_api_key else None,
    api_version=azure_api_version,
    temperature=0
)

# Crie o SQLDatabaseToolkit, que contém as ferramentas para interagir com o banco de dados
toolkit = SQLDatabaseToolkit(db=db, llm=llm)

# Crie o agente SQL usando a abordagem mais estável
agent_executor = create_sql_agent(
    llm=llm,                            # Language model instance to use
    toolkit=toolkit,                    # SQL toolkit containing database interaction tools
    agent_type="openai-tools",          # Type of agent to create (using OpenAI tools format)
    verbose=True,                       # Enable detailed output of agent's thought process
    max_iterations=15,                  # Maximum number of reasoning steps before stopping
    max_execution_time=None,            # No time limit for execution
    early_stopping_method="force",      # Force stop when max iterations reached
)

print("Agente SQL pronto! Faça suas perguntas sobre o banco de dados Chinook.")
print("Exemplos: 'Liste todos os artistas', 'Quantos funcionários existem?', 'Quais são os álbuns do artista Queen?'")
print("Digite 'sair' para terminar.")
print("-" * 30)

# --- 4. Loop de Interação com o Agente ---
while True:
    user_input = input("Sua pergunta: ")
    if user_input.lower() == 'sair':
        break

    try:
        # Use invoke diretamente no agente criado pelo create_sql_agent
        response = agent_executor.invoke({"input": user_input})
        final_response = response.get("output")
        print("\nResposta Final:")
        print(final_response)
        print("-" * 30)
    except Exception as e:
        print(f"\nOcorreu um erro durante a execução: {e}")
        print("-" * 30)
