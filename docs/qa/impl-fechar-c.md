---
tipo: qa
contrato: 1
pedido: impl-fechar-c
branch: melhoria/impl-fechar-c-c2
commit: b8ffe882bb62075d7f876e72ce1e8f4cd2c4eb59
parecer: aprovado
revisor: forge:qa-engineer
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-31
---
# QA: impl-fechar-c (branch c2)

Etapa E1.4, `R-QA`. Diff lido: `234dbe0..b8ffe88` (`tests/test_fechar.py` +1, `tests/test_fechar_tmp.py` novo, fragmento do changelog; mais os pareceres).

## Item entregue e M14
Item E2 do pedido (FECHAR-B-REC-REVIEW 1): os subtestes não deixam pastas `fechar-*` no TMPDIR (`addCleanup` no `Fechar.setUp`, mais o teste que prova). Só teste, nenhum código de produção. M14 (agents/tech-lead.md:19): um comportamento, 34 linhas de teste, abaixo do teto; fora de `hooks/` e `PROTEGIDOS`. Cumpre.

## Achados

## Critério → teste → resultado
O pedido não traz `CA-n`; o critério é o C2 do modelo de ameaças (SEC-FECHARC-3): nenhuma pasta `fechar-*` sobra no TMPDIR e o teste não apaga nada fora da própria pasta.
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| C2: laços com preparo repetido não deixam pasta | `test_fechar_tmp.SubtestesSemLixo.test_laco_com_preparo_repetido_nao_deixa_pasta_fechar_no_tmpdir` | TMPDIR próprio e vazio; só lê a pasta dele | passou (vermelho sem o `addCleanup`) |

## Cenários e resultado real
Vermelho antes do verde. O `forge-testes --vermelho` não vale aqui, porque a correção é ela mesma um arquivo de teste, mantido no HEAD: saída `test_fechar_tmp ... H=ok · B=ok · não prova (passa na base)`, rc=1. Feito à mão, numa cópia do head com o `tests/test_fechar.py` da base (`234dbe0`):
```
sobram 7 pastas fechar-* no TMPDIR de teste
Ran 1 test in 10.212s / FAILED (failures=2)     (sem o addCleanup)
Ran 1 test in 4.595s / OK                        (head)
```
A mutação é essa mesma remoção (única linha de código do item); não há `bin/` nem `hooks/` no diff.

Suíte: módulos `tests/test_fechar*.py` no head, sem bytecode: `Ran 203 tests` / `OK (skipped=1)` (o skip é `test_shellcheck_fechar_passa_limpo`, que pula sem `shellcheck` no PATH; o CI o roda). A bateria completa e o `scripts/validar-plugin.sh` ficam com o pre-push e o CI do envio.
