---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-pr-hook-rapido
commit: 0620dc23a27fa7ca5068f8a47fc38e27152d91b6
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-16
---
# Code review: hook R-REVIEW rápido no gh pr ready e no gh pr merge (PR-HOOK-RAPIDO, E2.117)

Escopo: pedido v047, etapa E2.177 (`R-REVIEW`), classe C, head `0620dc23` (Base-sha `134ea4c8`). Revalidação por delta do parecer aprovado no head `6f3f4e70` (E2.153), vencido pelo `2d1503c5` e pela junção com a develop no `0620dc23`.

Delta lido: `forge-check parecer delta docs/reviews/v047-pr-hook-rapido.md`, intervalo `6f3f4e70..0620dc23`, sem o que veio da base; no domínio só `tests/mutantes/v047-pr-hook-rapido.json` (PHR6: `de` e `para` passam a `cod, lote = git(`, a linha de bin/forge-check:354 desde o `6f3f4e70`) e `tests/test_testes_tocados.py` (contagem 85 mantida, comentário refeito sobre os 84 da develop na resolução da junção). Nenhum código de `bin/` ou `hooks/` mudou no intervalo fora da base.

Histórico: aprovado no `8eebc2a5` (E2.141) e no `6f3f4e70` (E2.153); o texto abaixo do A4 é o da E2.153, que segue valendo para o código.

## Achados
- A1 (recomendado) hooks/parecer.py:567 · resolvido no projeto: fora do clone do Forge o aprovado gravado não libera o ready nem o merge e a conferência roda (teste S3 e PHR9). No Forge segue o afrouxamento aceito pelo dono (v046), declarado no fragmento, com o CI de pareceres como portão
- A2 (recomendado) bin/forge-check:365 · resolvido: lote com rc do cat-file diferente de 0 e corpo truncado devolvem {} (bin/forge-check:355 e :365; PHR10 e PHR11 morrem)
- A3 (recomendado) bin/forge-check:5 · resolvido: docstring, comentário em bin/forge-check:1567, hooks/_comum.py:2757 e docs/hooks.md dizem o atalho novo e o limite do projeto
- A4 (recomendado) bin/forge-check:338 · M14: 361 linhas contadas de código e teste (bf475209...6f3f4e70), acima de 150; o corpo do PR precisa de `teto: excedido, 361 linhas, <motivo>`

- A5 (recomendado) tests/mutantes/v047-pr-hook-rapido.json:59 · resolvido no 2d1503c5: o PHR6 não seguiu a linha que o 6f3f4e70 mudou (AR-12); o review da E2.153 conferiu só a spec -2

## Sondas

## Parecer
**Revalidação E2.177 (delta 6f3f4e70..0620dc23): aprovado.** O PHR6 volta a achar o trecho e morre; a contagem do mapa bate com a develop da junção. AR-12 sobe para 3 em `achados-recorrentes.md`. Verificação no `0620dc23`: `python3 -m unittest tests.test_testes_tocados.Mapa` `Ran 18 tests` `OK`; `bin/forge-mutante --processos 1 tests/mutantes/v047-pr-hook-rapido.json`: PHR1 a PHR8 `morreu` (8/8). Suíte: CI run 43792699555 com as seis partes da suíte verdes no `0620dc23`. O A4 (teto M14 no corpo do PR) segue com o autor.

Parecer da E2.153 (head `6f3f4e70`):
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
