---
tipo: qa
contrato: 1
pedido: versao-033
branch: melhoria/permissao-agentes-md
commit: ce082b2864ee78172fc3b5bd1e2f1b2e822b4e17
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-04
---
# QA: versao-033 (PERMISSAO-AGENTES-MD)

Links: não há `docs/ux` neste repositório; o critério vem do cartão (`docs/propostas/backlog/versao-0.34-triagem.md`) e do pedido de QA. Código testado: ce082b2864ee78172fc3b5bd1e2f1b2e822b4e17 (um commit sobre b45e40a). Entrega só de texto: escopo incremental, suíte completa não rodada. Review lido só pelo número do parecer; segurança não é deste parecer.

## Achados
- Nenhum.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| CA-1: avisar o dono antes de delegar edição de `agents/*.md` quando a regra de permissão falta | tests.test_permissao_agentes_md.PermissaoAgentesMd.test_skill_manda_avisar_antes_de_delegar_edicao_de_agents | três trechos: o título do item, a condição "não estiver configurada" e a proibição de contornar por script (`R-CONFORMIDADE`) | passou; cai na base |
| CA-2: com a regra de permissão já aplicada, o dono não é avisado nem interrompido | leitura do texto ("com a regra já aplicada, não avise nem interrompa o dono") | n/a | passou; sem teste próprio |

## Execução
- `python3 -I -m unittest discover -s tests -p test_permissao_agentes_md.py`: 1 OK.
- Leitura: o item cobre o aviso, o brief que declara a necessidade, o caso com a regra já aplicada e a recusa sem contorno. Entrega o cartão.
- `python3 -I tests/neutralidade.py` no head: rc 0, sem saída.
- Vermelho antes do verde: arquivos de texto trazidos a b45e40a na worktree qa-permissao-agentes-md (`git checkout b45e40a -- <arquivos>`), teste rodado, árvore restaurada ao head e limpa. Falha observada na base, abaixo; no head, o teste passa.
- Base (`skills/trabalho-em-paralelo/SKILL.md` em b45e40a): `FAILED (failures=1)`, AssertionError: '**Delegação que edita `agents/*.md`:**' not found.
- Bugs abertos: nenhum.
