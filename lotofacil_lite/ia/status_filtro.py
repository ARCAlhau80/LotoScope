import time
import os
from pathlib import Path

# Verificar status do filtro
pasta = Path(__file__).parent

print("🔍 STATUS DO FILTRO INTERSECÇÃO")
print("=" * 40)
print(f"⏰ {time.strftime('%H:%M:%S')}")
print(f"📁 Pasta: {pasta}")

# Verificar arquivos de resultado
arquivos = list(pasta.glob("combinacoes_filtradas_*.txt"))

if arquivos:
    print(f"\n📊 {len(arquivos)} arquivo(s) de resultado encontrado(s):")
    
    for arquivo in sorted(arquivos, reverse=True):
        tamanho = arquivo.stat().st_size
        modificado_timestamp = arquivo.stat().st_mtime
        modificado = time.ctime(modificado_timestamp)
        
        # Verificar se foi modificado recentemente (últimos 60 segundos)
        tempo_desde_modificacao = time.time() - modificado_timestamp
        
        status = "🔄 ATIVO" if tempo_desde_modificacao < 60 else "✅ FINALIZADO"
        
        print(f"   📄 {arquivo.name}")
        print(f"      📊 {tamanho:,} bytes")
        print(f"      ⏰ {modificado}")
        print(f"      🎯 {status}")
        print()
        
        # Se o arquivo foi modificado recentemente, ler estatísticas
        if tempo_desde_modificacao < 60:
            print(f"      🔥 PROCESSO ATIVO - Arquivo sendo escrito!")
        else:
            # Tentar ler estatísticas finais
            try:
                with open(arquivo, 'r', encoding='utf-8') as f:
                    conteudo = f.read()
                    if "Total de combinações válidas:" in conteudo:
                        for linha in conteudo.split('\n'):
                            if "Total de combinações válidas:" in linha:
                                print(f"      ✅ {linha.strip()}")
                                break
            except:
                pass
else:
    print("\n⚠️ Nenhum arquivo de resultado encontrado")
    print("   O processo pode ainda estar carregando dados...")

print("\n" + "=" * 40)
print("💡 Para monitorar continuamente, execute:")
print("   python monitor_filtro.py")
