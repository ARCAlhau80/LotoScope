import requests, sys; sys.path.insert(0, '.')
from lotofacil_lite.utils.database_config import db_config

loterias = {
    'lotofacil':   {'nome': 'Lotofácil',   'nums': 15, 'total': 25,  'min': 1},
    'megasena':    {'nome': 'Mega-Sena',   'nums': 6,  'total': 60,  'min': 1},
    'quina':       {'nome': 'Quina',       'nums': 5,  'total': 80,  'min': 1},
    'duplasena':   {'nome': 'Dupla Sena',  'nums': 6,  'total': 50,  'min': 1},
    'lotomania':   {'nome': 'Lotomania',   'nums': 50, 'total': 100, 'min': 0},
    'diadesorte':  {'nome': 'Dia de Sorte','nums': 7,  'total': 31,  'min': 1},
    'timemania':   {'nome': 'Timemania',   'nums': 10, 'total': 80,  'min': 1},
    'supersete':   {'nome': 'Super Sete',  'nums': 7,  'total': 7,   'min': 1},  # special: 7 columns 0-9 each
    'milionaria':  {'nome': 'Milionária',  'nums': 6,  'total': 50,  'min': 1},  # +2 trevos 1-6
}

conn = db_config.get_connection()
cursor = conn.cursor()

print('=== TABELAS EXISTENTES ===')
for lid, info in loterias.items():
    nome_tabela = f"Resultados_{lid.capitalize()}"
    cursor.execute(f"SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME='{nome_tabela}'")
    exists = cursor.fetchone()[0] > 0
    if exists:
        cursor.execute(f"SELECT ISNULL(MIN(Concurso),0), ISNULL(MAX(Concurso),0), ISNULL(COUNT(*),0) FROM [{nome_tabela}]")
        r = cursor.fetchone()
        print(f'{lid:15s} {nome_tabela:30s} min={r[0]:>6} max={r[1]:>6} total={r[2]:>6}')
    else:
        # try lowercase
        nome_tabela2 = f"Resultados_{lid}"
        cursor.execute(f"SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME='{nome_tabela2}'")
        if cursor.fetchone()[0] > 0:
            cursor.execute(f"SELECT ISNULL(MIN(Concurso),0), ISNULL(MAX(Concurso),0), ISNULL(COUNT(*),0) FROM [{nome_tabela2}]")
            r = cursor.fetchone()
            print(f'{lid:15s} {nome_tabela2:30s} min={r[0]:>6} max={r[1]:>6} total={r[2]:>6}')
        else:
            print(f'{lid:15s} NÃO EXISTE')

cursor.close()
conn.close()

print()
print('=== API CHECK ===')
for lid, info in loterias.items():
    try:
        r = requests.get(f'https://servicebus2.caixa.gov.br/portaldeloterias/api/{lid}/', timeout=15)
        if r.status_code == 200:
            d = r.json()
            print(f'{lid:15s} OK  ultimo={d.get("numero")}  dataApuracao={d.get("dataApuracao")}')
            # show listadezenas keys if available
            if 'listaDezenas' in d:
                print(f'                 listaDezenas={d["listaDezenas"]}')
            elif 'dezenas' in d:
                print(f'                 dezenas={d["dezenas"]}')
            # show special fields
            if 'listaDezenasSegundoSorteio' in d:
                print(f'                 2o sorteio={d["listaDezenasSegundoSorteio"]}')
            if 'trevos' in d:
                print(f'                 trevos={d["trevos"]}')
            # show all keys
            # keys = [k for k in d.keys() if 'dezena' in k.lower() or 'trevo' in k.lower() or 'sorteio' in k.lower() or 'numero' in k.lower()]
            # if keys: print(f'                 relevant_keys={keys}')
        else:
            print(f'{lid:15s} ERROR {r.status_code}')
    except Exception as e:
        print(f'{lid:15s} EXCEPTION {e}')
