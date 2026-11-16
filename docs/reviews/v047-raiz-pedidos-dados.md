---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-raiz-pedidos-dados
commit: ccd65b30e4075f293df74851fa5ab09919c105e2
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-15
---
# Review: v047 (E2.99), lote PL1 RAIZ-PEDIDOS-PERDE-DADOS

Escopo revisado: `bf475209...ccd65b30` (1 commit), `bin/forge-check:9690-9691`, `bin/forge-placar:4,469,499-500`, `tests/test_voltas.py`, `tests/evals/test_placar.py`, `tests/mutantes/v047-raiz-pedidos-dados.json` e o fragmento em `changelog.d/`. Parecer completo (não havia parecer anterior), escrito por uma instância que não fez a entrega.

## Achados
- A1 (recomendado) bin/forge-placar:8 · a docstring ainda diz que as fontes ficam na `--raiz`; quando o `--raiz-pedidos` vem, é ele que vale (AR-9, limite antigo no texto). Sugestão: "na `--raiz-pedidos`, senão na `--raiz`".

## Sondas

## Parecer
**Aprovado.**

- Requisito: o parser comum do `forge-check` já aceitava o `--raiz-pedidos`, mas o despacho do `voltas` o ignorava. Agora o despacho segue o mesmo padrão do `dora` (`:9693`) e a pasta passa pela validação de pasta permitida (`:9606`). O `forge_voltas.cmd_voltas` só usa a raiz para `docs/kanban` e `docs/pedidos`, então trocar a raiz inteira não perde nenhuma leitura do clone. No `forge-placar`, todas as fontes (`conferencias`, `escapes`, `historicos`, `vereditos_por_papel` e `melhorias.md`) ficam sob a raiz dos dados; `--erros`, `--git`, `--ci` e `--evals` são caminhos próprios e não mudam. A entrega faz o que o cartão pede, nem mais, nem menos.
- Mutantes declarados (AR-1, AR-12): há uma linha de guarda em cada arquivo, e as duas estão declaradas e morreram no head (`bin/forge-mutante`: `RP-M1 · morreu · bin/forge-check:9691`, `RP-M2 · morreu · bin/forge-placar:499`). O ramo sem `--raiz-pedidos` segue coberto pelos testes que já existiam em `Voltas` e `Medir` (AR-2).
- Testes novos (AR-4, AR-5): rodam em subprocesso com ambiente limpo (`PATH` e `HOME` próprios), Python com `-I` e `cwd` no clone vazio, e afirmam os números exatos lidos da pasta de fora. Rodei os 2 aqui: OK.
- Suíte: não rerrodada (R-REVIEW); valem a entrega conferida em ccd65b30 (pedido v047, Histórico de 2026-11-15 21:02) e o CI do PR.
- Tamanho (M14): 39 linhas de código e teste contadas, um comportamento só.
- Segurança: tem parecer próprio em `docs/security/v047-raiz-pedidos-dados.md`, que não refiz. O `forge-placar` é só leitura e não valida a pasta como o `forge-check` faz; sem gatilho, isso não é achado.
