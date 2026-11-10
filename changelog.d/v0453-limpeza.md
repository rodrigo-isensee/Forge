### Alterado
- F4 e F5 (FILA-31): `promover` (scripts/promover-homolog.py) e `orquestrar` (scripts/suite-paralela.py) quebradas em funções menores, sem mudar saída nem códigos de saída.

### Adicionado
- S7 bancada de instrução: `tests/bancada/bancada.py --antes <a> --depois <b>` compara duas versões de um texto sobre casos gravados (tokens e tempo por rodada); sem `--executar` só valida os casos e estima o custo; com ele chama o modelo, só com aprovação do dono (R-CUSTO), nunca no CI.
