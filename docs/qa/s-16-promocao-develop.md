---
tipo: qa
contrato: 1
pedido: s-16-promocao-develop
branch: melhoria/s-16-promocao-develop
commit: f804072b4d48680bd65e8d38f2bf6cfb36517f9f
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-21
---
# Parecer de QA - s-16-promocao-develop

Código testado: f804072 (HEAD remoto 1b66c9e, que só acrescenta pareceres de review e segurança). Review e segurança aprovados.

## Achados

## Critério -> teste -> resultado
| Obrigação (E1/E2 do pedido) | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1: conteúdo já rotulado em PR mesclado passa na promoção develop -> homolog | `RotuloDePrSquash.test_b1_*` e sonda 1 | head com vários commits | passou |
| E1: conteúdo novo ou alterado pede rótulo | `test_b2`, `test_b3`, `test_b17`, sonda 2 | uma linha a mais; push depois do rótulo | passou |
| E1: commit que nunca esteve na develop não libera | `test_b4`, `test_b5`, `test_b7`, `test_b8`, `test_b9`, sondas 3 e 3b | ref divergente do head da API; head ausente; fora do primeiro pai | passou |
| E1: violação sem arquivo e custo pedem sempre | `test_b15` | n/a | passou |
| E1: dono só da base, falha fechada | `test_b16`, `DonoSoDaBase` | rótulo de outra conta, de app, removido | passou |
| E1: falha de fetch e prazo não viram traceback | `test_b6_*` | fetch falho; TimeoutExpired | passou |
| M1, M4, B14: fetch com refspec explícita, sem escrever em refs existentes | `test_m1`, `test_b14` | refs e FETCH_HEAD intactos | passou |
| E2: changelog.d/s-16-promocao-develop.md | presente no diff; suíte estrutural verde | n/a | passou |

## Execução (worktree, HEAD 1b66c9e)
- `.githooks/pre-push --status`: rc=0 (outra suíte, pid 38) -> esperei; depois rc=1 ("nenhuma suíte do Forge rodando").
- `python3 -m unittest discover -s tests -q`: `Ran 1105 tests in 286.197s`, `OK`. Nenhum teste falhou e passou de novo (sem FLAKY-CARGA).
- `scripts/validar-plugin.sh`: `Validation passed`, rc=0.

## Sondas da catraca (cópia em $TMPDIR/sonda, harness de tests/test_catraca.py: origin bare real, API falsa via `--mesclados`; comando `python3 sonda.py`, que chama `tests/catraca.py --raiz ... --base homolog --head develop --mesclados <json>`)
1. Conteúdo já rotulado no PR mesclado #10 (squash; S só em refs/pull/10/head): rc=0, `catraca: 2 violação(ões) liberada(s) pelo rótulo afrouxa-regra do dono (mesmo conteúdo já rotulado no PR mesclado #10).`
2. Conteúdo novo (head e squash com outro conteúdo, sem rótulo para ele): rc=1, `R-CONFORMIDADE: mudança em .github/workflows/ci.yml ... só passa com o rótulo afrouxa-regra do dono` e o mesmo para `tests/catraca.py`.
3. Commit que nunca esteve na develop (refs/pull/10/head aponta a outro commit, diferente do head da API): rc=1, as duas mudanças pedem o rótulo. 3b: head rotulado inexistente no origin: rc=1, idem.

## Vermelho antes do verde
Na cópia, com `tests/catraca.py` de origin/develop e os testes novos: `python3 -m unittest tests.test_catraca.RotuloDePrSquash -q` -> `Ran 21 tests`, `FAILED (failures=6)`: test_b1 (2), test_b6 (2), test_b14, test_m1. Os demais são guardas que já passam (fronteira "fecha por padrão"); a mutação de M3/M4/M7 está nos pareceres de review e segurança (test_b3, b4, b7, b8, b9 falham sem elas).

## Recomendações (não bloqueiam)
- Cartões já abertos: CATRACA-ISENCAO-AMBIENTE (isenção do catraca.py em test_ambiente_git.py ficou falsa) e CATRACA-PRAZO-API (prazo total do fetch e TimeoutExpired fora do invólucro).
- `test_b8` usa `time.sleep(1.2)`: determinístico, mas soma 1,2 s à suíte.
- Mutação por ferramenta não foi rodada por mim (a stack do Forge não traz ferramenta); confiei nas mutações manuais dos pareceres anteriores.
