---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-ordens-hook
commit: a9187ffe255cf7ba75af7490340d882cc651079b
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-24
---
# QA: hook ordens e laço das fixtures do vigia (v0478 E123.5)

## Critério → teste → resultado
| Critério (E123.1) | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Reinjeta as ordens no UserPromptSubmit e no SessionStart (startup, resume, compact), com linha fixa | `injeta-no-userpromptsubmit`, `sessionstart-compact-injeta`, `test_hooks_json_registra_o_ordens_nos_matchers_da_emenda` | controle (tab, ESC) vira espaço | passou |
| Teto de 15 linhas e 2000 caracteres, com aviso do corte | `teto-linhas-corta-e-avisa`, `teto-caracteres-corta-e-avisa` | limite e logo acima | passou |
| Arquivo ausente ou vazio: silêncio | `arquivo-ausente-silencio`, `vazio-silencio` | ausente, 0 byte | passou |
| Link para fora da raiz: silêncio | `link-para-fora-silencio` | symlink externo | passou |
| Erro interno: sai 0, linha no erros.log | `erro-interno` | exceção em `ler_ordens` | passou |
| Fora de projeto do Forge: silêncio; sessão do Forge lê o contrib | `sem-forge-versao`, `sessao-do-forge-le-o-contrib` | sem `.forge/versao` | passou |
| Só o Jarvis grava o arquivo | `test_so_o_jarvis_escreve_o_arquivo_de_ordens` | permissão | passou |
| Laço das fixtures do vigia aceita decision/reason só no Stop do item 7 | 4 fixtures `time-parado-*` | subagente, `stop_hook_active`, id fora do formato | passou |

## Sondas manuais (hook real, projeto temporário com `.forge/versao`)
- Ausente, vazio (0 byte), 70000 bytes (acima de 64 KiB), link para fora, diretório no lugar do arquivo: silêncio, rc=0.
- 40 linhas: 15 linhas e `ordens cortadas no teto: 40 linhas, 149 caracteres`, rc=0.
- FIFO no lugar do arquivo: não trava (O_NONBLOCK, rejeitado como não regular), rc=0.
- Bytes UTF-8 inválidos: viram U+FFFD, sem erro.
- Erro interno: fixture `erro-interno` (erros.log com `ordens RuntimeError`).

## Execução
- `python3 -I -m unittest discover -s tests -p test_hooks.py -k fixtures_fatia -k ordens -k conformidade_tem`: 19 testes, OK (todas as fixtures de `tests/hooks/ordens` e `tests/hooks/vigia`).
- `tests/test_vigia_parado.py`: 22 testes, OK.
- `bin/forge-mutante tests/mutantes/v0480-ordens-hook.json tests/mutantes/v0480-ordens-hook-2.json`: M1 a M14 `morreu`, nenhum sobrevivente (M2, M5, M12, M13 por erro do teste sob o mutante com o controle verde).
- `bin/forge-mutante --cobertura --base 48d6f4b86`: toda condição mudada de `hooks/ordens.py` coberta por mutante declarado.
- Suíte inteira: no CI do PR, fora deste parecer (sem suíte local, como pede o brief).

## Revalidação do delta (E123.9, head cf679683, base do delta c63e9615)
Delta no domínio (`forge-check parecer delta`): modelo de projeto sem o arquivo de ordens; `hooks/conformidade.py` com o arquivo nas listas `CAMINHOS_DO_CONTROLE` e `CONTROLE_NO_TEXTO`; `hooks/ordens.py` lendo da cópia principal (`fontes`, `diretorio_comum`) e `sem_controle`; 8 fixtures `tests/hooks/conformidade/ordens-*`; `tests/test_hooks.py`; mutantes M15 a M20.

| Mudança do delta | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Escrita do arquivo recusada ao dev e ao security, liberada ao Jarvis (Write, `>>`, ln, mv, rm, variável) | 8 fixtures `ordens-*` da conformidade | permissão por papel; pasta mãe em variável | passou |
| Lê da cópia principal, nunca da worktree | `test_na_worktree_le_so_a_copia_principal` | worktree com arquivo próprio | passou |
| `.git` nu ou que não se resolve cala | `test_worktree_de_repositorio_nu_cala` | repositório nu | passou |
| Pasta `kanban` por link sai da base | `test_no_forge_a_pasta_kanban_por_link_sai_da_base` | link para fora | passou |
| Sequência de controles vira um espaço | `test_sequencia_de_controles_vira_um_espaco_so` | sequência de controle | passou |

## Provas
- `env -i PATH HOME TMPDIR python3 -I -m unittest discover -s tests -p test_hooks.py -k OrdensEmVigor -k test_cada_hook -k ordens`: 22 testes, OK.
- As 8 fixtures `ordens-*` pelo lote do `Hooks.executar_em_lote`: 8 verificadas, OK.
- `bin/forge-mutante --base c63e96158e67cb61056a5552a12ed7a3f7354925` sobre as 3 specs (`base=c63e96158e67cb61056a5552a12ed7a3f7354925 ... rev=cf6796830336`): M1 a M20 `morreu`, nenhum sobrevivente (M15 a M20 em `v0480-ordens-hook-3.json`).
- `bin/forge-mutante --cobertura --base c63e96158e67`: condições mudadas de `hooks/ordens.py` (linhas 40 e 65) cobertas por M17 e M20; as de `hooks/meta.py` pertencem à base e as não cobertas (`.sh`, `pesos-d4.json`) não são do delta.
- Observação: uma rodada com `-k fixtures_fatia` deu 1 falha em 4 testes (497 s, sob carga, em paralelo aos mutantes) e a repetição sozinha deu OK (subtestes de pid pulados pelo ns de pid do sandbox, 550 s). Não reproduzida; a suíte inteira roda no CI do PR (check-run `bateria` do mesmo sha).

## Revalidação do delta (E123.13, head 8e84ef3b, base do delta e34c7466, 2ª volta)
Delta no domínio: pasta própria `docs/ordens/` do Forge (`hooks/ordens.py`), a pasta como pasta em `CAMINHOS_DO_CONTROLE` e `CONTROLE_NO_TEXTO` (A1), guarda pela cópia principal `relativos_a_copia_principal` (A2), `.forge/ordens-em-vigor.md` nos ignorados do `bin/forge-init` (A3), fixtures `ordens-s1` a `s5`, specs de mutantes 3 e 4, `tests/test_hooks.py`, `tests/test_forge.py`.

| Mudança do delta | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Pasta das ordens recusada ao dev (cp, curinga, mover ou remover pasta forjada) | `test_conformidade_recusa_a_pasta_das_ordens_e_a_copia_principal`, fixtures `ordens-s1` a `s3` | permissão por papel; pasta inteira | passou |
| Escrita pela cópia principal a partir da worktree (absoluto, `../`, `>>`) recusada ao dev, liberada ao Jarvis | `test_conformidade_ve_o_arquivo_pela_copia_principal`, fixtures `ordens-s4-*` | worktree para cópia principal | passou |
| Pasta das ordens trocada por link sai da base | `test_no_forge_a_pasta_das_ordens_por_link_sai_da_base` | link para fora | passou |
| Worktree forjada injeta só o dono | fixture `s5-worktree-forjada-injeta-so-o-dono` | worktree com arquivo próprio | passou |
| Arquivo de ordens fora do git | `test_o_arquivo_de_ordens_fica_fora_do_git` | `.gitignore` do projeto | passou |

## Provas (2ª volta)
- `env -i PATH HOME TMPDIR python3 -I -m unittest discover -s tests -p test_hooks.py -k OrdensEmVigor -k test_cada_hook -k ordens -k conformidade_tem`: 24 testes, OK.
- `bin/forge-mutante --base e34c7466e <specs 3 e 4> --processos 3` (`base=e34c7466e61b785683baf48201f20110ce3b2af2 ... rev=8e84ef3b57fa`): M15 a M26 e M28 `morreu`, nenhum sobrevivente (M26 por erro do teste sob o mutante com o controle verde). A spec 4 não tem M27: a sequência salta de M26 para M28, sem efeito no veredito.
- `bin/forge-mutante --cobertura --base e34c7466e`: linhas 1610, 1642 e 1645 de `hooks/conformidade.py` cobertas por M23, M24 e M25; `hooks/conformidade.json` e `bin/forge-init` (shell) saem `não coberto` pela checagem e têm M28 e M26 declarados e mortos.
- Suíte inteira: no CI do PR (check-run `bateria` do mesmo sha), fora deste parecer.

## Revalidação do delta (E123.17, head fe14fb1e, base do delta 8e84ef3b)
Delta no domínio (`forge-check parecer delta`): `bin/forge-init`, `hooks/conformidade.py` e `.json`, `hooks/ordens.py`, 11 fixtures `ordens-a4-*`, 5 `ordens-s4-*` e a `s5` em `tests/hooks`, `tests/test_hooks.py`, `tests/test_forge.py`, mutantes M21 a M31.

| Mudança do delta | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Curinga no nome do arquivo de ordens do projeto recusado (S1 a S3), Jarvis liberado | `test_conformidade_recusa_curinga_no_nome_das_ordens_do_projeto` (11 fixtures `ordens-a4-*`: 2 liberam, 9 bloqueiam) | curinga, classe, absoluto, pasta inteira | passou |
| Cópia principal protegida (S4), worktree forjada injeta só o dono (S5) | fixtures `ordens-s4-*`, `s5-worktree-forjada-injeta-so-o-dono` | permissão por papel, caminho relativo | passou |
| `forge-init` e modelo de projeto | `tests.test_forge.ForgeInit` | n/a | 12 testes, OK |

## Provas (E123.17)
- `python3 -m unittest discover -s tests -p test_hooks.py -k OrdensEmVigor -k ordens` (sem `-I`, da raiz, TMPDIR do sandbox): 24 testes, OK.
- `python3 -m unittest tests.test_forge.ForgeInit`: 12 testes, OK.
- `bin/forge-mutante --base 8e84ef3b57fa6fe7cee56e7b640dfecaba1a8271` sobre `v0480-ordens-hook-4.json` e `-5.json` (`base=8e84ef3b57fa6fe7cee56e7b640dfecaba1a8271 rev=fe14fb1ea179`): M21 a M26 (M26 com o texto novo, `bin/forge-init:222`, por erro do teste sob o mutante com o controle verde), M28 a M31 `morreu`; nenhum sobrevivente.
- Suíte inteira: no CI do PR (check-run `bateria` do mesmo sha), sem suíte local.

## Revalidação do delta (E123.22, head 35211762, base do delta fe14fb1e, sem o merge da develop)
Delta no domínio (`forge-check parecer delta`): `hooks/conformidade.py` (`entrada_valida` sem função por campo, mesmas guardas), `tests/test_hooks.py` (5 casos novos de política malformada), spec U6 (`v0479-conformidade-trilha-7.json`), spec `v0480-ordens-hook-6.json` (M32 a M37), índice. O delta não toca o teto do corpus (`tests/apoio_volta_unica.py` e `tests/test_hooks_volta_corpus.py` sem diff).

| Mudança do delta | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Política com entrada malformada bloqueia (não objeto, caminho vazio ou não texto, motivo vazio, quem com item não texto, so_forge não booleano, branch vazia ou não texto) | `test_politica_de_conformidade_malformada_bloqueia` | vazio, tipo errado por campo | passou |
| U6 com a guarda atual de `CONTROLE_NO_TEXTO` (inclui `ordens`) | `test_fixtures_do_controle_so_jarvis` | pasta mãe e pasta em qualquer posição | passou |
| Corpus do hook abaixo do teto, sem mexer no teto | `test_corpus_nos_dois_hooks` (módulo `test_hooks_volta_corpus`) | teto de trabalho | passou |

## Provas (E123.22)
- `python3 -m unittest tests.test_hooks.Hooks.test_politica_de_conformidade_malformada_bloqueia tests.test_hooks.Hooks.test_fixtures_do_controle_so_jarvis`: 2 testes, OK.
- `python3 -m unittest tests.test_hooks_volta_corpus`: 33 testes, OK (374 s).
- `bin/forge-mutante --base fe14fb1ea179e325195005e2cab46a2bc95d4eaa tests/mutantes/v0480-ordens-hook-6.json --processos 2` (rev=35211762d50a): M32 a M37 `morreu`, nenhum sobrevivente.
- `bin/forge-mutante --base fe14fb1ea179e325195005e2cab46a2bc95d4eaa tests/mutantes/v0479-conformidade-trilha-7.json --processos 2`: U1 a U8 `morreu`, U6 com a guarda atual.
- `bin/forge-mutante --cobertura --base fe14fb1ea179`: linhas 3605 e 3608 de `hooks/conformidade.py` cobertas por M32 a M37; `tests/pesos-d4.json` `não coberto` (dado, não guarda).
- Suíte inteira: no CI do PR (check-run `bateria` do mesmo sha), sem suíte local.

## Revalidação do delta (E140.9, head a6e0d101, base do delta 35211762)
Delta no domínio (`forge-check parecer delta`, sem o que veio da develop): a guarda das ordens saiu de `OrdensEmVigor` para a classe nova `GuardaDasOrdens` (4 testes movidos, `worktree` compartilhado), os mutantes M15 a M26, M28 e M30 a M37 passaram para `v0480-ordens-guarda*.json` (pedido `v0480-ordens-guarda`) e os de `hooks/ordens.py` ficaram em `v0480-ordens-hook*.json`. `hooks/conformidade.py:1612` (`em_qualquer_lugar(posix, c)` antes de ler o disco, vindo do #814) está na árvore e coberto por M23. `hooks/ordens.py` não mudou no delta.

| Mudança do delta | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Guarda das ordens na classe própria, mesmos 4 testes | `GuardaDasOrdens` (recusa na sessão do Forge, pasta e cópia principal, curinga A4, cópia principal pela worktree) | permissão por papel; worktree; repositório nu | passou |
| Leitura do hook de ordens, sem a guarda | `OrdensEmVigor` | ausente, vazio, teto, link, erro interno | passou |
| Guarda lê o disco só se o texto cita a pasta (#814) | `test_conformidade_recusa_a_pasta_das_ordens_e_a_copia_principal`, mutante M23 | destino sem a pasta no texto | passou |

## Provas (E140.9)
- `python3 -m unittest tests.test_hooks.OrdensEmVigor tests.test_hooks.GuardaDasOrdens` (da raiz, sem `-I`): `Ran 24 tests in 5.470s`, OK.
- `bin/forge-mutante tests/mutantes/v0480-ordens-hook.json … -2 … -3 … -4 … -5.json --processos 3` (`pedido=v0480-ordens-hook rev=a6e0d1014e26`): M1 a M14, M17 a M21 e M29 `morreu` (M2, M5, M12, M13 por erro do teste sob o mutante com o controle verde), nenhum sobrevivente; rc=0.
- `bin/forge-mutante tests/mutantes/v0480-ordens-guarda.json tests/mutantes/v0480-ordens-guarda-2.json --processos 3` (`pedido=v0480-ordens-guarda rev=a6e0d1014e26`): M15, M16, M22 a M26, M28, M30 a M37 `morreu` (M26 por erro com o controle verde), nenhum sobrevivente; rc=0. As duas famílias de specs são de pedidos diferentes e saem em chamadas separadas (uma chamada com as sete sai 2, "spec inválida").
- Fixture `pesado/mesma-sessao-libera`: no head, 8 rodadas isoladas pelo `Hooks.executar_em_lote`: 7 OK (0,1 s) e 1 `TimeoutExpired` de 120 s (`hooks/pesado.py`, espera da vez). Na develop (`origin/develop` e694510844, árvore extraída por `git archive`), as mesmas 8 rodadas: 7 OK e 1 `TimeoutExpired` igual. `hooks/pesado.py` e `tests/hooks/pesado` sem diff entre develop e head (`git diff --quiet`). Falha igual na develop, intermitente, fora do delta: causa já registrada em `tests/provas/v0479-testes-prazo.md` (pid do pai lido de outro namespace no sandbox); a bateria do CI é a prova do sha.
- Suíte inteira: no CI do PR (check-run `bateria` do mesmo sha), sem suíte local.

## Revalidação do delta (E140.14, head a9187ffe, base do delta a6e0d101)
Delta no domínio (`forge-check parecer delta`, sem o que veio da develop): `docs/hooks-fixtures.md` (contagem do corpus, 3429 para 3515, e a linha `trava-*`) e `tests/test_hooks.py` (`test_fixtures_do_repo_publico`, vindo do merge da develop). `hooks/ordens.py`, `tests/hooks/ordens`, `tests/hooks/vigia` e as specs `v0480-ordens-hook*.json` sem diff no delta.

| Mudança do delta | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Índice do corpus em dia com as fixtures | `scripts/indice-fixtures.py --conferir` | contagem do corpus | passou |
| Hook de ordens e guarda, sem mudança | `OrdensEmVigor`, `GuardaDasOrdens` | ausente, vazio, teto, link, permissão | passou |
| Lote do repo público (herdado da develop, fora do pedido) | `test_fixtures_do_repo_publico` | os dois lados (0 e 2), prazo | passou |

## Provas (E140.14)
- `python3 scripts/indice-fixtures.py --conferir`: `docs/hooks-fixtures.md: em dia`.
- `python3 -m unittest tests.test_hooks.OrdensEmVigor tests.test_hooks.GuardaDasOrdens`: `Ran 24 tests in 18.289s`, OK.
- `python3 -m unittest tests.test_hooks.Hooks.test_fixtures_do_repo_publico`: `Ran 1 test in 22.812s`, OK.
- `bin/forge-mutante --base a6e0d1014e2643e21e1b261154a1ce9160c87662` sobre as 5 specs `v0480-ordens-hook*.json` (`--processos 3`, rev=a9187ffe255c): rc=0, M13, M14, M17 a M21 e M29 `morreu` no delta, nenhum sobrevivente.
- Suíte inteira: no CI do PR (check-run `bateria` do mesmo sha), sem suíte local.
