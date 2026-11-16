---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-ambiente-sobrevive
commit: 680725756d94129c230f52c6401d697463f6e88d
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-15
---
# QA: v047 AMBIENTE-SOBREVIVE-RECRIACAO (E2.54, parecer E2.91)

Código testado 68072575, base cb45a962. Sem parecer anterior: parecer completo. Escopo: `.devcontainer/devcontainer.json`, `scripts/preparar-estacao.sh` (`--verificar`, `container_hooks`, `FORGE_PREPARO_ESSENCIAL`), modelo `templates/projeto/.devcontainer/` e `PrepararEstacao` em `tests/test_forge.py`. Sem PR ainda: não há check-run `bateria` para citar; a suíte inteira fica com o CI do PR.

## Achados
- A1 (recomendado) templates/projeto/.devcontainer/preparar-ambiente.sh:33 · mutante sobrevivente: trocar `link_ok || faltas+=` por `: || faltas+=` no `--verificar` do modelo mantém os 19 testes verdes. Falta afirmar a linha `falta: link ... ausente` no teste de verificação do modelo.

## Critério → teste → resultado
| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| postStartCommand lê a origin/main, não roda o work tree, termina em `; true`, sem segredo, GH_TOKEN só por localEnv (B2 0.43.1, Forge e modelo) | `test_devcontainer_prepara_sozinho_sem_rodar_o_work_tree` | outros hooks de ciclo de vida ausentes; token literal | passou |
| Modo essencial dispensa cópia vigente e dev-marketplace | `test_container_essencial_nao_roda_vigente_nem_marketplace` | sem `claude plugin`, sem `~/.local/share/forge` | passou |
| core.hooksPath refeito, idempotente, não troca o de outra ferramenta | `test_container_refaz_hookspath_e_nao_troca_o_de_outra_ferramenta` | 2 rodadas; valor alheio mantido | passou |
| `--verificar` dá o comando exato e não altera nada | `test_verificar_diz_o_comando_exato_do_que_falta_e_nao_altera_nada` | sem login, sem link, sem hooksPath; sem escrita | passou |
| `--verificar` sai 0 com "ambiente: ok" após o preparo | `test_verificar_sai_ok_depois_do_preparo` | saída exata | passou |
| gh ausente manda instalar | `test_verificar_sem_gh_manda_instalar` | PATH sem gh | passou |
| Modelo de projeto: link, hooks, idempotência, `--verificar` | `test_modelo_de_projeto_prepara_link_e_hooks_e_e_idempotente`, `..._verificar_e_sem_login_dizem_o_que_falta`, `..._recusa_opcao_desconhecida` | sem login; opção inválida rc 2 | passou |

## Cenários e resultado real
- `python3 -m unittest tests.test_forge.PrepararEstacao` -> Ran 19 tests, OK; `shellcheck` dos 2 scripts sem aviso.
- `forge-init --stack python` num repositório novo cria `.devcontainer/devcontainer.json` (`name` substituído, sem `{{`) e `preparar-ambiente.sh` executável.
- Vermelho antes do verde: `forge-testes --vermelho cb45a962` estourou o prazo (máquina carregada, sinal 143): sem veredito, não vale. Prova manual em cópia: scripts e devcontainer da base com os testes do head -> `Ran 19 tests, FAILED (failures=9, errors=4)`; os 11 testes novos ou mudados caem (os 8 antigos seguem verdes).
- Mutação à mão (cópia descartável, 6 mutantes nos scripts alterados): 5 mortos (`!= ".githooks"`, `FORGE_PREPARO_ESSENCIAL = 1`, a checagem de hooksPath no `--verificar`, o `config core.hooksPath` do modelo, a negação do `gh auth status`); 1 sobrevivente (A1).
- Fora do que testei: o `postStartCommand` real no VS Code e o apt/rede do `gh` (cobertos só com falsos, como nos testes anteriores).

## Provas
- PQ-1 `forge-check docs` -> rc=0 (aviso: "versão não conferida (versão 0.47.1 do cache sem prova do código)").
- PQ-2 `git ls-remote origin refs/heads/melhoria/v047-ambiente-sobrevive` -> 680725756d94129c230f52c6401d697463f6e88d (igual ao head testado); o parecer vai num commit seguinte.
