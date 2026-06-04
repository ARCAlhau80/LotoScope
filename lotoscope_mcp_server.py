#!/usr/bin/env python3
"""
LotoScope MCP Server - Orquestração Bidirecional
Integração completa entre Copilot Agents e OpenCode.

Fluxo:
1. Copilot Agent (@Agente X) recebe comando do usuário
2. Agente executa via MCP tools
3. Se não souber resolver, chama lotoscope_delegate → OpenCode
4. OpenCode responde e agente retorna ao usuário
"""

import json
import sys
import os
from typing import Any, Dict, List
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lotoscope_agents import AgentOrchestrator, AGENTS, WORKFLOWS

app = Server("lotoscope-agents")
orchestrator = AgentOrchestrator()

# Cache de delegações pendentes (agente → opencode)
pending_delegations: Dict[str, Dict[str, Any]] = {}


@app.list_tools()
async def list_tools() -> List[Tool]:
    """Lista todas as tools MCP disponíveis."""
    return [
        Tool(
            name="lotoscope_list_agents",
            description="Lista todos os agentes disponíveis no LotoScope",
            inputSchema={"type": "object", "properties": {}, "required": []}
        ),
        Tool(
            name="lotoscope_list_workflows",
            description="Lista todos os workflows disponíveis",
            inputSchema={"type": "object", "properties": {}, "required": []}
        ),
        Tool(
            name="lotoscope_route",
            description="Roteia uma request para o agente mais apropriado baseado em keywords",
            inputSchema={
                "type": "object",
                "properties": {
                    "request": {"type": "string", "description": "A request do usuário"}
                },
                "required": ["request"]
            }
        ),
        Tool(
            name="lotoscope_call_agent",
            description="Chama um agente específico do LotoScope com uma tarefa",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_id": {
                        "type": "string",
                        "description": "ID: coordinator, architect, analyst, pool23, strategy, dev, docs"
                    },
                    "task": {"type": "string", "description": "Tarefa a ser executada"}
                },
                "required": ["agent_id", "task"]
            }
        ),
        Tool(
            name="lotoscope_get_context",
            description="Obtém o contexto completo de um agente (system prompt, tools, etc)",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_id": {"type": "string", "description": "ID do agente"}
                },
                "required": ["agent_id"]
            }
        ),
        Tool(
            name="lotoscope_orchestrate",
            description="Orquestra múltiplos agentes em sequência seguindo um workflow pré-definido",
            inputSchema={
                "type": "object",
                "properties": {
                    "workflow_id": {
                        "type": "string",
                        "description": "ID: pos_sorteio, preparacao, nova_feature, investigacao_bug"
                    },
                    "params": {"type": "object", "description": "Parâmetros adicionais"}
                },
                "required": ["workflow_id"]
            }
        ),
        Tool(
            name="lotoscope_delegate",
            description="""DELEGA TAREFA AO OPENCODE.
Use quando o agente não souber resolver ou precisar de ajuda do OpenCode.
O OpenCode receberá a tarefa e retornará a resposta.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "request": {
                        "type": "string",
                        "description": "Tarefa a delegar ao OpenCode"
                    },
                    "context": {
                        "type": "object",
                        "description": "Contexto adicional (agente atual, dados coletados, etc)"
                    },
                    "agent_id": {
                        "type": "string",
                        "description": "ID do agente que está delegando"
                    }
                },
                "required": ["request"]
            }
        ),
        Tool(
            name="lotoscope_check_delegation",
            description="Verifica se há delegações pendentes do agente para o OpenCode",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_id": {
                        "type": "string",
                        "description": "ID do agente para verificar delegações"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="lotoscope_execute_command",
            description="Executa um comando Python/PowerShell no ambiente LotoScope",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Comando a executar"
                    },
                    "working_dir": {
                        "type": "string",
                        "description": "Diretório de trabalho (opcional)"
                    }
                },
                "required": ["command"]
            }
        ),
        Tool(
            name="lotoscope_query_database",
            description="Executa query SQL no banco Lotofacil (Resultados_INT)",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Query SQL (use parâmetros ? para segurança)"
                    },
                    "params": {
                        "type": "array",
                        "description": "Parâmetros da query",
                        "items": {"type": "string"}
                    }
                },
                "required": ["query"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Executa uma tool MCP."""
    
    try:
        if name == "lotoscope_list_agents":
            result = orchestrator.list_agents()
            return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
        
        elif name == "lotoscope_list_workflows":
            result = orchestrator.list_workflows()
            return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
        
        elif name == "lotoscope_route":
            request = arguments.get("request", "")
            result = orchestrator.route_request(request)
            return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
        
        elif name == "lotoscope_call_agent":
            agent_id = arguments.get("agent_id", "")
            task = arguments.get("task", "")
            result = orchestrator.call_agent(agent_id, task)
            return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
        
        elif name == "lotoscope_get_context":
            agent_id = arguments.get("agent_id", "")
            result = orchestrator.get_agent_context(agent_id)
            return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
        
        elif name == "lotoscope_orchestrate":
            workflow_id = arguments.get("workflow_id", "")
            params = arguments.get("params", {})
            result = orchestrator.orchestrate(workflow_id, params)
            return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
        
        elif name == "lotoscope_delegate":
            # Registra delegação pendente
            request = arguments.get("request", "")
            context = arguments.get("context", {})
            agent_id = arguments.get("agent_id", "unknown")
            
            delegation_id = f"delegation_{agent_id}_{len(pending_delegations)}"
            pending_delegations[delegation_id] = {
                "agent_id": agent_id,
                "request": request,
                "context": context,
                "status": "pending",
                "timestamp": str(__import__('datetime').datetime.now())
            }
            
            result = {
                "delegation_id": delegation_id,
                "status": "delegated",
                "message": f"Tarefa delegada ao OpenCode pelo agente {agent_id}",
                "request": request,
                "instruction": "OpenCode: execute esta tarefa e retorne o resultado via lotoscope_respond"
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
        
        elif name == "lotoscope_check_delegation":
            agent_id = arguments.get("agent_id", "")
            if agent_id:
                delegations = {k: v for k, v in pending_delegations.items() if v.get("agent_id") == agent_id}
            else:
                delegations = pending_delegations
            
            result = {
                "total": len(delegations),
                "delegations": delegations
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
        
        elif name == "lotoscope_execute_command":
            import subprocess
            command = arguments.get("command", "")
            working_dir = arguments.get("working_dir", os.getcwd())
            
            try:
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    cwd=working_dir,
                    timeout=30
                )
                return [TextContent(type="text", text=json.dumps({
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "returncode": result.returncode
                }, indent=2, ensure_ascii=False))]
            except subprocess.TimeoutExpired:
                return [TextContent(type="text", text=json.dumps({
                    "error": "Comando excedeu tempo limite (30s)"
                }, indent=2, ensure_ascii=False))]
        
        elif name == "lotoscope_query_database":
            import pyodbc
            query = arguments.get("query", "")
            params = arguments.get("params", [])
            
            conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=Lotofacil;Trusted_Connection=yes;'
            
            try:
                with pyodbc.connect(conn_str) as conn:
                    cursor = conn.cursor()
                    if params:
                        cursor.execute(query, params)
                    else:
                        cursor.execute(query)
                    
                    columns = [column[0] for column in cursor.description]
                    rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
                    
                    return [TextContent(type="text", text=json.dumps({
                        "columns": columns,
                        "rows": rows[:100],  # Limitar a 100 rows
                        "total": len(rows)
                    }, indent=2, ensure_ascii=False))]
            except Exception as e:
                return [TextContent(type="text", text=json.dumps({
                    "error": str(e)
                }, indent=2, ensure_ascii=False))]
        
        else:
            return [TextContent(type="text", text=f"Tool '{name}' não encontrada")]
    
    except Exception as e:
        return [TextContent(type="text", text=f"Erro ao executar tool: {str(e)}")]


async def main():
    """Entry point do MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
