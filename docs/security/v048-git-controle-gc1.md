---
tipo: revisao-seguranca
contrato: 1
pedido: v048
branch: melhoria/v048-git-controle-gc1
commit: 29bdda157d3e984cf5cafd71c9647874b4769f1b
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-28
---
# Review de segurança: v048 (E3.4, PR #957, GC1 GIT-CONTROLE-CONFIG-DA-COPIA)

1ª rodada completa no head `29bdda15`, contra o mapa da E3.1 (`docs/anexos/git-controle-config-2711.md`, seções 2 e 3.1) e o diff `1ced5c09...29bdda15` (8 arquivos, `bin/forge_git.py` e `tests/test_forge_git.py`). Não há modelo de ameaças desta família em `docs/security/ameacas/` (a linha nova é do GC7, anexo 3.2); o requisito vem do anexo.

## Gatilhos
Gatilhos: execução fora do sandbox (hooks), config e arquivos de `.git` graváveis pelo time, rede e credencial do git, controle que analisa entrada (lista positiva de subcomandos).

## Achados
- A1 (bloqueante) bin/forge_git.py:89 · Submódulo fura o INDICE: com a config de topo limpa (config_permitida True), um gitlink e filter.clean na config do submódulo com info/attributes dele, status, diff, checkout, switch e commit --dry-run executam o programa (S1, S2). Recusar INDICE com gitlink no índice.
- A2 (recomendado) bin/forge_git.py:82 · REATIVA compara a opção inteira, mas o git aceita prefixo de opção longa: cat-file --textc e --filt e grep --textc (LEITURA, sem conferir config) rodam textconv e filtro da cópia; e --output= de log, show e diff grava arquivo onde quem chama mandar.
- A3 (recomendado) bin/forge_git.py:85 · A opção de leitura vale em qualquer posição: worktree add list passou como leitura e rodou o smudge da config da cópia; remote -v add gravou remote novo. Exigir a ação no 1º argumento de remote e worktree, e branch só com as opções de listagem.
- A4 (recomendado) bin/forge_git.py:43 · Corpus de legítimos sem o clone principal: as chaves branch.*.vscode-merge-base e branch.main.github-pr-owner-number dele ficam fora da PERMITIDAS, e o INDICE recusa lá. Pôr o conjunto real de chaves do clone principal no corpus e decidir se o GC2 chama o INDICE nele.

## Sondas
- S1 · forge_git.git(copia, "status", "--porcelain"); copia com config de topo só core.* e user.*, gitlink sub no índice, filter.mal.clean=<programa> em sub/.git/config, "* filter=mal" em sub/.git/info/attributes, sub/f sujo · espera: marcador ausente · obtido: rc=0, marcador gravado
- S2 · mesma copia da S1 (com .gitmodules ignore = none), forge_git.git com diff; checkout HEAD; switch --detach HEAD; commit --dry-run --allow-empty · espera: marcador ausente nos quatro · obtido: marcador gravado nos quatro (ls-files, add, commit -m, reset, restore, rm, mv: ausente)

## Detalhe dos achados

**A1 (alta).** Evidência: `bin/forge_git.py:89-90` confere só `<git-common-dir>/config` (`:71-76`); os comandos do INDICE (`:40-41`) entram no submódulo (o git roda `status` filho dentro dele), e a config e o `info/attributes` do submódulo nunca são lidos pela função. Os `-c` do `NEUTRO` chegam ao filho (hooks e fsmonitor ficam fechados), mas o driver tem nome escolhido pelo atacante e não há chave que desligue o `info/attributes`. Caminho de ataque: o agente, dentro do sandbox, monta na cópia um gitlink (`update-index --cacheinfo 160000,...`) e, no `.git` do submódulo, `filter.<x>.clean` mais `* filter=<x>`; quando um hook (no GC2, o `status` de `bin/forge-check`, anexo 3.2) chamar `forge_git.git(<cópia>, "status")`, o programa roda fora do sandbox, com a rede e as credenciais do hook. É o mesmo ganho da pior linha do anexo (S-A12), e o docstring (`:12`) declara o submódulo como resíduo "do anexo, seção 4", que não o lista e que ninguém aceitou. Controle de correção (sonda local): `-c diff.ignoreSubmodules=all` no `NEUTRO` **não basta**, porque o `submodule.<nome>.ignore = none` do `.gitmodules` (arquivo da árvore, gravável) vence a chave; `--ignore-submodules=all` na linha fecha `status` e `diff`, mas `checkout` e `switch` não têm a opção. Correção mínima: em `montar`, para `sub in INDICE`, recusar (falha fechada, `Recusado`) quando `ls-files --stage` (rodado com `NEUTRO`, sem recursão) listar entrada de modo `160000`; teste com a cópia da S1 nos 11 subcomandos do INDICE e uma linha nova da matriz (dimensão "repositório aninhado"). O corpus do Forge não tem gitlink (`ls-files -s` sem `160000`, sem `.gitmodules`). Esforço P. Dono: tech-lead (autor da E3.2).

**A2 (média, depende de quem chama).** Evidência: `bin/forge_git.py:82` (`arg.split("=", 1)[0] in REATIVA`), sonda local: `cat-file --textc HEAD:f`, `cat-file --filt HEAD:f` e `grep --textc a HEAD` executam o driver de `info/attributes` + config da cópia; `show`, `log` e `diff-tree` com `--textc` falham porque o `--no-textconv` posto antes conflita, por sorte e não por desenho. `log -1 --output=<caminho>` gravou o arquivo pedido. Caminho: só existe se um chamador do GC2 a GC6 repassar opção vinda do agente; hoje não há chamador. Correção mínima: em `montar`, recusar toda opção longa que seja prefixo de um item da REATIVA (de `--e` em diante, o mesmo para `--t`, `--sh`, `--f`, `--pa`, `--op`) e acrescentar `--output` à REATIVA, que fica com: `--ext-diff`, `--textconv`, `--show-signature`, `--filters`, `--path`, `--open-files-in-pager`, `--output`; testes das abreviações. Esforço P. Dono: tech-lead.

**A3 (média, depende de quem chama).** Evidência: `bin/forge_git.py:85` testa interseção com o resto inteiro; `worktree add list` (o caminho "list" satisfaz a lista) fez checkout com o smudge da config da cópia (o `worktree` não é INDICE e não confere config), e `remote -v add x <url>` gravou `remote.x.url`. Caminho: igual ao A2, só com chamador que monte ação a partir de dado do agente. Correção mínima: para `remote` e `worktree`, exigir `resto[0]` no conjunto; para `branch`, recusar qualquer argumento que não seja opção de listagem, nome de padrão ou revisão do `--contains`. Esforço P. Dono: tech-lead.

**A4 (baixa, falha fechada).** Evidência: `bin/forge_git.py:43-45` e `config_permitida('/workspaces/Forge')` devolve `False` (chaves `branch.<nome>.vscode-merge-base`, `branch.main.github-pr-owner-number`). Não abre execução; é o corpus de legítimos do analisador incompleto, que vira recusa falsa quando o GC2 apontar para o clone principal. Correção mínima: o teste de legítimos ganha uma cópia com o conjunto real de chaves do clone principal; se o GC2 rodar INDICE lá, a PERMITIDAS aceita essas duas chaves por nome (nenhuma aponta programa). Esforço P. Dono: tech-lead.

Conferido e coberto (anexo 3.1, itens 1 a 4): ambiente sem `GIT_*` e `XDG_CONFIG_HOME` (`:52-55`, teste `test_ambiente_de_quem_chama_nao_vale`); `-c` por protocolo e demais chaves antes do subcomando (`:25-31`, testes de uploadpack, insteadOf, sshCommand, credential.helper); `--no-ext-diff --no-textconv --no-show-signature --no-filters` (`:37-39`), e a sonda local mostrou que esses flags chegam ao `diff` filho do submódulo (`log -p`, `show` e `diff-tree -p` com `diff.submodule=diff` e textconv no submódulo: marcador ausente); config lida com `--no-includes` e `include.*`/`extensions.worktreeconfig` recusados pela PERMITIDAS; `merge_tree` e `rede` em repositório neutro sob `~/.forge/maquina/neutro` (`:23`, `:99-139`), e a escrita nessa pasta é negada pelo sandbox (conferido: `mkdir` e `touch` dão "Read-only file system"); `rede` só https e sem config da cópia. A janela de corrida (anexo seção 4) continua resíduo registrado.

Catraca e teste de custo (ordem do dono 28/11 07:41): `tests/catraca.py` (modo regras, base `origin/develop`) rc=0 local e job `catraca` verde no run 46136709586; `tests/test_forge_git.py` 19 testes OK local; teste de custo dos hooks (tests/test_hooks_volta_corpus.py) 33 testes OK local; o diff não toca `hooks/`. CI do head: todos os checks verdes (`gh pr checks 957`).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: sondas locais em repositórios descartáveis no `$TMPDIR` (git 2.43), sem rede e sem hook real. Faltaram no PATH: `gitleaks`, Semgrep CE, `osv-scanner`, `zizmor` e `actionlint` (lacuna; o diff não traz segredo à leitura, nem dependência ou workflow).
