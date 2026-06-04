@echo off
REM LotoScope Agent Orchestrator - Executa workflow
REM Uso: agent-run pos_sorteio
python "%~dp0lotoscope_agents.py" orchestrate %*
