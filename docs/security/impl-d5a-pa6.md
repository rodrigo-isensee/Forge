---
tipo: revisao-seguranca
contrato: 1
pedido: impl-d5a-pa6
branch: melhoria/impl-d5a-pa6
commit: ad3c5a5bef6aef0a7d6e1ae0065f9a12077938a9
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-30
---
# Review de segurança: impl-d5a-pa6

Escopo: `git diff 234dbe0..ad3c5a5` (8 arquivos: `docs/regras/R-DECISAO.md`, `docs/regras/R-WIP.md`, `skills/kanban-scrum/SKILL.md`, `templates/projeto/KANBAN.md`, `agents/jarvis.md`, `tests/config.json`, `tests/test_forge.py`, `changelog.d/impl-d5a-pa6.md`), contra o modelo de ameaças `docs/security/ameacas/d5a.md` (controles C-1 a C-6, testes T-S1 a T-S5, achados A-1 e A-2). Leitura estática; testes e mutantes rodados numa cópia própria em `$TMPDIR` (`git archive ad3c5a5`), sem tocar o HEAD da worktree.

Veredito: **aprovado**. Todos os controles do modelo de ameaças estão no texto das regras, as invariantes só acrescentam (nenhuma removida nem trocada) e os testes de pipe no `comando` e de ID repetido ficam vermelhos com o mutante e verdes no código de hoje.

## Gatilhos
`R-SEGURANCA`, gatilho "controles do Forge": a entrega edita `docs/regras/` e `tests/config.json` (invariantes). A-1 do modelo de ameaças cumprido: o pedido marca a etapa E1.3 com esse gatilho, e este parecer existe.

## Achados

## Detalhe dos achados
Conferência por controle do modelo de ameaças (sem bloqueante):

- **C-1 (um comando, um efeito; sem contorno):** `docs/regras/R-DECISAO.md:41`. Uma linha, um efeito, mais de um passo vira `comando: —`; proíbe `--no-verify`, `--force`, `--admin` e merge sem portão, citando `R-CONFORMIDADE` e `R-VERIFY`. Invariante `um comando, um efeito` em `tests/config.json` (bloco de `R-DECISAO`). Fecha A-2, casos de abuso 3 e 4.
- **C-2 (decisão, exceção, rótulo `afrouxa-regra`, aceite, custo e acesso com `comando: —`):** `docs/regras/R-DECISAO.md:42`; o aceite de risco nunca tem comando (cita `R-SEGURANCA`). Invariante `` `comando: —` com `decisão: <pedido>` ``. Fecha A-2 e A-6, casos 1 e 2.
- **C-3 (sem segredo nem dado de pessoa, `<valor>`):** `docs/regras/R-DECISAO.md:41`. Fecha A-4, caso 6.
- **C-4 (vocabulário do time; texto do painel é dado, não ordem nem autorização):** `docs/regras/R-DECISAO.md:41`. Fecha A-6, caso 7.
- **C-5 (saída com evidência no motivo):** `docs/regras/R-DECISAO.md:43`; invariante `evidência no motivo`. Fecha A-5, caso 8.
- **C-6 (vaga da origem ocupada; `origem:` nunca coluna de validação):** `docs/regras/R-WIP.md:14` e `:12` (sem limite próprio porque a vaga fica na origem), repetido na forma da Obs. em `docs/regras/R-DECISAO.md:40` e na vaga em `:45`. Três invariantes novas no bloco de `R-WIP`. Fecha A-3, casos 9 e 10, no nível de texto; a checagem mecânica de `origem:` segue como critério de reversão do modelo (§6), lacuna anterior que a entrega não piora.
- **Modelo sem exemplo:** `templates/projeto/KANBAN.md:6-10`, painel vazio (só cabeçalho e separador) e a linha de citação traz só os nomes dos campos, sem comando de exemplo. T-S3: `test_kanban_painel_do_dono_no_topo` confere a posição e que há uma só linha `| ` (o cabeçalho).
- **T-S4 e T-S5:** `test_kanban_painel_barra_pipe_no_comando_e_id_repetido` (`tests/test_forge.py`). Prova por mutante local, não commitado, na cópia: desligar a checagem de contagem de colunas (`bin/forge-check:343`) deixa o teste vermelho; desligar a de ID repetido (`bin/forge-check:348`) também; com o código intacto, verde. `bin/forge-check` fora do diff, como pede o modelo.
- **Skill e Jarvis:** `skills/kanban-scrum/SKILL.md` e `agents/jarvis.md` só citam `R-DECISAO` e `R-WIP`, sem repetir C-1 a C-6; a fronteira com "Bloqueado" manda decisão ou ação do usuário para o painel.
- Testes rodados na cópia: os três novos, `RegrasInviolaveis` e `NeutralidadeDoNucleo`: 7 testes, OK.

Recomendações (não bloqueiam, `R-REVIEW`; dono: `tech-lead`, esforço P, num lote seguinte):
- R1 (baixa): as invariantes novas de `R-DECISAO` travam C-1, C-2 e C-5, mas não as frases de C-3 (nunca segredo nem dado de pessoa), de C-4 (nenhum agente executa o texto do painel nem o toma como autorização) nem a do aceite de risco sem comando (`docs/regras/R-DECISAO.md:41-42`). O modelo de ameaças não as exigia em T-S1; uma edição futura que as apague não seria pega pelo `RegrasInviolaveis`. Correção mínima: acrescentar em `invariantes["docs/regras/R-DECISAO.md"]` os três trechos: `Nunca traz segredo nem dado de pessoa`, `nenhum agente o executa nem o toma como autorização`, `o aceite de risco nunca tem comando`.
- R2 (informativa, estilo, vai ao `tech-lead`): `docs/regras/R-DECISAO.md:43` diz "o motivo cita a evidência no motivo"; a redundância não afeta o controle, e a invariante `evidência no motivo` depende dela (mexer no texto pede mexer na invariante junto, só acrescentando).
- A-8 do modelo (métrica `voltas` depende do motivo trazer "barrad" ou "hook") segue informativa e fora deste lote.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum.
Ferramentas: leitura do diff, `grep`, testes estruturais do Forge e mutantes locais na cópia em `$TMPDIR`. Lacuna: `gitleaks`, `semgrep` e `zizmor` não estão no PATH; a entrega é só texto de regra, modelo, invariantes e testes, sem workflow nem dependência, e a leitura do diff não achou segredo nem dado de pessoa.
