---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-proximo-por-etapa
commit: 7d675afaa992f35ac6030fbf232c2b8fcc77b47a
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-15
---
# Review de segurança: v047 (proximo por etapa, E2.72; revisão E2.120)

Escopo: `bf475209..7d675afa`, `bin/forge-check` (`etapas_conferidas`, `etapas_do_proximo`, `mescladas_na_develop`, `com_branch_mesclada`, `cmd_proximo --etapa`), `tests/test_proximo.py`, mutantes e fragmento do changelog. Pergunta do coordenador: um parecer ou merge forjado faz uma etapa aberta sair `feita (PR mesclado)`? Sim, por três caminhos (S1 a S3 no detalhe). Severidade baixa: o `proximo` é só leitura e não é portão (`R-SEGURANCA`, `R-REVIEW`); o merge da branch citada continua preso ao CI e aos pareceres. O efeito é esconder a etapa da lista padrão e do `passo` do coordenador, por isso as recomendações abaixo, sem bloqueio.

## Gatilhos
Ferramenta do Forge que decide o que o coordenador vê como próximo passo (controle do Forge, leitura do git sem rede). Não toca pipeline, dependência, segredo nem `hooks/conformidade.json`.

## Achados
- A1 (recomendado) bin/forge-check:6954 · o git grep conta qualquer linha `branch:` na coluna 0 de qualquer arquivo das pastas de parecer, até documento livre sem frontmatter (S1 reproduzido); ler só o frontmatter dos arquivos com o `tipo:` do contrato
- A2 (recomendado) bin/forge-check:6951 · `git log --merges` sem `--first-parent` lê merges de dentro de branch mesclada sem squash: um merge com assunto forjado fecha etapa de outra branch (S3 reproduzido); com `--first-parent` só contam os merges da própria develop
- A3 (recomendado) bin/forge-check:6954 · parecer com `branch:` errado (cópia, como as correções de campo do v047) fecha a etapa da branch citada, mesmo reprovado (S2); limite do sinal sem rede: dizer na saída que `feita` é indício do git, não registro de entrega

## Sondas

## Detalhe dos achados
Sondas executadas em repositório temporário (pedido com E1.1 `[branch melhoria/alvo]` e E1.2 `[branch melhoria/outra]`, ambas delegadas, `melhoria/alvo` nunca mesclada; roteiro em `$TMPDIR/sondas.sh`, fora do repositório):
- S1 · `docs/security/ameacas/x.md` sem frontmatter com a linha `branch: melhoria/alvo`, commitado na develop · espera: E1.1 em curso · obtido: E1.1 `feita (PR mesclado)`, fora da lista padrão, passo pula para E1.2.
- S2 · `docs/reviews/outra.md` com frontmatter `branch: melhoria/alvo` e `parecer: reprovado`, no squash da outra · espera: em curso · obtido: `feita (PR mesclado)`.
- S3 · na `melhoria/outra`, `git merge --no-ff -m "Merge pull request #1 from qualquer/melhoria/alvo" lixo`; a outra entra na develop por merge · espera: em curso · obtido: `feita`; passo: "todas as etapas têm registro de entrega".
- Controles que passaram: commit comum (não merge) com o assunto forjado não conta (`--merges`); nome parecido (`melhoria/alvo-2`) não conta; com `origin/develop` presente, merge forjado só na develop local não conta. Sem `origin/develop`, a develop local vale (S4b): só afeta a cópia de quem forja.

A1. Evidência `bin/forge-check:6954` (o padrão `^branch:` sem âncora no frontmatter nem filtro por `tipo:`; inclui `_modelo.md`, hoje inócuo porque `<branch>` não casa `BRANCH_DA_ETAPA`). Caminho: autor ou erro de redação põe a linha num documento livre de `docs/security/`, `docs/devops/`, `docs/reviews/`, `docs/qa/` ou `docs/architecture/features/` que chega à develop por review. Hoje a develop não tem nenhuma linha dessas fora do frontmatter (conferido). Severidade baixa. Correção mínima: ler o frontmatter (o leitor de contrato que o `forge-check docs` já usa) e aceitar `branch:` só de arquivo com `tipo:` de parecer. Esforço P. Dono: autor da E2.72.

A2. Evidência `bin/forge-check:6951`. Caminho: um merge com assunto `Merge pull request #N from x/melhoria/<alvo>` criado dentro de uma branch que a develop recebe por merge (a develop tem merges de `melhoria/*`, ex.: `melhoria/v0451`). Severidade baixa. Correção mínima: `git log --first-parent --merges` (como já fazem as leituras de merge em `bin/forge-check:2503` e `:3136`). Esforço P. Dono: autor da E2.72.

A3. Evidência `bin/forge-check:6954`. Caminho: parecer commitado na branch X com `branch:` de Y (erro de cópia; o v047 teve etapas só para corrigir campo de parecer, E1.40 a E1.42) faz as etapas de Y sumirem da lista padrão. Sem rede não há como provar o merge do squash; a correção proporcional é transparência: a linha de contagem ou o estado dizerem que vem do git, e `--etapa` mostrar a fonte (merge ou parecer). Esforço P. Dono: autor da E2.72.

Demais pontos conferidos, sem achado: `--etapa` validado por `ETAPA_DO_BRIEF` em `fullmatch` antes de qualquer uso e ecoado por `nome_seguro(sem_controle(...))`; todas as linhas de saída passam por `sem_controle` e pela largura; `BRANCH_DA_ETAPA` limitado (sem retrocesso explosivo); `rev-list` e `git grep` recebem sha40 e pastas fixas, com `--` antes das pastas; `contem` equivale à antiga checagem `e_ancestral` (sha40 na lista do `rev-list` do head) e branch de brief sem ref sai vazia sem quebrar (teste `test_selo_de_branch_sem_ref_nao_entrega_e_nao_quebra`); o índice `por_termo` mantém o limite de termo da regex antiga (`E1.3` não casa `E1.30` nem `E1.3.1`).

Suíte: rodei só `tests/test_proximo.py` (23 testes, OK, 62 s), como pede o brief; a suíte inteira fica para o CI do PR.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática e sondas locais em repositório temporário; varredura de segredos e SAST não estão no PATH deste ambiente (lacuna registrada; a entrega não toca segredo nem dependência).
