---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-d6-resto
commit: 1afd54b5fe5b5a25dd2a96fd490c57469228e9bb
parecer: reprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 1
bugs_medios: 1
bugs_baixos: 0
data: 2026-11-24
---
# QA: v0481 E11.8 (PR #877, hook salvar, volta E11.6; classe C)

Delta lido: `git diff 9a708f86..1afd54b5` (hooks/salvar.py, 8 testes novos, specs de mutantes 5 e 6, ADR 0003, R-LIMITES). Os achados A1 e A2 do parecer anterior estão resolvidos; a volta abriu dois novos: lacuna de varredura de segredo na branch nova (A3) e dois mutantes sobreviventes (A4). **Reprovado.** O merge segue esperando o dono pelos afrouxamentos (ADR 0003 item 2 e R-VERIFY).

## Achados
- A3 (bloqueante) hooks/salvar.py:145 · Branch nova: a varredura de segredo usa `HEAD^` e o push leva os commits anteriores sem varredura. Provado por sonda: `ghp_...` em commit local anterior foi ao remoto (`enviado`). Usar base `origin/develop`, como o pre-push. Bug v0481-salvar-segredo-em-commit-anterior.
- A4 (bloqueante) tests/test_hooks.py:4200 · Mutantes M8 e M9 (escopo exato x prefixo) sobrevivem desde `--untracked-files=no`: `docs/a.md2` é não rastreado e o status não o vê. Rastrear `docs/a.md2` no setUp. Bug v0481-salvar-mutante-escopo-exato.

## Revalidação dos achados anteriores
- A1 (config da cópia): resolvido. `config_permitida` roda antes de qualquer outro git na cópia (`plano`, `or` em curto-circuito), lê `--local --no-includes`, lista positiva por `fullmatch`, origin igual à da principal; `extensions.worktreeConfig` e `include.path` ficam fora da lista. Pontos de abuso que pensei (chave duplicada de `remote.origin.url`, `config.worktree`, `branch.<x>.remote` com URL: o push usa `origin` explícito) não passam ou não importam. Minha sonda do filtro virou `test_config_local_fora_da_lista_nao_age` (subtestes: filter, receivepack, sshCommand, gpg.program, credential.helper, include, pushurl, insteadOf, hooksPath, worktreeConfig).
- A2 (não rastreado, varredura, R-LIMITES): resolvido, salvo o A3 acima. `scripts/verificar-contribuicao.sh` vem do plugin (`Path(__file__)`, fora da cópia), roda com `bash --noprofile --norc` e sem as variáveis de startup do bash; o script, lido inteiro, só chama `git diff --no-ext-diff --no-textconv` (não executa filtro). Julgo correto não usar o da origin/develop: o do plugin é o que o agente não grava; ele existe no cache do plugin. A exceção está em R-LIMITES.md e a ADR pede o destaque no título do PR: o tech-lead confere no PR.
- Prazo: resolvido. `FIM` único de 50 s, `rodar` desconta a cada chamada; `test_prazo_total_dividido_entre_os_comandos` e M38.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Regra 4: config local só da lista | `test_config_local_fora_da_lista_nao_age`, `test_config_so_com_gpgsign_nao_age` | chave fora da lista | passou |
| Regra 4: origin igual à principal | `test_origin_diferente_da_principal_nao_age` | origin trocada | passou |
| Regra 4: XDG e GIT_* ignorados | `test_config_global_de_fora_nao_roda` | config global de fora | passou |
| Regra 2: não rastreado fica fora | `test_nao_rastreado_fica_de_fora` | arquivo novo no escopo | passou |
| Regra 3: segredo não vai | `test_segredo_no_escopo_fica_na_copia`, `test_varredura_vai_da_origin_da_branch` | segredo no escopo, delta da origin | passou; branch nova com commit anterior: falha (A3) |
| Regra 3: prazo de 50 s | `test_prazo_total_dividido_entre_os_comandos` | prazo esgotado | passou |
| Regra 2: escopo exato x prefixo | `test_salva_e_envia_so_o_escopo` | `docs/a.md2` | mutantes sobrevivem (A4) |
| Regras 1, 5 e 6 | os 23 testes anteriores | ver parecer anterior | passaram |

## Execução (clone `/root/.forge-contrib/wt/v0481-d6-resto-qa`, HEAD = `1afd54b5f`)
- `python3 -m unittest tests.test_hooks.SalvarAoParar tests.test_hooks.Hooks.test_hooks_json tests.test_hooks.Hooks.test_cada_hook_tem_caso_que_passa_e_que_bloqueia`: 33 testes, OK. O `tests.test_hooks` inteiro não rodou (passa de 10 min; fica para o CI).
- Vermelho, à mão (cópia em `$TMPDIR`, testes do head com o `hooks/salvar.py` do 9a708f86): `SalvarAoParar` `FAILED (failures=17, errors=1)`; caem os 8 testes novos.
- Mutantes: `bin/forge-mutante --processos 4` das 6 specs, `rev=1afd54b5fe5b`: M1 a M7, M10 a M28 e M30 a M39 `morreu`; M29 `equivalente` (aceito); **M8 e M9 `sobreviveu`** (A4).
- Sonda do A3: repositório bare e clone em `$TMPDIR`, saída no arquivo do bug.
- CI: não li o `bateria` do mesmo sha; o tech-lead confere antes do merge.

## Melhoria vista
Mudança de fixture (rastreado x não) pode desarmar mutante sem aviso; a rodada de `forge-mutante` do autor deveria ser exigida quando o diff muda o `setUp` ou o `status` de um hook com spec de mutantes.
