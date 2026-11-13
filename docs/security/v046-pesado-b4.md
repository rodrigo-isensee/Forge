---
tipo: revisao-seguranca
contrato: 1
pedido: v046
branch: melhoria/pesado-b4
commit: c443050f82ddd8d7118be5c6c59273050cbae47f
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-11
---
# Review de segurança: v046 (E14.1, pesado B4 e PROCESSO-ORFAO)

## Revalidação (volta 1): 3e830f9b..c443050f
`hooks/pesado.py:176-185` agora soma a leitura original às de `separar_lancadores` (`simples = [palavras] + [...]`): A1 corrigido. S1 a S4 refeitas no head c443050f com `hooks/` da base e do head extraídos por `git archive`: todas True, igual à base (resultado abaixo). A2 corrigido: `gravar_a_vez` grava o `dono` e o início lidos uma vez (`:154`, `:330`), sem reler `getppid()` depois da checagem. Delta só toca `hooks/pesado.py`, testes e mutantes; nada de rede, segredo, escrita fora de `.forge/run/` ou custo. `tests.test_pesado_v046` 15 OK (1 pulado pelo namespace do sandbox) e `tests.test_hooks -k esado` 5 OK na worktree da branch. Sem bloqueante aberto; A3 segue recomendado (não regressão).

Escopo: `git diff 2b896503..3e830f9b` (3 commits: e5132755, 649921be, 3e830f9b), `hooks/pesado.py` (+76/-14), `tests/test_pesado_v046.py`, dois arquivos de mutantes e o fragmento do changelog. Só leitura da branch (Z10). Método: sonda diferencial com `hooks/` da base e do head extraídos por `git archive` para `$TMPDIR`, 53 entradas (lançadores da tabela e fora dela, caminhos, padrões de projeto); `tests.test_pesado_v046` (11 OK, 1 pulado pelo namespace do sandbox) e `tests.test_hooks -k esado` (5 OK) rodados na worktree da branch.

## Gatilhos
Controle do Forge que analisa entrada (classificador de comando do hook `pesado`, `R-TETO`) e liberação de trava de recurso compartilhado entre sessões (PROCESSO-ORFAO).

## Achados
- A1 (recomendado) hooks/pesado.py:176 · CORRIGIDO no c443050f (era bloqueante) · `inicios` lia só as leituras sem lançador; padrão de `pesados` que começa por lançador (`nice`, `sudo`, `time` + comando de testes) escapava. Corrigido somando a leitura original às de `separar_lancadores`.
- A2 (recomendado) hooks/pesado.py:339 · CORRIGIDO no c443050f · a vez grava `pid_da_sessao()` de novo depois da checagem da linha 326; se a sessão morre entre as duas, a trava fica com o pid do reaper (vivo) por até TRAVA_S. Gravar `dono` (e o início lido dele) em vez de reler.
- A3 (recomendado) hooks/pesado.py:171 · formas pesadas que já escapavam na develop e seguem (não regressão): `bash .githooks/pre-push --suite`, `bash -c '…'`, `python3 -m unittest` sem `discover`, `python3.12 -m …`, `bin//forge-testes`, `bin/./forge-testes`, `ionice`/`chrt`/`taskset`, `npx timeout …`. Entram na matriz de dimensões.

## Sondas
- S1 · `pesado.pesado("nice <testes>", ["nice <testes>"])` no head 3e830f9b · espera: True (como na base 2b896503) · obtido: False no 3e830f9b, True no c443050f
- S2 · `pesado.pesado("sudo <testes>", ["sudo <testes>"])` no head 3e830f9b · espera: True (como na base 2b896503) · obtido: False no 3e830f9b, True no c443050f
- S3 · `pesado.pesado("time <testes>", ["time <testes>"])` no head 3e830f9b · espera: True (como na base 2b896503) · obtido: False no 3e830f9b, True no c443050f
- S4 · `pesado.pesado("timeout 600 <testes>", ["timeout 600 <testes>"])` no head 3e830f9b · espera: True (como na base 2b896503) · obtido: False no 3e830f9b, True no c443050f

## Detalhe dos achados
**A1.** Evidência: `hooks/pesado.py:175-179`. Na base, `inicios(palavras)` devolvia o texto inteiro do comando simples e, a partir dele, os textos depois de cada lançador; um padrão de `pesados` que começa por `nice`, `sudo`, `time`, `timeout`, `env`, `nohup`, `exec`, `command`, `builtin`, `setsid`, `stdbuf` ou `xargs` casava pelo texto inteiro. No head, `simples` só traz as leituras de `separar_lancadores`, que começam depois dos lançadores; o texto original só volta no `except ValueError`. Sondas S1 a S4 (base True, head False). `docs/hooks.md` documenta `pesados` como "início de comando" e não proíbe padrão com lançador na frente, e a lista é do usuário (`.forge/config.json`), então é configuração válida que perdeu cobertura. Caminho de risco: sem atacante; um agente roda o comando exatamente como o projeto o declarou pesado, em paralelo com outro, e as duas tarefas esgotam memória (o motivo do `R-TETO`). Severidade baixa (guarda de processo, não fronteira de segurança), mas é defeito provado e contraria o foco desta entrega: nenhuma forma pesada nova pode escapar. Correção mínima: `simples = [palavras] + [comando for comando, _ in separar_lancadores(palavras)]` (o `inicios_sem_lancador` de `palavras` reproduz a leitura da base) e um caso no `test_pesado_v046.py` com cada lançador da tabela do `_comum` (`env`, `sudo`, `command`, `nohup`, `time`, `exec`, `builtin`, `nice`, `setsid`, `stdbuf`, `timeout`, `xargs`) como primeira palavra do padrão do projeto. Esforço P. Dono: tech-lead.

**A2.** Evidência: `hooks/pesado.py:326` compara `pid_da_sessao()` com `dono` e `:332` grava `"pid": pid_da_sessao()` e `inicio_da_sessao()`, que releem o `getppid()`. Se a sessão acaba entre as duas linhas (janela de microssegundos), o hook órfão grava o pid do processo que o adotou (init do contêiner ou subreaper), vivo e com início coerente, e a trava prende as outras sessões até TRAVA_S (600 s). A mesma corrida existe em `:300` (caminho sem fila), já na base. Não é forçável por um agente (exige a morte da própria sessão no meio do passo); efeito limitado ao prazo da trava. Severidade informativa. Correção mínima: na linha 332 gravar `dono` e o início lido de `dono`; opcional, não gravar quando o pid é 1. Esforço P. Dono: tech-lead.

**A3.** Evidência: sonda diferencial; todas as formas listadas dão False na base e no head. Destaque: `env -a -b -c -d bin/forge-testes --completa` (mais de `TETO_FORA_DA_TABELA` palavras fora da tabela) cai, por `LancadorDemais`, na leitura antiga e libera, o que segue a ADR 0013 (a trava de recurso abre na dúvida) e não é regressão. Correção mínima: registrar as dimensões (shell como lançador, módulo sem subcomando, versão no nome do interpretador, caminho não normalizado, lançadores fora da tabela) na matriz do analisador e decidir cada uma em cartão próprio. Esforço M. Dono: tech-lead.

**Conferido sem achado (PROCESSO-ORFAO não forçável).**
- `pid_vivo` (`:152-168`): só passa a dar morto para o zumbi (`Z`, `X`) e para o pid cujo início (`/proc/<pid>/stat`, campo 22, índice 19 depois do `)`, conferido) difere do gravado. Um agente não muda o início de um processo vivo; o estado `Z` só aparece com a sessão dona morta. `PermissionError` agora segue para a leitura do `/proc` e, se ela falha (por exemplo `hidepid`), volta ao vivo, como antes. Trava sem `inicio` (antiga) ou `/proc` de outro namespace (checagem `/proc/self` contra `os.getpid()`, `:140`) mantém o comportamento da base.
- A saída da fila (`:326-327`) só afeta o próprio hook e falha fechado (bloqueia o próprio comando); o `finally` solta o `flock` e apaga a senha, coberto por `test_sessao_que_acabou_sai_da_fila_sem_pegar_a_vez`.
- O único jeito de um agente liberar a vez de outro continua o de antes: apagar ou reescrever `pesado.json` (documentado em `docs/hooks.md`); o campo `inicio` novo não abre caminho que a escrita do arquivo já não abrisse.
- Pré-filtro (`:231`): `all(m in texto for m in p.split())` é superconjunto do `p in texto` da base; não descarta nada que a base examinava.
- `palavra_casa` (`:210-213`): exige `/` antes do molde (`/x/xbin/forge-testes` não casa, testado) e só amplia o que conta como pesado; `/x/bin/forge-mutante --listar` segue leve, `--listar x` vira pesado (correto).
- Nenhum segredo, rede, escrita fora de `.forge/run/` ou custo (`R-CUSTO`) no diff.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: `gitleaks`, Semgrep, `zizmor` e `actionlint` ausentes do PATH (lacuna; o diff não toca workflow). Busca manual por padrões de credencial no diff: nada.
