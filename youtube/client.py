from mcp import ClientSession, StdioServerParameters
from langchain_openai import AzureChatOpenAI
from pydantic import SecretStr
from langchain_mcp_adapters.tools import load_mcp_tools
from mcp.client.stdio import stdio_client
from langgraph.prebuilt import create_react_agent
import asyncio
import os
from dotenv import load_dotenv


load_dotenv()

# Carrega variáveis de ambiente
azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
azure_deployment = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME") or os.getenv("AZURE_MODEL_NAME")
azure_api_version = os.getenv("OPENAI_API_VERSION")

model = AzureChatOpenAI(
    azure_endpoint=azure_endpoint,
    azure_deployment=azure_deployment,
    api_key=SecretStr(azure_api_key) if azure_api_key else None,
    api_version=azure_api_version,
)

server_params = StdioServerParameters(
    command="python",
    args=["math_server.py"],
)
async def run_agent():
    # Inicia o cliente MCP com os parâmetros do servidor
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await load_mcp_tools(session)
            agent = create_react_agent(model, tools)
            agent_response = await agent.ainvoke({"messages": ["Qual é a soma de 5 e 3?"]})
           
            # Retorna apenas o conteúdo da resposta da IA
            return agent_response["messages"][-1].content

if __name__ == "__main__":
    response = asyncio.run(run_agent())
    print(response)
