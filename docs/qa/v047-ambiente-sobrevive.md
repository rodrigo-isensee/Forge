---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-ambiente-sobrevive
commit: 584b2239f8debe47126d1b4fee8a24f6996cab9f
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-15
---
# QA: v047 AMBIENTE-SOBREVIVE-RECRIACAO (E2.54, parecer E2.91)

Parecer anterior no 68072575 (aprovado, A1 recomendado); este revalida por delta o head 584b2239, base cb45a962. Escopo: `.devcontainer/devcontainer.json`, `scripts/preparar-estacao.sh` (`--verificar`, `container_hooks`, `FORGE_PREPARO_ESSENCIAL`), modelo `templates/projeto/.devcontainer/` e `PrepararEstacao` em `tests/test_forge.py`. Sem PR ainda: não há check-run `bateria` para citar; a suíte inteira fica com o CI do PR.

## Achados
- A1 (recomendado) templates/projeto/.devcontainer/preparar-ambiente.sh:45 · o mutante `: || faltas+=` do link agora morre (M20); fechado, sem pendência. Conferi à mão: 1 falha em 24.
- A2 (recomendado) hooks/ambiente.py:21 · sem mutante e sem `isentas`: linhas 21 (padrão `/workspaces`), 33 (`is_file`, defesa) e 40 (`startswith`, `returncode == 1`) sobrevivem a mutação à mão (`rc in (0,1)` imprime só `ambiente: ok`). São equivalentes; declare-os em `equivalente`/`isentas`.
- A3 (recomendado) tests/test_forge.py:2043 · M23 morre por `CalledProcessError` do helper `git` (chave `core.hooksPath` ausente), não por asserção; a morte é legítima (passa sem o mutante), mas a mensagem some. Ler com `check=False` e `assertEqual` dá falha clara.

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
