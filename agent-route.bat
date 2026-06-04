@echo off
REM LotoScope Agent Orchestrator - Roteia request para agente
REM Uso: agent-route "analisar concurso 3643"
python "%~dp0lotoscope_agents.py" route %*
