---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-devcontainer-sem-gh
commit: a5f6c0f1343dbad87df1f227b647e9c0e8460515
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-26
---
# QA: v0481 E35.9 (DEVCONTAINER-SEM-GH, #926), 1ª rodada completa

Sem especificação de UX: os critérios vêm do brief e da decisão do dono de 22:18 (opção 1), numerados CA-1 a CA-6 abaixo. Código testado: `a5f6c0f1`; os commits seguintes só tocam pareceres (`git diff a5f6c0f1 HEAD` só em docs/reviews e docs/security).

## Verificação
- ci: a5f6c0f1343dbad87df1f227b647e9c0e8460515 verde
- CI lido (check-runs do commit a5f6c0f1): suítes 3.12 e 3.14 (partes 1 a 5), teto de pulados, instalação, passos, verificações longas, `bateria (python 3.14)`, árvore provada e catraca: success. Vermelhos só `bateria` e `bateria (pareceres)`, que esperam os pareceres. O `gh pr checks 926` de hoje mostra o head posterior (47e4a197, só pareceres) com as suítes ainda pendentes.
- Vermelho antes do verde: `bin/forge-testes --vermelho ee05ee84 --modulos test_forge,test_ambiente_recriacao` estourou o prazo (rc=124, o `test_forge` inteiro passa de 10 min), sem veredito. Refeito à mão numa cópia em `$TMPDIR`: código da base (`.devcontainer/devcontainer.json` e `scripts/preparar-estacao.sh` de `ee05ee84`) com os testes do head, `python3 -m unittest tests.test_forge.PrepararEstacao tests.test_ambiente_recriacao.ConfiguracaoDoContainer`: 37 testes, 9 FALHAM na base (`sem_tmux`, `sem_gh`, `sem_a_config_do_gh`, `com_o_link_da_area_ausente`, `poststart_do_forge_exige_a_guarda`, `poststart_..._preparo_falha`, `poststart_..._sem_alcancar_a_main`, `devcontainer_prepara_sozinho_sem_rodar_o_work_tree`, `postStart_roda_o_preparo_de_um_clone_novo_da_main`).
- Verde no head (flock trava-teste-a): os mesmos 37 testes, OK em 3,2 s.
- Mutantes: `bin/forge-mutante --processos 2 tests/mutantes/v0481-devcontainer-sem-gh.json` (spec bda70031...): M1 a M12 morreram, rc=0. Lista conferida contra o diff: as linhas de guarda mudadas (`preparar-estacao.sh` 439, 457, 458, 466 a 469 e o `postStartCommand`, linha 30 do JSON) têm mutante. `--cobertura --base ee05ee84` só diz `não coberto` para os dois arquivos (shell e JSON, que a ferramenta não lê); a conferência foi feita à mão.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| CA-1 postStart clona a main pela URL fixa, sem credencial nem gh | `ConfiguracaoDoContainer.test_postStart_roda_o_preparo_de_um_clone_novo_da_main...`, `test_poststart_roda_so_a_main_do_remoto_nunca_o_ref_local_forjado` | remoto sem credencial; ref local forjado | passou (cai na base) |
| CA-2 nada da cópia de trabalho roda como root | `test_devcontainer_prepara_sozinho_sem_rodar_o_work_tree`, `..._nunca_o_ref_local_forjado` (script do work tree e `origin/main` local forjados não rodam) | script forjado em /workspaces | passou |
| CA-3 main antiga, sem a marca, é recusada | `test_poststart_do_forge_exige_a_guarda_no_script_da_main` (M10) | main sem `FORGE_PREPARO_ESSENCIAL` | passou (cai na base) |
| CA-4 falha do clone ou do preparo sai 1 com `ERRO:`, sem `; true` | `test_poststart_do_forge_sai_1_com_aviso_quando_o_preparo_falha`, `..._sem_alcancar_a_main_sai_1_com_aviso`, `ConfiguracaoDoContainer` (sem `; true` no fim) | remoto inalcançável; preparo com rc 1 | passou (caem na base) |
| CA-5 guardas tmux, ~/.config/gh e link: rc 1 e linha `erro:` | `test_container_sem_tmux...`, `..._sem_a_config_do_gh...`, `..._com_o_link_da_area_ausente...`, `test_container_sem_gh...` (M6, M7, M8) | cada item ausente; `--simular` não roda a conferência (M12) | passou (caem na base) |
| CA-6 caminho feliz: essencial no lugar sai 0 e cria ~/.config/gh | `test_container_cria_config_do_gh_e_sai_0_com_o_essencial_no_lugar` | `~/.config/gh` criado antes do resto (M5) | passou |
| Modelo de projeto não muda | `ConfiguracaoDoContainer` (ramo `templates/`, ainda exige `; true`) | regressão no modelo | passou |

## Cenários e resultado real
- Abuso: o teste roda o `postStartCommand` literal com a URL trocada por um remoto `file://`. O script forjado do work tree não executa e o `gh` falso não é chamado.
- Falha de rede: remoto inexistente sai 1 com `ERRO:`.
- Acessibilidade e E2E de navegador não se aplicam (sem interface). O container real não foi recriado nesta rodada: a prova do comando é por simulação com remoto `file://`.
- Recomendado já registrado pelo review (A3, `mktemp` sem `&&`) vira cartão depois do merge; não repito como achado do QA.
