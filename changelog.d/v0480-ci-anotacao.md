### Corrigido
- Anotação forge-suite parte K/N e tempos por unidade voltam a sair no CI: o scripts/suite-partes.py copia o ambiente antes do discover, que importa o tests/test_catraca.py (tira GITHUB_ACTIONS no import) (v0478 E137.2).
