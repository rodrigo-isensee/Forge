---
tipo: review
contrato: 1
pedido: suite-paralela-d4
branch: melhoria/suite-paralela-d4
commit: 84de155340ab1991d6aa494d1de96e221ae8628c
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-22
---
# Code review: SUITE-PARALELA-D4 (E1.2)

## Rodada 3: revalidação por delta (`830bf9f..84de155`)

Motivo da volta: renome autorizado pelo dono (2026-10-22 03:54) da palavra que casava o padrão de segredo em `tests/test_pre_push_trava.py`. Revisor diferente do autor (D-ETAPAS-INST).

**Delta lido** (`git diff 830bf9f 84de155`): um arquivo, 15 linhas trocadas por 15. Só nomes e comentários: `senhas()` virou `vezes()`, `segura_senha()` virou `segura_vez()`, `test_senha_de_processo_morto_e_descartada` virou `test_vez_de_processo_morto_e_descartada`, a variável local `senha` virou `vez`, e três mensagens de asserção e dois comentários trocam a palavra. Nenhuma asserção removida, afrouxada ou acrescentada: cada `assert` do delta tem par com a mesma comparação e os mesmos valores; os textos que o hook emite e que os testes procuram (`esperando a vez`, `a vez não chegou`, `2 na fila`) não mudaram. Não sobrou `senha`, `senhas(` nem `segura_senha` em `tests/`. Em cópia da worktree, `python3 -m unittest tests.test_pre_push_trava` deu `Ran 25 tests in 9.302s OK`. R-VERIFY: nada pulado nem repetido.

**Já lido** (inalterado desde a rodada 2, revisado nela): todo o resto da entrega, incluindo `scripts/suite-paralela.py`, `.githooks/pre-push`, `ci.yml`, `hooks/pesado.py` e os demais testes. A suíte inteira roda no pre-push deste envio (R-TETO). Os pareceres de segurança, QA e devops anteriores são sobre `36e913d`; o delta não toca código de produção, e a revalidação deles em proporção ao delta cabe a quem os deu.

Recomendações R1 a R7 da rodada 1 seguem válidas e não bloqueiam. Parecer: aprovado.

## Rodada 2: revalidação por delta (`1bdd3e8..36e913d`)

Motivo da volta: a `bateria` do PR #277 (run 39690069997, 4 processos) falhou em dois testes de `tests/test_atualizar.py` com `[TRAVOU esperando resposta]` e a saída completa. Revisor diferente do autor (D-ETAPAS-INST).

**Delta lido** (`forge-check delta --parecer` sobre este parecer: intervalo `1bdd3e8..36e913d`):
- `70359f5`, merge da develop `c092f1b` (release 0.28.0, #273 e #274), sem conflito. Conferido mecanicamente: `git diff c092f1b 70359f5` só traz os arquivos desta entrega, e `git diff 8201795 70359f5` nos arquivos desta entrega é vazio; os dois lados entraram intactos. Os arquivos que vieram da develop (`bin/forge-fechar`, `tests/test_fechar.py`, `tests/test_clareza.py`, `skills/modo-iniciante/SKILL.md`, `CHANGELOG.md`, versão, fragmentos apagados pela release) ficam como "já lido": revisados nos PRs deles. As duas asserções removidas que aparecem em `git diff 8201795 36e913d -- tests` são de `tests/test_fechar.py`, que é idêntico ao da develop (`git diff c092f1b 36e913d -- tests/test_fechar.py` vazio): vieram do #274, não desta entrega.
- `36e913d`, lido inteiro. `tests/test_atualizar.py:158-182`: EIO no mestre do pty passa a valer como terminal fechado (antes era `break` direto); com o terminal fechado, o `rodar` espera o processo até o `limite` e só então confere `p.poll()`. `tests/test_sugerir.py:85-96`: a mesma corrida, a mesma correção, com o prazo absoluto de 25 s que já existia.

**R-VERIFY.** Nenhuma asserção removida nem afrouxada no `36e913d` (só acréscimos); nenhum teste pulado, nenhuma repetição. A pergunta sem resposta continua marcada como travou: o processo bloqueado no `readline` mantém o terminal aberto, então o laço sai pelo `ocioso` sem `fechou`, `p.poll()` é `None` e a marca entra (`test_pergunta_sem_resposta_continua_marcada_como_travou`, `tests/test_atualizar.py:357`, passa). O efeito colateral é só de tempo: um processo que fecha o terminal e não termina passa a esperar até o `limite` antes de ser marcado; o prazo segue limitado.

**Teste novo.** `EsperaDoTerminal.test_saida_fechada_antes_do_fim_do_processo_nao_marca_travou` (`tests/test_atualizar.py:347`) alarga a janela de propósito (fecha 0, 1 e 2 e dorme 2 s). Conferido em cópia própria (`$TMPDIR/rv7`, HEAD destacado em 36e913d): com o teste novo enxertado no `rodar` antigo (`70359f5`), `EsperaDoTerminal` dá `FAILED (failures=1)`; no HEAD, `python3 -m unittest tests.test_atualizar tests.test_sugerir` → `Ran 95 tests in 42.319s OK`. Vermelho antes, verde depois. O `rodar` de `tests/test_sugerir.py` não ganhou teste próprio; é o mesmo laço, e o teste de `test_atualizar` cobre o comportamento.

Suíte inteira não refeita aqui (R-TETO): o pre-push deste envio a roda, e a volta registrou 1372 OK em 193 s, 196 s e 173 s. A prova no runner é a próxima `bateria` do PR #277. O alerta de conexão negada a `api.anthropic.com` durante a suíte (cartão SUITE-REDE-API) é de segurança (E1.3), não refeito aqui.

Recomendações R1 a R7 da rodada 1 seguem válidas e não bloqueiam. Parecer: aprovado.

## Rodada 1 (sobre `1bdd3e8`)

Rodada 1, entrega inteira: `ad6d96c..1bdd3e8` (merge-base real; o merge `a615047` da develop fica fora do diff), 9 commits, 13 arquivos, 1213+/19-. Lote: D4, SUITE-FILA-JUSTA, PREPUSH-PKILL-ALHEIO e PREPUSH-JA-NO-REMOTO (decisão do dono de 2026-10-21 14:12, opção B). Revisor diferente do autor (D-ETAPAS-INST). Lido contra o desenho (E0.1) e o modelo de ameaças (E0.2, T1 a T9, AB-1 a AB-14).

Ferramentas rodadas em cópia própria (`$TMPDIR/rv-d4`, clone sem hardlinks, HEAD destacado em 1bdd3e8): `python3 -m unittest tests.test_suite_paralela tests.test_pre_push_trava tests.test_pre_push_parecer tests.test_ci_local` → `Ran 116 tests in 22.035s OK`; `python3 -m unittest tests.test_hooks.Hooks.test_vigia_com_git_lento_nao_falha_por_carga -v` → `ok` (11,4 s, os dois subtestes: prazo 120 passa, prazo 5 falha). `shellcheck` e `actionlint` não estão no PATH desta máquina: pendência para o CI (o passo `shellcheck` da `bateria` já lista `.githooks/pre-push`) e para o parecer de devops (E1.6). Suíte inteira e `scripts/validar-plugin.sh` não refeitos aqui (R-TETO; o pre-push deste envio roda a suíte, e o QA a refaz). Segurança (E1.3) e devops (E1.6): pareceres próprios, não refeitos.

## O que foi conferido, por foco do brief

**`scripts/suite-paralela.py`: divisão e guarda de completude (T1, T2, T4; AB-1 a AB-5).** A divisão é LPT determinística por módulo (`repartir`, empate por índice e nome), sobre `modulos()`, e o peso só equilibra (peso ausente vale a mediana). A guarda não confia na lista: o esperado é o multiconjunto de IDs do `discover` inteiro (`ids(descobrir())`), e o executado é o multiconjunto dos IDs que cada filho anotou em `startTest`; soma e diferença nos dois sentidos (`conferir_completude`). Isso fecha os buracos que a lista de módulos poderia abrir: teste em subpasta de `tests/` ou módulo fora do glob aparece como ausente e reprova; teste rodado em dobro aparece como extra. A classe importada de outro módulo (`test_pedido_fora` importa `Raiz` de `test_voltas`) conta duas vezes no `discover` e duas vezes na execução, e o multiconjunto bate. Filho com rc diferente de 0, morto por sinal (rc negativo), sem relatório ou com zero testes reprova (`resumir`); falhas e erros somados reprovam; pulados aparecem no resumo. O rc de cada filho é lido um a um pelo objeto `Popen` (`esperar`), sem depender da ordem de término. `FORGE_SUITE_PROCS` fora de 1..4 recusa (falha fechada, `test_procs_acima_do_teto_e_recusado`).

**TMPDIR por processo, árvore e `.git/config` (T5; AB-13).** Cada filho recebe `TMPDIR` próprio (`p<i>`, modo 700) dentro de uma pasta `mkdtemp` apagada no `finally`; `nice(10)`; `start_new_session`. O orquestrador compara `git status --porcelain --untracked-files=all` e o `.git/config` comum antes e depois (`estado_da_arvore`, `conferir_arvore`), além da guarda por módulo. Coberto por `test_cada_processo_tem_tmpdir_proprio_nice_e_grupo_proprio` e `test_teste_que_escreve_na_arvore_reprova`.

**Sinais e killpg (T6; AB-6, AB-12).** `SIGTERM`/`SIGINT`/`SIGHUP` viram `Interrompido`; `encerrar` manda TERM ao grupo de cada filho, espera até 10 s e manda KILL ao grupo; nada fora desses grupos é tocado. No hook, a suíte roda em segundo plano com `trap parar TERM INT HUP`: `parar` manda TERM só ao pid da suíte, espera por ele e sai com 1, então a trava só solta depois dos filhos, e o `.verde` não é anotado (a anotação fica depois do `[ "$rc" -eq 0 ] || exit 1`). O filho ainda vigia o pai (`vigiar_pai`) para não ficar órfão se o orquestrador levar KILL. Coberto por `test_sigterm_encerra_o_grupo_de_cada_processo`, `test_parar_o_pre_push_encerra_os_processos_da_suite` e `test_parar_o_hook_para_so_a_propria_suite`. O hook imprime o pid para `kill <pid>` e desaconselha `pkill -f`.

**Trava e chamada à mão (R-TETO).** Com `FORGE_SUITE_TRAVA`, o script confere que a trava é arquivo do próprio usuário, não é link, está presa (o `flock -n` de outra abertura falha) e está anotada pelo pid do pai ou do próprio processo; senão recusa sem rodar (dois testes). Sem a variável, o script se troca por `.githooks/pre-push --suite`, que entra na mesma fila e na mesma trava e faz `exec` da suíte herdando o descritor 9 (morre a suíte, solta a trava). `hooks/pesado.py` passou a contar o script e o `--suite` como a suíte inteira, com teste dos dois lados (conta no clone do Forge, não conta em projeto). `bin/forge-testes` e `release.yml` não mudaram (AB-14 e T7d; o teste novo do `test_ci_local` confere a `release.yml` em série).

**Fila FIFO (SUITE-FILA-JUSTA; AB-7).** Senha `<ns>-<pid>` criada com nome oculto, já presa por `flock` no descritor 8 e só então renomeada (ninguém a vê solta); pasta conferida (do próprio usuário, não é link, modo 700); senha de processo morto é reconhecida pelo `flock -n` que se obtém e é descartada; só a menor senha viva disputa a trava, e a exclusão continua sendo do kernel. O prazo é um só (`limite_ns`), dividido entre a espera na fila e o `flock -w` do resto; esgotado, `barrar` sai da fila e recusa o envio. Falha da fila cai na espera só pela trava, com aviso, nunca em rodar sem trava. Testes de ordem, de senha morta, de anterior viva com a trava livre e de fila que é link.

**PREPUSH-JA-NO-REMOTO.** Sai com 0 só com `n_refs` igual a 0 e fora do modo `--suite`, depois do laço de refs (onde ficam as checagens de R-VERIFY e das três branches protegidas, que com stdin vazio não têm o que barrar) e antes de tudo da trava; não anota `.verde`. Não consulta o remoto: usa o que o git entrega no stdin, então AB-9 não se aplica e AB-10 (mesmo sha em outra ref) traz uma linha e roda a suíte. O push que só apaga traz uma linha e segue rodando a suíte (`test_push_que_so_apaga_ainda_roda_a_suite`), como o dono decidiu; PREPUSH-DELETE-SEM-SUITE ficou fora.

**Lançador de 120 s do `test_hooks`.** Ele só troca `GIT_TIMEOUT_S` do `forge-check` carregado pelo `_comum.forge_check()` (com `lru_cache`, então é o mesmo módulo que o hook usa) e roda o hook por `runpy` como `__main__`; o resto do caminho é o de produção. O `timeout` do `subprocess.run` passou de 30 para 120 s: um hook pendurado ainda reprova, só mais tarde. Procurei testes que dependam do prazo do git pelo `rodar` e não achei (o único com `sleep` é de `gh` pendurado, que tem prazo próprio e não passa pelo `GIT_TIMEOUT_S`). O teste novo prova o efeito nos dois sentidos: com 5 s o vigia falha com git lento, com 120 s passa. Não esconde falha real de lógica; esconde só a lentidão por carga, que é o objetivo.

**`ci.yml`.** `rapida` e `bateria` trocam o `discover -v` pelo script, um job `bateria` com o mesmo nome e a mesma condição; o passo dos pareceres e a `release.yml` ficam como estavam; sem permissão, ação, runner ou custo novo (R-CUSTO). No CI o script entra sem `FORGE_SUITE_TRAVA`, então passa pelo `pre-push --suite` (trava em `XDG_RUNTIME_DIR` ou `/tmp`, sem contenda). Esse caminho está coberto localmente (`test_modo_suite_usa_a_trava_e_nao_le_refs`, `test_a_mao_espera_a_trava_do_pre_push`), mas ainda não rodou num runner: não há PR nem execução de workflow para a branch (`gh pr list --head` vazio). A primeira `bateria` do PR é a prova; fica para o devops (E1.6) e para quem abrir o PR.

**Regras.** R-VERIFY: nenhum teste pulado, nenhuma repetição automática, prazo da fila só barra. R-NEUTRO: nada de projeto. Fragmento em `changelog.d/`, versão não sobe. README e `docs/hooks.md` atualizados. Commits em Conventional Commits, um por item, com o ID do cartão.

## Achados

## Recomendações (não bloqueiam)
- R1 `scripts/suite-paralela.py:193`: `vigiar_pai` lê o pid do pai com `os.getppid()` quando a thread nasce; se o orquestrador morrer antes disso (sinal entre o `Popen` e o `append` de `lancar`, janela de milissegundos), o pai lido já é o init e o filho roda órfão até o fim. Passar o pid do orquestrador como argumento de `--processo` fecha a janela.
- R2 `scripts/suite-paralela.py:258-263`: o KILL final em `encerrar` vai ao grupo `p.pid` depois de o líder já ter sido colhido; o Linux não reaproveita o número enquanto o grupo tem membros, então o risco de acertar processo alheio é teórico, mas um `p.poll() is None or` antes do KILL o deixa explícito.
- R3 `tests/test_hooks.py:288-290`: o comentário diz que o prazo de produção é conferido à parte pelo `test_timeout_de_rede...`, mas esse teste varre só `hooks/*.py` (rede: `gh`, `fetch`...), não o `GIT_TIMEOUT_S = 5` de `bin/forge-check`; nenhum teste confere esse valor contra o `timeout` do `hooks.json`. Ajustar o comentário ou juntar ao cartão FC-GIT-TIMEOUT-ENV.
- R4 `docs/hooks.md:107`: o limite conhecido (a trava cobre o `pre-push`, não a suíte lançada à mão) ficou meio desatualizado: o script à mão agora passa pela trava e pela fila; só o `discover` à mão segue fora. O `--status` também passou a dizer quantos esperam na fila.
- R5 `.githooks/pre-push:74`: `date +%s%N` é GNU; num `date` sem `%N` a senha e o `limite_ns` quebram. Hoje a fábrica roda em Linux e no runner Ubuntu; se um dia houver outra plataforma, cair para a espera só pela trava.
- R6 (para E1.6) Medição: a E1.1 registrou 3 execuções com N=4 (125 s vermelha por carga, 132 s e 122 s), sem os blocos serial, 2 e 3 nem a execução sequencial de referência na mesma árvore que o desenho (seção 5) e o T4 pedem. O número 4 segue o desenho, mas o fechamento do critério de 10% e 30% cabe ao parecer de devops.
- R7 A frase na regra do teto sobre o paralelo interno a uma suíte (desenho, seção 4) não entrou; é texto de regra, com rito próprio, fora deste lote.
