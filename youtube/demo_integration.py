#!/usr/bin/env python3
"""
Demo de Integração: LLM + Servidor HTTP MCP

Este script demonstra como um cliente LLM pode descobrir e consumir
automaticamente as ferramentas disponíveis em um servidor HTTP MCP.

Arquitetura:
1. Servidor HTTP (http_server.py) expõe ferramentas MCP via REST API
2. Cliente LLM descobre automaticamente as ferramentas disponíveis
3. LLM usa as ferramentas para responder perguntas em linguagem natural
"""

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

# URL do servidor HTTP MCP
SERVER_URL = "http://localhost:8000"

class MCPHTTPClient:
    """Cliente que consome ferramentas MCP via HTTP"""
    
    def __init__(self, server_url: str):
        self.server_url = server_url
        self.discovered_tools = []
        self.server_info = {}
        
    def discover_server_capabilities(self) -> bool:
        """Descobre automaticamente as capacidades do servidor MCP"""
        print(f"🔍 Descobrindo capacidades do servidor: {self.server_url}")
        
        try:
            # 1. Informações gerais da API
            response = requests.get(f"{self.server_url}/")
            if response.status_code == 200:
                self.server_info = response.json()
                print(f"✅ Servidor: {self.server_info.get('message', 'Desconhecido')}")
                print(f"   Versão: {self.server_info.get('version', 'N/A')}")
            
            # 2. Descoberta de ferramentas MCP
            tools_response = requests.get(f"{self.server_url}/tools")
            if tools_response.status_code == 200:
                tools_data = tools_response.json()
                self.discovered_tools = tools_data.get('tools', [])
                
                print(f"\n🛠️  Ferramentas MCP descobertas: {len(self.discovered_tools)}")
                for i, tool in enumerate(self.discovered_tools, 1):
                    name = tool.get('name', 'Sem nome')
                    desc = tool.get('description', 'Sem descrição')
                    print(f"   {i}. {name}: {desc}")
                    
                    # Mostra schema de entrada se disponível
                    if 'inputSchema' in tool:
                        schema = tool['inputSchema']
                        if 'properties' in schema:
                            props = list(schema['properties'].keys())
                            print(f"      Parâmetros: {', '.join(props)}")
                
                return True
            else:
                print(f"❌ Erro ao descobrir ferramentas: {tools_response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            print(f"❌ Não foi possível conectar ao servidor: {self.server_url}")
            print("   Certifique-se de que o servidor HTTP está rodando")
            return False
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")
            return False
    
    def call_tool_by_name(self, tool_name: str, **params) -> Dict[str, Any]:
        """Chama uma ferramenta específica pelo nome"""
        try:
            # Mapeia nomes de ferramentas para endpoints HTTP
            endpoint_mapping = {
                'add': '/add',
                'subtract': '/subtract'
            }
            
            endpoint = endpoint_mapping.get(tool_name)
            if not endpoint:
                return {
                    'success': False,
                    'error': f"Ferramenta '{tool_name}' não mapeada para endpoint HTTP"
                }
            
            # Faz a requisição HTTP
            response = requests.post(f"{self.server_url}{endpoint}", json=params)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'result': result.get('result'),
                    'tool_name': tool_name,
                    'params': params
                }
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f"Erro na chamada: {str(e)}"
            }

# Instância global do cliente MCP
mcp_client = MCPHTTPClient(SERVER_URL)

def create_llm_tools() -> List:
    """Cria ferramentas LangChain que consomem o servidor MCP via HTTP"""
    
    @tool
    def discover_available_tools() -> str:
        """Descobre e lista todas as ferramentas matemáticas disponíveis no servidor MCP."""
        if not mcp_client.discovered_tools:
            if not mcp_client.discover_server_capabilities():
                return "❌ Não foi possível descobrir ferramentas no servidor MCP"
        
        if not mcp_client.discovered_tools:
            return "❌ Nenhuma ferramenta encontrada no servidor"
        
        tool_descriptions = []
        for tool in mcp_client.discovered_tools:
            name = tool.get('name', 'Sem nome')
            desc = tool.get('description', 'Sem descrição')
            
            # Extrai informações do schema
            schema_info = ""
            if 'inputSchema' in tool and 'properties' in tool['inputSchema']:
                props = tool['inputSchema']['properties']
                param_list = []
                for param_name, param_info in props.items():
                    param_type = param_info.get('type', 'unknown')
                    param_desc = param_info.get('description', '')
                    param_list.append(f"{param_name} ({param_type}): {param_desc}")
                
                if param_list:
                    schema_info = f"\n    Parâmetros: {'; '.join(param_list)}"
            
            tool_descriptions.append(f"• {name}: {desc}{schema_info}")
        
        return f"Ferramentas disponíveis no servidor MCP:\n" + "\n".join(tool_descriptions)
    
    @tool
    def add_numbers(a: int, b: int) -> str:
        """Soma dois números inteiros usando o servidor MCP.
        
        Args:
            a: Primeiro número
            b: Segundo número
            
        Returns:
            Resultado da soma
        """
        result = mcp_client.call_tool_by_name('add', a=a, b=b)
        
        if result['success']:
            return f"✅ {a} + {b} = {result['result']}"
        else:
            return f"❌ Erro na soma: {result['error']}"
    
    @tool
    def subtract_numbers(a: int, b: int) -> str:
        """Subtrai dois números inteiros usando o servidor MCP.
        
        Args:
            a: Primeiro número (minuendo)
            b: Segundo número (subtraendo)
            
        Returns:
            Resultado da subtração
        """
        result = mcp_client.call_tool_by_name('subtract', a=a, b=b)
        
        if result['success']:
            return f"✅ {a} - {b} = {result['result']}"
        else:
            return f"❌ Erro na subtração: {result['error']}"
    
    return [discover_available_tools, add_numbers, subtract_numbers]

def setup_llm_agent():
    """Configura o agente LLM com as ferramentas MCP"""
    # Configuração do modelo Azure OpenAI
    model = AzureChatOpenAI(
        azure_endpoint=azure_endpoint,
        azure_deployment=azure_deployment,
        api_key=SecretStr(azure_api_key) if azure_api_key else None,
        api_version=azure_api_version,
    )
    
    # Cria ferramentas que consomem o servidor MCP
    tools = create_llm_tools()
    
    # Cria agente React
    agent = create_react_agent(model, tools)
    
    return agent

def demo_automatic_discovery():
    """Demonstra a descoberta automática de ferramentas"""
    print("\n" + "="*60)
    print("🚀 DEMO: Descoberta Automática de Ferramentas MCP")
    print("="*60)
    
    # Tenta descobrir as ferramentas
    if mcp_client.discover_server_capabilities():
        print("\n✅ Descoberta bem-sucedida!")
        
        # Testa chamadas diretas
        print("\n🧪 Testando chamadas diretas às ferramentas:")
        
        test_cases = [
            ('add', {'a': 15, 'b': 27}),
            ('subtract', {'a': 50, 'b': 18}),
            ('add', {'a': -5, 'b': 10}),
            ('subtract', {'a': 0, 'b': 5})
        ]
        
        for tool_name, params in test_cases:
            result = mcp_client.call_tool_by_name(tool_name, **params)
            if result['success']:
                a, b = params['a'], params['b']
                op = '+' if tool_name == 'add' else '-'
                print(f"   {a} {op} {b} = {result['result']}")
            else:
                print(f"   ❌ Erro em {tool_name}: {result['error']}")
        
        return True
    else:
        print("\n❌ Falha na descoberta de ferramentas")
        return False

def demo_llm_integration():
    """Demonstra a integração com LLM"""
    print("\n" + "="*60)
    print("🤖 DEMO: Integração LLM + Servidor MCP")
    print("="*60)
    
    try:
        agent = setup_llm_agent()
        
        # Casos de teste em linguagem natural
        test_queries = [
            "Quais ferramentas estão disponíveis no servidor?",
            "Quanto é 25 + 17?",
            "Subtraia 12 de 45",
            "Calcule 100 menos 37",
            "Some 999 com 1"
        ]
        
        print("\n🗣️  Testando perguntas em linguagem natural:")
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n{i}. Pergunta: '{query}'")
            print("   Resposta: ", end="")
            
            try:
                response = agent.invoke({"messages": [query]})
                answer = response["messages"][-1].content
                print(answer)
            except Exception as e:
                print(f"❌ Erro: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na configuração do LLM: {e}")
        return False

def interactive_demo():
    """Demo interativo"""
    print("\n" + "="*60)
    print("💬 DEMO INTERATIVO: Converse com o LLM")
    print("="*60)
    print("\nO LLM pode usar automaticamente as ferramentas do servidor MCP!")
    print("\nExemplos de perguntas:")
    print("• 'Quanto é 123 + 456?'")
    print("• 'Subtraia 25 de 100'")
    print("• 'Quais ferramentas você tem disponível?'")
    print("• 'Liste as capacidades do servidor'")
    print("\nDigite 'sair' para encerrar.\n")
    
    try:
        agent = setup_llm_agent()
        
        while True:
            user_input = input("🧑 Você: ").strip()
            
            if user_input.lower() in ['sair', 'exit', 'quit', 'q']:
                print("👋 Encerrando demo...")
                break
                
            if not user_input:
                continue
                
            print("🤖 LLM: ", end="")
            
            try:
                response = agent.invoke({"messages": [user_input]})
                answer = response["messages"][-1].content
                print(answer + "\n")
            except Exception as e:
                print(f"❌ Erro: {e}\n")
                
    except Exception as e:
        print(f"❌ Erro na configuração: {e}")

def main():
    """Função principal da demonstração"""
    print("🎯 DEMONSTRAÇÃO: LLM consumindo ferramentas MCP via HTTP")
    print("\nEsta demo mostra como:")
    print("1. O cliente descobre automaticamente as ferramentas do servidor")
    print("2. O LLM usa essas ferramentas para responder perguntas")
    print("3. Tudo acontece via HTTP, sem dependências diretas do MCP")
    
    # Verifica se o servidor está rodando
    try:
        response = requests.get(f"{SERVER_URL}/")
        if response.status_code != 200:
            print(f"\n❌ Servidor não está respondendo em {SERVER_URL}")
            print("Por favor, inicie o servidor HTTP:")
            print("python http_server.py")
            return
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Não foi possível conectar ao servidor em {SERVER_URL}")
        print("Por favor, inicie o servidor HTTP:")
        print("python http_server.py")
        return
    
    print(f"\n✅ Servidor HTTP detectado em {SERVER_URL}")
    
    # Menu de opções
    while True:
        print("\n" + "="*50)
        print("📋 MENU DE DEMONSTRAÇÕES")
        print("="*50)
        print("1. 🔍 Descoberta automática de ferramentas")
        print("2. 🤖 Integração LLM (casos de teste)")
        print("3. 💬 Demo interativo (chat com LLM)")
        print("4. 🚪 Sair")
        
        choice = input("\nEscolha uma opção (1-4): ").strip()
        
        if choice == "1":
            demo_automatic_discovery()
        elif choice == "2":
            if demo_automatic_discovery():  # Precisa descobrir primeiro
                demo_llm_integration()
        elif choice == "3":
            if demo_automatic_discovery():  # Precisa descobrir primeiro
                interactive_demo()
        elif choice == "4":
            print("👋 Encerrando demonstração...")
            break
        else:
            print("❌ Opção inválida. Tente novamente.")
        
        input("\nPressione Enter para continuar...")

if __name__ == "__main__":
    main()