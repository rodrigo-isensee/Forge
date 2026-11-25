---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-fechar-ci-topo
commit: dd2fcada2719cafad4eee2d8e31f3aaec2e8d5c3
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-24
---
# Review de segurança: v0481 (E13.9, #880, forge-fechar: CI do topo, branch criada do servidor, cópia certa)

## Gatilhos
Gatilhos: controle do fluxo de merge (portões do `forge-fechar`, R-FLUXO), CI da develop, guardas de mutação e catraca (R-CONFORMIDADE).

## Achados
- A1 (bloqueante) tests/mutantes/v047-integracao-em-lote-3.json:46 · O CI do Revisar-sha está vermelho: o `de` de IL-M21 (guarda "CI do merge não verde liga a falha", a do passo 8 que o item muda) e o de M2 (mp1311-fechar-cartao.json:16, FECHAR-REF-POR-NOME) não casam mais com bin/forge-fechar:1241 e :1657.
- A2 (bloqueante) tests/test_fechar_sha_conferido.py:122 · A catraca do Revisar-sha está vermelha: `test_commit_que_falta_aqui_pede_o_fetch` sumiu (renomeado). A garantia dele (commit ausente: rc 1, pede o fetch, nada chamado) segue neste teste; devolva-lhe o nome antigo em vez de pedir o rótulo.

## Sondas
- S1 · python3 -m unittest tests.test_forge_mutante.ConferirTodas.test_toda_spec_do_forge_confere_com_a_fonte_fora_as_pendentes · espera: OK · obtido: FAILED, mp1311-fechar-cartao.json: M2 e v047-integracao-em-lote-3.json: IL-M21 (igual à parte 4/5 do CI 45527336208)
- S2 · python3 -I tests/catraca.py --modo regras --base d49accf8 --head HEAD --ramo melhoria/v0481-fechar-ci-topo (eventos e execuções vazios) · espera: sem recusa · obtido: R-CONFORMIDADE, teste test_commit_que_falta_aqui_pede_o_fetch apagado ou renomeado

## Detalhe dos achados
O que o brief pede conferir, no Revisar-sha (código; os dois achados são de guarda e CI, não do comportamento):
- **Nenhum caminho mescla sem os checks verdes do head.** O FECHAR-CI-TOPO (bin/forge-fechar:1231-1246) só roda no passo 8, depois do merge; o 6, o 6b (`ci_antes_do_merge`, :1220) e o `--match-head-commit` não mudam. O 0 que agora sai com o topo verde deixa o lote e o laço seguirem, mas cada merge seguinte passa de novo pelo 6b. O FECHAR-CRIA-BRANCH (:1655-1666) cria a branch no sha lido do servidor (`remoto_exato`, só hex de 40 ou 64) e volta ao caminho da branch local (`so_remota=0`, `ref_check=refs/heads/<ref>`): o `forge-check pr` confere esse sha, o passo 2 relê o local e o servidor (:1739-1747). A busca (`buscar_de`, :635) é só por sha, sem ref nova nem FETCH_HEAD; `git branch --no-track` sem `-f` falha se a branch aparecer no meio (para no passo 1). O nome já passou por `check-ref-format --branch` (:214), que recusa `-x`, `-f` e `--force` (sondado à parte: nada de opção injetada no `git branch`).
- **O CI do topo só vale quando contém o merge.** A comparação é sempre `compare/<merge>...<topo>` com `$1` fixo, aceita só `ahead` ou `identical`; topo vazio, ilegível, igual ao sha já lido, `behind` ou `diverged` saem do laço como `cancelado` (código 5). Cada volta exige um topo novo e o prazo restante cai até 0: o laço termina. `pr_merge` vem do GitHub sem checagem de hex, mas o erro de leitura falha fechado (cancelado).
- **Nada que barra hoje deixa de barrar.** Vermelho, pendente e ilegível seguem 5; busca que não traz o commit para no passo 1 com a mesma mensagem; o FECHAR-COPIA-CERTA (:1685-1689) só acrescenta parada e não pega worktree ligada. No código, só aperta ou neutro. Nos controles em volta, não: A1 e A2 deixam vermelhos o CI e a catraca do head.

A1. Evidência: tests/mutantes/v047-integracao-em-lote-3.json:46 (`de` com `${1:0:7}`; a linha virou bin/forge-fechar:1241 com `${sha_ci:0:7}`) e tests/mutantes/mp1311-fechar-cartao.json:16 (`de` `  ref_check="$sha_conferido"\nfi`; agora :1657 tem 4 espaços e `else` depois). Caminho: a spec que não casa deixa a guarda do passo 8 e a do FECHAR-REF-POR-NOME sem prova de mutação, e o CI vermelho barra o merge. Severidade: média (perda de prova de guarda, falha fechada). Correção mínima: no mesmo commit, alinhar o `de` e o `para` dos dois mutantes à fonte atual: IL-M21 com `${sha_ci:0:7}`; M2 com `    ref_check="$sha_conferido"\n  else` e o `para` com `$ref` no lugar. Rodar `bin/forge-mutante` nas duas specs (os mutantes têm de morrer). Esforço P. Dono: autor da entrega.

A2. Evidência: tests/test_fechar_sha_conferido.py:122; a catraca (run 45527336207) reprova em "Regras que somem ou afrouxam, testes que somem". Caminho: sem correção, o merge depende do rótulo `afrouxa-regra` do dono para uma mudança que não afrouxa nada. Severidade: baixa (processo; falha fechada). Correção mínima: renomear `test_commit_que_a_busca_nao_traz_pede_o_fetch` para `test_commit_que_falta_aqui_pede_o_fetch` (o corpo fica como está) e conferir a catraca local (S2) limpa. Esforço P. Dono: autor da entrega.

Os recomendados A1 a A3 do code review (docs/reviews/v0481-fechar-ci-topo.md) ficam com o tech-lead; nenhum deles abre caminho de merge sem os checks.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Rodados por mim no Revisar-sha: `tests.test_fechar_ci_topo` e `tests.test_fechar_sha_conferido` (18 testes, OK), S1 e S2. CI do Revisar-sha (run 45527336208): parte 4/5 em 3.14 com 1 falha (a de A1), o resto cancelado pelo envio do parecer de review. gitleaks, zizmor, actionlint, semgrep e shellcheck ausentes no PATH (lacuna; o diff não toca workflow nem segredo).
