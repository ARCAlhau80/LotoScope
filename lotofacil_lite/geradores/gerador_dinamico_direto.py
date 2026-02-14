#!/usr/bin/env python3
"""
GERADOR ACADÊMICO DINÂMICO MEGA-SENA - ACESSO DIRETO
Executa diretamente o menu principal do gerador avançado
"""

def main():
    """Execução direta do gerador dinâmico"""
    print("🎯 GERADOR ACADÊMICO DINÂMICO MEGA-SENA")
    print("🚀 ACESSO DIRETO - VERSÃO AVANÇADA")
    print("=" * 55)
    print()
    
    try:
        from gerador_academico_dinamico_megasena import GeradorAcademicoDinamicoMegaSena
        
        print("✅ Carregando sistema avançado...")
        gerador = GeradorAcademicoDinamicoMegaSena()
        
        print("🎯 Iniciando menu principal...")
        print("-" * 55)
        
        # Executar o menu principal diretamente
        gerador.menu_principal()
        
    except ImportError as e:
        print(f"❌ Erro ao importar: {e}")
        print("💡 Verifique se o arquivo gerador_academico_dinamico_megasena.py existe")
    except KeyboardInterrupt:
        print("\n\n🔙 Sistema encerrado pelo usuário")
    except Exception as e:
        print(f"❌ Erro durante execução: {e}")

if __name__ == "__main__":
    main()
