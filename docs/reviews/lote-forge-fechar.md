---
tipo: review
contrato: 1
pedido: lote-forge-fechar
branch: melhoria/lote-forge-fechar
commit: 468f6c3f54645024be19a39a6262bf3156734bf6
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-21
---
# Review: lote do bin/forge-fechar (log endurecido, número das execuções, limpeza com --limpar)

Escopo: entrega inteira (`ad6d96c..468f6c3`), contra o desenho `docs/propostas/aq/lote-forge-fechar.md` e o pedido. Revisor: instância separada da do autor (D-ETAPAS-INST). Segurança é do parecer do `security-engineer` em `docs/security/`; não refeita aqui.

## Achados

## Revalidação (volta por delta)
- Parecer anterior (e5ef160, reprovado por A1) relido. Delta lido: `agents/tech-lead.md` e `tests/test_fechar.py` (commit 468f6c3). Já lido e mantido: C1, C2 e C3 de `bin/forge-fechar`, `docs/fechamento-integrador.md` e o fragmento de changelog.
- A1 resolvido: `agents/tech-lead.md:31` diz que o código 3 é merge feito com limpeza pendente, não falha, e cita `--limpar`.
- Recomendação R3 do parecer de segurança: `test_c3_branch_remota_com_commit_alem_do_mesclado_nao_e_apagada` cria na remota um commit além do sha mesclado e prova o controle: saída 3, `remota=pendente`, nenhum `push --delete` e a remota intacta no novo sha.
- Merge da develop (4e3c2cb) sem perda: o diff contra a base ad6d96c lista só 7 arquivos, todos da entrega.

## Ferramentas (citadas, não refeitas)
- `python3 -m unittest tests.test_fechar`: 80 testes, OK (rodado nesta revisão, 15 s).
- Suíte do pre-push e `scripts/validar-plugin.sh`: rodam no push desta branch e no CI do PR.
- `shellcheck`: não instalado nesta máquina; fica com o CI do PR (pendência, não review manual).

## Recomendações (não bloqueiam)
- `bin/forge-fechar`, `limpar_entrega`: o awk do `git worktree list --porcelain` lê `$2` e corta caminho com espaço (já existia antes); se tocar o arquivo de novo, usar `substr($0, 10)`.
- `sha_confere` usa a ancestralidade em `$base` local sem `git fetch`; é conservador (base velha só deixa pendente), vale uma linha no doc.
