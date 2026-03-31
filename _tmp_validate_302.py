import io
from contextlib import redirect_stdout
from unittest.mock import patch
from lotofacil_lite.interfaces.super_menu import SuperMenuLotofacil

inputs = iter([
    '0',
    '',
    'N',
    '10',
    '1 2 3 4 5 7 8 9 11 12',
    '0',
    'SAIR',
    ''
])

buf = io.StringIO()
with patch('builtins.input', side_effect=lambda prompt='': next(inputs)):
    with redirect_stdout(buf):
        try:
            SuperMenuLotofacil()._executar_backtesting_pool23()
        except StopIteration:
            pass

out = buf.getvalue()
markers = [
    'ESTRATÉGIA DE EXCLUSÃO',
    'Estratégia? [0-5, ENTER=2]',
    'COMPARAR TODAS (diagnóstico será exibido no PASSO 4)',
    'PASSO 4: INFORMAR RESULTADO PARA VALIDAÇÃO',
    'Validação cancelada.'
]
print('---MARKERS---')
for m in markers:
    print(m + ' => ' + ('OK' if m in out else 'MISS'))
print('---COMPARE-HITS---')
for line in out.splitlines():
    if 'COMPARAÇÃO DE ESTRATÉGIAS' in line or 'Melhor no resultado informado' in line:
        print(line)
