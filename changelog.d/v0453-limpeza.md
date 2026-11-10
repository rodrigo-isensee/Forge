### Alterado
- F4 e F5 (FILA-31): `promover` (scripts/promover-homolog.py) e `orquestrar` (scripts/suite-paralela.py) quebradas em funções menores, sem mudar saída nem códigos de saída.
- F3 (FILA-31): o `git(projeto, *args)` idêntico de `bin/forge-atualizar` e `bin/forge-voltar-versao` passa a morar em `bin/forge_versoes.py`, que os dois já importam. Sem mudança de comportamento.

### Adicionado
- S7 bancada de instrução: `tests/bancada/bancada.py --antes <a> --depois <b>` compara duas versões de um texto sobre casos gravados (tokens e tempo por rodada); sem `--executar` só valida os casos e estima o custo; com ele chama o modelo, só com aprovação do dono (R-CUSTO), nunca no CI.
- `scripts/publicar-releases-faltantes.sh`: para cada versão do CHANGELOG entre 0.43.1 e 0.44.2 sem release no GitHub, mostra o `gh release create` no commit `release: X.Y.Z` da main, com a seção do CHANGELOG e `--latest=false`; só imprime, `--publicar` executa.
