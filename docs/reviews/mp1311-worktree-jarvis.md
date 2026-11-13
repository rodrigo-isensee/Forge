---
tipo: review
contrato: 1
pedido: melhorias-de-projeto-1311
branch: melhoria/mp1311-worktree-jarvis
commit: c61435e6efaa446b3c73bb4504ea6e1cf60ca06c
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-13
---
# Review: melhorias-de-projeto-1311 (item 12, E2.18)

## Achados
- A1 (bloqueante, resolvido em c61435e6) skills/briefs-e-conferencia/SKILL.md:12 · o corte de redação tirou a frase que tests/test_modelos_projeto.py:113 exige ("Leia a skill `checagem-do-brief` para o que a ferramenta não sabe"); o teste passa na develop e falha no head; restaure a frase ou ajuste o teste com o motivo
- A2 (recomendado) agents/jarvis.md:40 · a regra "worktree antes de delegar" fica só no passo 4 e o teste a cobre por trecho de texto; aceitável, sem ação

## Sondas

## Parecer
Reprovado por A1, defeito provado (reproduzido, 1 falha em 17 testes de `test_modelos_projeto.py` no head; a mesma suíte passa em `origin/develop`).

Conferido: os cortes em `agents/jarvis.md` e na skill não tiraram regra com ID nem invariante; o "(padrão `node-react`)" da tabela segue na skill `iniciar-projeto`. Passam no head: `test_jarvis_nucleo` (20), `test_aq1_texto`, `test_novo_projeto`, `test_qa_lote_l09`, `test_jarvis_n_jar_a`, `test_testes_tocados`, `test_metricas_texto`, `test_orcamento_instrucao`, `test_skills_v0442`, `test_textos_dono_f7`, `test_textos_dono_f10`, `test_parecer_conteudo`. `test_forge` e `test_selo_e_entrega` não foram concluídos aqui (carga); valem pelo CI. Sem PR aberto.

## Revalidação (delta b94e026e..c61435e6)
Lido `forge-check parecer delta`: só `skills/briefs-e-conferencia/SKILL.md`. A frase "Leia a skill `checagem-do-brief` para o que a ferramenta não sabe" voltou (A1 resolvido) e saiu ", selado como qualquer outro" em 'Brief de volta', sem teste nem regra que o cite (grep). `test_modelos_projeto` passa no head (17 testes, discover). Sem PR aberto; suíte completa vale pelo CI. Aprovado; A2 segue recomendado, sem ação.
