---
tipo: review
contrato: 1
pedido: lote-unico-032
branch: melhoria/lote-unico-032
commit: 9f32431def2214ca564c4d1968c48b726e2d8d45
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-03
---
# Review: lote-unico-032 (review único do experimento do dono, lote-unico-032-REV E1.1, volta 2)

Volta 2, por delta. Rodada anterior: parecer `3052f00` sobre `0c90721c86b15d89ea0aec0befa1850b45948698` (52 commits, `b2580c6...0c90721`; as seções por item abaixo ficam mantidas). Delta lido nesta rodada: `git diff 0c90721c86b15d89ea0aec0befa1850b45948698..9f32431def2214ca564c4d1968c48b726e2d8d45` (`forge-check delta --parecer docs/reviews/lote-unico-032.md`), que é o merge da develop `6ef56a0` e os oito commits de correção `0e7f04a`, `7eae698`, `d58718a`, `7d0f599`, `bcad27a`, `c0c180e`, `9b1e375` e `9f32431`. Ficou como "já lido": todo o resto da branch (`b2580c6...0c90721`), sem byte novo fora desses commits.

Dispensados só neste PR pela decisão 3 = A do dono, e por isso fora dos achados: o teto de 150 linhas, um comportamento por PR e uma classe por PR em `hooks/` (o lote não toca `hooks/`; o `hooks/` do delta veio da develop, #427 e #428).

## Achados
- A3 (bloqueante) bin/forge-check:4021 · L13, defeito provado: a lista negativa conta como reprovação toda linha escopo: que não começa com ok ou confira; escopo: integração da base, sem commit (nada a conferir) e união de N briefs, que o entrega imprime sem reprovar, com veredito cumpriu dão (1, 1).
- A6 (bloqueante) tests/config.json:666 · L35, requisito (OK-11): o legado por trecho não encolhe; agents/jarvis.md tem n=73 com 51 trechos sem motivo hoje, então 22 trechos novos entram sem regra e porque, e subir o n de qualquer arquivo passa sem aviso. Fixar n igual ao de hoje e a soma num teto.
- A8 (recomendado) bin/forge-check:2026 · L16: cada parada lê todas as transcrições das pastas padrão (2481 arquivos nesta máquina) e o custo total soma só trechos que terminaram em parada, não o ciclo do cartão; dizer isso na skill ou medir o tempo do movimento.
- A9 (recomendado) bin/forge-check:4384 · L10: valor de opção conta como posicional, e `grep -c -m 1 padrao` não avisa; é só aviso, falso negativo.
- A10 (recomendado) bin/forge-check:4026 · L13: a docstring de medir_vereditos e o texto de uso (bin/forge-check:107) ainda dizem só PQ-n não cumpriu, escopo: fora ou pendente:; alinhar com a regra nova junto da correção do A3.

## Parecer
**Reprovado**, por dois bloqueantes (A3 e A6), numa passada só sobre o delta inteiro. Dos sete achados da rodada anterior que pediam correção, cinco estão corrigidos e provados (A1, A2, A4, A5 e A7); A3 e A6 foram corrigidos em parte e o resíduo de cada um está provado abaixo. Os outros itens seguem aprovados como estavam; o merge da develop está certo.

Classes, sem linha AR nesta rodada (DECISÃO TÉCNICA de 2026-10-29 15:28 do T1-CONF-ESCOPO-REV): A3 segue "vocabulário do conferente lido por lista incompleta" (na volta 1 a lista positiva esquecia linhas que reprovam; na volta 2 a lista negativa esquece linhas que não reprovam; a fonte que já diz qual reprova é o par `(linha, reprova)` que o `cmd_entrega` monta); A6 segue "granularidade da guarda mais larga que o requisito" (a contagem por arquivo sem amarra ao valor de hoje deixa a folga que o L51 abriu no Jarvis). É a segunda volta das duas classes neste pedido.

## Revalidação por delta (volta 2)
Cada correção traz um teste novo. Rodei os seis testes novos que exercitam `bin/forge-check` com o `bin/forge-check` de `0c90721` numa cópia da árvore de `9f32431` (`git archive` em `$TMPDIR/tech-lead-lote-unico-032/antes`): os seis falham (`FAILED (failures=6)`), e na árvore de `9f32431` passam. O teste mostra o defeito.

- **A1 (L16) · 0e7f04a · corrigido.** `custo_do_trecho` soma por `somar_uso` (só `CAMPOS_USO`, inteiros positivos) e depois `total_uso`; `server_tool_use` aninhado e `service_tier` deixam de entrar. Teste `tests/test_sobreposicao_quadro.py::Movimento.test_custo_do_trecho_com_o_uso_no_formato_real_do_claude_code`, com o `usage` no formato real (20 tokens = 10+5+3+2): falha antes, passa agora.
- **A2 (L18) · 7eae698 · corrigido.** `ocupacao_da_trava` só executa o hook que traz o `[ "$1" = "--status" ]` do Forge (`.githooks/pre-push:108`; o `templates/projeto/.githooks/pre-push` não o tem); senão, devolve `None` e nada roda. Teste `tests/test_fila_ocupacao.py::OcupacaoDaTrava.test_hook_alheio_sem_o_status_do_forge_nao_e_executado_nem_vira_trava_presa`: o hook alheio não roda nem vira trava presa. Ler a trava sem executar nada seria mais firme (é o recomendado A1 da segurança, com o `security-engineer`), mas o defeito provado da rodada anterior não se reproduz.
- **A3 (L13) · d58718a · corrigido em parte, segue bloqueante.** Os dois casos da rodada anterior (`escopo: Base-sha fora da branch`, `forma: ...`) agora contam certo, e `escopo: ok (...)`, `escopo: confira` e `forma: ok` não reprovam. Resíduo provado com `medir_vereditos({'s': [("PQ-1 cumpriu\n<linha>\nveredito: cumpriu\n", None)]})`: com `escopo: integração da base (o que difere dos dois pais)`, `escopo: sem commit (nada a conferir)` e `escopo: união de 2 briefs (mesma Branch, Base, Base-sha e pedido)` sai `{'s': (1, 1)}` nos três; com `escopo: ok (parecer de tech-lead) ...`, `(1, 0)`. As três linhas saem do `cmd_entrega` marcadas como não reprovação (bin/forge-check:1070, 1198, 1231), e a primeira aparece em toda conferência de entrega depois de merge da base, como esta. Sugestão: tirar as linhas que não reprovam (ou as que reprovam) das mesmas strings do `cmd_entrega`, com um caso de teste para cada uma.
- **A4 (L15) · 7d0f599 · corrigido.** `pedidos_do_registro` lista também `RAIZES_DE_BRIEF`. Teste `tests/test_decisoes.py::Decisoes.test_sem_pedido_lista_tambem_a_raiz_de_pedidos`. No Forge: `forge-check decisoes` → `decisoes: total=2023 avisos=646` (na rodada anterior, `total=0`); com `--raiz-pedidos ~/.forge-contrib`, o mesmo.
- **A5 (L49) · bcad27a · corrigido.** O laço só pula o pedido sem volta quando ele também não tem relógio. Teste `tests/test_voltas.py::Voltas.test_pedido_que_andou_sem_volta_traz_o_relogio_tambem_sem_pedido` (com e sem `--pedido`); o teste antigo `test_pedido_sem_voltas_so_aparece_com_pedido_explicito` segue verde (o pedido sem histórico de quadro continua fora).
- **A6 (L35) · c0c180e · corrigido em parte, segue bloqueante.** O legado vira `{arquivo: trechos de antes}` e `invariantes_motivo_trecho` traz `regra` e `porque` dos trechos novos (os cinco do L50 e os três ponteiros do L51); o teste cobre trecho novo sem motivo, motivo curto e motivo fora do legado, e toda chave de `invariantes_motivo_trecho` existe em `invariantes`. Resíduo provado com `problemas_de_motivo` sobre o `tests/config.json` de `9f32431`: hoje `[]`; com um trecho novo sem motivo em `agents/jarvis.md`, `[]` (o n é 73, o número de `b2580c6`, e o Jarvis tem 51 trechos sem motivo depois do L51); com um trecho novo em `agents/tech-lead.md`, a guarda pega, e com o mesmo trecho mais `"agents/tech-lead.md": 20`, `[]`. O `LEGADO_SEM_MOTIVO_MAXIMO` só conta arquivos, então o n de cada um sobe sem teste cair. Os outros 33 arquivos do legado estão com n igual à contagem de hoje. Sugestão: n do Jarvis em 51 e uma constante para a soma dos n (só encolhe), com os dois casos no teste.
- **A7 (L17) · 9f32431 · corrigido.** `etapas_do_proximo` só põe `em curso` com verbo de início na linha (`VERBO_DE_INICIO`); menção solta sai `não verificável`. Teste `tests/test_proximo.py::Proximo.test_mencao_a_etapa_sem_verbo_de_inicio_nem_de_entrega_nao_a_poe_em_curso`. Era recomendado.
- **A1 do QA (L31) · 9b1e375.** Só a spec `tests/mutantes/lote-unico-032-l31.json` muda: o M6 aponta `tests.test_fechar_sinal.Teste.test_o_sleep_das_esperas_roda_em_segundo_plano_com_wait`, que existe (tests/test_fechar_sinal.py:87) e passa. Matar o mutante é do QA, que revalida o achado dele.
- **Merge da develop · 6ef56a0 (A7 do QA, A1 do devops).** `git show --remerge-diff 6ef56a0`: o único conflito é `tests/test_catraca.py:2697`, e a resolução mantém as duas linhas: o `assertIn("docs/(reviews|qa|security|devops|ux)/", ci)` da branch (L01, que contém o `docs/(reviews|qa)/` da develop) e o `assertEqual(re.findall(r"timeout-minutes: (\d+)", ci), ["20", "25", "25"])` do #429. Nenhum outro byte difere do merge automático. `hooks/_comum.py`, `hooks/conformidade.py`, o corpus de `tests/hooks/conformidade/`, `tests/test_hooks.py`, os timeouts do `.github/workflows/ci.yml` e os pareceres de `heredoc-comentario`, `heredoc-donos` e `ci-suite-no-teto` vêm iguais aos da develop (#427 a #429, já revistos lá); `tests.test_catraca` passa no head.
- **Fragmento do changelog.** `changelog.d/lote-unico-032.md` ganhou uma linha por correção (8 linhas), no mesmo arquivo único já aceito.

## Testes e ferramentas (D-5: só os módulos tocados, carga abaixo de 7, núcleos 8-15)
Volta 2 (módulos tocados pelo delta; `taskset -c 8-15`, carga de 5,9 e de 4,8 no início de cada rodada):
- `python3 -m unittest tests.test_sobreposicao_quadro tests.test_fila_ocupacao tests.test_decisoes tests.test_voltas tests.test_proximo tests.test_catraca.Workflows tests.test_fechar_sinal.Teste.test_o_sleep_das_esperas_roda_em_segundo_plano_com_wait`: `Ran 86 tests in 16.240s` / `OK`.
- `python3 -m unittest tests.test_forge tests.test_catraca`: `Ran 753 tests in 214.325s` / `OK`.
- Os seis testes novos que exercitam `bin/forge-check`, com o `bin/forge-check` de `0c90721`: `Ran 22 tests` / `FAILED (failures=6)`, um por achado (A1, A2, A3, A4, A5, A7).
- Nenhum shell tocado pelo delta fora do que veio da develop. A suíte inteira, `scripts/validar-plugin.sh` e os mutantes ficam com o QA (D-5); pipeline com o `devops-engineer`, segurança com o `security-engineer`, não refeitos aqui.

Volta 1 (sobre `0c90721`, mantido):
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

### L13 (P7, veredito contraditório) · 9cca941, d58718a · reprovado (A3, volta 2: o falso positivo mudou de lado)
A contagem acerta o caso `cumpriu` com linha reprovada, mas trata como contradição todo `não cumpriu` que não traga `PQ-n não cumpriu`, `escopo: fora` ou `pendente:`, e o conferente reprova também por `forma:` e por outras linhas de `escopo:`. Como a P7 decide hook só com ocorrência, o falso positivo infla a medida que decide.

### L14 (P9, recusas por papel) · b7729a0 · aprovado
Só papel e contagem saem; o comando recusado nunca. `docs/hooks.md` ganhou a forma de leitura.

### L15 (EXT-2, registro das decisões) · 7100834, 7d0f599 · aprovado na volta 2 (A4 corrigido)
O formato do registro, o aviso da linha torta e o `sem_controle` estão certos, e com `--pedido` funciona; a listagem sem `--pedido` não alcança a raiz de pedidos que o resto do `forge-check` já lê, e no Forge o registro sai vazio.

### L16 (EXT-3, custo em toda parada) · 266fd1b, 0e7f04a · aprovado na volta 2 (A1 corrigido), com A8 (recomendado)
A regra "lacuna, nunca 0" está certa, mas a soma usa o `usage` cru e quebra o `movimento` em uso real; o teste usa só inteiros. Enquanto isso não se corrige, o item piora o comando de quadro mais usado do Jarvis.

### L17 (AQ-2, `proximo`) · b255e99, 87b54be, 9f32431 · aprovado (A7 corrigido na volta 2)
Só leitura, sem rede, linhas por `sem_controle` e largura de 160, teto de 40 linhas, `não verificável` onde falta registro, veredito só de parecer commitado. A heurística de estado por menção é fraca (A7), mas está dentro do que a seção 2 pede.

### L18 (M7, ocupação da trava) · 6cff313, 595af30, 7eae698 · aprovado na volta 2 (A2 corrigido)
No Forge a leitura do `--status` está certa (0 é presa, 1 é livre, outro código é não verificável). O defeito é fora do Forge: o comando executa o hook do repositório que estiver na raiz e lê o código de saída dele como estado de trava.

### L31 (M1, prazo sem depender da carga) · 6ef2997, 55f12ec, 9b1e375 · aprovado (o M6 da spec é do QA)
A parede vem de dentro do lançador e a CPU de `MedidaDeCpu`, sem subir teto; o teste da subida lenta prova que a espera fica fora. Spec `tests/mutantes/lote-unico-032-l31.json`.

### L32 (OK-3 e OK-13, registro da suíte vermelha) · 5c30b85, 0e8b9f5, ecf192b, 8b5e8d8, 1845f3f, 2908366 · aprovado
Grava só ids e números em `~/.forge-contrib/suite-vermelha.jsonl`, nunca no CI, só em pasta do próprio usuário sem escrita de outros, com `O_NOFOLLOW`, depois do veredito e sem mudar o código de saída.

### L33 (M4, mutantes em k processos) · d0e94e2, 963cc5b, 2c35fab, 3376ed9, 830d390, d06d288 · aprovado
`--processos` de 1 a 4, padrão 1; o controle por conjunto de testes se calcula uma vez sob trava por chave, antes da mutação da cópia; o código agrega por máximo (2 > 1 > 0), igual à série; erro ou SIGTERM mata os grupos e cancela o resto.

### L34 (OK-4, caminhos citados) · a96f038 · aprovado
Lista fechada do que só nasce no projeto, mínimo de 35 arquivos e de 120 caminhos lidos, link para fora conta como ausente.

### L35 (OK-11, invariante com regra e porque) · d6ea7e6, c0c180e · reprovado (A6, volta 2: corrigido em parte)
O formato (`invariantes_motivo` com `regra` de `docs/regras/` e `porque` de 30+ caracteres) e o legado que só encolhe estão certos para arquivo novo; a guarda não alcança o trecho novo em arquivo antigo, que é onde o próprio lote acrescentou invariantes.

### L36 (AQ-7, regressão de comportamento) · f658ceb, 35d353d · aprovado
Cinco casos anonimizados com o verificador da ADR 0007, sessão limpa sem regra, teste do caso não detectado, manifesto fechado sem link e varredura de dado pessoal e termos proibidos.

### L37 (D-3, integrador traz a develop) · 68db7a2, 60805de, 982d462, ecf192b · aprovado
Só em `melhoria/*`, uma vez por cadeia (`--trazida`), árvore do `merge-tree --write-tree` conferida no commit de merge, avanço por fast-forward (worktree limpa) ou `update-ref` com o valor antigo, envio sem `--force` nem `--no-verify` e recomeço da cadeia no head novo; conflito, falha de leitura ou envio recusado param. O parecer anterior continua valendo pelo `--base` (merge sem byte a mais).

### L49 (D-4, dois relógios) · 312723f, 1507cf8, d175e11, e671c89, bcad27a · aprovado na volta 2 (A5 corrigido)
`relogios_do_cartao` está certo e o pedido que não chegou à develop sai com rc 0; o filtro antigo do laço esconde a linha nova justamente no uso por release que o `agile-coach.md` manda.

### L50 (D-5, só o QA roda a suíte inteira) · 428d0a1 · aprovado (o trecho novo nos invariantes entra no A6)
Texto igual nos cinco arquivos, sem contradição com `R-QA` nem com o V2 do `tech-lead.md`; este parecer seguiu a D-5.

### L51 (AQ-8, Jarvis em núcleo curto) · 0c90721 · aprovado
Nenhuma regra perdida: (1) `tests/test_jarvis_nucleo.py` compara os 73 trechos de `tests/fixtures/jarvis-invariantes-b2580c6.json` com os exigidos hoje no Jarvis e nas três skills, e o texto de cada um existe no arquivo exigido; (2) conferi por frase o `agents/jarvis.md` de `0c90721^` contra o núcleo mais as três skills: das frases de 25 caracteres ou mais, só "Dispare de uma vez os agentes que podem começar, em segundo plano;" não casa, e ela segue no núcleo com ponto final no lugar do ponto e vírgula; (3) o núcleo manda ler cada skill no passo dela, e o ponteiro é invariante; (4) nenhum script de `bin/`, `hooks/`, `scripts/`, `.githooks/` ou `.github/` lê frase do `agents/jarvis.md`. Desvios já decididos no Histórico e aceitos aqui: `tests/apoio_jarvis.py`, os seis testes adaptados (`test_anotar`, `test_clareza`, `test_forge`, `test_medidas_m14b`, `test_sobreposicao_quadro`, `test_volta_por_delta`), a fixture e o `LEITORES_DE_TEXTO` de `bin/forge-testes`.

## Desvios decididos e documentação afetada
Aceitos como estão: o fragmento único do changelog (com uma linha por item), `docs/fechamento-integrador.md` no L02 e no L37, o mapa de módulos de `bin/forge-testes` (3b967a9 e L51) e os refactors 87b54be e 595af30. A documentação afetada de cada item foi atualizada na mesma entrega (`docs/hooks.md`, `docs/melhoria-continua.md`, `docs/transcricoes.md`, skills `kanban-scrum`, `software-architecture`, `engineering-practices`, `cyber-security` e `qa-testing`).

## Volta
O brief da volta 3 sai dos dois bloqueantes (A3 e A6), cada um com o teste que cai hoje: A3 com as três linhas `escopo:` do `cmd_entrega` que não reprovam e veredito `cumpriu`; A6 com trecho novo sem motivo em `agents/jarvis.md` e com o n de um arquivo do legado aumentado. O A10 pode ir junto do A3 (recomendado). A revalidação lê só o delta (`forge-check delta --parecer docs/reviews/lote-unico-032.md`).
