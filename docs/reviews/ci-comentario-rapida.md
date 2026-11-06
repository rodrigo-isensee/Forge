---
tipo: review
contrato: 1
pedido: versao-033
branch: melhoria/ci-comentario-rapida
commit: 4135cde473cb64838e0eeb8f593343adb6ddc50a
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-04
---
# Review: ci-comentario-rapida (comentário do job `rapida`)

## Achados
- A1 (recomendado) .github/workflows/ci.yml:25 · o `name:` do job ainda diz "checagem rápida", o mesmo rótulo que o comentário deixou de usar; avaliar trocar em PR próprio, conferindo antes que o nome não é check exigido

## Parecer
Aprovado. Delta próprio `c481b78...4135cde` (8bcc469): só o comentário do topo do `ci.yml` muda (nenhuma linha executável) e passa a dizer que o push na develop roda o job `rapida`, com a suíte inteira por `scripts/suite-paralela.py` no Python 3.12, sem os demais passos da bateria. Conferido contra o job (`ci.yml:23-36`): o texto bate.

- M14: delta próprio 5+4 (`ci.yml`) e 9+0 (`tests/test_ci_local.py`) = 18 linhas; um comportamento. A branch está empilhada em `melhoria/ci-ubuntu-26`: contra a develop atual dá 37 linhas e dois comportamentos. O PR desta branch só abre depois do merge da `ci-ubuntu-26` (ou já sobre a develop que a contém); aberto antes, carrega dois comportamentos e cai no M14.
- Teste reprova sem a mudança: com o teste da branch sobre o `ci.yml` de c481b78, `test_comentario_do_topo_diz_que_a_rapida_roda_a_suite` falha. O teste também amarra o comentário ao passo real do job (o `run` cita `scripts/suite-paralela.py`).
- `python3 -I -m unittest discover -s tests -p test_ci_local.py`: 54 testes, OK.
- Fragmento `changelog.d/ci-comentario-rapida.md` presente. Commit em Conventional Commits.
- Devops: `docs/devops/ci-comentario-rapida.md` aprovado (citado). Ele declara `pedido: ci-comentario-rapida`, não `versao-033`: alinhar antes do `forge-check pr versao-033`. Mexe em `.github/`: rótulo `afrouxa-regra` e push com escopo `workflow` são do dono.
