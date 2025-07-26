import asyncio
import requests
from langchain_openai import AzureChatOpenAI
from pydantic import SecretStr
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
import os
from dotenv import load_dotenv

load_dotenv()

# Configuração do Azure OpenAI
azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
azure_deployment = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME") or os.getenv("AZURE_MODEL_NAME")
azure_api_version = os.getenv("OPENAI_API_VERSION")

# URL do servidor HTTP
SERVER_URL = "http://localhost:8000"

# Configuração do modelo LLM
model = AzureChatOpenAI(
    azure_endpoint=azure_endpoint,
    azure_deployment=azure_deployment,
    api_key=SecretStr(azure_api_key) if azure_api_key else None,
    api_version=azure_api_version,
)

def call_math_server(endpoint: str, **params):
    """Chama o servidor de matemática via HTTP"""
    try:
        response = requests.post(f"{SERVER_URL}{endpoint}", json=params)
        if response.status_code == 200:
            return response.json().get('result')
        else:
            return f"Erro: {response.status_code}"
    except Exception as e:
        return f"Erro na conexão: {e}"

@tool
def add_numbers(a: int, b: int) -> str:
    """Soma dois números inteiros.
    
    Args:
        a: Primeiro número
        b: Segundo número
        
    Returns:
        Resultado da soma
    """
    result = call_math_server('/add', a=a, b=b)
    return f"A soma de {a} + {b} = {result}"

@tool
def subtract_numbers(a: int, b: int) -> str:
    """Subtrai dois números inteiros.
    
    Args:
        a: Primeiro número (minuendo)
        b: Segundo número (subtraendo)
        
    Returns:
        Resultado da subtração
    """
    result = call_math_server('/subtract', a=a, b=b)
    return f"A subtração de {a} - {b} = {result}"

@tool
def list_available_tools() -> str:
    """Lista as ferramentas matemáticas disponíveis no servidor."""
    try:
        response = requests.get(f"{SERVER_URL}/tools")
        if response.status_code == 200:
            tools_data = response.json()
            tools = tools_data.get('tools', [])
            
            tool_list = []
            for tool_info in tools:
                name = tool_info.get('name', 'Sem nome')
                desc = tool_info.get('description', 'Sem descrição')
                tool_list.append(f"• {name}: {desc}")
            
            return "Ferramentas disponíveis no servidor:\n" + "\n".join(tool_list)
        else:
            return f"Erro ao buscar ferramentas: {response.status_code}"
    except Exception as e:
        return f"Erro na conexão: {e}"

def create_agent():
    """Cria o agente LangChain com as ferramentas do servidor HTTP"""
    tools = [add_numbers, subtract_numbers, list_available_tools]
    return create_react_agent(model, tools)

async def get_agent_response(agent, message: str):
    """Obtém resposta do agente para uma mensagem"""
    try:
        response = await agent.ainvoke({"messages": [message]})
        return response["messages"][-1].content
    except Exception as e:
        return f"Erro no agente: {e}"

async def test_server_connection():
    """Testa a conexão com o servidor HTTP"""
    try:
        response = requests.get(f"{SERVER_URL}/")
        if response.status_code == 200:
            print("✅ Servidor HTTP está rodando!")
            return True
        else:
            print(f"❌ Servidor retornou status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Não foi possível conectar ao servidor HTTP.")
        print("   Certifique-se de que o servidor está rodando em http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

async def main():
    """Função principal"""
    print("🧮 Cliente LangChain + Servidor HTTP de Matemática")
    print("="*50)
    
    # Verifica conexão com o servidor
    if not await test_server_connection():
        print("\nPor favor, inicie o servidor HTTP primeiro:")
        print("python http_server.py")
        return
    
    # Cria o agente
    print("\n🤖 Criando agente LangChain...")
    agent = create_agent()
    
    # Testa algumas consultas
    test_queries = [
        "what's (3 + 5) x 12?",
        "Quanto é 25 + 17?",
        "Subtraia 12 de 45",
        "Quais ferramentas estão disponíveis?",
        "Calcule 100 menos 37"
    ]
    
    print("\n🧪 Testando consultas:")
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Pergunta: '{query}'")
        print("   Resposta: ", end="")
        
        response = await get_agent_response(agent, query)
        print(response)
    
    print("\n✅ Teste concluído!")

if __name__ == "__main__":
    # Executa a função principal
    asyncio.run(main())