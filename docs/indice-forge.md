# Índice do Forge

<!-- Gerado por scripts/indice-forge.py; não edite à mão. Rode o script depois de mudar bin/, hooks/, scripts/ ou o mapa de testes. -->

Os 77 arquivos versionados de `bin/`, `hooks/` e `scripts/`: o que cada um faz (a primeira linha da doc) e os módulos de `tests/` que o cobrem (o plano dirigido do `bin/forge-testes` para o arquivo, sem os oráculos do portão). A lista inteira de um arquivo: `bin/forge-testes --listar <arquivo>`.

## `bin/`

| Arquivo | O que faz | Testes |
| --- | --- | --- |
| `forge` | despachante de subcomandos. `forge <sub> [args]` executa `bin/forge-<sub>`. | `test_forge`, `test_atualizar`, `test_doutor`, `test_novo_projeto`, `test_salvar_desfazer`, `test_sempre_atual` |
| `forge-adotar` | traz um projeto que já existe para o Forge, sem quebrar nada (ADR 0015, item 4; fase E, L46). | `test_adotar`, `test_forge`, `test_stack_python` |
| `forge-atualizar` | atualiza o Forge do projeto com ponto de retorno (primeiro uso, F5). Rode no terminal, dentro do projeto. | `test_atualizar`, `test_doutor`, `test_forge` |
| `forge-changelog` | changelog por fragmentos (ADR 0006), para PRs paralelos não conflitarem no CHANGELOG.md. Só biblioteca padrão. | `evals.test_erros_por_papel`, `evals.test_regressao_forma`, `test_changelog`, `test_conferir_release`, `test_forge`, `test_pre_push_afetados` |
| `forge-check` | valida o contrato entre agentes (ADR 0004). Só biblioteca padrão; não executa nada dos documentos. | `test_fechar_forge_check_real`, `test_forge_check_base_igual`, `test_forge_check_pr`, `test_forge_check_versao_livre`, `evals.test_erros_por_papel`, `evals.test_regressao_forma` e mais 93 |
| `forge-copia` | cria a cópia de trabalho (clone ou worktree) SÓ dentro da pasta liberada do sandbox (~/.forge-contrib). | `test_forge_copia`, `test_forge` |
| `forge-cota-ci` | aviso de minutos do Actions perto do fim (R-CUSTO). Só leitura, sem custo, só biblioteca padrão. | `test_cota_ci`, `test_forge` |
| `forge-desfazer` | volta ao último ponto bom, sem apagar histórico. Rode no terminal, dentro do projeto. | `test_forge`, `test_salvar_desfazer` |
| `forge-doutor` | doutor, o diagnóstico do projeto em linguagem simples (primeiro uso, F3). Rode no terminal, dentro do projeto. | `test_atualizar`, `test_doutor`, `test_doutor_branch_atrasada`, `test_doutor_custo`, `test_doutor_protecao_gh`, `test_doutor_relogio` e mais 4 |
| `forge-fechar` | fecha uma entrega na branch de integração com os passos mecânicos do integrador (TA-5, R-FLUXO, R-CONTRIB). | `test_forge_fechar`, `test_conf_escopo`, `test_entrega_git_falha`, `test_erros_no_brief`, `test_fechar`, `test_fechar_auto_merge` e mais 29 |
| `forge-init` | prepara um projeto para ser desenvolvido pela fábrica. | `test_adotar`, `test_forge`, `test_modelo_ci`, `test_novo_projeto`, `test_reval_delta`, `test_salvar_desfazer` e mais 1 |
| `forge-mutante` | mutantes declarados do pedido (OK-14 e M-1). Só biblioteca padrão. | `test_forge_mutante`, `test_forge` |
| `forge-novo-projeto` | cria um projeto novo e abre o Jarvis nele. Rode no terminal, antes do Claude (use: forge novo-projeto). | `test_adotar`, `test_forge`, `test_modelo_ci`, `test_novo_projeto`, `test_reval_delta`, `test_salvar_desfazer` e mais 1 |
| `forge-pesado` | quem tem a vez da bateria pesada e a espera pela vez com teto (M12, R-TETO). Só biblioteca padrão. | `test_forge_pesado`, `test_forge` |
| `forge-placar` | placar de qualidade do processo e portão de evolução (0.43.1, frente I). Só leitura, sem rede, biblioteca padrão. | `evals.test_placar`, `test_forge` |
| `forge-ritmo` | ritmo do time no projeto (0.45.7, E3). Rode no terminal, dentro do projeto. Só biblioteca padrão. | `test_forge`, `test_ritmo`, `test_testes_tocados` |
| `forge-salvar` | salva o trabalho (commit e envio ao GitHub) na branch de trabalho. Rode no terminal, dentro do projeto. | `test_forge`, `test_salvar_desfazer` |
| `forge-sempre-atual` | mantém o plugin na última versão publicada (FORGE-SEMPRE-ATUAL, ADR 0017). Só biblioteca padrão. | `test_forge`, `test_sempre_atual` |
| `forge-status` | uma linha por pedido em curso, para a statusLine do Claude Code (S3, 0.44.1). Só biblioteca padrão. | `test_forge_status`, `test_forge`, `test_maquina` |
| `forge-sugerir` | sugestão de melhoria ao Forge, sem dados do projeto (primeiro uso, F6). Rode no terminal, dentro do projeto. | `test_forge`, `test_sugerir` |
| `forge-testes` | teste dirigido durante a iteração do autor (TA-3). Só biblioteca padrão. | suíte completa (bin/forge-testes altera o mapa ou a configuração) |
| `forge-upgrade` | traz um projeto para a versão atual do plugin (ADR 0005). Rode NO projeto, quando quiser. | `test_atualizar`, `test_doutor`, `test_forge`, `test_sempre_atual` |
| `forge-voltar-versao` | volta para a versão do Forge de antes da última atualização (primeiro uso, F5). Rode no terminal, dentro do projeto. | `test_atualizar`, `test_doutor`, `test_forge` |
| `forge_apoio_testes.py` | o que `bin/forge-testes` e `bin/forge-mutante` têm em comum: a linha de contexto do log (MAQ-A7), com as outras | `test_forge`, `test_forge_mutante`, `test_pre_push_afetados`, `test_pre_push_link_apoio`, `test_pre_push_parecer_curto`, `test_testes_tocados` |
| `forge_autorizacao.py` | as autorizações do dono gravadas (ADR 0018, G1.1: formato, integridade e estado). Só biblioteca padrão; só leitura. | `test_autorizacao`, `test_forge` |
| `forge_corrigidos.py` | `forge-check corrigidos` e `forge-check afrouxamentos` (M14b; FILA-31 F6, 0.45.7 E5.3): os PRs `fix` que corrigem PR já | `test_forge`, `test_medidas_m14b` |
| `forge_decisor.py` | decisão óbvia por regra fixa (orkastery 3, 0.44.2). Só biblioteca padrão. | `test_acao_da_reprovacao`, `test_anotar`, `test_aq1_texto`, `test_aq5_parecer_novo`, `test_autorizacao`, `test_brief_forma_aceita` e mais 91 |
| `forge_disco.py` | o uso do disco e o limiar único da cópia de trabalho (MP6, v0474 E3.251). | `evals.test_placar`, `test_forge`, `test_forge_copia` |
| `forge_dono.py` | a conversa com o dono e entre sessões, gravada no disco (0.44.1). Só biblioteca padrão. | `test_forge_dono`, `test_forge` |
| `forge_dora.py` | DORA e vazão (0.45.7, TM-16): `forge-check dora`, só leitura, sem rede, só biblioteca padrão. | `test_forge_dora`, `test_acao_da_reprovacao`, `test_anotar`, `test_aq1_texto`, `test_aq5_parecer_novo`, `test_autorizacao` e mais 91 |
| `forge_fontes.py` | `forge-check fontes` (FILA-31 F6, 0.45.7 E5.1): compara o commit mais recente de cada fonte do registro local | `test_forge`, `test_testes_tocados` |
| `forge_governanca.py` | as medidas de governança do processo (0.43.1, frente H): `forge-check metricas` e `forge-check regras`. | `test_acao_da_reprovacao`, `test_anotar`, `test_aq1_texto`, `test_aq5_parecer_novo`, `test_autorizacao`, `test_brief_forma_aceita` e mais 91 |
| `forge_medidas.py` | `forge-check medida` (D12, E3a e E3b) e `forge-check escape registrar\|resumo` (M14b) (FILA-31 F6, 0.45.7 E5.5): a medida de um | `test_forge_medidas`, `test_forge`, `test_medidas_m14b` |
| `forge_meta.py` | arma o objetivo que o hook de Stop (hooks/meta.py) confere (S4, 0.44.2). Só biblioteca padrão. | `test_acao_da_reprovacao`, `test_anotar`, `test_aq1_texto`, `test_aq5_parecer_novo`, `test_autorizacao`, `test_brief_forma_aceita` e mais 91 |
| `forge_provas.py` | o arquivo de provas da branch, gerado do brief pela lista do script que o CI roda (M15 E5a1; FILA-31 F6, 0.45.5). | `test_acao_da_reprovacao`, `test_anotar`, `test_aq1_texto`, `test_aq5_parecer_novo`, `test_autorizacao`, `test_brief_forma_aceita` e mais 91 |
| `forge_run.py` | execução capturada como prova (S5, 0.44.2). Só biblioteca padrão. | `test_forge_run`, `test_acao_da_reprovacao`, `test_anotar`, `test_aq1_texto`, `test_aq5_parecer_novo`, `test_autorizacao` e mais 91 |
| `forge_sempre_atual.py` | FORGE-SEMPRE-ATUAL (v047, diretriz 30, ADR 0017): o núcleo que mantém o plugin do Forge na última versão publicada. | `test_forge`, `test_sempre_atual` |
| `forge_tamanho.py` | os avisos de tamanho do `forge-check pr` e do `brief gerar` (H1-TETO-DE-TAMANHO-POR-ITEM e PEDIDO-TETO-BRIEF, v0474 E2.13). | `test_forge_tamanho`, `test_forge` |
| `forge_transcricao.py` | `forge-check transcricao lastro\|vereditos\|decisoes\|avisos` (FILA-31 F6, 0.45.7 E5.2): a linha de base da proteção contra | `test_forge`, `test_medidas_m14b` |
| `forge_versoes.py` | o que `forge atualizar`, `forge voltar-versao` e o aviso de versão nova do doutor têm em comum (primeiro uso, F5). | `test_atualizar`, `test_doutor`, `test_forge` |
| `forge_voltas.py` | `forge-check voltas` (T-1, M13) e `forge-check esperas` (M14b) (FILA-31 F6, 0.45.7 E5.4): o vai e volta de cada pedido e | `test_forge`, `test_voltas` |

## `hooks/`

| Arquivo | O que faz | Testes |
| --- | --- | --- |
| `_comum.py` | base comum dos hooks do plugin (ADR 0003). | `test_hook_git_comum`, `evals.test_erros_por_papel`, `evals.test_regressao_forma`, `test_agentes_clone`, `test_agentes_hash_brief`, `test_ambiente_git` e mais 75 |
| `_maquina.py` | estado da máquina (diretriz 35), fora dos repositórios, em PASTA (0700), gravado só pelos hooks. | `test_maquina`, `test_maquina_teto`, `evals.test_erros_por_papel`, `evals.test_regressao_forma`, `test_agentes_clone`, `test_agentes_hash_brief` e mais 74 |
| `agentes.py` | teto de agentes, relançamento duplicado (ADR 0003, R-TETO), brief selado do especialista e forma da mensagem ao conferente (R-BRIEF). | `test_agentes_clone`, `test_agentes_hash_brief`, `test_hooks_agentes_autor`, `evals.test_erros_por_papel`, `evals.test_regressao_forma`, `test_ambiente_git` e mais 74 |
| `ambiente.py` | ambiente (E2.54, ordem do dono) - ao abrir a sessão no container, confere o ambiente e põe as linhas `falta:` no contexto. | `test_ambiente_git`, `test_ambiente_hook`, `evals.test_erros_por_papel`, `evals.test_regressao_forma`, `test_agentes_clone`, `test_agentes_hash_brief` e mais 71 |
| `conformidade.json` | — | `test_conformidade_opaco`, `test_conformidade_verde`, `evals.test_erros_por_papel`, `evals.test_regressao_forma`, `test_agentes_clone`, `test_agentes_hash_brief` e mais 28 |
| `conformidade.py` | conformidade dos agentes por papel (ADR 0009, seções 2, 3, 6 e 7; R-CONFORMIDADE). | `test_conformidade_opaco`, `test_conformidade_verde`, `evals.test_erros_por_papel`, `evals.test_regressao_forma`, `test_agentes_clone`, `test_agentes_hash_brief` e mais 71 |
| `doutor.py` | doutor (primeiro uso, F3) - roda as conferências rápidas do `forge doutor` ao abrir a sessão e uma vez por dia. | `test_doutor`, `test_doutor_branch_atrasada`, `test_doutor_custo`, `test_doutor_protecao_gh`, `test_doutor_relogio`, `test_qa_doutor_034` e mais 51 |
| `hooks.json` | — | `test_hooks`, `test_hooks_parecer_pasta`, `test_hooks_volta_corpus`, `test_hooks_volta_lancador`, `test_hooks_volta_propriedades`, `evals.test_erros_por_papel` e mais 28 |
| `meta.py` | objetivo armado no Stop (S4) e medida da mensagem ao dono (S6), 0.44.2. Só biblioteca padrão. | `test_meta`, `evals.test_erros_por_papel`, `evals.test_regressao_forma`, `test_agentes_clone`, `test_agentes_hash_brief`, `test_ambiente_git` e mais 71 |
| `parecer.py` | parecer de review e de QA antes de PR e de merge (ADR 0003, R-REVIEW, R-QA). | `test_aq5_parecer_novo`, `test_hooks_parecer_pasta`, `test_parecer_conteudo`, `test_parecer_delta`, `evals.test_erros_por_papel`, `evals.test_regressao_forma` e mais 71 |
| `pesado.py` | tarefa pesada uma de cada vez (ADR 0003, R-TETO). | `test_pesado_fila`, `test_pesado_v046`, `evals.test_erros_por_papel`, `evals.test_regressao_forma`, `test_agentes_clone`, `test_agentes_hash_brief` e mais 74 |
| `quadro.py` | quadro válido após edição (ADR 0003, R-WIP). | `evals.test_erros_por_papel`, `evals.test_regressao_forma`, `test_agentes_clone`, `test_agentes_hash_brief`, `test_ambiente_git`, `test_ambiente_hook` e mais 71 |
| `vigia.py` | vigia (ADR 0009, seção 8) - detecta o que escapou dos bloqueios e avisa o USUÁRIO, não o modelo. | `test_vigia`, `evals.test_erros_por_papel`, `evals.test_regressao_forma`, `test_agentes_clone`, `test_agentes_hash_brief`, `test_ambiente_git` e mais 71 |

## `scripts/`

| Arquivo | O que faz | Testes |
| --- | --- | --- |
| `arvore-testada.py` | a árvore deste checkout já passou pela suíte na develop? (EST-M7, decisões do dono 7a e 29). Só biblioteca padrão. | `test_arvore_testada`, `test_forge`, `test_testes_tocados` |
| `ci-local` | ci-local: roda localmente a bateria do CI sobre um PR e, com --publicar, grava o resultado como commit status `ci-local`. | `test_ci_local`, `test_forge`, `test_testes_tocados` |
| `cobertura.py` | coletor de cobertura por linha (piso de cobertura, versao-048 E3). Só biblioteca padrão. | `test_cobertura`, `test_forge`, `test_testes_tocados` |
| `conferir-promocao.py` | Forge DV-3(b), uso `conferir-promocao.py --ref REF`: a ponta da homolog e da main é merge commit sem conteúdo próprio | suíte completa (scripts/conferir-promocao.py sem mapa) |
| `conferir-release.py` | Release exige versão nova e changelog fechado (mesma checagem para o PR para a main e para a homolog). | suíte completa (scripts/conferir-release.py sem mapa) |
| `conferir-reversao.py` | confere, antes do review, se cada commit da branch se reverte sozinho (M10). Só biblioteca padrão. | `test_conferir_reversao`, `test_forge`, `test_testes_tocados` |
| `configurar-ambiente-local.sh` | Grava (ou mescla) a chave "env" em .claude/settings.local.json, que o git ignora. | `test_forge`, `test_pre_push_afetados`, `test_pre_push_leve`, `test_pre_push_segredo`, `test_salvar_desfazer`, `test_sessao_automatica` e mais 1 |
| `falhas-no-resumo.py` | as falhas de uma parte da suíte no resumo do GitHub e em anotações (v047 E2.270). | `test_falhas_no_resumo`, `test_forge`, `test_testes_tocados` |
| `indice-fixtures.py` | índice do corpus de fixtures dos hooks (`tests/hooks/<hook>/<caso>.json`, ADR 0003). Só biblioteca padrão. | `test_indice_fixtures`, `test_forge`, `test_testes_tocados` |
| `indice-forge.py` | índice do Forge (arquivo, o que faz e os testes que o cobrem), para o brief citar em vez de colar trechos (H7). | `test_indice_forge`, `test_forge`, `test_testes_tocados` |
| `instalar-atalho.sh` | instala os comandos `jarvis`, `jarvis-forge` e `forge` em ~/.local/bin e garante esse diretório no PATH do bash. | `test_doutor`, `test_forge`, `test_sempre_atual`, `test_sessao_automatica`, `test_testes_tocados` |
| `jarvis` | abre o Jarvis num projeto, retomando a última conversa, com o chat remoto (claude.ai/code) | `test_doutor`, `test_forge`, `test_sempre_atual`, `test_sessao_automatica`, `test_testes_tocados` |
| `jarvis-forge` | abre o Jarvis dentro do repositório ~/Forge (onde se edita), usando como plugin uma CÓPIA VIGENTE do Forge | `test_doutor`, `test_forge`, `test_sempre_atual`, `test_sessao_automatica`, `test_testes_tocados` |
| `pesos-do-ci.py` | refaz `tests/pesos-d4.json` com os tempos por unidade que as pernas do CI gravaram em anotação de check run | `test_pesos_do_ci`, `test_forge`, `test_testes_tocados` |
| `placar-mutacao.py` | placar de mutação da release (M-5). Medida, não portão. Só biblioteca padrão. | suíte completa (scripts/placar-mutacao.py sem mapa) |
| `preparar-estacao.sh` | prepara do zero uma estação WSL (Ubuntu 24.04) para trabalhar com o Forge. Idempotente: | `test_forge`, `test_pre_push_afetados`, `test_pre_push_leve`, `test_pre_push_segredo`, `test_salvar_desfazer`, `test_sempre_atual` e mais 2 |
| `promover-homolog.py` | prepara e confere a promoção develop -> homolog (D5b, PA-5; R-FLUXO, R-CONTRIB). Só biblioteca padrão. | suíte completa (scripts/promover-homolog.py sem mapa) |
| `publicar-releases-faltantes.sh` | publica as releases do GitHub que faltam entre 0.43.1 e 0.44.2 (versões que foram direto para a main). | suíte completa (scripts/publicar-releases-faltantes.sh sem mapa) |
| `reexecutar-provas.py` | Reexecuta as provas `cmd` de um arquivo de provas da branch (R-PROVA, EST-030-L2). | suíte completa (scripts/reexecutar-provas.py sem mapa) |
| `suite-paralela.py` | a suíte inteira (`python3 -m unittest discover -s tests`) dividida em até 4 processos (D4, R-TETO). | suíte completa (scripts/suite-paralela.py sem mapa) |
| `suite-partes.py` | uma parte da suíte em paralelo, sobre o mecanismo de `scripts/suite-paralela.py` (D4), sem mudá-lo. | suíte completa (scripts/suite-partes.py sem mapa) |
| `validar-plugin.sh` | Valida o plugin (claude plugin validate --strict) numa cópia limpa em $TMPDIR. | `test_forge`, `test_pre_push_afetados`, `test_pre_push_leve`, `test_pre_push_segredo`, `test_salvar_desfazer`, `test_sessao_automatica` e mais 1 |
| `verificar-contribuicao.sh` | Varre o diff da ponta ($2, padrão HEAD) contra origin/develop (ou a base dada em $1) atrás de segredos | `test_forge`, `test_pre_push_afetados`, `test_pre_push_leve`, `test_pre_push_segredo`, `test_salvar_desfazer`, `test_sessao_automatica` e mais 1 |
