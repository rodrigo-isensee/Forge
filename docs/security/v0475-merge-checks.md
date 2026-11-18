---
tipo: revisao-seguranca
contrato: 1
pedido: v0474
branch: melhoria/v0475-merge-checks
commit: 27c4c5672f8dda2d9381c04179b8d028fabfaaef
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-17
---
# Review de segurança: v0474 E3.143 (revalidação por delta, E3.80 sobre o E3.45)

Delta lido (`forge-check parecer delta`, `9f497b0f..27c4c567`, sem o que veio da develop): `bin/forge-check` (`GH_SEM_PR`, `SEM_CHECKS_DO_FECHAR`, `CHECKS_NAO_CONFERIDOS`, `gh_json`, `checks_do_head`, `pr_da_cli`, `executar`, `ref_publicada`, `documento_sem_parecer`, recusa do brief com PR mesclado), `bin/forge-fechar:1222`, `bin/forge-testes`, `tests/test_forge_check_pr.py`, `tests/test_fechar_forge_check_real.py`. Já lido antes: o resto do E3.45 (parecer no `9f497b0f`, no git).

Conclusão: aprovado. Pontos pedidos:
- `FORGE_FECHAR_PASSO_1` não vale no hook do `gh pr merge`: só o `executar` do `forge-check` a lê (`bin/forge-check:10245`, só o valor `1`; o mutante de `tests/mutantes/v0474-merge-checks-4.json` prende). O hook `parecer` não lê a variável nem chama `pr_da_cli` ou `checks_do_head` (decide pelo resultado gravado e pelo `cmd_pr`, `hooks/parecer.py:684-700`) e roda no ambiente do Claude Code, não no da linha de comando. Com a variável, nada é gravado (`bin/forge-check:10254`): o reprovado anterior do mesmo head continua valendo e não há como gravar aprovado sem conferir os checks. Um agente que a usa obtém o mesmo que não rodar o `forge-check pr` (sem resultado gravado), nada a mais.
- `gh pr view` que falha (rede, teto, saída ilegível, vazio) entra em `CHECKS_NAO_CONFERIDOS` (`bin/forge-check:1491-1497`) e é gravado como reprovado (`:10257`); o hook recusa o `gh pr merge` pelo reprovado (`hooks/parecer.py:686-687`). Só as marcas de "sem PR a conferir" (`:1444`: sem PR, sem remoto do GitHub, sem login, sem gh) dispensam, e em todas o `gh pr merge` também não roda. O A1 anterior está corrigido.

Gatilhos: controle do Forge (portão de merge e hook `parecer`), integração com o GitHub, `bin/` do fluxo de branches (`R-MAIN`).

## Achados
- A2 (recomendado) bin/forge-check:1503 · projeto sem ruleset nem proteção legível, logo depois do push (lista vazia), o pr aprova; aberto da rodada anterior, sem mudança.
- A3 (recomendado) bin/forge-check:1491 · até 4 chamadas ao gh de 10 s no caminho do pr contra o prazo de 8 s do hook do merge; aberto da rodada anterior, falha fechada.
- A4 (recomendado) bin/forge-fechar:1297 · com --armar num projeto sem checks obrigatórios no destino, nem o passo 1 (agora sem checks) nem o 4 os conferem e o gh pr merge --auto pode mesclar com o CI rodando; recusar --armar com a lista de exigidos vazia.
- A5 (recomendado) bin/forge-check:10259 · com o PR não lido, o pr sai 0 e imprime o veredito aprovado no stdout enquanto grava reprovado para o hook; somar CHECKS_NAO_CONFERIDOS às violações do rc ou ao veredito.

## Sondas

## Detalhe dos achados
- A4: severidade baixa. Caminho: agente roda `forge-fechar --armar` num projeto cujo destino não exige checks; o passo 4 não espera (`:1297`), o `ler_exigidos_do_destino` não roda (`:1276`) e o passo 1 dispensa os checks (`:1222`), então o auto-merge do GitHub não tem requisito a esperar. Antes do delta, o passo 1 só pegava isso com o PR já aberto fora do rascunho (o PR que o fechar abre no passo 3 e o rascunho D-1 já não eram conferidos), por isso não fica mais frouxo no caminho comum; no Forge, o ruleset exige os três pares. Correção mínima: com `--armar` e sem exigido algum no destino (nem os fixos do Forge, nem ruleset, nem proteção), parar com a orientação de rodar sem `--armar`. Esforço P. Dono: autor da branch (tech-lead).
- A5: informativa. O hook recusa (falha fechada), mas quem lê só o stdout vê "aprovado". Esforço P. Dono: tech-lead.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Testes rodados aqui no `27c4c567`: `tests/catraca.py --base origin/develop` e `tests.test_forge_check_pr`, `tests.test_fechar_forge_check_real`, `tests.test_parecer_delta`, `tests.test_revisar_sha`, `tests.test_ambiente_git`. CI: a branch não tem PR nem execução (`gh pr list` e `gh run list` vazios); a suíte inteira fica para o CI do PR, que o passo 4 do forge-fechar exige verde. Ferramentas ausentes no PATH (lacuna): gitleaks, zizmor, actionlint, semgrep, shellcheck; nenhum workflow mudou.
