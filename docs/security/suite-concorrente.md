---
tipo: revisao-seguranca
contrato: 1
pedido: suite-concorrente
branch: melhoria/suite-concorrente
commit: 82c32f816268d0f32ee8298946043b9b3a0ff22b
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-20
---
# Review de segurança: suite-concorrente

Revalidação por delta (E1.3) da volta do autor (E1.1v). Escopo: `git diff af586f1caea8df7b953b3f77d79f3c92527aff92 82c32f816268d0f32ee8298946043b9b3a0ff22b` (`.githooks/pre-push`, `docs/hooks.md`, `tests/test_pre_push_trava.py`, `changelog.d/suite-concorrente.md`); `forge-check delta --parecer` sobre o parecer anterior (commit revisado aed7b97) lista os mesmos trechos. Como `.githooks/pre-push` é controle do Forge, o hook foi relido inteiro em 82c32f8, não só as linhas do delta. Substitui o parecer anterior (reprovado em aed7b97, A1).

## Gatilhos
Controles do Forge (R-SEGURANCA): `.githooks/pre-push` barra envio direto para develop, homolog e main (R-MAIN, R-FLUXO), histórico reescrito (R-VERIFY) e roda a suíte antes do envio.

## Achados

## Detalhe dos achados
Verificações pedidas, com resultado:

- **A1 fechado.** `.githooks/pre-push:50` só entra no modo `--status` com `[ "$#" -eq 1 ] && [ "$1" = "--status" ]`; o git sempre passa nome e URL do remoto. Reproduzido num repositório descartável no `$TMPDIR` com outro processo segurando a trava: `git -c remote.--status.url=<bare> push -- --status feat` esperou e saiu 1 com a mensagem do limite (antes, saía 0 sem rodar a suíte); `push -- --status feat:refs/heads/develop` saiu 1 com o bloqueio de envio direto; `pre-push --status x` (dois argumentos) seguiu o caminho normal; `pre-push --status` sozinho saiu 0 com a trava presa e 1 sem ela; solta a trava, o push rodou a suíte e saiu 0. Cobertura nos testes `test_remoto_chamado_status_segue_o_caminho_normal` e `test_envio_direto_continua_barrado_com_trava_e_com_status`.
- **R1 atendida.**
  - Abertura uma vez, sem seguir link: `:95-98` recusa link antes de abrir; `:100` abre com `>>` (sem truncar); `:101` (`trava_confere`, `:42-47`) confere de novo que o caminho não é link e que o arquivo **aberto** (`-O /proc/self/fd/9`) é do próprio usuário. No `--status`, `:55` abre só para leitura (não cria nem trunca) e `:56` faz a mesma conferência.
  - `-O` depois de abrir: sim, sobre o descritor (`:43`), não sobre o caminho.
  - Pid pelo mesmo descritor: `:110` escreve com `>&9`.
  - Subpasta `forge-<uid>`: `:22-35`, criada com `mkdir -m 700` (`:24`, o modo explícito ignora o umask) e conferida (`:30`: não é link, é pasta, é do próprio usuário); qualquer falha devolve 1 e o hook sai 1 (`:94`). Testes `test_recuo_cria_subpasta_700_do_usuario`, `test_subpasta_que_e_link_e_recusada`, `test_trava_link_dentro_da_subpasta_e_recusada`, `test_subpasta_que_nao_da_para_criar_falha_fechado`.
- **`: > /proc/self/fd/9` (`:109`), observação do conferente: aceito.** A reabertura por `/proc/self/fd/N` não resolve o caminho de novo: o kernel segue o link mágico para o mesmo arquivo já aberto no descritor 9 (o que o `-O` de `:101` conferiu) e o trunca. Sonda: abri um arquivo no descritor 9, troquei o caminho por um link para outro arquivo e rodei `: > /proc/self/fd/9; printf ... >&9`; o alvo do link ficou intacto e o pid foi para o arquivo original. A R1 pedia que nada fosse escrito por caminho depois da conferência; isso vale. Sem `/proc`, o `-O /proc/self/fd/9` de `:43` é falso e o hook sai 1 antes (falha fechada); se só o truncamento falhasse, o hook seguiria para a suíte (nunca a pula). O `:` roda no próprio shell do hook, então `/proc/self` é o processo que segura o descritor.
- **Pasta de recuo sem escrita pulada (DECISÃO TÉCNICA de 2026-10-20): aceito, não é falha de segurança.** `:16` pula a pasta que não existe ou não é gravável e tenta a próxima; a pasta escolhida passa pelas mesmas conferências (subpasta 700 do usuário, não link, arquivo aberto do usuário), e sem nenhuma válida `:38-39` devolve 1 e o hook sai 1. Sonda: `XDG_RUNTIME_DIR` vazio, `$TMPDIR` com modo 500 e `/tmp` sem escrita no sandbox: saída 1 com a mensagem de pasta. Pular uma pasta não dá a ninguém um caminho para escolher a trava (o atacante não torna sem escrita uma pasta do usuário nem a `/tmp` do root) e não pula a suíte; o efeito possível é dois ambientes usarem travas diferentes, limite de R-TETO já registrado no pedido, não de segurança.
- **Outro dono, conferido por leitura pelo autor: certo no código.** Subpasta de outro usuário: `:30` (`! -O "$sub"`) devolve 1, também no `--status` (`:26` só devolve o caminho sem conferir quando a subpasta não existe, e aí `:53` diz que não há suíte, sem abrir nada). Arquivo de trava de outro usuário: `:43` sobre o descritor aberto, no caminho normal e no `--status`. Não há segundo usuário neste ambiente para reproduzir; a leitura basta, porque o teste é o `-O` do bash sobre o arquivo aberto.
- **Nenhum caminho da trava pula a suíte (falha fechada).** Todas as saídas antes da suíte são `exit 1` (`:51-53`, `:55-57` só no `--status` de um argumento; `:93`, `:94`, `:95-98`, `:100`, `:101`, `:104-107`); o único `exit 0` do caminho normal é `:112`, depois da suíte verde em `:111`. O `9>&-` em `:111` tira o descritor da suíte, e a trava continua presa pelo shell do hook enquanto ela roda.
- **Sem rede (R-CUSTO).** O hook usa só `id`, `mkdir`, `flock`, `cat`, `date` e a suíte que já rodava; os testes novos usam repositórios locais e `subprocess`. Nenhuma ocorrência de `http`, `curl`, `urllib` ou `socket` no hook nem em `tests/test_pre_push_trava.py`.

Recomendações (não bloqueantes):

- R1 (baixa) `.githooks/pre-push:30` · a subpasta `forge-<uid>` que já existe é conferida por dono e tipo, não por modo: se o próprio usuário a deixou gravável por outros (por exemplo, 777), outro usuário pode plantar nela um link para um arquivo do usuário e trocá-lo de volta entre a abertura (`:100`) e a conferência (`:101`), e o truncamento de `:109` cairia nesse arquivo. Sonda: uma `forge-<uid>` 777 do usuário foi aceita. Caminho realista só em máquina compartilhada, com a pasta afrouxada pelo próprio usuário e uma corrida ganha; nunca pula a suíte. Correção mínima: recusar a subpasta com escrita para grupo ou outros (`find "$sub" -maxdepth 0 -perm /022` não vazio → `return 1`) e um teste. Esforço P. Dono: tech-lead.
- R2 (informativa) `.githooks/pre-push:18` · o `$XDG_RUNTIME_DIR` é usado sem subpasta nem conferência de dono, por ser privado do usuário; se a sessão o apontar para uma pasta compartilhada, a trava fica direto nela (sonda: aceito). A variável vem do ambiente do próprio usuário, então não há caminho de outro usuário; o `-O` sobre o descritor continua valendo. Nada a fazer agora; se a R1 for feita, a mesma conferência de modo pode valer aqui.
- R3 (informativa) o limite de R-TETO já registrado (sandbox e terminal com pastas de trava diferentes) não muda com esta volta.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Revisão manual do delta e do hook inteiro em 82c32f8; sondas com uma cópia do hook (`git show`) em repositório git descartável no `$TMPDIR`, sem rede e sem trocar o HEAD da worktree; `python3 -m unittest tests.test_pre_push_trava` (15 OK); `forge-check delta --parecer`. `gitleaks`, `osv-scanner`, `semgrep`, `zizmor`, `actionlint` e `shellcheck` não estão no PATH (lacuna; o delta não toca dependência, workflow nem segredo, e o CI roda o shellcheck). A suíte completa roda no pre-push do envio deste parecer.
