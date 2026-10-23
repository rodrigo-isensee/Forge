---
tipo: review
contrato: 1
pedido: impl-n-reg
branch: melhoria/impl-n-reg
commit: eaa30f89d08afa9431935a7d2469831842743aeb
parecer: aprovado
revisor: forge:tech-lead (outra instância, E1.2)
data: 2026-10-22
---
# Review do IMPL-N-REG (E1.2)

Code review (R-REVIEW) da entrega inteira, `38c58247fdae5482ed441db4dd21bff4d55471d7..eaa30f89d08afa9431935a7d2469831842743aeb` (6 commits, 5 arquivos, +72 −11, só `docs/` e `changelog.d/`). Não houve review de segurança: pela DECISÃO TÉCNICA registrada no Histórico do pedido, a entrega só copia pareceres em `docs/` e não aciona R-SEGURANCA.

## Achados

## Conferência item a item

| Item | Veredito | Evidência |
|---|---|---|
| c405785, `docs/qa/conformidade-leitura.md` | ok | O blob `bcf12f7` é o mesmo em `e77dbd0` e em `HEAD`. Entre o head do PR #270 (`445e769`) e `e77dbd0`, só esse arquivo muda. |
| cac4500, `docs/reviews/forge-check-lote.md` | ok | O blob `41723e3` é o mesmo em `b3b165c` e em `HEAD`. Entre o head do PR #252 (`b69dbe9`) e `b3b165c`, só esse arquivo muda. |
| 8282f00, `docs/qa/suite-paralela-d4.md` | ok | O blob `858e4da` é o mesmo em `ad65236` e em `HEAD`. Entre o head do PR #277 (`b578714`) e `ad65236`, só esse arquivo muda. |
| Mensagens dos 3 commits | ok | Seguem Conventional Commits, um arquivo por commit (cada um se reverte sozinho) e citam a origem, o PR e o commit que a develop tinha antes. |
| Varredura (`docs/kanban/limpeza-0.28.0.md`) | ok | Refiz a varredura de forma independente: comparei os blobs de `docs/reviews`, `docs/qa`, `docs/security` e `docs/devops` de cada `origin/melhoria/*` (15 branches) com o `HEAD`. Nenhuma branch com PR mesclado ficou com parecer final fora deste registro. As diferenças que restam ou são rodadas reprovadas, cujo parecer final aprovado já está na develop pela branch sucessora (impl-n-doutor, impl-n-fechar-a, impl-n-qa/qa2/qa3, impl-n-tpl-a), ou são branches sem PR que a tabela "Não apagar" já lista (lote-leitura-hook, lote-forge-check-0.28.0, impl-n-fechar-b). |
| Critério da E2 | ok | A tabela registra que `--merged` volta vazio por causa do squash e propõe o critério por PR mesclado, o mesmo da DECISÃO TÉCNICA do Jarvis no Histórico. Nada foi apagado. |
| eaa30f8 (neutralidade) | ok | A linha deixa de citar o nome da ferramenta de stack (R-NEUTRO). Rodei os testes de neutralidade, `test_regra_so_na_fonte` e os de changelog numa cópia em `$TMPDIR` sobre `eaa30f8`: 49 testes, OK (1 skip). |
| `changelog.d/impl-n-reg.md` | ok | Um fragmento só, com a seção `### Alterado` e uma linha que descreve o que a entrega faz. O `CHANGELOG.md` não foi editado. |
| `forge-check docs` | ok | Rodado na mesma cópia: rc=0. |

## Recomendações (não bloqueiam)
- `docs/kanban/limpeza-0.28.0.md:24` diz que `melhoria/impl-n-fechar-b` está "sem parecer". Desde `c97e2cc` (13:39, depois da varredura), a branch tem um review reprovado e um parecer de segurança aprovado. A classificação "Não apagar" continua certa, porque é uma branch em voo, fora do escopo do pedido. Quem fizer a E2.1 deve reler essa linha antes de agir, ou atualizá-la numa volta futura.

## Parecer
Aprovado. Os três pareceres foram copiados byte a byte da origem, a varredura confere com a minha, a correção de neutralidade está certa e o fragmento está no formato. Segue para o QA (E1.4).
