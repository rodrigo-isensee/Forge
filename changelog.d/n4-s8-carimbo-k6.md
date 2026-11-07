### Alterado
- O hook `conformidade` barra também a escrita no carimbo K6 (`forge-suite-verde` no `git-common-dir`) e no temporário dele (`forge-suite-verde.<pid>`), mesmo com o caminho montado por `git rev-parse --git-common-dir`; só a suíte (`scripts/suite-paralela.py`) o grava, e a leitura continua livre (E5a N4/P3, versao-045).
