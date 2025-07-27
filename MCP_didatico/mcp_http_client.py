#!/usr/bin/env python3
"""
Cliente MCP via HTTP

Este cliente se conecta a um servidor MCP via HTTP usando o protocolo MCP completo.
Demonstra como consumir ferramentas MCP através de transporte HTTP.
"""

import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import AzureChatOpenAI
from pydantic import SecretStr
from langgraph.prebuilt import create_react_agent
import os
from dotenv import load_dotenv

load_dotenv()

# Configuração do Azure OpenAI
azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
azure_deployment = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME") or os.getenv("AZURE_MODEL_NAME")
azure_api_version = os.getenv("OPENAI_API_VERSION")

# Configuração do cliente MCP
client = MultiServerMCPClient(
    {
        # "math_server": {
        #     "url": "http://localhost:8001/mcp",
        #     "transport": "streamable_http",  # Usa transporte HTTP streamable para MCP
        # },
        # "duckduckgo": {
        #     "command": "docker",
        #     "args": ["run", "-i", "--rm", "mcp/duckduckgo"],  # Docker run command: -i enables interactive mode (stdin), --rm removes container after exit
        #     "transport": "stdio"
        # },
        "SQLite": {
            "command": "docker",
            "args": [
                "run",
                "-i",
                "--rm",
                "-v",
                # Maps a local directory from host machine to container for SQLite database persistence
                "C:\\Users\\lzandrade.TOPAZ\\Documents\\GitHub\\MCP\\MCP_didatico:/local-directory",
                "mcp/sqlite",
                "--db-path",
                "/local-directory/db.sqlite"
            ],
            "transport": "stdio",
            "name": "SQLite",
            "description": "Banco de dados SQLite para armazenar informações"
        }
    }
)

# Configuração do modelo LLM
model = AzureChatOpenAI(
    azure_endpoint=azure_endpoint,
    azure_deployment=azure_deployment,
    api_key=SecretStr(azure_api_key) if azure_api_key else None,
    api_version=azure_api_version,
)

async def test_mcp_connection():
    """Testa a conexão com o servidor MCP via HTTP"""
    print("🔍 Testando conexão com servidor MCP via HTTP...")
    
    try:
        # Obtém as ferramentas disponíveis
        tools = await client.get_tools()
        
        print(f"✅ Conexão estabelecida com sucesso!")
        print(f"🔧 Ferramentas descobertas: {len(tools)}")
        
        for i, tool in enumerate(tools, 1):
            print(f"   {i}. {tool.name}")
        
        return True, tools
        
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        print("   Certifique-se de que o servidor MCP está rodando em http://localhost:8001")
        return False, []

async def create_llm_agent():
    """Cria um agente LLM que usa as ferramentas MCP via HTTP"""
    print("\n🤖 Criando agente LLM com ferramentas MCP...")
    
    try:
        # Obtém as ferramentas do servidor MCP
        tools = await client.get_tools()
        
        # Cria o agente React
        agent = create_react_agent(model, tools)
        
        print(f"✅ Agente criado com {len(tools)} ferramentas MCP")
        return agent
        
    except Exception as e:
        print(f"❌ Erro ao criar agente: {e}")
        return None

async def interactive_chat():
    """Chat interativo com o agente LLM + MCP"""
    print("\n" + "="*60)
    print("💬 CHAT INTERATIVO: LLM + Servidor MCP via HTTP")
    print("="*60)
    print("\nO LLM pode usar todas as ferramentas matemáticas do servidor MCP!")
    print("\nDigite 'sair' para encerrar.\n")
    
    agent = await create_llm_agent()
    if not agent:
        print("❌ Não foi possível criar o agente")
        return
    
    while True:
        try:
            user_input = input("🧑 Você: ").strip()
            
            if user_input.lower() in ['sair', 'exit', 'quit', 'q']:
                print("👋 Encerrando chat...")
                break
                
            if not user_input:
                continue
                
            print("🤖 LLM: ", end="")
            
            response = await agent.ainvoke({"messages": [user_input]})
            answer = response["messages"][-1].content
            print(answer + "\n")
            
        except KeyboardInterrupt:
            print("\n👋 Chat interrompido pelo usuário")
            break
        except Exception as e:
            print(f"❌ Erro: {e}\n")

async def main():
    """Função principal"""
    print("🎯 CLIENTE MCP VIA HTTP")    
    # Testa a conexão
    connected, tools = await test_mcp_connection()
    if not connected:
        print("\n❌ Não foi possível conectar ao servidor MCP")
        print("Por favor, inicie o servidor MCP primeiro:")
        print("python mcp_http_server.py")
        return
    
    # Menu de opções
    while True:
        print("\n" + "="*50)
        print("📋 MENU DE TESTES")
        print("="*50)
        print("1. 💬 Chat interativo com LLM")
        print("2. 🔍 Reconectar e listar ferramentas")
        print("3. 🚪 Sair")
        
        choice = input("\nEscolha uma opção (1-3): ").strip()
        
        if choice == "1":
            await interactive_chat()
        elif choice == "2":
            await test_mcp_connection()
        elif choice == "3":
            print("👋 Encerrando cliente MCP...")
            break
        else:
            print("❌ Opção inválida. Tente novamente.")
        
        if choice in ["1", "2"]:
            input("\nPressione Enter para continuar...")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Cliente MCP encerrado pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")