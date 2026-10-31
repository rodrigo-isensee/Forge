---
tipo: qa
contrato: 1
pedido: impl-pre-push
branch: melhoria/impl-pre-push-c6
commit: 7ecec3f08e1c71be8650a4a577d8899c1c2ec437
parecer: aprovado
revisor: forge:qa-engineer
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-31
---
# QA: impl-pre-push (c6)

Item entregue: o C-14 do E3 (texto da trava limitado e imprimível), nada mais. Diff da base 234dbe0 ao head 7ecec3f: `.githooks/pre-push` (+6/-2), `tests/test_pre_push_trava.py` (+17), fragmento de changelog e os pareceres de review e segurança.

## Achados
- A1 (recomendado) .githooks/pre-push:43 · a c6 precisa entrar antes ou junto da c4 (condição já registrada no review e na segurança); o QA não a promove, a ordem é do fechamento.

## Conformidade com a M14 (agents/tech-lead.md:19)
- Linhas de código e teste: 25 (6+2 em `.githooks/pre-push`, 17 em `tests/test_pre_push_trava.py`), abaixo do teto de 150.
- Um comportamento só (saída da trava de outro processo), sem arquivo de `hooks/` nem `PROTEGIDOS`. Cumpre.

## Critério → teste → resultado
O pedido não traz `CA-n` para o C-14; a obrigação é o item C-14 do modelo de ameaças (E3).

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| C-14 `--status` sem escape nem excesso | `test_texto_da_trava_sai_limitado_e_sem_controle` | trava com 1 MiB e ESC/BEL; saída até 320 caracteres | passou |
| C-14 aviso de espera sem escape nem excesso | o mesmo teste (via `FORGE_TRAVA_ESPERA=1`) | stderr até 600 caracteres, sem ESC | passou |
| Sem regressão no restante do hook | `tests.test_pre_push_trava` (30 testes) | n/a | passou |

## Execução real
- `python3 -m unittest tests.test_pre_push_trava`: 30 testes, OK.
- Vermelho antes do verde, `forge-testes --vermelho 234dbe0fb90b005450d7c2eb59e6241ea9779155 --modulos test_pre_push_trava`, rc=0:
  `vermelho: base=234dbe0fb90b head=7ecec3f08e1c módulos=test_pre_push_trava (restrito por --modulos)`
  `revertidos à base: .githooks/pre-push, changelog.d/impl-pre-push-c6.md, docs/reviews/impl-pre-push.md, docs/security/impl-pre-push.md`
  `...test_texto_da_trava_sai_limitado_e_sem_controle · H=ok · B=falha · prova (asserção)`
  `contagem: não prova (passa na base)=29; prova (asserção)=1`
- Mutação, 4 mutantes (um por linha de guarda mudada: limite de 200 bytes, filtro de imprimíveis, uso no `--status`, uso no aviso de espera), spec fora da árvore, `forge-mutante`:
  `M1 · morreu · .githooks/pre-push:43`, `M2 · morreu · .githooks/pre-push:43`, `M3 · morreu · .githooks/pre-push:102`, `M4 · morreu · .githooks/pre-push:222`. Nenhum sobrevivente; a lista cobre as 4 linhas de guarda do diff.
- Suíte completa e `validar-plugin.sh`: rodam no pre-push do envio, que só passa com tudo verde.

Bugs: nenhum.
