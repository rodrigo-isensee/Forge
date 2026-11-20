---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-pv-b1-registros
commit: 1aed3a743d433c903454422acad73859c12b67b9
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: v0479-pv-b1-registros (PR-VERDE B1, v0478 E57.13)

Escopo: `5ccac0bf..1aed3a74` (`bin/forge-testes` `--registros`, `tests/test_testes_tocados.py` classe `Registros`, specs de mutante, fragmento do changelog). Uma passada, em paralelo ao review e ao QA.

## Gatilhos
Gatilhos: ferramenta de envio do Forge (`bin/forge-testes`, classificada como pesada por `hooks/pesado.py:46`), `git fetch` com o ambiente e a configuração de git da sessão; o diff não toca `hooks/`, `.github/`, `docs/regras/` nem caminho de `PROTEGIDOS`.

## Achados
- A1 (recomendado) bin/forge-testes:919 · `buscar_base` passa o ramo de `--base` cru ao `git fetch`: `origin/--upload-pack=<cmd>` vira opção e executa comando (remoto local), e `origin/+x:refs/heads/y` sobrescreve ramo local; validar o ramo e usar `--end-of-options`.

## Sondas
- S1 · `buscar_base('origin/--upload-pack=touch $d/PWNED;git-upload-pack')` em repositório de brinquedo com origin local · espera: recusa ou fetch do ramo literal · obtido: arquivo PWNED criado, retorno None
- S2 · `buscar_base('origin/+develop:refs/heads/sobrescrita')` no mesmo repositório · espera: recusa · obtido: ramo local `sobrescrita` criado pelo refspec, retorno None

## Detalhe dos achados
**Pergunta do Jarvis: o ambiente da sessão (com `GIT_CONFIG_*`) na busca abre caminho para configuração de git vinda de fora?** Não. O `GIT_CONFIG_COUNT/KEY/VALUE` e o `GIT_CONFIG_PARAMETERS` vêm do processo que chama a ferramenta (a sessão ou o hook que o git lançou com `git -c`), o mesmo principal que já controla `PATH` e o próprio comando; o git nunca recebe configuração do remoto. Esse ambiente já valia, antes deste diff, para todo `git()` da ferramenta (`bin/forge-testes:293`: `merge-base`, `diff`, `ls-files`), e a configuração do repositório (`.git/config`) segue protegida pelo sandbox (ADR 0009). A busca não acrescenta fronteira: só passa a usar, para a rede, o proxy e a credencial que a sessão já entrega. O que importa ao isolamento, os processos que rodam código da branch (os `unittest` dos grupos e o `forge-changelog`), segue com `ambiente_da_copia()` (`bin/forge-testes:950`, sem `GIT_*`, `FORGE_*` nem `CLAUDE_PROJECT_DIR`), e o teste `Registros.test_em_dia_sai_0_sem_gravar_nada_e_sem_o_ambiente_herdado` prova que nenhum `GIT_*`/`FORGE_*` chega a eles; `test_a_busca_usa_o_git_config_da_sessao` prova o lado da busca. Nota de estilo ao `tech-lead`, sem achado: o cabeçalho em `bin/forge-testes:910` diz "sem `GIT_*` herdado", que vale para os subprocessos e não para a busca nem para o `git()`.

**A1.** Evidência: `bin/forge-testes:915` (`base.partition("/")`) e `:919` (`["git", "fetch", "-q", "origin", ramo]`); só o prefixo `origin` é conferido. O `git fetch` aceita opções depois do remoto, então um `ramo` que começa com `-` vira opção (`--upload-pack` executa comando no transporte local e no ssh; `-c`/`--refmap`/`--prune` também passam), e um `ramo` com `:` ou `+` é refspec que grava ramo local, até à força (sondas S1 e S2, git 2.43). Caminho de ataque: hoje o `--base` vem só da linha de comando de quem roda a ferramenta (nenhum hook a chama com `--registros`), logo quem injeta já executa o que quiser; o risco realista é a ferramenta virar um caminho que o classificador de comandos não lê (um `forge-testes --registros --base origin/+develop:refs/heads/main` passa por "conferência só de leitura" e reescreve o `main` local) e, quando o envio passar a chamá-la (PR-VERDE B1 prevê o envio local), um `--base` vindo de configuração ou brief. Severidade: baixa. Correção mínima: em `buscar_base`, recusar o ramo que não casa `[A-Za-z0-9._/-]+`, que começa com `-` ou que contém `..`, devolvendo o aviso "ramo inválido" sem buscar (o `merge-base` seguinte já sai 2 com base que não resolve), e chamar `git fetch -q --end-of-options origin <ramo>`; teste com as duas entradas das sondas. Esforço: P. Dono: autor da E57.2 (`tech-lead`).

Fora isso, sem achado: os comandos dos grupos são constantes (`REGISTROS`, `CHANGELOG`) em lista, sem casca; o `base` só chega ao `forge-changelog` como argumento de lista e ao `git()` como ref depois de `origin/` ou como ref local (o `merge-base` e o `diff` recebem o sha da âncora); a leitura de `tests/pesos-d4.json` falha fechada (rc 2) com JSON ilegível ou que não é objeto; os nomes de módulo novos passam por `MODULO_DE_TESTE.fullmatch` antes de chegar à mensagem; o `ThreadPoolExecutor` com 4 vagas não multiplica a carga além do teto de processos, e `hooks/pesado.py` trata o `--registros` como pesado (falha fechada, fila da máquina).

## Riscos aceitos e ferramentas
Sem risco aceito. Suíte: não rodada aqui (brief: sem suíte local); rodei o teste novo `tests.test_testes_tocados.Registros` (10 testes, OK, árvore limpa depois) e as sondas S1 e S2 num repositório de brinquedo em diretório temporário. O CI do head não foi visto deste ambiente (sem PR; consulta de execuções sem saída); o parecer conta com o CI verde no head, como o `forge-check` exige. Ferramentas ausentes no PATH: varredor de segredos, SAST e linter de workflow (lacuna registrada, sem instalação, `R-CUSTO`); o diff não traz segredo nem workflow.
