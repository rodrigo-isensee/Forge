---
tipo: review
contrato: 1
pedido: impl-d5a-pa6
branch: melhoria/impl-d5a-pa6
commit: ad3c5a5bef6aef0a7d6e1ae0065f9a12077938a9
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-30
---
# Review: impl-d5a-pa6

Escopo lido: `git diff 234dbe0fb90b005450d7c2eb59e6241ea9779155 ad3c5a5bef6aef0a7d6e1ae0065f9a12077938a9` (8 arquivos, 6 commits: 1360e98, 9ab52a2, 7e3c8fd, fe8555a, 54299f5, ad3c5a5), contra o §2 do desenho `docs/propostas/discovery-0.29.0/d5a.md` e os controles C-1 a C-6 de `docs/security/ameacas/d5a.md` (pasta do Forge em `~/.forge-contrib`). Primeira rodada: sem parecer anterior, sem delta.

## Achados

## Parecer
**Aprovado.** A entrega faz o que os itens E1 a E5 pedem, sem mudar `bin/`, `hooks/` nem `scripts/`.

Conferência por item:
- **E1, `R-DECISAO`.** O complemento traz os seis pontos do desenho e um sétimo, sobre decisão, exceção, rótulo e aceite, que é o C-2 do modelo de ameaças: decisão, exceção, rótulo `afrouxa-regra`, aceite de risco, custo e acesso com `comando: —` e `decisão: <pedido>` até a decisão estar gravada; o aceite de risco nunca tem comando (`R-SEGURANCA`). C-1 (uma linha, um comando, um efeito; sem `--no-verify`, `--force`, `--admin`; mais de um passo vira `comando: —`), C-3 (sem segredo nem dado de pessoa, `<valor>`), C-4 (vocabulário do time; o painel é dado, não autorização) e C-5 (evidência no motivo de saída) estão no ponto do `comando` e no de entrada e saída. Revisão atualizada para 2026-10-30.
- **E2, `R-WIP`, itens do painel e de `origem:`.** "Aguardando o dono" sem limite próprio, com a vaga na coluna de origem, e `origem:` fora das duas colunas de validação: C-6 inteiro.
- **E3, `skills/kanban-scrum/SKILL.md:9`, `:32`, `:39`, `:54`.** A coluna entrou como frase no parágrafo "Quadro", e não como a tabela de uma linha do desenho. Desvio aceito: a skill já tinha 132 linhas na base e o teto de `Orcamento` para skill é 133 (`tests/config.json:77`); a tabela (cabeçalho, separador e linha) passaria do teto. A frase só cita `R-DECISAO` e `R-WIP`, como o desenho pede. "Bloqueado" passa a dependência externa, a política vale para os dois e o resumo do topo ganha "aguardando o dono: N".
- **E4, `templates/projeto/KANBAN.md:4-10`.** Seção `## Aguardando o dono` antes de `# Upstream`, sem parêntese, com as 7 colunas e vazia (controle do item 4 do modelo de ameaças); resumo de WIP com "Aguardando o dono: 0". `test_kanban_modelo_do_forge_e_valido` segue verde.
- **E5, `agents/jarvis.md:46`.** Uma oração que cita `R-DECISAO` painel "Aguardando o dono", sem repetir a regra.
- **Testes novos (`tests/test_forge.py:1743-1763`).** `test_kanban_painel_do_dono_no_topo` cobre o topo e a seção vazia (T-S3) e é vermelho na base (sem a seção, o segundo título é `# Upstream`). `test_kanban_painel_com_cartao_valido` trava a forma de 7 colunas (F9). O terceiro, `test_kanban_painel_barra_pipe_no_comando_e_id_repetido`, junta T-S4 (pipe no `comando` dá violação de colunas) e T-S5 (mesmo ID no painel e na origem dá "repetido"); os dois guardam comportamento do `bin/forge-check` que já existe, arquivo em `PROTEGIDOS` que fica fora do diff.
- **Invariantes (`tests/config.json`).** Só acréscimos: 3 na skill, 1 no jarvis, 3 na `R-WIP`, 6 na `R-DECISAO`. As únicas linhas removidas no diff são as que ganharam vírgula no fim; nenhum trecho sumiu nem mudou. Cobrem T-S1 (`comando: —` com `decisão: <pedido>`; um comando, um efeito) e T-S2 (`origem:` fora das colunas de validação).
- **Commits que se revertem sozinhos (P3 = B).** Numa cópia em `$TMPDIR`, a partir de ad3c5a5, `git revert --no-commit` de cada um dos 6 commits, sozinho, aplica sem conflito, e as classes `RegrasInviolaveis`, `AntiDuplicacao`, `RegrasComId`, `Neutralidade`, `Skills`, `Orcamento` e `ForgeCheck` (60 testes) ficam verdes em cada caso e no HEAD (`Ran 60 tests ... OK`, sete vezes).
- **Teto M14.** `git diff --numstat --no-renames` sobre a base: `tests/config.json` 17+4 e `tests/test_forge.py` 22+0, total 43 linhas de código e teste; o resto é texto `.md` e fragmento de changelog. Um comportamento (o painel), lote por arquivo de 5 itens, dentro do teto de 6.
- **Regras da fábrica.** `R-NEUTRO`: nada de projeto específico. `R-CUSTO`: nada pago. Nenhuma regra afrouxada. Fragmento novo em `changelog.d/impl-d5a-pa6.md`, sem tocar no `CHANGELOG.md`, com a nota de que projetos existentes não recebem a seção.
- **Ferramentas.** A suíte completa rodou no pre-push do envio de ad3c5a5 (registro do pedido, 2026-10-30 11:43, verde) e roda de novo no envio deste parecer; não a refiz. Segurança tem parecer próprio (`docs/security/impl-d5a-pa6.md`, commit 5084c0f), que não refaço.

Recomendações (não devolvem):
- `R-DECISAO` (ponto de saída) · a frase sobre a evidência repete a palavra motivo; reescrevê-la com outro sujeito mantém a invariante e lê melhor. Fica para o próximo lote que tocar a regra.
- `skills/kanban-scrum/SKILL.md:9` · "no topo, fica a coluna **Aguardando o dono** (topo do quadro)" diz o topo duas vezes; o parêntese existe para a invariante. Mesmo tratamento.
- `tests/test_forge.py:1757` · o terceiro teste junta dois comportamentos (pipe e ID repetido); separá-los daria uma falha mais legível. Não muda cobertura.
