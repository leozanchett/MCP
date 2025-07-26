#!/usr/bin/env python3
"""
Servidor MCP via HTTP

Este servidor implementa o protocolo MCP (Model Context Protocol) completo
via transporte HTTP, permitindo que clientes MCP se conectem via HTTP.
"""

from fastmcp import FastMCP
import uvicorn
from typing import Any

# Cria o servidor MCP
server = FastMCP("Math Server")

@server.tool()
def add(a: int, b: int) -> int:
    """Soma dois números inteiros.
    
    Args:
        a: Primeiro número
        b: Segundo número
        
    Returns:
        A soma de a + b
    """
    return a + b

@server.tool()
def subtract(a: int, b: int) -> int:
    """Subtrai dois números inteiros.
    
    Args:
        a: Primeiro número (minuendo)
        b: Segundo número (subtraendo)
        
    Returns:
        A diferença de a - b
    """
    return a - b

@server.tool()
def multiply(a: int, b: int) -> int:
    """Multiplica dois números inteiros.
    
    Args:
        a: Primeiro número
        b: Segundo número
        
    Returns:
        O produto de a * b
    """
    return a * b

@server.tool()
def divide(a: int, b: int) -> float:
    """Divide dois números inteiros.
    
    Args:
        a: Dividendo
        b: Divisor (não pode ser zero)
        
    Returns:
        O quociente de a / b
        
    Raises:
        ValueError: Se b for zero
    """
    if b == 0:
        raise ValueError("Divisão por zero não é permitida")
    return a / b

@server.tool()
def power(base: int, exponent: int) -> int:
    """Calcula a potência de um número.
    
    Args:
        base: Número base
        exponent: Expoente
        
    Returns:
        base elevado à potência exponent
    """
    return base ** exponent

@server.tool()
def factorial(n: int) -> int:
    """Calcula o fatorial de um número.
    
    Args:
        n: Número não-negativo
        
    Returns:
        O fatorial de n
        
    Raises:
        ValueError: Se n for negativo
    """
    if n < 0:
        raise ValueError("Fatorial não é definido para números negativos")
    if n == 0 or n == 1:
        return 1
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

def main():
    """Inicia o servidor MCP via HTTP"""
    print("🚀 Iniciando Servidor MCP via HTTP...")
    print("📡 Protocolo: MCP (Model Context Protocol)")
    print("🌐 Transporte: HTTP")
    print("🔧 Ferramentas disponíveis:")
    print("   • add - Soma dois números")
    print("   • subtract - Subtrai dois números")
    print("   • multiply - Multiplica dois números")
    print("   • divide - Divide dois números")
    print("   • power - Calcula potência")
    print("   • factorial - Calcula fatorial")
    print("\n📍 Servidor rodando em: http://localhost:8001")
    print("📚 Documentação MCP: http://localhost:8001/docs")
    print("\n🔗 Para conectar um cliente MCP:")
    print("   URL: http://localhost:8001")
    print("   Transporte: HTTP")
    print("\n⚡ Pressione Ctrl+C para parar o servidor")
    
    # Usa o método run() do FastMCP com transporte HTTP
    server.run(
        transport="http",
        host="0.0.0.0",
        port=8001
    )

if __name__ == "__main__":
    main()