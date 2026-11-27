---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-f6-ci-uma-vez
commit: e8368a4cdd98951a1a3b96d18eb539e648d299ca
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-26
---
# Review: v0481 (E32.4, #929, F6 no CI: cada teste roda uma vez), 1ª rodada completa

Diff lido: `6edd59d2..e8368a4c` (3 commits: `4108333a` ci, `6b21cbae` M9, `e8368a4c` teste do diário). O Base-sha do brief (`ee05ee84`) fica atrás: a branch já trouxe #920 e #923, que estão na `develop`, e eles ficam fora da leitura. Código pelo H1: 500 linhas (`ci.yml` +56/-251, `diario.yml` +148, `scripts/arvore-testada.py` +45), 4 arquivos fora dos testes.

## Achados
- A1 (bloqueante) .github/workflows/ci.yml:360 · O `name:` sem aspas tem `: ` dentro (`F6: a suíte...`) e o YAML fica inválido. O GitHub não cria o CI do PR: o run 45924102244 falhou por "workflow file issue", sem jobs, e `gh pr checks 929` só lista `catraca`. É o A1 do parecer de devops. Ponha aspas no nome.
- A2 (bloqueante) scripts/arvore-testada.py:141 · O diff deixa 11 mutantes velhos (est-m7-verificador-decisao M3 e M4, v047-ci-rapido-3 M26 a M33, v047-ci-binario-cli M1 e M3, v047-ci-falhas-no-resumo F14). O teste ConferirTodas (tests/test_forge_mutante.py:1564) falha no head (AR-12). Alinhe as specs no mesmo commit.
- A3 (bloqueante) .github/workflows/diario.yml:107 · A fatia junta as specs pelo campo `pedido`. Specs de itens diferentes do mesmo pedido repetem ids, e o forge-mutante recusa o conjunto inteiro com rc 2, sem rodar nada (S1). Isso vale para 13 dos 420 grupos, entre eles v047, v0478 e v0481. Agrupe pelo nome da spec sem o sufixo `-<n>`.
- A4 (bloqueante) .github/workflows/diario.yml:118 · As 26 entradas de tests/fixtures/mutantes-pendentes.txt (o `de` fora da fonte, já conhecido) saem como inválidas e deixam o diário vermelho em 14 de 30 fatias. O cartão passa a avisar dívida conhecida, não quebra. Pule os ids da lista de pendentes (`--ids`) ou rode `--conferir --todas` antes.
- A5 (bloqueante) .github/workflows/ci.yml:35 · H1: são 500 linhas de código e três comportamentos. Corte: `arvore-envio` e `--do-pr` (o envio reaproveita o PR) saem para uma branch própria, depois deste. O #929 fica com a mudança "do PR para o diário", com `teto: excedido, <n> linhas, <motivo>` no corpo (detalhe no Parecer).
- A6 (recomendado) tests/test_ci_local.py:584 · O comentário cita "validação do plugin e portão das provas", mas a instalação do portão das provas saiu. As duas que ficam são a do e2e no 3.14 e a da validação do plugin.
- A7 (recomendado) scripts/arvore-testada.py:34 · A entrada "3.14" de JOBS_DE_PROVA fica morta: nenhum job da develop tem mais esse nome, e ninguém chama `--python 3.14`. Tire a entrada junto com o teste que a cita.
- A8 (recomendado) tests/test_arvore_testada.py:267 · O teste com subprocesso chama o Python sem `-I` (V2: o subprocesso roda com o ambiente limpo e `-I`).
- A9 (recomendado) tests/mutantes/v0481-f6-ci-uma-vez.json:1 · A spec tem 10 mutantes. Acima de 8, abra um `-2.json` (V2).
- A10 (recomendado) .github/workflows/diario.yml:91 · As fatias vão de 128 a 957 mutantes por dia (v047 tem 640 sozinho), com `--processos 2` e teto de 60 min. Meça a primeira execução por `workflow_dispatch` antes de confiar no teto.

## Sondas
- S1 · `bin/forge-mutante tests/mutantes/v0481-f6-ci-uma-vez.json tests/mutantes/v0481-fechar-dryrun-branch.json --processos 2` (par da fatia) · espera: os mutantes rodam · obtido: `spec inválida; nada foi executado. id de mutante repetido entre as specs: M1, M2, M3, M4, M5`, rc=2
- S2 · `python3 -m unittest tests.test_forge_mutante.ConferirTodas.test_toda_spec_do_forge_confere_com_a_fonte_fora_as_pendentes` no head · espera: ok · obtido: FAILED, `First list contains 11 additional elements` (est-m7-verificador-decisao.json: M3...)
- S3 · `python3 bin/forge-mutante --conferir --todas` no head e na base 6edd59d2 · espera: só as pendentes · obtido: 37 no head e 26 na base, 11 novas

## Parecer
**Reprovado.** O desenho está certo, mas há quatro defeitos provados e um corte pelo H1.

**CI (G3):** não há linha `ci:`. O head não tem run do `ci.yml` (A1): `gh pr checks 929` traz só `catraca pass`. Sem `bateria` e `bateria (python 3.14)`, não dá para aprovar, nem para medir a meta de 8 min. A `catraca` passou no run 45925050166, com dois "confira no parecer" de valor esperado trocado:
- `test_toda_instalacao_global_do_cli...`: 3 para 2. Confere, o e2e saiu das verificações; só o comentário está errado (A6).
- `test_cada_perna_roda_uma_vez_e_a_igual_reaproveita`: as pernas do 3.14 sumiram. Confere com o pedido.

O rótulo `afrouxa-regra` está no PR. A decisão do dono de 2026-11-26 19:37 manda tirar do PR a suíte do 3.14.

**O que confere na leitura:**
- `prova_do_pr` está correta e fecha na dúvida. O head descende da develop anterior, então o merge testado no PR tem a árvore do head. O merge por rebase cai em `diverged` e a suíte roda inteira.
- O token fica só no passo.
- Os nomes dos checks exigidos não mudam.
- Os 12 casos de `ProvaDoPr` cobrem cada condição.
- Os `needs` batem com as referências de cada job; a conferência foi por script.

**Corte (A5, decidido aqui):**
- O `arvore-envio` e o `--do-pr` são separáveis: cerca de 100 linhas, com teste e mutantes próprios. Vão para outra branch, aberta quando o teto de PRs der vaga. O mesmo autor faz as duas partes em sequência (diretriz 33).
- Fica no #929 a troca do 3.14 junto com o `diario.yml`. Separar as duas tira a suíte do 3.14 de todo lugar. A remoção das pernas também não cabe num pedaço menor: um `needs` órfão invalida o workflow, a mesma falha do A1.
- Registre no corpo do PR `teto: excedido, <n> linhas, a troca do 3.14 e o diário não se separam sem deixar o 3.14 sem suíte nem o workflow sem needs válidos`.
- Com o `arvore-envio` fora, o A2 encolhe: as specs da est-m7 deixam de envelhecer. As do `ci.yml` continuam a ser alinhadas aqui.

**Volta:** corrija o A1 primeiro, porque sem ele nenhum check roda. Antes do envio, rode `bin/forge-mutante --conferir --todas` e o teste da S2. A próxima rodada lê o delta e o CI verde no head novo.

**AR-12:** a classe volta neste pedido (A2). A linha `AR-12` de docs/engineering/achados-recorrentes.md sobe para 6, mas o brief limita o commit ao parecer. Fica para quem fecha a volta.
