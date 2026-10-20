---
tipo: revisao-seguranca
contrato: 1
pedido: suite-concorrente
branch: melhoria/suite-concorrente
commit: aed7b97a61e2e0449cec5741175fba9d44164631
parecer: reprovado
revisor: forge:security-engineer
data: 2026-10-20
---
# Review de segurança: suite-concorrente

Escopo: `git diff 50997b72e65d11a7cace0bbc5d4aaf5a55b68d60 aed7b97a61e2e0449cec5741175fba9d44164631` (trava `flock` e `--status` em `.githooks/pre-push`, seção nova em `docs/hooks.md`, `tests/test_pre_push_trava.py`, fragmento `changelog.d/suite-concorrente.md`).

## Gatilhos
Controles do Forge (R-SEGURANCA): `.githooks/pre-push` é o hook que barra envio direto para develop, homolog e main (R-MAIN, R-FLUXO), histórico reescrito (R-VERIFY) e roda a suíte antes do envio.

## Achados
- A1 (bloqueante) .githooks/pre-push:23 · o modo --status olha só $1, que no git é o nome do remoto; com um remoto chamado --status e outra suíte rodando, o hook sai 0 antes do laço: não roda a suíte e não barra envio direto para develop, homolog ou main

## Detalhe dos achados
Verificações pedidas, com resultado:

- **A trava não pode ser usada para pular a suíte.** Falha em um caminho (A1). No caminho normal, todas as saídas antes da suíte são `exit 1` (pasta, link, `FORGE_TRAVA_ESPERA` inválido, abertura da trava, limite estourado: `.githooks/pre-push:18-22,62-69`), e o único `exit 0` depois do laço vem depois da suíte verde (`:72-73`). O problema é o `--status` (`:23-29`): o git chama o pre-push com `$1` = nome do remoto e `$2` = URL, e o ramo `--status` roda antes do laço que lê as refs.
  - Evidência: num repositório descartável no `$TMPDIR`, com outro processo segurando a trava, `git -c core.hooksPath=<worktree>/.githooks -c remote.--status.url=<bare local> push -- --status develop` imprimiu `suíte do Forge rodando ()` e o push de `develop` entrou (rc 0). O mesmo push por URL esperou a vez e rodou a suíte. O `-c remote.--status.url=` fica só na memória: não precisa gravar o `.git/config`, que é protegido no sandbox.
  - Caminho de ataque: um agente (ou um comando colado) que queira enviar sem a suíte, ou direto para develop, homolog ou main, num momento em que outra suíte roda, e esse é justamente o caso que a entrega trata. Os contornos que já existiam (`--no-verify`, `core.hooksPath`) estão nomeados no `hooks/conformidade.py` (docstring e `:783`, `:964-968`); este não está, então a entrega abre um contorno novo de um controle do Forge (R-CONFORMIDADE). A proteção da branch no GitHub e o CI continuam do lado do servidor; o hook local é a defesa que a fábrica documenta para ninguém enviar direto.
  - Severidade: média (precisa de ação deliberada e de uma suíte concorrente; o ganho é pular a suíte e o bloqueio de envio direto).
  - Correção mínima: só entrar no modo `--status` quando o hook é chamado à mão com um argumento só (o git sempre passa dois): `if [ "$#" -eq 1 ] && [ "$1" = "--status" ]; then`. Mais um teste: `pre-push --status <url>` com a trava presa não sai 0 sem rodar a suíte, e envio para develop continua barrado. Esforço P. Dono: tech-lead.
- **Recusa link simbólico.** Sim, na hora da checagem (`:19-22`); conferido pelo teste `test_trava_que_e_link_simbolico_e_recusada`. Ver R1 sobre a janela entre a checagem e as aberturas.
- **Recusa arquivo de outro usuário.** Não há checagem de dono no código; a recusa depende do kernel (`fs.protected_regular` e `fs.protected_symlinks`, não legíveis neste ambiente) e só importa quando a trava cai numa pasta gravável por outro usuário. Ver R1.
- **Processo morto não deixa a trava presa.** Sim: `flock` em descritor; o kernel solta a trava quando o último descritor fecha. O descritor 9 passa ao `python3` da suíte (que segura a trava enquanto roda, o que é o certo) e não passa aos subprocessos dele (`subprocess` fecha descritores por padrão). Conferido pelo teste `test_trava_orfa_de_processo_morto_e_liberada`.
- **Caminho fora do repositório e de pasta gravável por outro usuário.** Fora do repositório, sim (`:10`, `$XDG_RUNTIME_DIR`, `$TMPDIR` ou `/tmp`). Pasta gravável por outro usuário: não garantido. Neste ambiente as duas primeiras são do usuário e não graváveis por outros (`/run/user/1000`, `/tmp/claude-1000` com 700), mas o terceiro degrau `/tmp` é gravável por todos e o `$TMPDIR` não é conferido (pode ser `/tmp`). Ver R1.
- **`FORGE_TRAVA_ESPERA` não contorna nada.** Sim. `:62` aceita só dígitos (vazio, `-1` e ` 5` saem com rc 1); `0` com trava presa sai com rc 1 sem rodar a suíte; um valor enorme (`99999999999999999999999`) faz o `flock` falhar e o hook sai com rc 1. Em nenhum caso a suíte é pulada com saída 0; o valor só muda quanto tempo se espera.
- **Sem rede (R-CUSTO).** Sim: o hook usa só `flock`, `id`, `date`, `cat` e o `python3 -m unittest` que já rodava; os testes novos usam `git init` local e `subprocess`, sem rede.

Recomendações (não bloqueantes):

- R1 (baixa) `.githooks/pre-push:10` e `:71` · quando a trava cai em `/tmp` (ou num `$TMPDIR` compartilhado), outro usuário da máquina pode criar antes `forge-suite-<uid>.lock`: com as proteções do kernel ligadas, o envio da vítima falha fechado (rc 1, negação de serviço local, nunca pula a suíte); com elas desligadas, o outro usuário segura a trava e, ao soltar, troca o arquivo por um link; a linha `:71` reabre a trava pelo caminho com `>` (trunca), depois da checagem de link em `:19`, e escreveria `pid ...` no alvo do link. Caminho realista só em máquina compartilhada com o kernel sem as proteções; em estação de um usuário só, nenhum. Correção mínima: escrever o pid pelo descritor já aberto (`printf ... >&9`, aceitando o acréscimo, ou truncar por `/proc/self/fd/9`), conferir `[ -O "$trava" ]` depois de abrir e, para `/tmp` e `$TMPDIR`, usar uma subpasta `forge-<uid>` criada com `mkdir -m 700` e conferida (dono e não link). Esforço P. Dono: tech-lead.
- R2 (informativa) `.githooks/pre-push:27` e `:65` · o conteúdo da trava vai para a tela sem filtro (`cat`); quem escreve a trava é o mesmo usuário nas pastas privadas, então não há caminho realista; com R1 resolvida, nada a fazer.
- R3 (informativa) o limite já registrado no pedido (sandbox e terminal podem usar pastas diferentes e não se enxergar) é de R-TETO, não de segurança: a suíte continua rodando nos dois lados. A alternativa do pedido (caminho fixo `/tmp/forge-suite-<uid>.lock`) piora R1; se for adotada, junto com a subpasta 700 e a checagem de dono.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Revisão manual do diff; execução local do hook em repositório git descartável no `$TMPDIR` (sem rede) e de `python3 -m unittest tests.test_pre_push_trava` (7 OK). `gitleaks`, `osv-scanner`, `semgrep`, `zizmor`, `actionlint` e `shellcheck` não estão no PATH (lacuna; o diff não toca dependência, workflow nem segredo, e o CI roda o shellcheck). A suíte completa não foi rodada por esta revisão (fica com o QA; a entrega registra 958 OK).
