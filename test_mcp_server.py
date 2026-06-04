#!/usr/bin/env python3
"""Teste básico do servidor MCP LotoScope."""

import asyncio
import json
import sys
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters


async def test_mcp_server():
    """Testa se o servidor MCP está funcionando."""
    print("Iniciando teste do servidor MCP LotoScope...")
    
    # Configuração do servidor
    server_params = StdioServerParameters(
        command=".venv\\Scripts\\python.exe",
        args=["lotoscope_mcp_server.py"]
    )
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Inicializar
                await session.initialize()
                print("[OK] Servidor inicializado com sucesso")
                
                # Listar tools
                tools = await session.list_tools()
                print(f"[OK] {len(tools.tools)} tools disponíveis:")
                for tool in tools.tools:
                    print(f"  - {tool.name}: {tool.description[:60]}...")
                
                # Testar list_agents
                result = await session.call_tool("lotoscope_list_agents", {})
                agents = json.loads(result.content[0].text)
                print(f"[OK] {len(agents)} agentes encontrados")
                
                # Testar route
                result = await session.call_tool("lotoscope_route", {"request": "analisar concurso 3643"})
                route = json.loads(result.content[0].text)
                print(f"[OK] Roteamento: {route['routed_to']} (confianca: {route['confidence']})")
                
                # Testar call_agent
                result = await session.call_tool("lotoscope_call_agent", {
                    "agent_id": "analyst",
                    "task": "verificar frequencias"
                })
                call = json.loads(result.content[0].text)
                print(f"[OK] Agente chamado: {call['agent_name']} - status: {call['status']}")
                
                print("\n[OK] Todos os testes passaram!")
                return True
    
    except Exception as e:
        print(f"[ERRO] {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_mcp_server())
    exit(0 if success else 1)
