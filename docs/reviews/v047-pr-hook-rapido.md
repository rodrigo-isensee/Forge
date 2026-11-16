---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-pr-hook-rapido
commit: 6f3f4e7042bf32734c23ae04f1141a7a6e117162
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-15
---
# Code review: hook R-REVIEW rápido no gh pr ready e no gh pr merge (PR-HOOK-RAPIDO, E2.117)

Escopo: pedido v047, etapa E2.153 (`R-REVIEW`), classe C, head `6f3f4e70` (Base-sha `bf475209`), instância que não fez a entrega. Revalidação por delta do parecer aprovado no head `8eebc2a5` (E2.141).

Delta lido: `forge-check parecer delta docs/reviews/v047-pr-hook-rapido.md`, intervalo `8eebc2a5..6f3f4e70`, no domínio: `bin/forge-check`, `changelog.d/v047-pr-hook-rapido.md`, `docs/hooks-fixtures.md`, `docs/hooks.md`, `hooks/_comum.py`, `hooks/conformidade.py`, `hooks/parecer.py`, as fixtures `tests/hooks/conformidade/gravar-resultado-do-pr-tech-lead-bloqueia.json` e `tests/hooks/parecer/pr-merge-review-reprovado-sem-resultado-bloqueia.json`, `tests/mutantes/v047-pr-hook-rapido-2.json` e `tests/test_pr_hook_rapido.py`. O resto do intervalo são os pareceres de QA, segurança e review e o merge `5f3f9d69`; o código da volta é o commit `6f3f4e70`.

## Achados
- A1 (recomendado) hooks/parecer.py:567 · resolvido no projeto: fora do clone do Forge o aprovado gravado não libera o ready nem o merge e a conferência roda (teste S3 e PHR9). No Forge segue o afrouxamento aceito pelo dono (v046), declarado no fragmento, com o CI de pareceres como portão
- A2 (recomendado) bin/forge-check:365 · resolvido: lote com rc do cat-file diferente de 0 e corpo truncado devolvem {} (bin/forge-check:355 e :365; PHR10 e PHR11 morrem)
- A3 (recomendado) bin/forge-check:5 · resolvido: docstring, comentário em bin/forge-check:1567, hooks/_comum.py:2757 e docs/hooks.md dizem o atalho novo e o limite do projeto
- A4 (recomendado) bin/forge-check:338 · M14: 361 linhas contadas de código e teste (bf475209...6f3f4e70), acima de 150; o corpo do PR precisa de `teto: excedido, 361 linhas, <motivo>`

## Sondas

## Parecer
**Aprovado**, com o A4 pendente para o corpo do PR. A volta faz o que o delta pede (`R-REVIEW`; `R-SEGURANCA` citado, não refeito):
- `verificar` (hooks/parecer.py:567): o aprovado gravado só libera com `EXIGE` (o `gh pr create`, como na v046) ou no clone do Forge (`e_clone_do_forge`, que dá falso quando há `.forge/versao`: escrever o manifesto no projeto não o torna o Forge). No projeto o aprovado cai na conferência de hoje, como antes da E2.117; o reprovado recusa em todo lugar só lendo. Teste de comportamento dos três ramos no projeto (`AtalhoNoProjeto`: aprovado gravado sobre review reprovado recusa; aprovado refaz a conferência; reprovado recusa sem refazer).
- `CITA_A_MARCA` (hooks/conformidade.py:76): a S2 da segurança entra como mais uma alternativa da mesma regra, só no projeto (`raiz_e_projeto`), com fixture própria no corpus do `conformidade`; a mensagem cita as duas formas. Limite conhecido, o mesmo da marca: o nome montado em tempo de execução escapa (BP-5, sandbox).
- `textos_da_arvore`: as duas guardas novas (rc e tamanho do corpo) falham fechado; o teste de rc tem controle com 0 que lê.
- Escopo: um commit de código, sem mudança fora do pedido. Nenhum invariante de `tests/config.json` tocado.
- PA-7 conferido: AR-1 e AR-2 (cada guarda nova com mutante e teste do ramo de falha: PHR9 a PHR12); AR-4 os testes montam o processo pelo `montar_proc` do `test_hooks`; AR-9 os textos antigos foram trocados (A3); AR-12 a spec nova bate com o head (os quatro mutantes acharam o trecho). Nenhuma classe repetida neste delta: `achados-recorrentes.md` sem linha nova.

Verificação (regra 5 de `docs/economia-de-tokens.md`; a suíte inteira fica com o CI do PR):
- `python3 -m unittest tests.test_pr_hook_rapido` no head: `Ran 15 tests in 42.289s` `OK`.
- `bin/forge-mutante --processos 1 tests/mutantes/v047-pr-hook-rapido-2.json`: PHR9, PHR10, PHR11 e PHR12 `morreu` (4/4).
- `bin/forge-mutante --cobertura --base 8eebc2a5…`: `coberta` em bin/forge-check:355, bin/forge-check:365 e hooks/parecer.py:567; nenhuma `apagada`.
