---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-ambiente-sobrevive
commit: 4ed7cb7d208f4c11686fad22c3ada3a90c1924fd
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-17
---
# QA: v047 AMBIENTE-SOBREVIVE-RECRIACAO (E2.54, parecer E2.91)

Parecer anterior no 68072575 (aprovado, A1 recomendado); este revalida por delta o head 584b2239, base cb45a962. Escopo: `.devcontainer/devcontainer.json`, `scripts/preparar-estacao.sh` (`--verificar`, `container_hooks`, `FORGE_PREPARO_ESSENCIAL`), modelo `templates/projeto/.devcontainer/` e `PrepararEstacao` em `tests/test_forge.py`. Sem PR ainda: não há check-run `bateria` para citar; a suíte inteira fica com o CI do PR.

## Achados
- A1 (recomendado) templates/projeto/.devcontainer/preparar-ambiente.sh:45 · o mutante `: || faltas+=` do link agora morre (M20); fechado, sem pendência. Conferi à mão: 1 falha em 24.
- A2 (recomendado) hooks/ambiente.py:21 · sem mutante e sem `isentas`: linhas 21 (padrão `/workspaces`), 33 (`is_file`, defesa) e 40 (`startswith`, `returncode == 1`) sobrevivem a mutação à mão (`rc in (0,1)` imprime só `ambiente: ok`). São equivalentes; declare-os em `equivalente`/`isentas`.
- A3 (recomendado) tests/test_forge.py:2043 · M23 morre por `CalledProcessError` do helper `git` (chave `core.hooksPath` ausente), não por asserção; a morte é legítima (passa sem o mutante), mas a mensagem some. Ler com `check=False` e `assertEqual` dá falha clara.

## Revalidação a359df54..4ed7cb7d (E2.671: mutantes das guardas restantes do hook)
- Delta no domínio do QA: `tests/mutantes/v047-ambiente-sobrevive-3.json` (M26..M30) e `tests/test_ambiente_hook.py` (+3 testes). `forge-mutante tests/mutantes/v047-ambiente-sobrevive-3.json` -> rc 0: M26 (21), M27 (22), M28 (33), M29 e M30 (40) todos `morreu`. `forge-mutante --cobertura --base 73a0ab81` -> linhas 21, 22, 33, 40 `coberta`; linha 55 `isenta` (ponto de entrada do script: todo teste o roda como processo; motivo aceito); `não coberto:` só de json e shell (limite do tipo). `python3 -m unittest tests.test_ambiente_hook` -> Ran 9 tests, OK. Fecha o A2; veredito mantido: aprovado, sem bugs abertos.

## Revalidação c2b55568..a359df54 (E2.659: índice de fixtures)
- Delta no domínio do QA: só `docs/hooks-fixtures.md` (2793 -> 2796, 3 fixtures `ambiente`: erro, fora, sem). `python3 -I scripts/indice-fixtures.py --conferir` -> `em dia`, rc=0; `python3 -m unittest tests.test_indice_fixtures` -> 7 testes, OK. Sem código nem teste mudado; veredito anterior mantido.

## Revalidação be5bf3ea..c2b55568 (E2.639: junção com a develop 73a0ab81 e testes do hook)
`forge-check parecer delta` lista no domínio: `bin/forge-testes`, 3 fixtures `tests/hooks/ambiente/*.json`, `tests/test_hooks.py`, `tests/test_forge.py`. O resto do diff contra a base é da develop (outros itens). `hooks/ambiente.py`, scripts e devcontainer sem mudança.
- Fixtures e `test_hooks` (E2.628): o `ambiente` entra no conjunto de hooks que só avisam (código 0) e no SessionStart permitido, com `sem-forge-versao` e `erro-interno` presentes; nenhuma asserção afrouxada além do que a emenda da ADR 0003 já prevê. `bin/forge-testes`: mapa ganha `test_ambiente_hook` para `hooks/` (lista unida com a da develop).
- `python3 -I -m unittest discover -s tests -p test_ambiente_hook.py` -> Ran 6 tests, OK. `test_testes_tocados.py` -> Ran 162 tests, OK (skipped=1; skip de ambiente já existente, não meu). `test_hook_destino_opaco.py` -> Ran 4 tests, OK. `test_hooks.py` com `-k ambiente -k fixtures -k SessionStart -k permitidos -k erro_interno` -> Ran 28 tests, OK (skipped=6, skips preexistentes do arquivo). O módulo `test_hooks.py` inteiro rodou (15 min) mas a linha final saiu cortada pelo meu `tail`; fica para o CI do PR (sem PR, sem check-run `bateria`).
- `forge-mutante --processos 3 --base be5bf3ea2fbadf41b490a3e24af6d56bb3a48361` nas specs -1 e -2 -> rc=0, 25 `morreu`, nenhum sobrevivente (M23 segue `(erro)`, aceito em A3); `base=be5bf3ea2fbadf41b490a3e24af6d56bb3a48361 mb=be5bf3ea2fbadf41b490a3e24af6d56bb3a48361 rev=c2b5556888ed272694c3d321244ea734a829c16c`.
- Vermelho antes do verde: sem teste novo do item desde o parecer anterior além das fixtures de hook (que o `test_hooks` exige, caem sem o `ambiente` na lista); `forge-testes --vermelho` não rerrodado (R-TETO, suíte local completa fora da ordem).
- Achados A1..A3 seguem recomendados, sem bloqueio. Sem bug novo (`docs/qa/bugs/` inalterado).

## Revalidação 443bd161..be5bf3ea (head b14da707; junção com a develop)
`forge-check parecer delta` (intervalo 443bd161..b14da707, "sem o que veio da base") lista no domínio só `tests/test_forge.py`: a classe `DocsPareceresPedidoECaminho` entrou pela develop (dd059105, E1.252, PR 616; `git show origin/develop:tests/test_forge.py` a contém), outro item. O b14da707 só difere do be5bf3ea por parecer de review. Código do item (`hooks/ambiente.py`, scripts, devcontainer, `tests/test_ambiente_hook.py`) sem mudança desde o parecer anterior.
- `docs/engineering/achados-recorrentes.md`: sem commit da branch no arquivo desde o 443bd161; a linha AR-4 (`tests/test_ambiente_hook.py:58`) é a da branch, conferida contra origin/develop (só AR-1 e AR-4 diferem, ambos deste item). Sem classe nova.
- `python3 -m unittest tests.test_ambiente_hook` -> Ran 6 tests, OK. Suíte inteira: só no CI do PR (sem PR, sem check-run `bateria`).
- Achados A1..A3 seguem recomendados, sem pendência bloqueante. Sem bug novo.

## Revalidação 584b2239..b5ec13af (E2.569: junção com a develop e conserto do autor)
Mudou no domínio (`forge-check parecer delta`): `scripts/preparar-estacao.sh`, `tests/test_ambiente_hook.py`, `tests/test_forge.py`, `docs/engineering/achados-recorrentes.md`. O 443bd161 (Revisar-sha) e o b5ec13af só diferem por parecer de review.
- `preparar-estacao.sh`: o `gh >= 2.47` (`gh_versao_ok`, `garantir_gh`) vem da develop (outro item); `git diff origin/develop` do arquivo mostra que a junção manteve nele só o que é deste item (impressão digital da chave, `FORGE_APT_*`, `--verificar`, essencial) e que `garantir_gh` o usa, inclusive no modo normal. Conferi à mão: `chave_confere` roda antes de instalar e falha fechada.
- Testes: `gh` falso responde `--version` com 2.104 e fora do registro; `sem_manutencao` nos helpers `git`; mensagem de `TesteEParecerSeparados` tolera o texto da base. Nenhum teste enfraquecido: mesmas asserções de comportamento.
- `nice -n 19 python3 -m unittest tests.test_ambiente_hook tests.test_ambiente_git tests.test_forge.PrepararEstacao tests.test_forge.TesteEParecerSeparados tests.test_forge.RodarUmModuloComIsolamento` -> Ran 56 tests, OK; `shellcheck` dos 2 scripts sem aviso. Suíte inteira: só no CI do PR (sem PR ainda, sem check-run `bateria`).
- `forge-mutante --processos 3 --base 584b2239f8debe47126d1b4fee8a24f6996cab9f` nas specs -1 e -2 (rev=b5ec13af8bb4): `base=584b2239f8debe47126d1b4fee8a24f6996cab9f mb=584b2239f8debe47126d1b4fee8a24f6996cab9f`; M1..M25 todos `morreu`, nenhum sobrevivente (M23 segue `(erro)`, aceito em A3). As linhas de M13, M14, M17..M19, M23 e M24 apontam para as linhas novas do script depois da junção.
- Fora do escopo do QA deste item: a lógica `gh_versao_ok` (versão mínima) é da develop e tem teste e mutante lá; aqui só conferi que os falsos a satisfazem.
- Vermelho antes do verde: sem alteração nos testes novos do item desde o parecer anterior (cópia da base, 11 testes caem); o delta só ajusta falsos. Não rerrodei `forge-testes --vermelho` (ordem do dono de não rodar suíte local completa).
- Os achados A1..A3 anteriores seguem recomendados e sem pendência bloqueante. Sem bug novo: `docs/qa/bugs/` inalterado.

## Critério → teste → resultado
| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| postStartCommand clona a main rasa em diretório temporário (URL do .git/config), não roda o work tree nem ref local, termina em `; true`, sem GH_TOKEN (B2 0.43.1, Forge e modelo) | `test_devcontainer_prepara_sozinho_sem_rodar_o_work_tree` | outros hooks de ciclo de vida ausentes; token literal; `remoteEnv` ausente | passou |
| Hook `ambiente` fala só com falta, só no container, só do script do plugin | `tests.test_ambiente_hook` (6 testes) | fora do container, ambiente ok, timeout: silêncio | passou |
| Chave do apt do gh conferida por impressão digital, falha fechada | `test_chave_do_apt_do_gh_so_e_instalada_com_a_impressao_digital_certa` | chave adulterada: nada instalado | passou |
| Modo essencial dispensa cópia vigente e dev-marketplace | `test_container_essencial_nao_roda_vigente_nem_marketplace` | sem `claude plugin`, sem `~/.local/share/forge` | passou |
| core.hooksPath refeito, idempotente, não troca o de outra ferramenta | `test_container_refaz_hookspath_e_nao_troca_o_de_outra_ferramenta` | 2 rodadas; valor alheio mantido | passou |
| `--verificar` dá o comando exato e não altera nada | `test_verificar_diz_o_comando_exato_do_que_falta_e_nao_altera_nada` | sem login, sem link, sem hooksPath; sem escrita | passou |
| `--verificar` sai 0 com "ambiente: ok" após o preparo | `test_verificar_sai_ok_depois_do_preparo` | saída exata | passou |
| gh ausente manda instalar | `test_verificar_sem_gh_manda_instalar` | PATH sem gh | passou |
| Modelo de projeto: link, hooks, idempotência, `--verificar` | `test_modelo_de_projeto_prepara_link_e_hooks_e_e_idempotente`, `..._verificar_e_sem_login_dizem_o_que_falta`, `..._recusa_opcao_desconhecida` | sem login; opção inválida rc 2 | passou |

## Delta 68072575..584b2239 (voltas E2.108 e E2.128)
Mudou no domínio: devcontainer (Forge e modelo) com clone raso da main e sem GH_TOKEN, chave do apt conferida por impressão digital (2 scripts), `--verificar` com a mensagem de login nova, novo hook SessionStart `hooks/ambiente.py` (+ `hooks.json`, emenda da ADR 0003), `tests/test_ambiente_hook.py`, `PrepararEstacao` ampliado, specs de mutante -1 e -2. O escopo da especificação (E2.54) segue coberto; o hook entra por ordem do dono registrada na ADR.
- `python3 -m unittest tests.test_ambiente_hook tests.test_forge.PrepararEstacao` -> Ran 30 tests, OK; `shellcheck` dos 2 scripts sem aviso.
- `forge-mutante --processos 3 tests/mutantes/v047-ambiente-sobrevive-1.json tests/mutantes/v047-ambiente-sobrevive-2.json` (rev=584b2239f8de) -> 25 mutantes (M1..M25), todos `morreu`, nenhum sobrevivente. M23 saiu `morreu · (erro)`: reproduzi à mão, o teste falha com `CalledProcessError` sob o mutante e passa sem ele; morte real, aceita (A3).
- `forge-mutante --cobertura --base cb45a962` rc 1: sem mutante só as linhas de A2 (equivalentes, conferidas à mão); `não coberto:` de json e shell é limite do tipo de arquivo, e M1..M6 e M13..M25 os cobrem.
- Mutante meu no hook: `return True` em `no_container` (linha 22) cai; os de A2 sobrevivem.
- Vermelho antes do verde: `forge-testes --vermelho` bloqueado pelo R-TETO (fila de outra sessão): sem veredito, não vale. Valem o vermelho do parecer anterior (cópia da base, 11 testes novos caem) e os mutantes acima.
- Não testei: `postStartCommand` real no VS Code, clone e apt com rede (só falsos), `gh auth status` real do hook.

## Cenários e resultado real
- `python3 -m unittest tests.test_forge.PrepararEstacao` -> Ran 19 tests, OK; `shellcheck` dos 2 scripts sem aviso.
- `forge-init --stack python` num repositório novo cria `.devcontainer/devcontainer.json` (`name` substituído, sem `{{`) e `preparar-ambiente.sh` executável.
- Vermelho antes do verde: `forge-testes --vermelho cb45a962` estourou o prazo (máquina carregada, sinal 143): sem veredito, não vale. Prova manual em cópia: scripts e devcontainer da base com os testes do head -> `Ran 19 tests, FAILED (failures=9, errors=4)`; os 11 testes novos ou mudados caem (os 8 antigos seguem verdes).
- Mutação à mão (cópia descartável, 6 mutantes nos scripts alterados): 5 mortos (`!= ".githooks"`, `FORGE_PREPARO_ESSENCIAL = 1`, a checagem de hooksPath no `--verificar`, o `config core.hooksPath` do modelo, a negação do `gh auth status`); 1 sobrevivente (A1).
- Fora do que testei: o `postStartCommand` real no VS Code e o apt/rede do `gh` (cobertos só com falsos, como nos testes anteriores).

## Provas
- PQ-1 `forge-check docs` -> rc=0 (saída vazia, rc=0).
- PQ-2 `git ls-remote origin refs/heads/melhoria/v047-ambiente-sobrevive` igual ao head local após o push do parecer (conferido na entrega).
