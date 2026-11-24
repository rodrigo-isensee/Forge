---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-clone-nome-unico
commit: d33eb54d678d9032d6901f733797534c6f625ab4
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-24
---
# Review de segurança: v0480-clone-nome-unico (PR #860, E172.19)

Gatilhos: forge-check (controle que monta o comando copiado pelo agente), R-CONFORMIDADE.

Escopo lido: `git diff 5f1c6e97..d33eb54d` inteiro (bin/forge-check, bin/forge-copia, changelog.d, tests/mutantes, tests/test_forge_copia.py), mais `valor_de_shell_seguro`, `interpolacao_segura`, `linhas_da_referencia`, `nome_unico` e o laço de opções do `forge-fechar`.

Mérito (BRIEF-PEDIDO-ID-CRU): **só aperta**. O `id:` fora de `ID_DE_PEDIDO` sai como `PREENCHER` (bin/forge-check:9567) nos três pontos que iam crus (`comece por`, `decisões:`, `forge-fechar` do merge); os pontos restantes já passavam por `interpolacao_segura`. A linha nova da cópia (CLONE-NOME-UNICO) só sai com branch na forma de shell e `git check-ref-format`, papel em `[a-z0-9][a-z0-9-]*` e caminho final em `FORMA_DE_SHELL["raiz"]` sem `..`; o `forge-copia` carregado é o do mesmo plugin (`PLUGIN`), com guarda `__main__`, sem nova fronteira de confiança. Sonda local: `$(id)`, `p;rm`, aspas simples e duplas, barra invertida, `|` e `<` saem como `PREENCHER`; testes de `tests/test_forge_copia.py` passam (76).

Não aprova: o CI do head está vermelho por defeito do próprio PR (A1). `bateria (pareceres)` e `catraca` (rótulo `afrouxa-regra` do dono para mudança em `bin/forge-check`) vermelhos são esperados nesta fase e não são achado.

## Achados
- A1 (bloqueante) bin/forge-testes:153 · CI do head vermelho: test_mapa_lista_todo_modulo_que_usa_o_forge_check falha com ['test_forge_copia'] != [] (suíte 3.12 parte 1/5, run 45429212837); o teste da guarda não roda no plano dirigido quando o forge-check muda
- A2 (recomendado) bin/forge-check:9567 · ID_DE_PEDIDO aceita '-' inicial: id '--lote' ou '-h' vai cru ao comando copiado (forge-check proximo --lote; forge-fechar --lote --ref ...); usar valor_de_shell_seguro("pedido", ...) (NOME_SEGURO_DE_BRIEF), como o ENVIO já faz
- A3 (recomendado) bin/forge-check:9629 · o comando copiável traz `forge-copia clone|worktree ...`: colado literal vira pipeline para um comando `worktree`; trocar por um só subcomando (ou o texto fora da crase)

## Sondas

## Detalhe dos achados
**A1.** Evidência: job `suíte (python 3.12, parte 1/5)` do run 45429212837 no head d33eb54d: `FAIL: test_testes_tocados.MapaDoForgeCheck.test_mapa_lista_todo_modulo_que_usa_o_forge_check`, `AssertionError: Lists differ: ['test_forge_copia'] != []`. Causa: `tests/test_forge_copia.py` passou a importar o forge-check (via `test_pre_envio_brief.fc`) e não entrou na tupla `FORGE_CHECK` de bin/forge-testes:153. Caminho: com `FORGE_PREPUSH_SUITE=afetados`, uma mudança futura no `forge-check` que reabra o id cru não roda `BriefSugereACopia` e só o CI pega. Severidade: baixa (o CI pega), mas defeito provado e CI vermelho. Correção mínima: acrescentar `"test_forge_copia"` à tupla `FORGE_CHECK` de bin/forge-testes:153. Esforço P. Dono: autor da branch.

**A2.** Evidência: bin/forge-check:416 e :7066 (`[A-Za-z0-9._-]+`) contra bin/forge-check:9687 (`NOME_SEGURO_DE_BRIEF`, sem `-` inicial). Sonda (pelo harness do teste, `gerar(id_="--lote")`): sai `comece por \`forge-check proximo --lote --etapa E1.1\``. Caminho: quem escreve o `id:` de um pedido (fonte de escrita restrita) põe um id em forma de opção; no merge, `bin/forge-fechar --lote --ref <branch> --dry-run` muda o modo do integrador (o `--dry-run` no fim segue valendo). Severidade: baixa, sem execução de comando arbitrário. Correção mínima: em bin/forge-check:9567 trocar `ID_DE_PEDIDO.fullmatch(pedido_id)` por `valor_de_shell_seguro("pedido", pedido_id)` e cobrir `-x` no teste. Esforço P. Dono: autor da branch.

**A3.** Evidência: bin/forge-check:9629. Caminho: agente que cola o trecho entre crases roda `forge-copia clone | worktree <copia> ...`; sem ganho de atacante, mas é um comando copiável que não é um comando. Severidade: informativa (recomendado). Correção mínima: escrever o comando com um subcomando (`forge-copia clone <copia> --branch ... --papel ...`) e citar `worktree` fora da crase. Esforço P. Dono: autor da branch.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática, a suíte do arquivo tocado (`python3 -m unittest tests.test_forge_copia`, 76 OK), sonda pelo harness do teste e o log do CI (`gh run view --job`). Varredores de segredo e SAST não estão no PATH (lacuna registrada; o diff não toca segredo nem dependência).
