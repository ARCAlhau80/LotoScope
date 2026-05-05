# -*- coding: utf-8 -*-
import os, sys
target = r"lotofacil_lite/interfaces/super_menu.py"
with open(target, "r", encoding="utf-8") as f: content = f.read()
patches = 0

# ---- PATCH 1: Op31 Alert ----
SEP31 = "# EXCLUS\u00c3O SUAVE (inspirado Op\u00e7\u00e3o 29)\n        # Permite 0-2"
SEP302 = "# EXCLUS\u00c3O SUAVE (inspirado Op\u00e7\u00e3o 29) \u2014 paridade Op31\n        # Permite 0-2"

# Build insert block 1 (Op31 alert)
ins1 = ("\n        # === ALERTA PADROES STRING (Op31) ===\n"
        "        _cold_bigrams_31 = set(); _cold_trigrams_31 = set()\n"
        "        _usar_filtro_string_31 = False; _max_viol_string_31 = 1\n"
        "        try:\n"
        "            _sd31 = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'sistemas')\n"
        "            if _sd31 not in sys.path: sys.path.insert(0, _sd31)\n"
        "            from analise_padroes_string import alerta_padroes_pool as _aps31\n"
        "            _r31 = _aps31(pool_final, janela=50)\n"
        "            _cold_bigrams_31, _cold_trigrams_31, _, _, _usar_filtro_string_31, _max_viol_string_31 = _r31\n"
        "        except Exception as _e31: print(f'   Info padroes string: {_e31}')\n"
        "\n        ")

if SEP31 in content and content.count(SEP31) == 1:
    content = content.replace(SEP31, ins1 + SEP31, 1)
    patches += 1; print("P1 OK")
else: print("P1 FAIL count=", content.count(SEP31))
