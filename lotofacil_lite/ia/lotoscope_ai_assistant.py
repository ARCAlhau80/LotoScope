#!/usr/bin/env python3
"""
LotoScope AI Assistant - v2 com Tool-Use
Assistente IA local com capacidade de executar ferramentas Python
O LLM entende o pedido e decide qual ferramenta chamar
"""

import os
import re
import sys
import json
import subprocess
import requests
from datetime import datetime
from pathlib import Path
from itertools import combinations

# ── Tools ──────────────────────────────────────────────────────────────

TOOLS_REGISTRY = {}

def tool(name, desc, example):
    def decorator(fn):
        fn.tool_name = name
        fn.tool_desc = desc
        fn.tool_example = example
        TOOLS_REGISTRY[name] = fn
        return fn
    return decorator

@tool(
    name="combinacoes_fixas",
    desc="Gera todas as combinacoes de 15 numeros para Lotofacil contendo obrigatoriamente os numeros fixos informados.",
    example="Use quando o usuario pedir combinacoes com numeros fixos. Ex: 'combinacoes com fixos 2,3,4,8,10'"
)
def tool_combinacoes_fixas(fixos):
    if not isinstance(fixos, list) or not all(isinstance(n, int) for n in fixos):
        fixos = [int(n) for n in str(fixos).split(",")]
    fixos = sorted(set(fixos))
    if any(n < 1 or n > 25 for n in fixos):
        return "Erro: numeros devem estar entre 1 e 25."
    if len(fixos) > 14:
        return "Erro: maximo 14 numeros fixos."

    restantes = [n for n in range(1, 26) if n not in fixos]
    precisamos = 15 - len(fixos)

    if precisamos < 1 or precisamos > len(restantes):
        return f"Erro: {len(fixos)} fixos precisam de {precisamos} numeros, mas ha {len(restantes)} disponiveis."

    combinacoes = [tuple(sorted(fixos + list(comb))) for comb in combinations(restantes, precisamos)]
    combinacoes.sort()

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    filename = f'combinacoes_fixas_{timestamp}.txt'
    filepath = os.path.join(base_dir, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"Fixos: {fixos}\n")
        f.write(f"Total: {len(combinacoes)} combinacoes\n")
        f.write("=" * 50 + "\n\n")
        for i, combo in enumerate(combinacoes, 1):
            f.write(f"{i:4d}. {str(list(combo))}\n")

    amostra = [str(list(c)) for c in combinacoes[:5]]
    return (
        f"{len(combinacoes)} combinacoes geradas!\n"
        f"Arquivo: {filepath}\n"
        f"Fixos: {fixos}\n"
        f"Amostra:\n  " + "\n  ".join(amostra) +
        ("\n  ..." if len(combinacoes) > 5 else "")
    )

@tool(
    name="combinacoes_repetidos",
    desc="Gera combinacoes filtrando por numeros que se repetem do ultimo concurso e/ou numeros fixos.",
    example="Use quando o usuario pedir combinacoes com 'X repetidos do ultimo concurso' ou 'X fixos'."
)
def tool_combinacoes_repetidos(repetidos=None, fixos=None):
    if fixos is None:
        fixos = []
    if repetidos is None:
        repetidos = []

    fixos = sorted(set(int(n) for n in (fixos if isinstance(fixos, list) else [])))
    if isinstance(repetidos, list):
        repetidos = [int(n) for n in repetidos]

    todos_fixos = sorted(set(fixos + repetidos))

    if any(n < 1 or n > 25 for n in todos_fixos):
        return "Erro: numeros devem estar entre 1 e 25."
    if len(todos_fixos) > 14:
        return "Erro: muitos numeros fixos."

    restantes = [n for n in range(1, 26) if n not in todos_fixos]
    precisamos = 15 - len(todos_fixos)

    if precisamos < 1 or precisamos > len(restantes):
        return f"Erro: {len(todos_fixos)} fixos precisam de {precisamos} numeros, mas ha {len(restantes)} disponiveis."

    combinacoes = [tuple(sorted(todos_fixos + list(comb))) for comb in combinations(restantes, precisamos)]
    combinacoes.sort()

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    filename = f'combinacoes_repetidos_{timestamp}.txt'
    filepath = os.path.join(base_dir, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        if repetidos:
            f.write(f"Repetidos do ultimo concurso: {repetidos}\n")
        if fixos:
            f.write(f"Fixos: {fixos}\n")
        f.write(f"Total: {len(combinacoes)} combinacoes\n")
        f.write("=" * 50 + "\n\n")
        for i, combo in enumerate(combinacoes, 1):
            f.write(f"{i:4d}. {str(list(combo))}\n")

    amostra = [str(list(c)) for c in combinacoes[:5]]
    return (
        f"{len(combinacoes)} combinacoes geradas!\n"
        f"Arquivo: {filepath}\n"
        f"Fixos: {todos_fixos}\n"
        f"Amostra:\n  " + "\n  ".join(amostra) +
        ("\n  ..." if len(combinacoes) > 5 else "")
    )

@tool(
    name="analisar_frequencias",
    desc="Analisa a frequencia dos numeros nos ultimos N concursos da Lotofacil.",
    example="Use quando o usuario pedir frequencia, numeros quentes/frios, estatisticas."
)
def tool_analisar_frequencias(janela=10):
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    sys.path.insert(0, base_dir)
    from shared.database import cached_query

    rows = cached_query(
        f'SELECT TOP {janela} N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15 '
        'FROM Resultados_INT ORDER BY Concurso DESC'
    )

    freq = {i: 0 for i in range(1, 26)}
    for row in rows:
        for j in range(15):
            freq[row[j]] += 1

    sorted_nums = sorted(freq.items(), key=lambda x: (-x[1], x[0]))
    resultado = f"Frequencia nos ultimos {janela} concursos:\n\n"
    for n, f in sorted_nums:
        barra = "#" * f + "." * (janela - f)
        resultado += f"  {n:2d}: {barra} ({f}/{janela})\n"
    return resultado


class LotoScopeAIAssistant:
    """Assistente IA especializado no projeto LotoScope com tool-use"""

    def __init__(self):
        self.model = "llama3:8b"
        self.project_root = Path(__file__).parent
        self.context_history = []
        self.knowledge_base = self._build_knowledge_base()
        self.model = self._detect_best_model()

    def _detect_best_model(self):
        preferred_models = [
            "llama3.2:3b", "llama3.2:1b", "llama3:8b",
            "llama3:latest", "llama3.1:8b", "phi:latest",
            "gemma:7b", "gpt-oss:20b"
        ]
        try:
            possivel_paths = [
                f"C:\\Users\\{os.environ.get('USERNAME', '')}\\AppData\\Local\\Programs\\Ollama\\ollama.exe",
                "ollama"
            ]
            for ollama_path in possivel_paths:
                try:
                    if ollama_path != "ollama" and not os.path.exists(ollama_path):
                        continue
                    result = subprocess.run([ollama_path, 'list'],
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        models_output = result.stdout.lower()
                        for model in preferred_models:
                            if model.lower() in models_output:
                                print(f"Usando modelo: {model}")
                                return model
                        lines = result.stdout.split('\n')[1:]
                        for line in lines:
                            if line.strip():
                                model_name = line.split()[0]
                                print(f"Usando modelo: {model_name}")
                                return model_name
                        break
                except:
                    continue
        except Exception as e:
            print(f"Erro ao detectar modelo: {e}")
        return "llama3:8b"

    def _build_knowledge_base(self):
        knowledge = {
            "project_name": "LotoScope",
            "focus_areas": ["Lotofacil", "Mega-Sena", "Analise Preditiva"],
            "technologies": ["Python", "SQL Server", "Machine Learning"],
            "number_ranges": {"lotofacil": "1-25 (15 numeros)", "megasena": "1-60 (6 numeros)"}
        }
        try:
            arquivos = []
            for f in self.project_root.glob("*.py"):
                if f.name != "lotoscope_ai_assistant.py":
                    arquivos.append(f.name)
            knowledge["arquivos_python"] = arquivos[:10]
        except:
            knowledge["arquivos_python"] = []
        return knowledge

    def check_ollama_status(self):
        try:
            import os
            possivel_paths = [
                f"C:\\Users\\{os.environ.get('USERNAME', '')}\\AppData\\Local\\Programs\\Ollama\\ollama.exe",
                "C:\\Program Files\\Ollama\\ollama.exe", "ollama"
            ]
            for ollama_path in possivel_paths:
                try:
                    if ollama_path != "ollama" and not os.path.exists(ollama_path):
                        continue
                    result = subprocess.run([ollama_path, 'list'],
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        models = result.stdout
                        if self.model.split(':')[0] in models:
                            return True, f"Ollama OK - {self.model} disponivel"
                        else:
                            return False, f"Ollama OK, mas {self.model} nao instalado. Execute: {ollama_path} pull {self.model}"
                    else:
                        continue
                except:
                    continue
            return False, "Ollama nao encontrado"
        except Exception as e:
            return False, f"Erro: {e}"

    def _tools_prompt(self):
        tools_desc = ""
        for name, fn in TOOLS_REGISTRY.items():
            tools_desc += f"\n- {name}: {fn.tool_desc}"
            tools_desc += f"\n  Exemplo: {fn.tool_example}\n"
        return tools_desc

    def query_llama(self, prompt, context=""):
        """Faz consulta ao Llama local com suporte a tool-use"""
        try:
            tools_desc = self._tools_prompt()

            system_prompt = f"""Voce e um assistente especializado no projeto LotoScope (analise de loterias).

VOCE TEM FERRAMENTAS DISPONIVEIS. Se o usuario pedir algo que uma ferramenta faz, responda APENAS com um JSON:
{{"tool": "nome_da_ferramenta", "params": {{...}}}}

Ferramentas disponiveis:{tools_desc}

Se nao precisar de ferramenta, responda normalmente em texto.

Regras:
- Para "combinacoes com fixos" use a ferramenta combinacoes_fixas com params {{"fixos": [lista de numeros]}}
- Para "combinacoes com X repetidos do ultimo concurso" use combinacoes_repetidos com params {{"repetidos": [lista], "fixos": [lista]}}
- Para "frequencia", "numeros quentes/frios" use analisar_frequencias com params {{"janela": numero}}
- Para perguntas gerais, responda em texto
- O nome do parametro DEVE ser "fixos" (nao "numeros_fixo", nao "numeros_fixos")
- Exemplo correto: {{"tool": "combinacoes_fixas", "params": {{"fixos": [2,3,4,8,10,11,12,14,15,18,19]}}}}

Pergunta: {prompt}

Contexto: {context}
Resposta:"""

            data = {
                "model": self.model,
                "prompt": system_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.2,
                    "num_predict": 800,
                    "repeat_penalty": 1.1,
                    "stop": ["\nPergunta:", "\nContexto:"]
                }
            }

            timeout = 180 if "20b" in self.model else (90 if "8b" in self.model else 60)

            response = requests.post(
                "http://localhost:11434/api/generate",
                json=data,
                timeout=timeout
            )

            if response.status_code != 200:
                return f"Erro HTTP {response.status_code}"

            result = response.json()
            resposta = result.get('response', '').strip()

            # Tentar interpretar como tool call
            tool_result = self._try_execute_tool(resposta)
            if tool_result is not None:
                return tool_result

            # Se nao for tool call, retorna texto normal
            if len(resposta) > 1500:
                resposta = resposta[:1500] + "..."
            return resposta if resposta else "Nao entendi. Pode reformular?"

        except requests.Timeout:
            return "O modelo demorou muito para responder. Tente com um modelo menor."
        except Exception as e:
            return f"Erro ao consultar Llama: {e}"

    def _try_execute_tool(self, llm_response):
        """Tenta extrair e executar uma tool call da resposta do LLM"""
        # Procura JSON com balancing de chaves {} para suportar nested
        json_str = None
        depth = 0
        start = -1
        for i, ch in enumerate(llm_response):
            if ch == '{':
                if depth == 0:
                    start = i
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0 and start >= 0:
                    json_str = llm_response[start:i+1]
                    break
        if not json_str:
            return None

        try:
            call = json.loads(json_str)
        except json.JSONDecodeError:
            return None

        tool_name = call.get("tool")
        params = call.get("params", {})

        if not tool_name or tool_name not in TOOLS_REGISTRY:
            return None

        fn = TOOLS_REGISTRY[tool_name]
        # Normaliza params: mapeia variacoes comuns de nomes de parametro
        normalized = {}
        param_aliases = {
            "fixos": ["fixos", "numeros_fixo", "numeros_fixos", "fixo", "fixed", "numeros_fixed"],
            "repetidos": ["repetidos", "numeros_repetidos", "repetido", "repeat", "rep", "ultimo_concurso"],
            "janela": ["janela", "window", "ultimos", "n", "quantidade"],
        }
        for key, value in params.items():
            key_lower = key.lower().replace(" ", "_")
            matched = False
            for canonical, aliases in param_aliases.items():
                if key_lower in aliases:
                    normalized[canonical] = value
                    matched = True
                    break
            if not matched:
                normalized[key_lower] = value
        try:
            return fn(**normalized)
        except TypeError as e:
            return f"Erro de parametros na ferramenta {tool_name}: {e}. Parametros recebidos: {normalized}"
        except Exception as e:
            return f"Erro ao executar {tool_name}: {e}"

    def responder(self, pergunta):
        """Responde perguntas usando o modelo de IA com tool-use"""
        return self.query_llama(pergunta)

    def analisar_codigo_python(self, codigo, nome_arquivo=""):
        prompt = f"Analise este codigo Python do projeto LotoScope:\n\nARQUIVO: {nome_arquivo}\n\nCODIGO:\n{codigo[:2000]}\n\nAnalise: funcionalidade, qualidade, melhorias, bugs, otimizacao."
        return self.query_llama(prompt)

    def analisar_estrutura_projeto(self):
        try:
            arquivos = list(self.project_root.glob("*.py"))
            estrutura = "\n".join([f"- {f.name}" for f in arquivos[:10]])
            return self.query_llama(f"Analise a estrutura deste projeto:\n{estrutura}")
        except Exception as e:
            return f"Erro: {e}"

    def suggest_improvements(self, topic):
        return self.query_llama(f"Sugira melhorias para: {topic}")

    def analyze_code_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            return self.analisar_codigo_python(code, file_path)
        except Exception as e:
            return f"Erro ao analisar: {e}"

    def research_patterns(self, lottery_type, data_sample=""):
        return self.query_llama(f"Pesquise padroes em {lottery_type}. Dados: {data_sample}")


def main():
    print("LOTOSCOPE AI ASSISTANT v2 - Tool Use")
    print("=" * 50)

    assistant = LotoScopeAIAssistant()
    status_ok, status_msg = assistant.check_ollama_status()
    print(f"Status: {status_msg}")

    if not status_ok:
        return

    response = assistant.query_llama(
        "Me gere todas as combinacoes de 15 numeros com os fixos 2,3,4,8,10,11,12,14,15,18,19"
    )
    print(f"\nResposta:\n{response}")

if __name__ == "__main__":
    main()
