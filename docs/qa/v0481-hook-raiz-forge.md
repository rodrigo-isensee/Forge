---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-hook-raiz-forge
commit: aa3472135b21f0539c3047d1e31fe6718a17bced
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-27
---
# QA: v0481 hook-raiz-forge (E37.16, PR #930, volta 3)

Delta e4998443..aa347213. O A12 da segurança e o A2 do review (variável nascida de `for` ou `read`, com resto e sem valor calculado, vale pelos textos largos na raiz do Forge) estão cobertos. Os pareceres anteriores seguem valendo para o resto.

## Critério → teste → resultado
Sem docs/ux nem contrato de API; critérios da etapa E37.1, do A9 e do A12.

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| CA-1 a CA-13 das voltas 1 e 2 | fixtures `raiz-forge-*` (sem mudança no delta) | ver pareceres anteriores | passou (CI do head) |
| CA-14 (A12) `for d in .githooks; do printf x > $d/pre-push; done` recusa na raiz | raiz-forge-variavel-de-for-githooks-bloqueia; mutante RD9 | variável de `for` com resto, entrada em vigor | passou |
| CA-15 (A2) `read d <<< .githooks; printf x > $d/pre-push` recusa na raiz | raiz-forge-variavel-de-read-githooks-bloqueia; mutante RD9 | variável de `read` com resto, entrada em vigor | passou |
| CA-16 `for` e `read` com valor fora das entradas (`scripts`) seguem livres | raiz-forge-variavel-de-for-scripts-libera, raiz-forge-variavel-de-read-scripts-libera | texto largo só conta se cita a entrada | passou |
| CA-17 `printf x > $TMPDIR/y; cat .githooks/pre-push` segue livre | fixture da volta 2 (sem mudança) | leitura que cita a entrada fora do valor | passou |
| CA-18 mínimos de `test_fixtures_da_raiz_do_forge` em 21/34 | tests/test_hooks.py:2930-2931 | suíte vazia: 21 liberam, 34 bloqueiam | passou |
| CA-19 docs/hooks.md descreve o texto largo e a falha fechada também em `wt/` | leitura do diff | n/a | coerente com o código (conformidade.py:4355) |

## Cenários e resultado real (volta 3)
- ci: aa3472135b21f0539c3047d1e31fe6718a17bced verde
- Leitura do CI (`gh pr checks 930`; head aa347213 conferido por `gh pr view`): tudo pass fora `bateria (pareceres)`, `bateria` e `catraca`, que esperam parecer ou rótulo; suítes 3.12 (partes 1 a 5), 3.14, instalação e teto de pulados passaram.
- Local sob o flock da trava A: `python3 -m unittest tests.test_hooks.Hooks.test_fixtures_da_raiz_do_forge tests.test_indice_fixtures` deu `Ran 11 tests ... OK`.
- Mutantes (`bin/forge-mutante` das specs -3 e -4, `--base e4998443f6eea0ef08c43dbbb9b35627f13582b0 --processos 2`, saída `base=e4998443f6eea0ef08c43dbbb9b35627f13582b0 mb=e4998443f6eea0ef08c43dbbb9b35627f13582b0 rev=aa3472135b21`): RD1 a RD6, RX1, RX2, RD7, RD8 e RD9 todos `morreu`, sem sobrevivente nem equivalente. RD9 troca `[1]` por `[0]` na linha 4355 (a mudada) e a fixture de `for` e `read` a mata.
- `--cobertura --base e4998443`: rc=0; a condição mudada (4355) tem mutante (RD9); RD7 e RD8 reancoradas (`spec editada`) e ainda morrem.
- Vermelho antes do verde: as fixtures novas são provadas pelo mutante RD9 (sem o texto largo, elas caem) e por RD7 e RD8. `forge-testes --vermelho` do módulo inteiro passou do limite local de 10 min sem veredito; não vale como vermelho.
- Acessibilidade e E2E: n/a (hook sem interface).
