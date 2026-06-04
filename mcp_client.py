#!/usr/bin/env python3
"""
MCP Client para chamar agentes via terminal.
Uso: python mcp_client.py <comando> <args>

Exemplos:
    python mcp_client.py list
    python mcp_client.py route "analisar concurso 3643"
    python mcp_client.py call coordinator "orquestrar analise"
    python mcp_client.py orchestrate pos_sorteio
"""

import asyncio
import json
import sys
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters


async def call_mcp_tool(tool_name: str, arguments: dict):
    """Chama uma tool do servidor MCP."""
    server_params = StdioServerParameters(
        command=".venv\\Scripts\\python.exe",
        args=["lotoscope_mcp_server.py"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, arguments)
            return json.loads(result.content[0].text)


def main():
    if len(sys.argv) < 2:
        print("Uso: python mcp_client.py <comando> [args]")
        print("\nComandos:")
        print("  list                          - Lista agentes")
        print("  workflows                     - Lista workflows")
        print("  route <request>               - Roteia para agente")
        print("  call <agent_id> <task>        - Chama agente")
        print("  context <agent_id>            - Contexto do agente")
        print("  orchestrate <workflow>        - Executa workflow")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "list":
        result = asyncio.run(call_mcp_tool("lotoscope_list_agents", {}))
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif command == "workflows":
        result = asyncio.run(call_mcp_tool("lotoscope_list_workflows", {}))
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif command == "route":
        if len(sys.argv) < 3:
            print("Uso: route <request>")
            sys.exit(1)
        request = " ".join(sys.argv[2:])
        result = asyncio.run(call_mcp_tool("lotoscope_route", {"request": request}))
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif command == "call":
        if len(sys.argv) < 4:
            print("Uso: call <agent_id> <task>")
            sys.exit(1)
        agent_id = sys.argv[2]
        task = " ".join(sys.argv[3:])
        result = asyncio.run(call_mcp_tool("lotoscope_call_agent", {
            "agent_id": agent_id,
            "task": task
        }))
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif command == "context":
        if len(sys.argv) < 3:
            print("Uso: context <agent_id>")
            sys.exit(1)
        agent_id = sys.argv[2]
        result = asyncio.run(call_mcp_tool("lotoscope_get_context", {"agent_id": agent_id}))
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif command == "orchestrate":
        if len(sys.argv) < 3:
            print("Uso: orchestrate <workflow>")
            sys.exit(1)
        workflow_id = sys.argv[2]
        result = asyncio.run(call_mcp_tool("lotoscope_orchestrate", {"workflow_id": workflow_id}))
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    else:
        print(f"Comando desconhecido: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
