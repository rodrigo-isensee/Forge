---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-hook-raiz-forge
commit: 3c1bd3823c82f5383b9df5e289bf7889d4774e97
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-27
---
# QA: v0481 hook-raiz-forge (E37.24, PR #930, volta 5)

Delta 1644a83f..3c1bd382. `colada_em_vigor` e `ref_inteira` (conformidade.py:4178-4198): a variável sem valor colada só recusa quando o primeiro componente, lido como curinga, casa uma entrada em vigor; colada por aspas ou barra vira o curinga com o resto. O texto do valor é lido sem barra invertida. Os pareceres anteriores seguem valendo para o resto.

## Critério → teste → resultado
Sem docs/ux nem contrato de API; critérios dos achados A2 (review) e A15 (segurança).

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| CA-1 a CA-25 das voltas 1 a 4 | fixtures `raiz-forge-*` anteriores | ver pareceres anteriores | passou |
| CA-26 (A15) `$d"s"/pre-push` com `d` sem valor recusa | raiz-forge-s14-colada-por-aspas-githooks-bloqueia; RD10, RD15 | colagem por aspas | passou |
| CA-27 (A15) a colagem por aspas no manifesto recusa | raiz-forge-s15-colada-por-aspas-manifesto-bloqueia | segundo nome de entrada | passou |
| CA-28 `for d in .git\hooks` recusa | raiz-forge-s13-barra-invertida-githooks-bloqueia; RD11 | texto do valor sem barra invertida | passou |
| CA-29 (A2) `$f.log`, `saida-$n.txt` e `${TMPDIR}x/y` liberam na cópia de wt/ e na raiz | review-s1 a s4 | curinga que não casa entrada | passou |
| CA-30 `"$TMPDIR"/y` e `"$f"x/y` liberam | raiz-forge-tmpdir-entre-aspas-raiz-libera, raiz-forge-colada-por-aspas-sem-entrada-raiz-libera; RD12 a RD14, RD16 | `*x` não casa | passou |
| CA-31 piso de recusas e liberações em `test_fixtures_da_raiz_do_forge` | tests/test_hooks.py | suíte vazia | passou |
| CA-32 docs/hooks.md descreve a colagem por aspas ou barra e as liberações | leitura do diff | n/a | coerente com conformidade.py:4378-4383 |

## Cenários e resultado real (volta 5)
- ci: 3c1bd3823c82f5383b9df5e289bf7889d4774e97 verde
- Leitura do CI (`gh pr checks 930`; head conferido por `gh pr view`: 3c1bd382): tudo pass fora `bateria (pareceres)`, `bateria` e `catraca`, que esperam parecer ou rótulo; suítes 3.12 (partes 1 a 5), 3.14, passos, verificações longas, instalação e teto de pulados passaram.
- Local: `python3 -m unittest tests.test_hooks.Hooks.test_fixtures_da_raiz_do_forge tests.test_indice_fixtures` deu `Ran 11 tests ... OK`.
- Mutantes (`bin/forge-mutante` das specs -3, -4 e -5, `--base 1644a83f0b3c4ed16e9fd5c8b49b71d4c6288980 --processos 3`, saída `base=1644a83f0b3c4ed16e9fd5c8b49b71d4c6288980 mb=1644a83f0b3c4ed16e9fd5c8b49b71d4c6288980 rev=3c1bd3823c82f5383b9df5e289bf7889d4774e97`): RD1 a RD16, RX1 e RX2 todos `morreu`, sem sobrevivente nem equivalente.
- `--cobertura --base 1644a83f`: rc=0; as condições mudadas (4183, 4192, 4194, 4197, 4381) estão cobertas por RD16, RD12, RD13, RD14 e RD4/RD10/RD11/RD15 (`spec editada` nas specs -3 e -4, esperado).
- Sondas próprias de `colada_em_vigor`: `$ds` com `$d"s"` e `$dn` com `"$d"n` casam; `"$f"x`, `"$TMPDIR"x`, `$f.log`, `$d"ss"` e `$d"x"s` não casam. Sem divergência.
- Vermelho antes do verde: as fixtures S13 a S15 e as liberações são provadas pelos mutantes RD10 a RD16, que as fazem cair sem o código novo. `forge-testes --vermelho` do módulo inteiro não foi rodado (passa do limite local de 10 min); não vale como vermelho.
- Acessibilidade e E2E: n/a (hook sem interface).
