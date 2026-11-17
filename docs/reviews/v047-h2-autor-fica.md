---
tipo: review
contrato: 1
pedido: v0474
branch: melhoria/v047-h2-autor-fica
commit: 6d73898a54d405cae438ed76d745fd32bc2436f4
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-17
---
# Review: v0474 (E2.28, H2-AUTOR-FICA-ATE-O-MERGE, parte de ferramenta)

Escopo lido: `git diff e2880b42...6d73898a` (3 commits): `hooks/agentes.py`, `tests/test_hooks.py`, `tests/test_hooks_agentes_autor.py`, 12 fixtures `autor-*`, 14 mutantes em `tests/mutantes/v047-h2-autor-fica{,-2}.json`, índice de fixtures e fragmento do changelog.

## Achados
- A1 (bloqueante) hooks/agentes.py:460 · o novo autor apaga o registro inteiro do anterior que tenha qualquer branch em comum; o anterior perde as outras branches e o aviso delas some (R-REVIEW, defeito provado em S1). Subtraia só as branches em comum e mantenha o registro com as que sobram; teste com autor de 2 branches
- A2 (recomendado) tests/test_hooks_agentes_autor.py:50 · o teste usa um registro por branch, por isso não pega A1; com a correção, cubra o registro com várias branches e declare o mutante da nova guarda
- A3 (recomendado) hooks/agentes.py:462 · o teto de `autores` reaproveita LAPIDES_MAX; uma constante própria (AUTORES_MAX) deixa claro que os dois limites são independentes

## Sondas
- S1 · guardar_autores([{id: B, escrita: [melhoria/a, melhoria/b]}], [{id: A, escrita: [melhoria/a]}], 2.0) · espera: B segue autor de melhoria/b · obtido: só [{id: A, escrita: [melhoria/a]}], B sumiu

## Parecer
Reprovado por A1. O resto atende à E2.10: o `SubagentStop` grava o autor de escrita com id na forma de agente; a retomada sem `escrita` herda as branches do mesmo id e renova o prazo; o disparo de escrita avisa com código 0 e o `SendMessage`; lápide, autor ativo, prazo vencido, outra branch e parecer não avisam; `autores` ilegível vale vazio e nunca recusa. O ramo de liberação (C5) passou a gravar `autores`, sem perder o registro. Os avisos D3 e H2 saem num JSON só (`avisar`). A chave `aviso` do `test_hooks.py` vale só para o hook `agentes`, com código 0, e confere o stderr e o `systemMessage`.

A1 é defeito do aviso (falso negativo), não do bloqueio: nenhum disparo é recusado por ele. Mesmo assim tem gatilho real: um agente com dois briefs de escrita fica com várias branches em `escrita` (Z10), e o autor seguinte de uma delas apaga as outras. A docstring de `guardar_autores` e o nome do teste da linha 50 prometem tirar o anterior só das branches em comum.

Mutantes: 14 declarados, um por linha de guarda do `hooks/agentes.py`. As duas guardas novas do `tests/test_hooks.py` são do harness, não do hook. A mutação ficou com o autor (V2), e não a rodei de novo.

Tamanho: 72 linhas de código em `hooks/` e 83 de teste. A decisão do dono de 17/11 11:15 (H1) conta só o código, abaixo de 150.

Verificação (este revisor, no 6d73898a, ambiente limpo):
- `python3 -m unittest tests.test_hooks_agentes_autor`: 6 testes, OK.
- Os 109 fixtures de `tests/hooks/agentes/`, no harness de `test_hooks.Hooks.executar_em_lote`: OK, todos verificados (4 subtestes de pid e sessão pulados com motivo).
- `tests.test_agentes_clone` e `tests.test_agentes_hash_brief`: 66 testes, OK.
- A suíte completa fica com o CI do PR (sem PR nesta etapa).
