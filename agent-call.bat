@echo off
REM LotoScope Agent Orchestrator - Chama agente específico
REM Uso: agent-call analyst "verificar frequências"
python "%~dp0lotoscope_agents.py" call %*
