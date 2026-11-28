---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-pv-b1-registros
commit: f7baaa533910b7af1777ad406f7bc940f8df669c
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-20
---
# QA: v0478 E57.2 (PR-VERDE B1, `forge-testes --registros`)

Pedido de controle (`bin/`): diff de `5ccac0bf` a `1aed3a74` em `bin/forge-testes`, `tests/test_testes_tocados.py`, duas specs de mutante e o fragmento de changelog. Sem especificação de UX (sem `CA-n`): as obrigações são as da decisão do dono de 20/11 no pedido (E57.2), citadas no cabeçalho do código: conferência só de leitura, os mesmos testes do CI (sem cópia da regra), saída 0/1/2, peso de módulo novo, busca da `origin/<ramo>`. Suíte inteira: só no CI do PR (`R-QA`); aqui rodei só o módulo tocado.

## Critério → teste → resultado
| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Em dia sai 0, sem gravar na árvore e sem `GIT_*`/`FORGE_*` herdado (AR-4) | `Registros.test_em_dia_sai_0_sem_gravar_nada_e_sem_o_ambiente_herdado` | árvore limpa com `--ignored` | passou |
| Grupo do CI vermelho sai 1 com o nome do registro | `Registros.test_grupo_do_ci_vermelho_sai_1_com_o_nome_do_registro` (subTest por grupo) | os 8 grupos de `REGISTROS` | passou |
| Changelog reprovado sai 1 | `Registros.test_changelog_reprovado_sai_1` | n/a | passou |
| Módulo de teste novo sem peso sai 1 (não versionado e commitado); com peso, 0 | `Registros.test_modulo_de_teste_novo_sem_peso_sai_1_e_com_peso_sai_0` | peso ausente x presente | passou |
| Módulo antigo sem peso não é do PR | `Registros.test_modulo_antigo_sem_peso_nao_e_do_pr` | pesos `{}` | passou |
| Pesos ilegíveis (`[]`, `{`) ou base que não resolve: sem veredito, saída 2 | `Registros.test_pesos_ilegiveis_ou_base_que_nao_resolve_saem_2` | JSON inválido, não objeto, base inexistente | passou |
| Busca a `origin/<ramo>` antes; sem rede avisa e confere a local | `Registros.test_busca_a_origin_antes_e_sem_rede_avisa_e_confere_a_local` | remoto removido | passou |
| A busca usa o `GIT_CONFIG_*` da sessão (proxy e credencial) | `Registros.test_a_busca_usa_o_git_config_da_sessao` | n/a | passou |
| `--registros` só combina com `--base` | `Registros.test_registros_so_combina_com_base` | 9 opções incompatíveis | passou |
| Todo nome de `REGISTROS` existe (suíte vazia / teste renomeado) | `Registros.test_todo_registro_do_forge_e_um_teste_que_existe` | mínimo de 8 grupos | passou |

## Cenários e resultado real
- `python3 -I -m unittest discover -s tests -p test_testes_tocados.py -k Registros -v`: `Ran 10 tests in 32.381s · OK`, rc=0.
- Vermelho antes do verde (`bin/forge-testes --vermelho 5ccac0bf616cea83f070d6a2408285c0f5a02933 --modulos test_testes_tocados`, rc=0):
  `vermelho: base=5ccac0bf616c head=1aed3a743d43 módulos=test_testes_tocados (restrito por --modulos)`; os 10 testes de `Registros` saem `H=ok · B=erro · prova (API ausente)`; contagem: não prova (passa na base)=163; prova (API ausente)=10; pulado=1 (os 163 são testes pré-existentes, neutros).
- Mutação (`bin/forge-mutante tests/mutantes/v0478-pv-b1-registros.json tests/mutantes/v0478-pv-b1-registros-2.json`, rc=0, `rev=1aed3a743d43`): R1 a R11 todos `morreu` (R1 `bin/forge-testes:916`, R2 `:922`, R3 `:943`, R4 `:934`, R5 `:936`, R6 `:947`, R7 `:963`, R8 `:950`, R9 `:1012`, R10 `:1046`, R11 `:956`); nenhum sobrevivente, nenhum equivalente.
- Cobertura de mutantes contra o diff (`bin/forge-mutante --cobertura --base 5ccac0bf616cea83f070d6a2408285c0f5a02933`, rc=0): as 9 condições Python mudadas (linhas 916, 922, 934, 936, 943, 956, 963, 1012, 1046) têm mutante declarado; nenhuma `não coberta`. R6 e R8 guardam linhas sem condição nova na lista (excedente aceito).
- Fumaça real na árvore do clone (`bin/forge-testes --registros --base origin/develop`): `forge-testes: registros rc=0 em 39 s (9 conferências e o peso dos módulos de teste novos)`; `git status --short` vazio depois (só leitura confirmada). Dentro dos "segundos" do desenho em máquina carregada por outras rodadas; o CI confere o limite.
- Bordas lidas no diff sem teste próprio, aceitas: timeout da busca (60 s, mesmo ramo de aviso que a falha); `base` sem `origin/` não busca (coberto indiretamente pelos testes com `develop`).
- Sem acessibilidade nem E2E (ferramenta de linha de comando).

## Prova de execução do CI
Não há check-run `bateria` citado: o brief manda parecer sem suíte local e o PR não foi aberto neste head; a bateria do PR é a prova da suíte inteira.

## Revalidação no head f7baaa53 (delta de 1aed3a74)
`forge-check parecer delta` listou 4 arquivos do domínio: `bin/forge-testes` (constante `RAMO_BUSCAVEL`, recusa do ramo inválido antes do `git fetch`, `--end-of-options`), o fragmento de changelog, a spec de mutantes `-2` (R12 a R15) e `tests/test_testes_tocados.py` (1 teste novo, abuso da segurança A1/E57.19).

| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Ramo de `--base` que seria opção (`--upload-pack=...`, `-x`), refspec (`+x:refs/heads/y`) ou `..` é recusado antes do fetch, com aviso e saída 2; nada executa, nada é gravado | `Registros.test_ramo_que_seria_opcao_ou_refspec_e_recusado_sem_buscar` (4 subTests) | início com `-`, caractere fora de `[A-Za-z0-9._/-]`, `..` | passou |

- Teste novo, local: `python3 -I -m unittest discover -s tests -p test_testes_tocados.py -k test_ramo_que_seria`: `Ran 1 test · OK`.
- Vermelho antes do verde (`bin/forge-testes --vermelho 1aed3a743d433c903454422acad73859c12b67b9 --modulos test_testes_tocados`, rc=0): `vermelho: base=1aed3a743d43 head=f7baaa533910 módulos=test_testes_tocados (restrito por --modulos)`; `Registros.test_ramo_que_seria_opcao_ou_refspec_e_recusado_sem_buscar · H=ok · B=falha · prova (asserção)`; `contagem: não prova (passa na base)=173; prova (asserção)=1; pulado=1`.
- Mutação do delta (`bin/forge-mutante --base 1aed3a743d433c903454422acad73859c12b67b9 tests/mutantes/v0478-pv-b1-registros.json tests/mutantes/v0478-pv-b1-registros-2.json`, rc=0, `base=1aed3a743d43… rev=f7baaa533910`): R1 a R15 todos `morreu`; R12 a R15 em `bin/forge-testes:920`, um por condição da guarda. Nenhum sobrevivente.
- Cobertura contra o diff inteiro (`--cobertura --base 5ccac0bf`): ver saída da rodada; sem condição Python mudada sem mutante.
- A troca por `--end-of-options` é argumento, não condição: sem mutante próprio; a recusa antes do fetch já impede opção (defesa em profundidade).
- Processo: uma primeira rodada com `TMPDIR` inexistente sujou a árvore e as ferramentas a descartaram, como projetado; refeita com o `TMPDIR` da sessão.
- Suíte inteira: só no CI do PR; sem check-run `bateria` neste head (PR não aberto), conforme o brief.
