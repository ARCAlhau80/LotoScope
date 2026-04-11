# -*- coding: utf-8 -*-
"""Pós-carga da Resultados_INT: recomputa campos posicionais dependentes do concurso anterior."""

import sys

from validar_campos_posicionais import recalcular_campos_posicionais

sys.stdout.reconfigure(encoding='utf-8')


def main():
    print('=' * 78)
    print('POS-CARGA RESULTADOS_INT')
    print('=' * 78)
    print('Recomputando: menor_que_ultimo, maior_que_ultimo, igual_ao_ultimo')
    print('Use este script sempre apos truncate/reimport da tabela Resultados_INT.')
    print()
    recalcular_campos_posicionais(verbose=True)


if __name__ == '__main__':
    main()
