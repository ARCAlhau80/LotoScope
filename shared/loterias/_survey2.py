import requests

# Check correct endpoint for Milionária
for endpoint in ['maismilionaria', 'milionaria', 'mais-milionaria', 'mais_milionaria']:
    try:
        r = requests.get(f'https://servicebus2.caixa.gov.br/portaldeloterias/api/{endpoint}/', timeout=10)
        print(f'{endpoint:25s} status={r.status_code}')
        if r.status_code == 200:
            d = r.json()
            print(f'  numero={d.get("numero")}')
            print(f'  listaDezenas={d.get("listaDezenas")}')
            print(f'  trevos={d.get("trevos")}')
    except Exception as e:
        print(f'{endpoint:25s} error={e}')

print()
print('=== TIMEMANIA FULL RESPONSE ===')
r = requests.get('https://servicebus2.caixa.gov.br/portaldeloterias/api/timemania/', timeout=15)
if r.status_code == 200:
    d = r.json()
    # show keys relevant
    for k in ['numero', 'dataApuracao', 'listaDezenas', 'timeDoCoracao', 'dezenas', 'dezenasSorteadasOrdemSorteio']:
        print(f'  {k}={d.get(k)}')
    # list all keys
    print(f'  all_keys={list(d.keys())}')

print()
print('=== DIA DE SORTE FULL RESPONSE ===')
r = requests.get('https://servicebus2.caixa.gov.br/portaldeloterias/api/diadesorte/', timeout=15)
if r.status_code == 200:
    d = r.json()
    for k in ['numero', 'dataApuracao', 'listaDezenas', 'mesDaSorte', 'dezenas', 'dezenasSorteadasOrdemSorteio']:
        print(f'  {k}={d.get(k)}')
    print(f'  all_keys={list(d.keys())}')

print()
print('=== SUPER SETE FULL RESPONSE ===')
r = requests.get('https://servicebus2.caixa.gov.br/portaldeloterias/api/supersete/', timeout=15)
if r.status_code == 200:
    d = r.json()
    for k in ['numero', 'dataApuracao', 'listaDezenas', 'dezenas', 'dezenasSorteadasOrdemSorteio']:
        print(f'  {k}={d.get(k)}')
    print(f'  all_keys={list(d.keys())}')

print()
print('=== LOTOMANIA FULL RESPONSE ===')
r = requests.get('https://servicebus2.caixa.gov.br/portaldeloterias/api/lotomania/', timeout=15)
if r.status_code == 200:
    d = r.json()
    print(f'  numero={d.get("numero")}')
    print(f'  listaDezenas count={len(d.get("listaDezenas", []))}')
    print(f'  listaDezenas={d.get("listaDezenas")}')
