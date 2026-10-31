### Corrigido
- `forge-testes --vermelho` sem `--modulos`: os dados de teste do diff (a spec `tests/mutantes/<pedido>.json` de todo item, fixtures, corpus) deixam de levar à suíte completa; roda só o plano do mapa mais os módulos de teste do diff, e quando o mapa não sabe diz o motivo numa linha e roda todos; com `--modulos`, nada muda (pedido VERMELHO-FILTRO, FT1).
