#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎯 SELETOR DE COMBINAÇÕES ALEATÓRIAS - DESKTOP GUI
Aplicativo desktop para seleção aleatória de combinações de arquivos TXT
Autor: AR CALHAU
Data: 13 de Agosto de 2025
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import random
from datetime import datetime
from typing import List

class SeletorCombinacoes:
    """Aplicativo desktop para seleção aleatória de combinações"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.arquivo_origem = ""
        self.combinacoes_carregadas = []
        self.setup_interface()
    
    def setup_interface(self):
        """Configura a interface gráfica"""
        # Configuração da janela principal
        self.root.title("🎯 Seletor de Combinações Aleatórias - LotoScope")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Ícone da janela (usando emoji como título)
        self.root.iconname("LotoScope")
        
        # Configurar estilo
        self.setup_styles()
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)  # Text area será expansível
        
        # Título
        title_label = ttk.Label(
            main_frame, 
            text="🎯 SELETOR DE COMBINAÇÕES ALEATÓRIAS",
            font=("Arial", 16, "bold"),
            foreground="#2c3e50"
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Seção 1: Seleção do arquivo
        arquivo_frame = ttk.LabelFrame(main_frame, text="📁 Arquivo de Origem", padding="10")
        arquivo_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        arquivo_frame.columnconfigure(1, weight=1)
        
        ttk.Button(
            arquivo_frame,
            text="📂 Selecionar Arquivo TXT",
            command=self.selecionar_arquivo,
            style="Accent.TButton"
        ).grid(row=0, column=0, padx=(0, 10))
        
        self.label_arquivo = ttk.Label(arquivo_frame, text="Nenhum arquivo selecionado", foreground="#7f8c8d")
        self.label_arquivo.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        # Informações do arquivo
        self.info_frame = ttk.Frame(arquivo_frame)
        self.info_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        self.info_frame.columnconfigure(1, weight=1)
        
        self.label_total = ttk.Label(self.info_frame, text="", foreground="#27ae60")
        self.label_total.grid(row=0, column=0, sticky=tk.W)
        
        # Seção 2: Configuração da seleção
        config_frame = ttk.LabelFrame(main_frame, text="⚙️ Configuração da Seleção", padding="10")
        config_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        config_frame.columnconfigure(1, weight=1)
        
        ttk.Label(config_frame, text="🎲 Quantidade de combinações:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        # Frame para entrada de quantidade
        qty_frame = ttk.Frame(config_frame)
        qty_frame.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        self.quantidade_var = tk.StringVar(value="15")
        self.entry_quantidade = ttk.Entry(qty_frame, textvariable=self.quantidade_var, width=10)
        self.entry_quantidade.grid(row=0, column=0, padx=(0, 10))
        
        # Botões de quantidade rápida
        quick_buttons_frame = ttk.Frame(qty_frame)
        quick_buttons_frame.grid(row=0, column=1, sticky=tk.W)
        
        for qty in [6, 10, 15, 25, 50, 100]:
            ttk.Button(
                quick_buttons_frame,
                text=str(qty),
                width=4,
                command=lambda q=qty: self.set_quantidade(q)
            ).pack(side=tk.LEFT, padx=2)
        
        # Seção 3: Ação
        action_frame = ttk.Frame(main_frame)
        action_frame.grid(row=3, column=0, columnspan=2, pady=(0, 15))
        
        self.btn_gerar = ttk.Button(
            action_frame,
            text="🎯 Gerar Seleção Aleatória",
            command=self.gerar_selecao,
            state="disabled",
            style="Accent.TButton"
        )
        self.btn_gerar.pack(side=tk.LEFT, padx=(0, 10))
        
        self.btn_salvar = ttk.Button(
            action_frame,
            text="💾 Salvar Resultado",
            command=self.salvar_resultado,
            state="disabled"
        )
        self.btn_salvar.pack(side=tk.LEFT)
        
        # Seção 4: Resultado
        resultado_frame = ttk.LabelFrame(main_frame, text="📊 Resultado da Seleção", padding="10")
        resultado_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        resultado_frame.columnconfigure(0, weight=1)
        resultado_frame.rowconfigure(0, weight=1)
        
        # Text area com scrollbar
        text_frame = ttk.Frame(resultado_frame)
        text_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        self.text_resultado = tk.Text(
            text_frame,
            height=15,
            wrap=tk.WORD,
            font=("Consolas", 10),
            state="disabled",
            bg="#f8f9fa",
            fg="#2c3e50"
        )
        self.text_resultado.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.text_resultado.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.text_resultado.configure(yscrollcommand=scrollbar.set)
        
        # Status bar
        self.status_var = tk.StringVar(value="Pronto - Selecione um arquivo para começar")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, foreground="#7f8c8d")
        status_bar.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Resultado da seleção
        self.combinacoes_selecionadas = []
    
    def setup_styles(self):
        """Configura estilos personalizados"""
        style = ttk.Style()
        
        # Configurar tema
        try:
            style.theme_use('clam')
        except:
            pass
        
        # Estilo para botão de destaque
        style.configure(
            "Accent.TButton",
            background="#3498db",
            foreground="white",
            borderwidth=0,
            focuscolor="none"
        )
        
        style.map(
            "Accent.TButton",
            background=[("active", "#2980b9")]
        )
    
    def set_quantidade(self, quantidade: int):
        """Define quantidade rapidamente"""
        self.quantidade_var.set(str(quantidade))
    
    def selecionar_arquivo(self):
        """Abre dialog para seleção do arquivo"""
        arquivo = filedialog.askopenfilename(
            title="Selecionar arquivo de combinações",
            filetypes=[
                ("Arquivos de texto", "*.txt"),
                ("Todos os arquivos", "*.*")
            ],
            initialdir=os.getcwd()
        )
        
        if arquivo:
            self.arquivo_origem = arquivo
            self.carregar_combinacoes()
    
    def carregar_combinacoes(self):
        """Carrega combinações do arquivo selecionado"""
        try:
            self.status_var.set("Carregando arquivo...")
            self.root.update()
            
            with open(self.arquivo_origem, 'r', encoding='utf-8') as f:
                linhas = f.readlines()
            
            # Processa as linhas
            self.combinacoes_carregadas = []
            linhas_validas = 0
            
            for linha in linhas:
                linha = linha.strip()
                
                # Ignora comentários e linhas vazias
                if not linha or linha.startswith('#'):
                    continue
                
                # Verifica se é uma combinação válida
                if ',' in linha:
                    try:
                        numeros = [int(x.strip()) for x in linha.split(',')]
                        if len(numeros) == 15:  # Lotofácil tem 15 números
                            self.combinacoes_carregadas.append(numeros)
                            linhas_validas += 1
                    except ValueError:
                        continue
            
            # Atualiza interface
            nome_arquivo = os.path.basename(self.arquivo_origem)
            self.label_arquivo.config(text=f"📄 {nome_arquivo}", foreground="#27ae60")
            self.label_total.config(text=f"📊 Total de combinações: {len(self.combinacoes_carregadas):,}")
            
            # Habilita botão de gerar
            if self.combinacoes_carregadas:
                self.btn_gerar.config(state="normal")
                self.status_var.set(f"Arquivo carregado com sucesso - {len(self.combinacoes_carregadas):,} combinações disponíveis")
                
                # Limpa resultado anterior
                self.text_resultado.config(state="normal")
                self.text_resultado.delete(1.0, tk.END)
                self.text_resultado.config(state="disabled")
                self.btn_salvar.config(state="disabled")
            else:
                raise ValueError("Nenhuma combinação válida encontrada")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar arquivo:\n{str(e)}")
            self.status_var.set("Erro ao carregar arquivo")
            self.arquivo_origem = ""
            self.label_arquivo.config(text="Nenhum arquivo selecionado", foreground="#7f8c8d")
            self.label_total.config(text="")
            self.btn_gerar.config(state="disabled")
    
    def gerar_selecao(self):
        """Gera seleção aleatória das combinações"""
        try:
            # Valida quantidade
            quantidade_str = self.quantidade_var.get().strip()
            if not quantidade_str:
                messagebox.showwarning("Aviso", "Digite a quantidade de combinações desejada")
                return
            
            try:
                quantidade = int(quantidade_str)
            except ValueError:
                messagebox.showerror("Erro", "Quantidade deve ser um número inteiro")
                return
            
            if quantidade <= 0:
                messagebox.showerror("Erro", "Quantidade deve ser maior que zero")
                return
            
            if quantidade > len(self.combinacoes_carregadas):
                resposta = messagebox.askyesno(
                    "Quantidade maior que disponível",
                    f"Você solicitou {quantidade} combinações, mas só há {len(self.combinacoes_carregadas)} disponíveis.\n\n"
                    f"Deseja usar todas as {len(self.combinacoes_carregadas)} combinações?"
                )
                if resposta:
                    quantidade = len(self.combinacoes_carregadas)
                else:
                    return
            
            # Gera seleção aleatória
            self.status_var.set("Gerando seleção aleatória...")
            self.root.update()
            
            self.combinacoes_selecionadas = random.sample(self.combinacoes_carregadas, quantidade)
            
            # Exibe resultado
            self.exibir_resultado()
            
            self.status_var.set(f"Seleção gerada com sucesso - {len(self.combinacoes_selecionadas)} combinações")
            self.btn_salvar.config(state="normal")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar seleção:\n{str(e)}")
            self.status_var.set("Erro ao gerar seleção")
    
    def exibir_resultado(self):
        """Exibe o resultado na área de texto"""
        self.text_resultado.config(state="normal")
        self.text_resultado.delete(1.0, tk.END)
        
        # Cabeçalho
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        nome_arquivo = os.path.basename(self.arquivo_origem)
        
        cabecalho = f"""🎯 SELEÇÃO ALEATÓRIA DE COMBINAÇÕES
{"="*50}
📁 Arquivo origem: {nome_arquivo}
📊 Total disponível: {len(self.combinacoes_carregadas):,} combinações
🎲 Selecionadas: {len(self.combinacoes_selecionadas)} combinações
⏰ Gerado em: {timestamp}

📋 COMBINAÇÕES SELECIONADAS:
{"-"*50}
"""
        
        self.text_resultado.insert(tk.END, cabecalho)
        
        # Combinações
        for i, combinacao in enumerate(self.combinacoes_selecionadas, 1):
            linha = f"{i:3d}: {','.join(f'{n:2d}' for n in combinacao)}\n"
            self.text_resultado.insert(tk.END, linha)
        
        # Estatísticas
        if self.combinacoes_selecionadas:
            estatisticas = self.calcular_estatisticas()
            
            self.text_resultado.insert(tk.END, f"\n{'-'*50}\n")
            self.text_resultado.insert(tk.END, "📈 ESTATÍSTICAS DA SELEÇÃO:\n")
            self.text_resultado.insert(tk.END, f"{'-'*30}\n")
            self.text_resultado.insert(tk.END, f"• Soma média: {estatisticas['soma_media']:.1f}\n")
            self.text_resultado.insert(tk.END, f"• Números mais frequentes: {estatisticas['mais_frequentes']}\n")
            self.text_resultado.insert(tk.END, f"• Range de somas: {estatisticas['soma_min']} - {estatisticas['soma_max']}\n")
            self.text_resultado.insert(tk.END, f"• Números únicos utilizados: {estatisticas['numeros_unicos']}/25\n")
        
        self.text_resultado.config(state="disabled")
    
    def calcular_estatisticas(self) -> dict:
        """Calcula estatísticas das combinações selecionadas"""
        if not self.combinacoes_selecionadas:
            return {}
        
        # Somas
        somas = [sum(comb) for comb in self.combinacoes_selecionadas]
        soma_media = sum(somas) / len(somas)
        soma_min = min(somas)
        soma_max = max(somas)
        
        # Frequência dos números
        contador_numeros = {}
        for combinacao in self.combinacoes_selecionadas:
            for numero in combinacao:
                contador_numeros[numero] = contador_numeros.get(numero, 0) + 1
        
        # Números mais frequentes
        mais_frequentes = sorted(contador_numeros.items(), key=lambda x: x[1], reverse=True)[:5]
        mais_frequentes_str = ', '.join([f"{num}({freq}x)" for num, freq in mais_frequentes])
        
        # Números únicos
        numeros_unicos = len(set(contador_numeros.keys()))
        
        return {
            'soma_media': soma_media,
            'soma_min': soma_min,
            'soma_max': soma_max,
            'mais_frequentes': mais_frequentes_str,
            'numeros_unicos': numeros_unicos
        }
    
    def salvar_resultado(self):
        """Salva o resultado em arquivo"""
        if not self.combinacoes_selecionadas:
            messagebox.showwarning("Aviso", "Não há combinações para salvar")
            return
        
        # Sugere nome do arquivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_origem = os.path.splitext(os.path.basename(self.arquivo_origem))[0]
        nome_sugerido = f"selecao_aleatoria_{len(self.combinacoes_selecionadas)}_de_{nome_origem}_{timestamp}.txt"
        
        arquivo_destino = filedialog.asksaveasfilename(
            title="Salvar seleção aleatória",
            defaultextension=".txt",
            filetypes=[("Arquivos de texto", "*.txt")],
            initialfilename=nome_sugerido
        )
        
        if arquivo_destino:
            try:
                with open(arquivo_destino, 'w', encoding='utf-8') as f:
                    # Cabeçalho
                    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    nome_arquivo_origem = os.path.basename(self.arquivo_origem)
                    
                    f.write(f"# SELEÇÃO ALEATÓRIA DE COMBINAÇÕES - LOTOSCOPE\n")
                    f.write(f"# Gerado em: {timestamp}\n")
                    f.write(f"# Arquivo origem: {nome_arquivo_origem}\n")
                    f.write(f"# Total disponível: {len(self.combinacoes_carregadas):,} combinações\n")
                    f.write(f"# Selecionadas: {len(self.combinacoes_selecionadas)} combinações\n")
                    f.write(f"#\n")
                    f.write(f"# Formato: N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15\n")
                    f.write(f"#{'='*60}\n")
                    
                    # Combinações
                    for combinacao in self.combinacoes_selecionadas:
                        linha = ','.join(map(str, combinacao))
                        f.write(f"{linha}\n")
                    
                    # Estatísticas no final (como comentário)
                    estatisticas = self.calcular_estatisticas()
                    if estatisticas:
                        f.write(f"\n# ESTATÍSTICAS DA SELEÇÃO:\n")
                        f.write(f"# Soma média: {estatisticas['soma_media']:.1f}\n")
                        f.write(f"# Números mais frequentes: {estatisticas['mais_frequentes']}\n")
                        f.write(f"# Range de somas: {estatisticas['soma_min']} - {estatisticas['soma_max']}\n")
                        f.write(f"# Números únicos utilizados: {estatisticas['numeros_unicos']}/25\n")
                
                messagebox.showinfo("Sucesso", f"Arquivo salvo com sucesso!\n\n📁 {arquivo_destino}")
                self.status_var.set(f"Arquivo salvo: {os.path.basename(arquivo_destino)}")
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar arquivo:\n{str(e)}")
                self.status_var.set("Erro ao salvar arquivo")
    
    def executar(self):
        """Executa o aplicativo"""
        # Centraliza a janela
        self.root.eval('tk::PlaceWindow . center')
        
        # Inicia o loop principal
        self.root.mainloop()

def main():
    """Função principal"""
    try:
        app = SeletorCombinacoes()
        app.executar()
    except Exception as e:
        print(f"Erro fatal: {e}")

if __name__ == "__main__":
    main()
