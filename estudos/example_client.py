import requests
import json

# URL base do servidor HTTP
BASE_URL = "http://localhost:8000"

def test_api():
    """Testa a API HTTP do MCP Math Server"""
    
    print("=== Testando MCP Math Server HTTP API ===")
    
    # 1. Testar endpoint raiz
    print("\n1. Informações da API:")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        else:
            print(f"Erro: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("Erro: Não foi possível conectar ao servidor. Certifique-se de que o servidor está rodando.")
        return
    
    # 2. Listar ferramentas disponíveis
    print("\n2. Ferramentas disponíveis:")
    try:
        response = requests.get(f"{BASE_URL}/tools")
        if response.status_code == 200:
            tools = response.json()
            print(json.dumps(tools, indent=2, ensure_ascii=False))
        else:
            print(f"Erro: {response.status_code}")
    except Exception as e:
        print(f"Erro ao listar ferramentas: {e}")
    
    # 3. Testar soma
    print("\n3. Testando soma (5 + 3):")
    try:
        data = {"a": 5, "b": 3}
        response = requests.post(f"{BASE_URL}/add", json=data)
        if response.status_code == 200:
            result = response.json()
            print(f"Resultado: {result['a']} + {result['b']} = {result['result']}")
        else:
            print(f"Erro: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Erro na soma: {e}")
    
    # 4. Testar subtração
    print("\n4. Testando subtração (10 - 4):")
    try:
        data = {"a": 10, "b": 4}
        response = requests.post(f"{BASE_URL}/subtract", json=data)
        if response.status_code == 200:
            result = response.json()
            print(f"Resultado: {result['a']} - {result['b']} = {result['result']}")
        else:
            print(f"Erro: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Erro na subtração: {e}")
    
    # 5. Testar endpoint genérico
    print("\n5. Testando endpoint genérico:")
    try:
        data = {"query": "Quanto é 7 + 2?"}
        response = requests.post(f"{BASE_URL}/calculate", json=data)
        if response.status_code == 200:
            result = response.json()
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"Erro: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Erro no cálculo genérico: {e}")

def example_javascript_fetch():
    """Exemplo de como consumir a API usando JavaScript/Fetch"""
    js_code = '''
// Exemplo de consumo da API usando JavaScript (Fetch)

// Função para somar dois números
async function addNumbers(a, b) {
    try {
        const response = await fetch('http://localhost:8000/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ a: a, b: b })
        });
        
        if (response.ok) {
            const result = await response.json();
            console.log(`${result.a} + ${result.b} = ${result.result}`);
            return result;
        } else {
            console.error('Erro na requisição:', response.status);
        }
    } catch (error) {
        console.error('Erro:', error);
    }
}

// Função para subtrair dois números
async function subtractNumbers(a, b) {
    try {
        const response = await fetch('http://localhost:8000/subtract', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ a: a, b: b })
        });
        
        if (response.ok) {
            const result = await response.json();
            console.log(`${result.a} - ${result.b} = ${result.result}`);
            return result;
        } else {
            console.error('Erro na requisição:', response.status);
        }
    } catch (error) {
        console.error('Erro:', error);
    }
}

// Exemplo de uso
addNumbers(5, 3);
subtractNumbers(10, 4);
'''
    
    print("\n=== Exemplo JavaScript/Fetch ===")
    print(js_code)

def example_curl_commands():
    """Exemplos de comandos cURL para testar a API"""
    curl_examples = '''
=== Exemplos de comandos cURL ===

# 1. Obter informações da API
curl -X GET http://localhost:8000/

# 2. Listar ferramentas disponíveis
curl -X GET http://localhost:8000/tools

# 3. Somar dois números
curl -X POST http://localhost:8000/add \
  -H "Content-Type: application/json" \
  -d '{"a": 5, "b": 3}'

# 4. Subtrair dois números
curl -X POST http://localhost:8000/subtract \
  -H "Content-Type: application/json" \
  -d '{"a": 10, "b": 4}'

# 5. Endpoint genérico
curl -X POST http://localhost:8000/calculate \
  -H "Content-Type: application/json" \
  -d '{"query": "Quanto é 7 + 2?"}'
'''
    
    print(curl_examples)

if __name__ == "__main__":
    # Testa a API Python
    test_api()
    
    # Mostra exemplos em outras linguagens
    example_javascript_fetch()
    example_curl_commands()
    
    print("\n=== Instruções ===")
    print("1. Primeiro, inicie o servidor HTTP: python http_server.py")
    print("2. Em seguida, execute este cliente: python example_client.py")
    print("3. Ou acesse a documentação interativa em: http://localhost:8000/docs")