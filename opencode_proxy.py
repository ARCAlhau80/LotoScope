#!/usr/bin/env python3
"""
OpenCode Proxy Server
Simula API OpenAI e roteia para o OpenCode via subprocess.
"""

import json
import asyncio
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import threading
import sys
import os

# Configuração
PORT = 8111
OPENCODE_CMD = r"C:\Users\AR CALHAU\AppData\Roaming\npm\opencode.cmd"

class OpenCodeProxyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests (health check, models)."""
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode())
        
        elif self.path == '/v1/models':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            models = {
                "object": "list",
                "data": [
                    {
                        "id": "qwen3.7-plus",
                        "object": "model",
                        "owned_by": "opencode"
                    }
                ]
            }
            self.wfile.write(json.dumps(models).encode())
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        """Handle POST requests (chat completions)."""
        if self.path == '/v1/chat/completions':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                request = json.loads(post_data)
                messages = request.get('messages', [])
                model = request.get('model', 'qwen3.7-plus')
                
                # Extrair última mensagem do usuário
                user_message = ""
                for msg in reversed(messages):
                    if msg.get('role') == 'user':
                        user_message = msg.get('content', '')
                        break
                
                # Chamar OpenCode via subprocess
                response = self.call_opencode(user_message)
                
                # Formatar resposta no formato OpenAI
                result = {
                    "id": "chatcmpl-opencode",
                    "object": "chat.completion",
                    "created": 1234567890,
                    "model": model,
                    "choices": [
                        {
                            "index": 0,
                            "message": {
                                "role": "assistant",
                                "content": response
                            },
                            "finish_reason": "stop"
                        }
                    ],
                    "usage": {
                        "prompt_tokens": 0,
                        "completion_tokens": 0,
                        "total_tokens": 0
                    }
                }
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
            
            except Exception as e:
                error_response = {
                    "error": {
                        "message": str(e),
                        "type": "server_error"
                    }
                }
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(error_response).encode())
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def call_opencode(self, message: str) -> str:
        """Chama o OpenCode e retorna a resposta."""
        try:
            # Usar subprocess para chamar o OpenCode com o comando 'run'
            result = subprocess.run(
                [OPENCODE_CMD, "run", message],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return f"Erro ao chamar OpenCode: {result.stderr}"
        
        except subprocess.TimeoutExpired:
            return "Erro: Timeout ao chamar OpenCode (60s)"
        except Exception as e:
            return f"Erro: {str(e)}"
    
    def log_message(self, format, *args):
        """Silenciar logs do servidor."""
        pass


def run_server():
    """Inicia o servidor proxy."""
    server = HTTPServer(('127.0.0.1', PORT), OpenCodeProxyHandler)
    print(f"OpenCode Proxy Server rodando em http://127.0.0.1:{PORT}")
    print(f"API compatível com OpenAI: http://127.0.0.1:{PORT}/v1")
    print("Pressione Ctrl+C para parar")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor parado")
        server.server_close()


if __name__ == "__main__":
    run_server()
