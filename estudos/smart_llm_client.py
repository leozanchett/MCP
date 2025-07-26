import requests
import json
from langchain_openai import AzureChatOpenAI
from pydantic import SecretStr
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
import os
from dotenv import load_dotenv
from typing import Dict, Any, List

load_dotenv()

# Configuração do Azure OpenAI
azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
azure_deployment = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME") or os.getenv("AZURE_MODEL_NAME")
azure_api_version = os.getenv("OPENAI_API_VERSION")

# URL base do servidor HTTP
BASE_URL = "http://localhost:8000"

# Configuração do modelo LLM
model = AzureChatOpenAI(
    azure_endpoint=azure_endpoint,
    azure_deployment=azure_deployment,
    api_key=SecretStr(azure_api_key) if azure_api_key else None,
    api_version=azure_api_version,
)

class DynamicHTTPClient:
    """Cliente que descobre automaticamente as ferramentas do servidor HTTP"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.available_tools = []
        self.endpoints = {}
        
    def discover_tools(self) -> bool:
        """Descobre as ferramentas disponíveis no servidor"""
        try:
            # 1. Busca informações gerais da API
            response = requests.get(f"{self.base_url}/")
            if response.status_code == 200:
                api_info = response.json()
                self.endpoints = api_info.get('endpoints', {})
                print(f"✅ API descoberta: {api_info.get('message', 'Desconhecida')}")
            
            # 2. Busca ferramentas específicas do MCP
            tools_response = requests.get(f"{self.base_url}/tools")
            if tools_response.status_code == 200:
                tools_data = tools_response.json()
                self.available_tools = tools_data.get('tools', [])
                print(f"✅ Ferramentas descobertas: {len(self.available_tools)}")
                
                for tool_info in self.available_tools:
                    print(f"   - {tool_info['name']}: {tool_info.get('description', 'Sem descrição')}")
                
                return True
            else:
                print(f"❌ Erro ao buscar ferramentas: {tools_response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao descobrir ferramentas: {e}")
            return False
    
    def call_tool(self, tool_name: str, **kwargs) -> str:
        """Chama uma ferramenta específica no servidor"""
        try:
            # Mapeia nomes de ferramentas para endpoints
            endpoint_map = {
                'add': '/add',
                'subtract': '/subtract'
            }
            
            endpoint = endpoint_map.get(tool_name)
            if not endpoint:
                return f"Ferramenta '{tool_name}' não encontrada"
            
            response = requests.post(f"{self.base_url}{endpoint}", json=kwargs)
            
            if response.status_code == 200:
                result = response.json()
                return str(result.get('result', 'Sem resultado'))
            else:
                return f"Erro na requisição: {response.status_code}"
                
        except Exception as e:
            return f"Erro ao chamar ferramenta: {e}"

# Instância global do cliente
http_client = DynamicHTTPClient(BASE_URL)

def create_dynamic_tools() -> List:
    """Cria ferramentas LangChain baseadas nas ferramentas descobertas"""
    tools = []
    
    # Ferramenta genérica que descobre e lista ferramentas
    @tool
    def list_server_tools() -> str:
        """Lista todas as ferramentas matemáticas disponíveis no servidor HTTP."""
        if not http_client.available_tools:
            if not http_client.discover_tools():
                return "Não foi possível descobrir as ferramentas do servidor"
        
        tool_list = []
        for tool_info in http_client.available_tools:
            name = tool_info['name']
            desc = tool_info.get('description', 'Sem descrição')
            tool_list.append(f"- {name}: {desc}")
        
        return "Ferramentas disponíveis no servidor:\n" + "\n".join(tool_list)
    
    # Ferramenta dinâmica para soma
    @tool
    def add_numbers(a: int, b: int) -> str:
        """Soma dois números inteiros usando o servidor HTTP.
        
        Args:
            a: Primeiro número
            b: Segundo número
            
        Returns:
            Resultado da soma
        """
        result = http_client.call_tool('add', a=a, b=b)
        return f"A soma de {a} + {b} = {result}"
    
    # Ferramenta dinâmica para subtração
    @tool
    def subtract_numbers(a: int, b: int) -> str:
        """Subtrai dois números inteiros usando o servidor HTTP.
        
        Args:
            a: Primeiro número (minuendo)
            b: Segundo número (subtraendo)
            
        Returns:
            Resultado da subtração
        """
        result = http_client.call_tool('subtract', a=a, b=b)
        return f"A subtração de {a} - {b} = {result}"
    
    tools.extend([list_server_tools, add_numbers, subtract_numbers])
    return tools

def check_server_connection() -> bool:
    """Verifica se o servidor está rodando e descobre as ferramentas"""
    print("🔍 Verificando conexão com o servidor...")
    
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Servidor HTTP está rodando!")
            
            # Descobre as ferramentas automaticamente
            if http_client.discover_tools():
                return True
            else:
                print("⚠️  Servidor rodando, mas não foi possível descobrir ferramentas")
                return False
        else:
            print(f"❌ Servidor retornou status: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Não foi possível conectar ao servidor HTTP.")
        print("   Certifique-se de que o servidor está rodando em http://localhost:8000")
        print("   Execute: python http_server.py")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def chat_with_agent(message: str, agent) -> str:
    """Conversa com o agente LLM"""
    try:
        response = agent.invoke({"messages": [message]})
        return response["messages"][-1].content
    except Exception as e:
        return f"Erro no agente: {e}"

def interactive_chat():
    """Interface interativa para conversar com o agente"""
    print("\n=== Cliente LLM Inteligente + Servidor HTTP ===")
    print("Este cliente descobre automaticamente as ferramentas do servidor!")
    print("\nExemplos de perguntas:")
    print("- 'Quanto é 15 + 27?'")
    print("- 'Subtraia 8 de 20'")
    print("- 'Quais ferramentas estão disponíveis?'")
    print("- 'Liste as ferramentas do servidor'")
    print("\nDigite 'sair' para encerrar.\n")
    
    # Cria o agente com ferramentas dinâmicas
    tools = create_dynamic_tools()
    agent = create_react_agent(model, tools)
    
    while True:
        user_input = input("Você: ").strip()
        
        if user_input.lower() in ['sair', 'exit', 'quit']:
            print("Encerrando...")
            break
            
        if not user_input:
            continue
            
        print("\n🤖 Agente: Processando...")
        response = chat_with_agent(user_input, agent)
        print(f"🤖 Agente: {response}\n")

def test_discovery():
    """Testa a descoberta automática de ferramentas"""
    print("\n=== Teste de Descoberta Automática ===")
    
    if http_client.discover_tools():
        print("\n📋 Resumo das ferramentas descobertas:")
        for tool in http_client.available_tools:
            print(f"   🔧 {tool['name']}: {tool.get('description', 'Sem descrição')}")
            
        print("\n🧪 Testando chamadas diretas:")
        print(f"   add(5, 3) = {http_client.call_tool('add', a=5, b=3)}")
        print(f"   subtract(10, 4) = {http_client.call_tool('subtract', a=10, b=4)}")
    else:
        print("❌ Falha na descoberta de ferramentas")

if __name__ == "__main__":
    if not check_server_connection():
        print("\n❌ Não foi possível conectar ao servidor.")
        print("Por favor, inicie o servidor HTTP primeiro:")
        print("python http_server.py")
        exit(1)
    
    print("\n🎯 Escolha uma opção:")
    print("1. Chat interativo com LLM")
    print("2. Testar descoberta de ferramentas")
    
    choice = input("\nDigite sua escolha (1 ou 2): ").strip()
    
    if choice == "1":
        interactive_chat()
    elif choice == "2":
        test_discovery()
        print("\n💡 Agora você pode executar o chat interativo!")
        interactive_chat()
    else:
        print("Opção inválida. Executando chat interativo...")
        interactive_chat()