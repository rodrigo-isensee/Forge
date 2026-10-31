---
tipo: review
contrato: 1
pedido: promover-auto
branch: melhoria/promover-auto
commit: 5c31a5fbbe2f0e3cdd36f3ccae05525f46b578d8
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-29
---
# Code review: PROMOVER-AUTO (cartão PROMOVER-SEM-AUTO)

Rodada 1 (pedido PROMOVER-AUTO-REV, E1.1), `R-REVIEW`. Diff lido: `99315cf...5c31a5f`, 3 commits (5c77008 script, testes e doc; 102decb spec de mutantes; 5c31a5f fragmento), 5 arquivos, 142+/22-.

## Ferramentas (citadas, não refeitas à mão)
- `python3 -m unittest tests.test_promover_homolog` em 5c31a5f: `Ran 29 tests ... OK`.
- `bin/forge-mutante tests/mutantes/promover-auto.json`: M1 a M6 `morreu` (6/6), rc 0.
- `bin/forge-mutante --cobertura --base 99315cf`: as guardas novas (`:192`, `:196`, `:244`) aparecem `coberta`; rc 1 só pelas três linhas `apagada` da base (`:189`, `:192`, `:240`), que são o parser antigo por tabulação, substituído pelo JSON, e a guarda "no checks reported", que não sumiu: mudou para `:244` e é coberta por M5 e M6. Remoção justificada, sem achado.
- `bin/forge-testes --listar`: pede a suíte completa (`scripts/promover-homolog.py sem mapa`); fica com o QA e o CI do PR (decisão M8), não refeita aqui.
- Teto M14: 88 linhas que contam (`scripts/promover-homolog.py` 35, `tests/test_promover_homolog.py` 53; spec em `tests/mutantes/`, fragmento e `.md` fora). Um comportamento só. Dentro do teto.
- Segurança e devops: o diff não toca pipeline, workflow, hook nem segredo; sem parecer próprio pedido. A mudança aperta o controle (lê menos checks como verdes), não afrouxa.

## O que o brief pediu conferir
1. **Leitura só do evento pull_request** (`scripts/promover-homolog.py:187-200`): `gh pr checks <PR> --json name,bucket,event,link` e descarte de todo item cujo `event` não seja `pull_request`. Conferi contra o `gh` real (2.103.0): `gh pr checks 345 --json name,bucket,event,link` devolve a lista com `event: pull_request` e o campo `event` consta em `JSON FIELDS` do `--help`. Os dois workflows que geram os checks lidos (`ci.yml`, `catraca.yml`) disparam em `pull_request`, então a catraca e a bateria continuam contadas. O caso da promoção #371 (só checks do `push` da `develop` no mesmo sha) cai em "nenhum check do evento pull_request", sai com 0, imprime o merge com `--auto` e não diz "checks verdes" (`test_so_checks_do_push_nao_sao_verdes_e_o_merge_sai_com_auto`, M1). Check do push não decide nem o vermelho nem o verde (`test_check_do_push_nao_decide_o_vermelho_nem_o_verde`).
2. **Saída que não é lista para com erro** (`:192` e `:244`): texto por tabulação e objeto JSON param com "não consegui ler os checks", rc 1, sem merge impresso (M4, M5). A mensagem do `gh` real sem checks (`no checks reported`, que sai no stderr com rc 1 e entra em `saida` por `ler`) segue como "sem check ainda" (M6). Ressalva da saída vazia em A2.
3. **`--auto` em todos os caminhos:** `comando_merge` (`:218`) é a única fonte do comando, e os três caminhos que saem com 0 (sem check, pendente, verde) o imprimem; vermelho (rc 1) e catraca pedindo rótulo (rc 3) não imprimem merge. O `--auto` já existia na base (histórico do pedido); o teste novo e M2 o fixam.
4. **Texto do dry-run** (`:222`): "pendente sai com 0", igual ao código (`:249-253` e o caminho de pendente); o "sai com 3" antigo estava errado e foi corrigido.
5. **`docs/promocao-integrador.md`:** passos 5 e 7 e a data de revisão atualizados, coerentes com o código e com a docstring (`:13-14`). Sem outro texto com o limite antigo no repositório (`grep` de "pendente sai com" e de `pr checks` em `agents`, `skills`, `docs/regras`, `scripts`, `bin`).

## Checklist (leitura)
- Faz o que o cartão pede, nem mais nem menos; legível; sem código morto (o `cod` devolvido por `ler` em `ler_checks` já era ignorado antes).
- Fragmento `changelog.d/promover-auto.md` presente, `### Corrigido`; `R-NEUTRO` e `R-CUSTO` preservados (nada pago, nada específico de projeto).
- Commits em Conventional Commits em português, um por item, cada um citando o cartão.
- Falso do `gh` (checklist 12): o teste novo confere o argumento exato (`pr checks 9 --json name,bucket,event,link`), não prefixo. Ressalva de fidelidade em A1.
- Classe de achados recorrentes (PA-7) conferida: AR-9 (limite antigo no texto) foi exatamente o que o item 4 corrigiu, e não sobra ocorrência; sem linha AR nova nesta rodada (DECISÃO TÉCNICA 2026-10-29 15:28 do T1-CONF-ESCOPO-REV); classe dos recomendados abaixo: falso de ferramenta mais frouxo que o real (A1) e texto que promete mais que o código (A2, vizinha de AR-9).

## Achados
- A1 (recomendado) tests/test_promover_homolog.py:25 · o falso do gh devolve "no checks reported" no stdout com rc 0; o gh real o põe no stderr com rc 1. Sugestão: um caso do falso com rc 1 e stderr, para fixar que `ler` junta o stderr nesse caminho.
- A2 (recomendado) scripts/promover-homolog.py:244 · saída vazia não é lista JSON e não para (segue como sem check, rc 0, com --auto), mas o passo 5 do doc diz que saída que não seja lista para. Sugestão: dizer no doc que a vazia conta como sem check, ou parar nela.

## Parecer
Aprovado. A correção real do cartão (a leitura só do evento `pull_request`) está certa, conferida contra o `gh` real e coberta por teste e por mutante (6/6). Os dois achados são recomendações, não devolvem: A1 é fidelidade do falso, sem defeito no script (o `ler` já trata o stderr); A2 não tem gatilho real, porque o `gh pr checks --json` devolve lista ou erro, e o caminho vazio cai no lado seguro (sem "checks verdes", merge automático que espera os checks exigidos).
