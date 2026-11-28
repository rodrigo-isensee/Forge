# Índice do Forge

<!-- Gerado por scripts/indice-forge.py; não edite à mão. Rode o script depois de criar, apagar ou mudar a primeira linha da doc de um arquivo de bin/, hooks/ ou scripts/. -->

Os arquivos versionados de `bin/`, `hooks/` e `scripts/` e o que cada um faz (a primeira linha da doc). Os testes de um arquivo: `bin/forge-testes --listar <arquivo>`.

## `bin/`

| Arquivo | O que faz |
| --- | --- |
| `forge` | despachante de subcomandos. `forge <sub> [args]` executa `bin/forge-<sub>`. |
| `forge-adotar` | traz um projeto que já existe para o Forge, sem quebrar nada (ADR 0015, item 4; fase E, L46). |
| `forge-atualizar` | atualiza o Forge do projeto com ponto de retorno (primeiro uso, F5). Rode no terminal, dentro do projeto. |
| `forge-changelog` | changelog por fragmentos (ADR 0006), para PRs paralelos não conflitarem no CHANGELOG.md. Só biblioteca padrão. |
| `forge-check` | valida o contrato entre agentes (ADR 0004). Só biblioteca padrão; não executa nada dos documentos. |
| `forge-contador` | linha do contador da versão e visão do backlog para o aviso de marco. Só leitura, sem rede; erro sai com 2. |
| `forge-copia` | cria a cópia de trabalho (clone ou worktree) SÓ na pasta liberada do sandbox (~/.forge-contrib; num projeto, <projeto>/.forge/wt). |
| `forge-cota-ci` | aviso de minutos do Actions perto do fim (R-CUSTO). Só leitura, sem custo, só biblioteca padrão. |
| `forge-desfazer` | volta ao último ponto bom, sem apagar histórico. Rode no terminal, dentro do projeto. |
| `forge-doutor` | doutor, o diagnóstico do projeto em linguagem simples (primeiro uso, F3). Rode no terminal, dentro do projeto. |
| `forge-fechar` | fecha uma entrega na branch de integração com os passos mecânicos do integrador (TA-5, R-FLUXO, R-CONTRIB). |
| `forge-init` | prepara um projeto para ser desenvolvido pela fábrica. |
| `forge-mutante` | mutantes declarados do pedido (OK-14 e M-1). Só biblioteca padrão. |
| `forge-novo-projeto` | cria um projeto novo e abre o Jarvis nele. Rode no terminal, antes do Claude (use: forge novo-projeto). |
| `forge-pesado` | quem tem a vez da bateria pesada e a espera pela vez com teto (M12, R-TETO). Só biblioteca padrão. |
| `forge-placar` | placar de qualidade do processo e portão de evolução (0.43.1, frente I). Só leitura, sem rede, biblioteca padrão. |
| `forge-ritmo` | ritmo do time no projeto (0.45.7, E3). Rode no terminal, dentro do projeto. Só biblioteca padrão. |
| `forge-salvar` | salva o trabalho (commit e envio ao GitHub) na branch de trabalho. Rode no terminal, dentro do projeto. |
| `forge-sempre-atual` | mantém o plugin na última versão publicada (FORGE-SEMPRE-ATUAL, ADR 0017). Só biblioteca padrão. |
| `forge-status` | uma linha por pedido em curso, para a statusLine do Claude Code (S3, 0.44.1). Só biblioteca padrão. |
| `forge-sugerir` | sugestão de melhoria ao Forge, sem dados do projeto (primeiro uso, F6). Rode no terminal, dentro do projeto. |
| `forge-testes` | teste dirigido durante a iteração do autor (TA-3). Só biblioteca padrão. |
| `forge-upgrade` | traz um projeto para a versão atual do plugin (ADR 0005). Rode NO projeto, quando quiser. |
| `forge-voltar-versao` | volta para a versão do Forge de antes da última atualização (primeiro uso, F5). Rode no terminal, dentro do projeto. |
| `forge_apoio_testes.py` | o que `bin/forge-testes` e `bin/forge-mutante` têm em comum: a linha de contexto do log (MAQ-A7), com as outras |
| `forge_autorizacao.py` | as autorizações do dono gravadas (ADR 0018, G1.1: formato, integridade e estado; G1.2: gravar). Só biblioteca padrão. |
| `forge_comparar.py` | `forge-check comparar <base> <head>` (AE7.1, v0478 E58.30): o "só aperta" medido nos hooks da base e do head. |
| `forge_controle.py` | salva a pasta de controle (quadro, pedidos, briefs, retros, pareceres) num commit local (AE3.1, v0478 E108.1). |
| `forge_corrigidos.py` | `forge-check corrigidos` e `forge-check afrouxamentos` (M14b; FILA-31 F6, 0.45.7 E5.3): os PRs `fix` que corrigem PR já |
| `forge_decisor.py` | decisão óbvia por regra fixa (orkastery 3, 0.44.2). Só biblioteca padrão. |
| `forge_disco.py` | o uso do disco e o limiar único da cópia de trabalho (MP6, v0474 E3.251). |
| `forge_dono.py` | a conversa com o dono e entre sessões, gravada no disco (0.44.1). Só biblioteca padrão. |
| `forge_dora.py` | DORA e vazão (0.45.7, TM-16): `forge-check dora`, só leitura, sem rede, só biblioteca padrão. |
| `forge_estado.py` | `forge-check status` (S1a, v0481 E20.1): o estado da fábrica lido na hora, para o Jarvis nunca afirmar estado de memória. |
| `forge_fontes.py` | `forge-check fontes` (FILA-31 F6, 0.45.7 E5.1): compara o commit mais recente de cada fonte do registro local |
| `forge_git.py` | ponto único do git de controle (GIT-CONTROLE-CONFIG-DA-COPIA, anexo E3.1, 3.1). Só biblioteca padrão. |
| `forge_governanca.py` | as medidas de governança do processo (0.43.1, frente H): `forge-check metricas` e `forge-check regras`. |
| `forge_medidas.py` | `forge-check medida` (D12, E3a e E3b) e `forge-check escape registrar\|resumo` (M14b) (FILA-31 F6, 0.45.7 E5.5): a medida de um |
| `forge_meta.py` | arma o objetivo que o hook de Stop (hooks/meta.py) confere (S4, 0.44.2). Só biblioteca padrão. |
| `forge_onde.py` | `forge-check onde <alvo>` (AE1.1, v0478 E58.1): onde está uma versão, um PR, um commit, uma branch ou um cartão, lido |
| `forge_pareceres.py` | G2.1 (pedido v0481, ADR 0019): a escrita do parecer de portão como comentário do PR e status do commit, pelo `gh` da sessão |
| `forge_pronto.py` | `forge-check pronto`, o portão de entrega do autor (D2-PORTAO-ENTREGA-AUTOR, v0481 E11.1; estudo determinístico de 24/11). |
| `forge_provas.py` | o arquivo de provas da branch, gerado do brief pela lista do script que o CI roda (M15 E5a1; FILA-31 F6, 0.45.5). |
| `forge_quarentena.py` | a quarentena de teste instável (BP1 Q1, pedido v0478). Só biblioteca padrão; só leitura. |
| `forge_run.py` | execução capturada como prova (S5, 0.44.2). Só biblioteca padrão. |
| `forge_sempre_atual.py` | FORGE-SEMPRE-ATUAL (v047, diretriz 30, ADR 0017): o núcleo que mantém o plugin do Forge na última versão publicada. |
| `forge_tamanho.py` | os avisos de tamanho do `forge-check pr` e do `brief gerar` (H1-TETO-DE-TAMANHO-POR-ITEM e PEDIDO-TETO-BRIEF, v0474 E2.13). |
| `forge_transcricao.py` | `forge-check transcricao lastro\|vereditos\|decisoes\|avisos` (FILA-31 F6, 0.45.7 E5.2): a linha de base da proteção contra |
| `forge_versoes.py` | o que `forge atualizar`, `forge voltar-versao` e o aviso de versão nova do doutor têm em comum (primeiro uso, F5). |
| `forge_voltas.py` | `forge-check voltas` (T-1, M13) e `forge-check esperas` (M14b) (FILA-31 F6, 0.45.7 E5.4): o vai e volta de cada pedido e |

## `hooks/`

| Arquivo | O que faz |
| --- | --- |
| `_comum.py` | base comum dos hooks do plugin (ADR 0003). |
| `_gh_api.py` | leitura única dos arquivos que o `gh api` envia (GH-API-LEITURA-UNICA, 0.47.8 E3.1). |
| `_json_raso.py` | Teto de aninhamento comum aos leitores de JSON de controle (JSON-PROFUNDO-PY314). |
| `_maquina.py` | estado da máquina (diretriz 35), fora dos repositórios, em PASTA (0700), gravado só pelos hooks. |
| `agentes.py` | teto de agentes, relançamento duplicado (ADR 0003, R-TETO), brief selado do especialista e forma da mensagem ao conferente (R-BRIEF). |
| `ambiente.py` | ambiente (E2.54, ordem do dono) - ao abrir a sessão no container, confere o ambiente e põe as linhas `falta:` no contexto. |
| `conformidade.json` | — |
| `conformidade.py` | conformidade dos agentes por papel (ADR 0009, seções 2, 3, 6 e 7; R-CONFORMIDADE). |
| `decisao.py` | decisao (ANTI-ALUC-F4-HOOK-DECISAO, fatia L28a; v0478 E172.6) - avisa a mensagem ao dono com mais de uma decisão. |
| `doutor.py` | doutor (primeiro uso, F3) - roda as conferências rápidas do `forge doutor` ao abrir a sessão e uma vez por dia. |
| `estado.py` | estado (S1 segunda parte, v0481 E20.11; emenda "estado na pergunta do dono" da ADR 0003) - o estado pela ferramenta. |
| `hooks.json` | — |
| `meta.py` | objetivo armado no Stop (S4) e medida da mensagem ao dono (S6), 0.44.2. Só biblioteca padrão. |
| `ordens.py` | ordens (ORDENS-EM-VIGOR, v0478 E123.1; emenda "ordens em vigor" da ADR 0003) - reinjeta as ordens do dono. |
| `ordens_teto.py` | ordens_teto (RECIBO-CONTADOR-PELO-HOOK, item 4; v0481 E20.11) - recusa gravar as ordens em vigor acima do teto. |
| `parecer.py` | parecer de review e de QA antes de PR e de merge (ADR 0003, R-REVIEW, R-QA). |
| `pesado.py` | tarefa pesada uma de cada vez (ADR 0003, R-TETO). |
| `quadro.py` | quadro válido após edição (ADR 0003, R-WIP). |
| `salvar.py` | salvar (D6-SESSAO-NAO-PERDE, parte a; v0481 E11.2) - ao parar, o trabalho em andamento do agente vira commit na cópia. |
| `vigia.py` | vigia (ADR 0009, seção 8) - detecta o que escapou dos bloqueios e avisa o USUÁRIO, não o modelo. |

## `scripts/`

| Arquivo | O que faz |
| --- | --- |
| `arvore-testada.py` | a árvore deste checkout já passou pela suíte na develop? (EST-M7, decisões do dono 7a e 29). Só biblioteca padrão. |
| `ci-local` | ci-local: roda localmente a bateria do CI sobre um PR e, com --publicar, grava o resultado como commit status `ci-local`. |
| `cobertura.py` | coletor de cobertura por linha (piso de cobertura, versao-048 E3). Só biblioteca padrão. |
| `conferir-promocao.py` | Forge DV-3(b), uso `conferir-promocao.py --ref REF`: a ponta da homolog e da main é merge commit sem conteúdo próprio |
| `conferir-release.py` | Release exige versão nova e changelog fechado (mesma checagem para o PR para a main e para a homolog). |
| `conferir-reversao.py` | confere, antes do review, se cada commit da branch se reverte sozinho (M10). Só biblioteca padrão. |
| `configurar-ambiente-local.sh` | Grava (ou mescla) a chave "env" em .claude/settings.local.json, que o git ignora. |
| `falhas-no-resumo.py` | as falhas de uma parte da suíte no resumo do GitHub e em anotações (v047 E2.270). |
| `gerar-derivados.py` | gerador único dos derivados versionados, rodado pelo autor antes do envio (proposta 1 da auditoria dos testes). |
| `indice-fixtures.py` | índice do corpus de fixtures dos hooks (`tests/hooks/<hook>/<caso>.json`, ADR 0003). Só biblioteca padrão. |
| `indice-forge.py` | índice do Forge (arquivo e o que faz), para o brief citar em vez de colar trechos (H7). |
| `instalar-atalho.sh` | instala os comandos `jarvis`, `jarvis-forge` e `forge` em ~/.local/bin e garante esse diretório no PATH do bash. |
| `jarvis` | abre o Jarvis num projeto, retomando a última conversa, com o chat remoto (claude.ai/code) |
| `jarvis-forge` | abre o Jarvis dentro do repositório ~/Forge (onde se edita), usando como plugin uma CÓPIA VIGENTE do Forge |
| `pesos-do-ci.py` | refaz `tests/pesos-d4.json` com os tempos por unidade que as pernas do CI gravaram em anotação de check run |
| `placar-mutacao.py` | placar de mutação da release (M-5). Medida, não portão. Só biblioteca padrão. |
| `preparar-estacao.sh` | prepara do zero uma estação WSL (Ubuntu 24.04) para trabalhar com o Forge. Idempotente: |
| `promover-homolog.py` | prepara e confere a promoção develop -> homolog (D5b, PA-5; R-FLUXO, R-CONTRIB). Só biblioteca padrão. |
| `publicar-releases-faltantes.sh` | publica as releases do GitHub que faltam entre 0.43.1 e 0.44.2 (versões que foram direto para a main). |
| `reexecutar-provas.py` | Reexecuta as provas `cmd` de um arquivo de provas da branch (R-PROVA, EST-030-L2). |
| `suite-paralela.py` | a suíte inteira (`python3 -m unittest discover -s tests`) dividida em até 4 processos (D4, R-TETO). |
| `suite-partes.py` | uma parte da suíte em paralelo, sobre o mecanismo de `scripts/suite-paralela.py` (D4), sem mudá-lo. |
| `validar-plugin.sh` | Valida o plugin (claude plugin validate --strict) numa cópia limpa em $TMPDIR. |
| `validar-yaml-workflow.py` | valida o YAML dos workflows antes do envio (VALIDAR-YAML-DO-WORKFLOW). Só biblioteca padrão, sem custo (R-CUSTO). |
| `varredura-divida.py` | varredura semanal de dívida técnica; só lê e lista os achados, um por linha, com a sugestão de cartão. |
| `verificar-contribuicao.sh` | Varre o diff da ponta ($2, padrão HEAD) contra origin/develop (ou a base dada em $1) atrás de segredos |
