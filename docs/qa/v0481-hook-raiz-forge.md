---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-hook-raiz-forge
commit: 1644a83f0b3c4ed16e9fd5c8b49b71d4c6288980
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-27
---
# QA: v0481 hook-raiz-forge (E37.20, PR #930, volta 4)

Delta aa347213..1644a83f. O A13 da segurança (sem valor calculado, a entrada vale também lida sem aspas e a variável colada no primeiro componente recusa) está coberto pelas fixtures S10, S11 e S12 e pelos mutantes RD10 e RD11. Os pareceres anteriores seguem valendo para o resto.

## Critério → teste → resultado
Sem docs/ux nem contrato de API; critérios da etapa E37.1 e dos achados A9, A12 e A13.

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| CA-1 a CA-19 das voltas 1 a 3 | fixtures `raiz-forge-*` (sem mudança de comportamento) | ver pareceres anteriores | passou |
| CA-20 (A13) `for d in .git''hooks; do printf x > $d/pre-push; done` recusa na raiz | raiz-forge-s10-for-aspas-partidas-githooks-bloqueia; mutante RD11 | texto do valor sem aspas | passou |
| CA-21 (A13) `read d <<< .git''hooks; printf x > $d/pre-push` recusa na raiz | raiz-forge-s11-read-aspas-partidas-githooks-bloqueia; mutante RD11 | texto do `read` sem aspas | passou |
| CA-22 (A13) variável colada no primeiro componente (`${d}s/pre-push`) recusa | raiz-forge-s12-variavel-colada-githooks-bloqueia; mutante RD10 | primeiro componente com variável | passou |
| CA-23 `printf x > $TMPDIR/y; cat .githooks/pre-push` e `for`/`read` com `scripts` seguem livres | fixtures das voltas 2 e 3 (sem mudança) | texto largo só conta se cita a entrada | passou |
| CA-24 piso de recusas 37 em `test_fixtures_da_raiz_do_forge` | tests/test_hooks.py:2931 | suíte vazia: 21 liberam, 37 bloqueiam | passou |
| CA-25 docs/hooks.md descreve o texto sem aspas e a variável colada | leitura do diff | n/a | coerente com conformidade.py:4356-4358 |

## Cenários e resultado real (volta 4)
- ci: 1644a83f0b3c4ed16e9fd5c8b49b71d4c6288980 verde
- Leitura do CI (`gh pr checks 930`; head conferido por `gh pr view`: 1644a83f): tudo pass fora `bateria (pareceres)`, `bateria` e `catraca`, que esperam parecer ou rótulo; suítes 3.12 (partes 1 a 5), 3.14, passos, verificações longas, instalação e teto de pulados passaram.
- Local sob o flock da trava A: `python3 -m unittest tests.test_hooks.Hooks.test_fixtures_da_raiz_do_forge tests.test_indice_fixtures` deu `Ran 11 tests ... OK`.
- Mutantes (`bin/forge-mutante` das specs -3 e -4, `--base aa3472135b21f0539c3047d1e31fe6718a17bced --processos 2`, saída `base=aa3472135b21f0539c3047d1e31fe6718a17bced mb=aa3472135b21f0539c3047d1e31fe6718a17bced rev=1644a83f0b3c4ed16e9fd5c8b49b71d4c6288980`): RD1 a RD11, RX1 e RX2 todos `morreu`, sem sobrevivente nem equivalente. RD4 reapontado para a linha 4357 morre; RD10 (`False or any(`) e RD11 (sem o texto sem aspas) morrem pelas fixtures S10 a S12.
- `--cobertura --base aa347213`: rc=0; a condição mudada (4357) está coberta por RD4, RD10 e RD11 (`spec editada` nas duas specs, esperado).
- Vermelho antes do verde: as fixtures S10 a S12 são provadas pelos mutantes RD10 e RD11, que as fazem cair sem o código novo. `forge-testes --vermelho` do módulo inteiro não foi rodado por passar do limite local de 10 min; não vale como vermelho.
- Acessibilidade e E2E: n/a (hook sem interface).
