---
tipo: review
contrato: 1
pedido: lote-unico-032
branch: melhoria/lote-unico-032
commit: 0c90721c86b15d89ea0aec0befa1850b45948698
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-03
---
# Review: lote-unico-032 (review único do experimento do dono, E1.4 / lote-unico-032-REV E1.1)

Intervalo lido: `b2580c6441549e1f1cf4d153ca8db3247cae8cf3...0c90721c86b15d89ea0aec0befa1850b45948698` (52 commits, 76 arquivos, +3377 -173). Referência de cada item: seção 2 de `docs/propostas/lote-unico-032.md` (fora do clone). Os commits de ajuste vão na seção do item deles. Um commit por item conferido no `git log`; o `dd51c0a` (sem Lnn) e o fragmento único `changelog.d/lote-unico-032.md` seguem a DECISÃO TÉCNICA de 2026-11-02 22:15 do pedido.

Dispensados só neste PR pela decisão 3 = A do dono, e por isso fora dos achados: o teto de 150 linhas, um comportamento por PR e uma classe por PR em `hooks/` (o lote não toca `hooks/`).

## Achados
- A1 (bloqueante) bin/forge-check:2036 · L16, defeito provado: custo_do_trecho soma o usage bruto; com o formato real do Claude Code (server_tool_use aninhado) o movimento para "Aguardando o dono" cai em TypeError, rc 1, nada gravado; a base grava. Somar por CAMPOS_USO e testar com o formato real.
- A2 (bloqueante) bin/forge-check:1941 · L18, defeito provado: a fila executa o .githooks/pre-push da raiz com --status; no projeto o hook do modelo não tem --status, roda o pre-push.local e sai 0, e a fila diz trava presa (1.0) sempre. Não executar hook alheio: conferir que é o do Forge ou ler a trava.
- A3 (bloqueante) bin/forge-check:4011 · L13, defeito provado: veredito não cumpriu sustentado por "escopo: Base-sha fora da branch" ou "forma:" conta como contraditório (medir_vereditos deu (1, 1)). A lista de linhas que reprovam precisa cobrir as do conferente.md.
- A4 (bloqueante) bin/forge-check:4665 · L15, defeito provado: sem --pedido, decisoes lê só a raiz e a cópia principal, nunca a raiz de pedidos; no Forge sai total=0, também com --raiz-pedidos (com --pedido lote-unico-032 saem 7). Incluir RAIZES_DE_BRIEF na listagem.
- A5 (bloqueante) bin/forge-check:2656 · L49, defeito provado: voltas sem --pedido pula o pedido sem volta e com ele a linha relogios:; a tabela por release do agile-coach perde os pedidos que andaram sem volta. Histórico sintético: sem --pedido nada, com --pedido a linha sai.
- A6 (bloqueante) tests/test_forge.py:512 · L35, requisito (OK-11): o motivo é por arquivo e o legado cobre 34 arquivos, então trecho novo em arquivo do legado nasce sem regra e porque; a L50 deste lote pôs 5 assim (tests/config.json:330, 364, 482, 503, 510). Exigir motivo por trecho novo.
- A7 (recomendado) bin/forge-check:4688 · L17: o estado da etapa vem de qualquer menção no Histórico; a linha "Próximo: os portões únicos E1.4 ..." pôs E1.4 a E1.7 do lote-unico-032 em "em curso" antes de começarem. Exigir verbo de início ou de entrega na linha.
- A8 (recomendado) bin/forge-check:2026 · L16: cada parada lê todas as transcrições das pastas padrão (2481 arquivos nesta máquina) e o custo total soma só trechos que terminaram em parada, não o ciclo do cartão; dizer isso na skill ou medir o tempo do movimento.
- A9 (recomendado) bin/forge-check:4384 · L10: valor de opção conta como posicional, e `grep -c -m 1 padrao` não avisa; é só aviso, falso negativo.

## Parecer
**Reprovado**, por seis bloqueantes numa passada só (A1 a A6); os outros itens estão aprovados como estão. Quatro dos defeitos são de medida ou leitura (A3, A4, A5) ou de texto de teste (A6), e dois quebram comando em uso real (A1 grava nada no quadro quando há transcrição; A2 dá ocupação falsa em todo projeto e executa o `pre-push.local` dele a partir de um comando de leitura). A2 toca execução de script do repositório por um comando que se declara só de leitura: vira cartão para o `security-engineer` (gatilho `bin-forge-check`), sem refazer aqui o parecer dele.

Classes, sem linha AR nesta rodada (DECISÃO TÉCNICA de 2026-10-29 15:28 do T1-CONF-ESCOPO-REV): A1 é "dado sintético mais frouxo que o real no teste" (o teste do L16 usa `usage` só com inteiros; mesma família do item 12 do checklist, falso mais frouxo que o script); A2 é "comando de leitura que executa código do repositório"; A3 é "lista positiva incompleta de vocabulário do conferente"; A4 é "raiz de pedidos esquecida" (`ler_registro` e `pedido_do_pr` olham `RAIZES_DE_BRIEF`, a listagem não); A5 é "filtro herdado esconde medida nova"; A6 é "granularidade da guarda mais larga que o requisito".

Achados recorrentes (`docs/engineering/achados-recorrentes.md`, PA-7) conferidos contra o diff: AR-4 (ambiente do CI) está tratado em `tests/test_suite_paralela.py` (`GITHUB_ACTIONS` limpo); AR-6 e AR-8 não se aplicam (nenhum shell novo de captura nem `cd` escondido); AR-9 (limite antigo no texto) não reapareceu nos textos do L18 e do L50; AR-1, AR-2, AR-3, AR-5, AR-7 e AR-10 ficam com o QA e a segurança (specs de mutantes e hooks).

## Testes e ferramentas (D-5: só os módulos tocados, carga abaixo de 7, núcleos 8-15)
- `python3 -m unittest tests.test_fechar_rascunho tests.test_fila_ocupacao tests.test_proximo tests.test_decisoes tests.test_voltas tests.test_jarvis_nucleo tests.test_comportamento tests.test_suite_paralela tests.test_etapa_do_brief tests.test_sobreposicao_quadro tests.test_volta_por_delta tests.test_anotar tests.test_clareza tests.test_medidas_m14b tests.test_pedido_fora tests.test_testes_tocados`: `Ran 413 tests in 155.456s` / `OK`.
- `python3 -m unittest tests.test_fechar tests.test_fechar_base_andou tests.test_fechar_sinal tests.test_forge_mutante tests.test_catraca`: `Ran 476 tests in 176.314s` / `OK`.
- `python3 -m unittest tests.test_forge tests.test_hooks_volta_propriedades`: `Ran 491 tests in 189.001s` / `OK`.
- `shellcheck bin/forge-fechar`: rc 0, sem saída.
- A suíte inteira, `scripts/validar-plugin.sh`, os mutantes e a reversão por commit ficam com o QA (D-5). Pipeline: parecer do `devops-engineer` (`docs/devops/`); segurança: parecer do `security-engineer` (`docs/security/`), não refeitos aqui.

Provas dos bloqueantes (sondas em `$TMPDIR/tech-lead-lote-unico-032/`):
- A1: raiz temporária com `KANBAN.md`, um movimento de 30 min atrás e uma transcrição com `"usage":{"input_tokens":2,"output_tokens":5,"server_tool_use":{"web_search_requests":0}}` (formato lido numa transcrição real desta máquina, que traz também `output_tokens_details`); `forge-check movimento k1 --de "Em andamento" --para "Aguardando o dono"` na branch: `TypeError: unsupported operand type(s) for +: 'int' and 'dict'`, rc 1, linha não gravada; o `forge-check` de b2580c6 na mesma raiz: rc 0, linha gravada.
- A2: repositório com o `templates/projeto/.githooks/pre-push` e um `pre-push.local` que grava um arquivo; `forge-check fila </dev/null`: `fila: trava ocupacao=1.0 limite=0.6 (presa, 0 na fila)` e o aviso de não despachar; o arquivo do `pre-push.local` foi gravado.
- A3: `medir_vereditos({'s': [("PQ-1 cumpriu\nescopo: Base-sha fora da branch\nveredito: não cumpriu\n", None)]})` → `{'s': (1, 1)}`; o mesmo com `forma: Arquivo fora do padrão`.
- A4: `forge-check decisoes` → `decisoes: total=0 avisos=0`; `forge-check --raiz-pedidos ~/.forge-contrib decisoes` → `total=0`; `forge-check decisoes --pedido lote-unico-032` → `total=7`.
- A5: histórico com p1 em "Pronto para fazer" → "Em andamento" → "Aguardando sua validação"; `forge-check voltas` → só `voltas: total: pedidos=0`; `forge-check voltas --pedido p1` → `voltas: p1 relogios: aberto_ate_develop=40 pronto_ate_develop=40 meta=30 dentro=nao`.
- A6: `invariantes_sem_motivo` tem `agents/tech-lead.md`, `agents/security-engineer.md`, `agents/qa-engineer.md`, `skills/engineering-practices/SKILL.md` e `skills/cyber-security/SKILL.md`, e os cinco ganharam no L50 o trecho "só o `qa-engineer` roda a suíte inteira" sem `regra` nem `porque`; `test_invariante_traz_regra_e_porque_e_o_legado_so_encolhe` passa.

## Rótulo e título do PR
O PR único muda texto de regra (`docs/regras/R-DECISAO.md`, L11), muda quem roda a suíte inteira (L50) e tira 21 trechos do Jarvis em `tests/config.json` para as skills novas (L51, movidos, nenhum perdido). O título do PR leva o destaque de regra e invariante que mudam, e o PR pede o rótulo `afrouxa-regra` do dono, que a Catraca exige pela remoção de linhas de `tests/config.json`; isso é do integrador (E1.8), não achado deste parecer.

## Por item
### L00 (ADRs 0014, 0015 e emendas da 0003 e 0009) · b08ac8f · aprovado
As duas ADRs e as duas emendas entram como proposta, com critério de reversão, leituras e "Por que o existente não basta"; a 0015 declara que a evidência de execução do fato 5 fica para o QA da fase E (aceitável em proposta). Índice do `docs/adr/README.md` atualizado. Nenhum controle muda por texto.

### L01 (VEL-P6-GATE) · 85f6a9d · aprovado
O gate pula os passos pesados também para `docs/security/`, `docs/devops/` e `docs/ux/`, mantendo a bateria verde no commit anterior e mandando modelos `_*` e `docs/security/{ameacas,aceites}/` para a bateria inteira; `NeutralidadeDoNucleo` entra nos testes leves. Testes em `tests/test_catraca.py` (classe `GateDoCi`) e spec `tests/mutantes/vel-p6-gate.json`. Pipeline: parecer de devops.

### L02 (D-1, rascunho reusado) · 1ad7be9 · aprovado
O passo 3 do `forge-fechar` conta os PRs abertos (mais de um para), lê o `headRefOid` da lista e exige igualdade com o sha conferido no passo 2. O `gh` falso de `tests/test_fechar.py` passou a devolver o head do PR aberto, como o GitHub (sem isso a guarda passaria por falta de valor): confere a mesma regra do script. Três casos em `tests/test_fechar_rascunho.py`; textos de `tech-lead.md`, `jarvis.md` e `docs/fechamento-integrador.md` alinhados.

### L03 (LOTE E5, volta grava Etapa e Cobre) · 3abcb87 · aprovado
`gerar_volta` copia `Etapa:` (ou o `--etapa`) e `Cobre:` do brief anterior, por `sem_controle`; sem etapa sai `PREENCHER`. Teste em `tests/test_volta_por_delta.py` e `tests/test_etapa_do_brief.py`.

### L04 (LOTE E2, coluna fora do quadro) · 3f85c29 · aprovado
`colunas_do_quadro` corta o limite de WIP do título e soma os três estados fora do quadro; `—` só na origem; nada se grava na recusa. Skill `kanban-scrum` atualizada.

### L05 (LOTE E1, veredito do pr) · f07e33f · aprovado
`exigidos_do_pr` vira a fonte única do que o `cmd_pr` exige, e a linha de veredito sai só com rc 0 (o `promover-homolog` segue contando o stdout com rc diferente de 0). A base do veredito é a mesma que o `pr_da_cli` resolve.

### L06 (LOTE E3, anotar o Histórico) · 0e5edc3 · aprovado
Frase do `anotar` no Jarvis (hoje na skill `trabalho-em-paralelo`, pelo L51); `tests/test_anotar.py` lê o texto do Jarvis pelo `apoio_jarvis`.

### L07 (LOTE E4, `--pedido` da mensagem) · ebcee31 · aprovado
`agents/conferente.md` usa o `<Pedido>` da mensagem; teste em `tests/test_forge.py`.

### L08 (P1 e P-CONF-SOBREPOR) · cbe48ef · aprovado
O recurso ao slug da branch só vale quando o `uso_do_pr` já recusaria o id (pedido existente, sem parecer com esse id) e um parecer da ref leva `pedido: <slug>`; ambíguo segue o `uso:`. No `entrega`, o commit de um pai já na base remota sai do escopo só nos arquivos cujo blob a base ainda tem igual; o resto segue do autor (falha fechada). `conferente.md` manda rodar da raiz; o Jarvis reenvia todo "não cumpriu".

### L09 (P3 e P4, Ler dirigido e haiku no integrador) · d1ea4a3, 0cd3fdf · aprovado
O `## Ler` passa a existir sempre, com a linha do trecho do pedido (regra 4 da economia de tokens); na `merge-integracao`, só o `forge-fechar --dry-run` e o `modelo: haiku` em stderr, sem efeito sobre portão. O ajuste 0cd3fdf faz o teste cair por asserção.

### L10 (OK-2, PQ fraco) · 312177c · aprovado, com A9 (recomendado)
Sha de 7 a 39 hex e `grep -c` sem arquivo saem como `aviso:`, sem reprovar; o sha40 e o sha256 não casam (lookarounds conferidos).

### L11 (OK-6, suposição com "muda com" e "custo de reverter") · fcfd46b · aprovado
Aviso no `brief`, contagem de `suposição revertida` no `voltas`, modelo do pedido e `R-DECISAO` com o complemento (muda o texto da regra: vai no destaque do título).

### L12 (OK-5, afirmação absoluta no lastro) · 6655353 · aprovado
A afirmação absoluta só tem lastro numa saída de teste com OK; a negação não conta. Só mede.

### L13 (P7, veredito contraditório) · 9cca941 · reprovado (A3)
A contagem acerta o caso `cumpriu` com linha reprovada, mas trata como contradição todo `não cumpriu` que não traga `PQ-n não cumpriu`, `escopo: fora` ou `pendente:`, e o conferente reprova também por `forma:` e por outras linhas de `escopo:`. Como a P7 decide hook só com ocorrência, o falso positivo infla a medida que decide.

### L14 (P9, recusas por papel) · b7729a0 · aprovado
Só papel e contagem saem; o comando recusado nunca. `docs/hooks.md` ganhou a forma de leitura.

### L15 (EXT-2, registro das decisões) · 7100834 · reprovado (A4)
O formato do registro, o aviso da linha torta e o `sem_controle` estão certos, e com `--pedido` funciona; a listagem sem `--pedido` não alcança a raiz de pedidos que o resto do `forge-check` já lê, e no Forge o registro sai vazio.

### L16 (EXT-3, custo em toda parada) · 266fd1b · reprovado (A1), com A8 (recomendado)
A regra "lacuna, nunca 0" está certa, mas a soma usa o `usage` cru e quebra o `movimento` em uso real; o teste usa só inteiros. Enquanto isso não se corrige, o item piora o comando de quadro mais usado do Jarvis.

### L17 (AQ-2, `proximo`) · b255e99, 87b54be · aprovado, com A7 (recomendado)
Só leitura, sem rede, linhas por `sem_controle` e largura de 160, teto de 40 linhas, `não verificável` onde falta registro, veredito só de parecer commitado. A heurística de estado por menção é fraca (A7), mas está dentro do que a seção 2 pede.

### L18 (M7, ocupação da trava) · 6cff313, 595af30 · reprovado (A2)
No Forge a leitura do `--status` está certa (0 é presa, 1 é livre, outro código é não verificável). O defeito é fora do Forge: o comando executa o hook do repositório que estiver na raiz e lê o código de saída dele como estado de trava.

### L31 (M1, prazo sem depender da carga) · 6ef2997, 55f12ec · aprovado
A parede vem de dentro do lançador e a CPU de `MedidaDeCpu`, sem subir teto; o teste da subida lenta prova que a espera fica fora. Spec `tests/mutantes/lote-unico-032-l31.json`.

### L32 (OK-3 e OK-13, registro da suíte vermelha) · 5c30b85, 0e8b9f5, ecf192b, 8b5e8d8, 1845f3f, 2908366 · aprovado
Grava só ids e números em `~/.forge-contrib/suite-vermelha.jsonl`, nunca no CI, só em pasta do próprio usuário sem escrita de outros, com `O_NOFOLLOW`, depois do veredito e sem mudar o código de saída.

### L33 (M4, mutantes em k processos) · d0e94e2, 963cc5b, 2c35fab, 3376ed9, 830d390, d06d288 · aprovado
`--processos` de 1 a 4, padrão 1; o controle por conjunto de testes se calcula uma vez sob trava por chave, antes da mutação da cópia; o código agrega por máximo (2 > 1 > 0), igual à série; erro ou SIGTERM mata os grupos e cancela o resto.

### L34 (OK-4, caminhos citados) · a96f038 · aprovado
Lista fechada do que só nasce no projeto, mínimo de 35 arquivos e de 120 caminhos lidos, link para fora conta como ausente.

### L35 (OK-11, invariante com regra e porque) · d6ea7e6 · reprovado (A6)
O formato (`invariantes_motivo` com `regra` de `docs/regras/` e `porque` de 30+ caracteres) e o legado que só encolhe estão certos para arquivo novo; a guarda não alcança o trecho novo em arquivo antigo, que é onde o próprio lote acrescentou invariantes.

### L36 (AQ-7, regressão de comportamento) · f658ceb, 35d353d · aprovado
Cinco casos anonimizados com o verificador da ADR 0007, sessão limpa sem regra, teste do caso não detectado, manifesto fechado sem link e varredura de dado pessoal e termos proibidos.

### L37 (D-3, integrador traz a develop) · 68db7a2, 60805de, 982d462, ecf192b · aprovado
Só em `melhoria/*`, uma vez por cadeia (`--trazida`), árvore do `merge-tree --write-tree` conferida no commit de merge, avanço por fast-forward (worktree limpa) ou `update-ref` com o valor antigo, envio sem `--force` nem `--no-verify` e recomeço da cadeia no head novo; conflito, falha de leitura ou envio recusado param. O parecer anterior continua valendo pelo `--base` (merge sem byte a mais).

### L49 (D-4, dois relógios) · 312723f, 1507cf8, d175e11, e671c89 · reprovado (A5)
`relogios_do_cartao` está certo e o pedido que não chegou à develop sai com rc 0; o filtro antigo do laço esconde a linha nova justamente no uso por release que o `agile-coach.md` manda.

### L50 (D-5, só o QA roda a suíte inteira) · 428d0a1 · aprovado (o trecho novo nos invariantes entra no A6)
Texto igual nos cinco arquivos, sem contradição com `R-QA` nem com o V2 do `tech-lead.md`; este parecer seguiu a D-5.

### L51 (AQ-8, Jarvis em núcleo curto) · 0c90721 · aprovado
Nenhuma regra perdida: (1) `tests/test_jarvis_nucleo.py` compara os 73 trechos de `tests/fixtures/jarvis-invariantes-b2580c6.json` com os exigidos hoje no Jarvis e nas três skills, e o texto de cada um existe no arquivo exigido; (2) conferi por frase o `agents/jarvis.md` de `0c90721^` contra o núcleo mais as três skills: das frases de 25 caracteres ou mais, só "Dispare de uma vez os agentes que podem começar, em segundo plano;" não casa, e ela segue no núcleo com ponto final no lugar do ponto e vírgula; (3) o núcleo manda ler cada skill no passo dela, e o ponteiro é invariante; (4) nenhum script de `bin/`, `hooks/`, `scripts/`, `.githooks/` ou `.github/` lê frase do `agents/jarvis.md`. Desvios já decididos no Histórico e aceitos aqui: `tests/apoio_jarvis.py`, os seis testes adaptados (`test_anotar`, `test_clareza`, `test_forge`, `test_medidas_m14b`, `test_sobreposicao_quadro`, `test_volta_por_delta`), a fixture e o `LEITORES_DE_TEXTO` de `bin/forge-testes`.

## Desvios decididos e documentação afetada
Aceitos como estão: o fragmento único do changelog (com uma linha por item), `docs/fechamento-integrador.md` no L02 e no L37, o mapa de módulos de `bin/forge-testes` (3b967a9 e L51) e os refactors 87b54be e 595af30. A documentação afetada de cada item foi atualizada na mesma entrega (`docs/hooks.md`, `docs/melhoria-continua.md`, `docs/transcricoes.md`, skills `kanban-scrum`, `software-architecture`, `engineering-practices`, `cyber-security` e `qa-testing`).

## Volta
O brief de volta sai dos seis bloqueantes; cada correção traz o teste que cai hoje (A1 com o `usage` no formato real; A2 com o hook do modelo de projeto; A3 com as linhas de reprovação de `agents/conferente.md`; A4 com pedidos só na raiz de pedidos; A5 com pedido sem volta; A6 com trecho novo em arquivo do legado). A revalidação lê só o delta (`forge-check delta --parecer docs/reviews/lote-unico-032.md`).
