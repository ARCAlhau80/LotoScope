#!/usr/bin/env python3
import sys
import os

print("=== DIAGNÓSTICO SUPER MENU ===")
print(f"Python: {sys.version}")
print(f"Diretório atual: {os.getcwd()}")

try:
    import pandas
    print("✅ pandas OK")
except ImportError as e:
    print(f"❌ pandas: {e}")

try:
    import numpy
    print("✅ numpy OK")
except ImportError as e:
    print(f"❌ numpy: {e}")

try:
    import sklearn
    print("✅ sklearn OK")
except ImportError as e:
    print(f"❌ sklearn: {e}")

print("\nTestando importação do super_menu...")
try:
    import super_menu
    print("✅ super_menu importado com sucesso!")
except ImportError as e:
    print(f"❌ Erro ao importar super_menu: {e}")
except Exception as e:
    print(f"❌ Erro inesperado: {e}")

print("\nArquivos no diretório:")
for f in os.listdir('.'):
    if f.endswith('.py'):
        print(f"  📄 {f}")
        
print("=== FIM DO DIAGNÓSTICO ===")
