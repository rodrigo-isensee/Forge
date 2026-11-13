---
tipo: revisao-seguranca
contrato: 1
pedido: v046
branch: melhoria/conformidade-curinga
commit: abfccb7e24fb7ef005e53080d81d60c3896234cc
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-12
---
# Review de segurança: v046 (E20.31, conformidade-caminho-git, revalidação por delta)

Delta revisado: `cddc8915..3b3d7a67` (volta 3, E20.29), lido por `forge-check parecer delta` e `git show`. No domínio: `hooks/conformidade.py` (`origens_do_rev_parse`, a escolha da regra genérica em `link_em_protegido` e a variável do `.git` que sobrevive à leitura do lançador), `bin/forge-testes` (A2) e as 6 fixtures `gitcomum-v3-*`. O merge da develop (`4f74842c`) não toca o domínio desta revisão. Parecer anterior: aprovado no `cddc8915` (E20.19).

Veredito: **reprovado**. A3 e A2 estão certos, e a liberação nova cumpre o que promete na grafia comum: `-S`, `-t`, `--symbolic` e `--` fecham, destino protegido (também por link para `.git`) recusa, e `cp -s`/`cp -l` com destino protegido recusam. Mas a origem com curinga ou chaves (`"$(git rev-parse --git-dir)"/c?nfig`) passa a escapar das regras específicas (`.git/config`, `.git/hooks/`, `.git/forge/`): o hook confere o nome literal `c?nfig`, que só casa a regra genérica, e a regra genérica agora se libera. Recusava no `cddc8915` e passa no head (A11, bloqueante). É contra o requisito da própria entrega ("as específicas seguem barrando", `hooks/conformidade.py:1070`) e a correção é pequena. A develop também deixa passar (lá a substituição é opaca), mas esta branch existe para fechar essa família. Os outros resíduos da liberação só tocam a regra genérica (A12) ou já existiam (A13): ficam em cartão.

Atualização (E20.41, DECISÃO DO DONO de 12/11 18:20, opção A): **aprovado** no head `abfccb7e` da branch `melhoria/conformidade-curinga`. A volta 5 fecha o A11 deste parecer: as sondas S6 a S9 e as grafias da volta 4 (S10 a S14, colchete, negação, classe e `nocaseglob`) recusam com rc 2; o detalhe está em `docs/security/conformidade-curinga.md`. Os recomendados (A12, A13, A4 a A10) seguem como cartões. O texto abaixo é o da E20.31 e fica como histórico.

## Gatilhos
`R-SEGURANCA`: controle do Forge (hook `conformidade`, guarda de escrita e de link em `.git/`), analisador de comando.

## Achados
- A12 (recomendado) hooks/conformidade.py:1076 · a liberação também cobre `commondir`, `worktrees/<n>/gitdir` e `config.worktree`, a sentinela FORGE_DIR_DO_GIT atribuída na linha e a variável redefinida depois do rev-parse (`d=$(…); d=.git`); só a regra genérica; cartão
- A13 (recomendado) hooks/conformidade.py:1046 · já existia (develop e cddc8915): `d=.git; ln "$d"/config h` passa rc 0; a escrita recusa a variável lida como .git (`d=.git; cp x "$d"/config` rc 2), o link não; cartão com prioridade
- A4 (recomendado) hooks/conformidade.py:1001 · cd para o opaco segue passando rc 0 (`cd "$(git rev-parse --git-dir)/hooks" && cp ../../x pre-push`); já existia (AR-7); cartão de segurança
- A5 (recomendado) hooks/conformidade.py:1516 · parcial: `mv x --target-directory=.git/hooks` passa rc 0; `mv` está em TODOS_OS_ARGUMENTOS (linha 124), que pula toda palavra que começa com `-`; cartão de segurança com prioridade
- A7 (recomendado) hooks/conformidade.py:983 · falso positivo segue (`cp x "$(mktemp -d)/config"`, `cp x $TMPDIR/logs/a.log`), com a mensagem que manda usar o caminho literal; limite aceito desta entrega; cartão
- A8 (recomendado) hooks/conformidade.py:1527 · opção de destino colada: `cp -t.git/hooks x`, `cp -t.git/config x`, `install -t.git/hooks x`, `mv -t.git/hooks x` e `cp -t"$(git rev-parse --git-path hooks)" x` passam rc 0; já existia; cartão com prioridade
- A9 (recomendado) hooks/conformidade.py:1001 · destino opaco sem resto cujo valor é o .git por indireção fora da família rev-parse: `cp config "$(echo .git)"` passa rc 0; ofuscação deliberada; cartão
- A10 (recomendado) hooks/conformidade.py:365 · resíduo da leitura por palavras: operador colado (`--git-dir;`, `--git-dir&&:`, `--git-dir|cat`), `eval '…'`, `sh -c '…'`, `$'--git-dir'` e `$(…)` aninhado sem aspas, sem resto, passam rc 0; cartão com prioridade

## Sondas

## Detalhe dos achados
Método: o montador de `tests/test_hooks.py` (`Fixture.montar`, `rodar`), papel `forge:tech-lead`, projeto em `melhoria/x` (e worktree em `melhoria/w`), com `x`, `config` e `pre-push` na raiz; só repositórios temporários. Comparei três árvores (`git archive`): o head `3b3d7a67`, o `cddc8915` e a develop `a1318e88`. Abusos pedidos pelo brief, 87 casos:
- origem que só parece vir de rev-parse: a sentinela `FORGE_DIR_DO_GIT=.git; ln "$FORGE_DIR_DO_GIT"/HEAD h` passa (A12), e com `/config` ou `/hooks/pre-push` recusa; `$(git rev-parse --show-toplevel)/.git/HEAD` recusa;
- variável redefinida: `d=$(…); d=.git; ln "$d"/HEAD h` passa (A12), com `/config` recusa; `d=.git; d=$(…)` libera, como deve;
- destino que é link para `.git` (`g -> .git`): `ln … g`, `ln … g/x` e `cp -l x g/config` recusam;
- `cp -s` e `cp -l` com destino protegido (`.git/config`, `.git/hooks/pre-push`, `.git`) recusam;
- `-S`, `-t`, `--symbolic`, `--` e `-S` no fim (fixture) fecham a liberação; `cp -rl` e `cp -al` da pasta `.git` recusam (regra da raiz `.git`);
- normalização (`/../.git/config`, `/./config`, `//config`, `hooks/../config`) recusa.

**A11 (alta, bloqueante; dimensão nova "curinga e chaves na origem liberada").** Evidência: `hooks/conformidade.py:1076` libera o índice da origem só pela presença da sentinela, e `hooks/conformidade.py:1059` descarta o achado quando ele é o da regra genérica. Com `c?nfig`, `[c]onfig` ou `conf{i,}g`, o caminho resolvido é o nome literal com o curinga, que não casa `.git/config` e só casa `.git/`; a regra genérica se libera e nada mais confere. Antes da volta 3, a genérica recusava (S6 e S7: rc 2 no `cddc8915`). Caminho de ataque: um agente barrado ao editar `.git/config` (por exemplo, para trocar `core.hooksPath` e calar o `pre-push`, ou pôr `core.fsmonitor` para executar código) cria o link físico `h` com uma grafia de curinga e grava em `h` num comando seguinte. `h` não é caminho protegido, e o link físico não se resolve por `realpath`. A S9 prova a gravação. É ofuscação deliberada, e `d=.git; ln "$d"/config h` (A13) já existia. Mesmo assim bloqueia: é defeito provado contra o requisito declarado pela entrega e pelo brief da E20.31 ("regras específicas da origem mantidas"), regride o que o `cddc8915` aprovado recusava, e a correção é de poucas linhas. Correção mínima, em `origens_do_rev_parse`: origem com `{` não se libera (falha fechada); origem com curinga (`CURINGA`, `hooks/conformidade.py:315`) só se libera se nenhum nome que o glob expande no diretório do git (o mesmo de `pastas_do_curinga`) cair em regra que não seja a genérica. O par legítimo de `tests/test_conformidade_verde.py:175` (`forge-suite-Xverd?`, que não casa nada) continua livre. Fixtures: S6, S7 e S8 (6 variantes), e o legítimo `ln "$(git rev-parse --git-dir)"/HEA? h`. Esforço P. Dono: tech-lead.

**A12 (baixa, recomendado; da liberação nova, só a regra genérica).** A liberação cobre o que o motivo da regra genérica cita (`commondir`, `worktrees/<n>/gitdir`), e o link físico deles permite redirecionar onde o worktree acha o repositório. Também cobre `config.worktree`, a sentinela `FORGE_DIR_DO_GIT` escrita à mão e atribuída na linha, e a variável redefinida depois do rev-parse. O `cddc8915` recusava tudo isso. A develop deixa passar, e o A9 dá a mesma capacidade a quem ofusca. Correção mínima: não liberar os nomes `commondir`, `gitdir`, `config.worktree` e o que fica em `worktrees/`; tratar a sentinela atribuída e a variável redefinida por valor não rev-parse como literais. Cartão. Esforço P. Dono: tech-lead.

**A13 (média, recomendado; já existia).** `link_em_protegido` não aplica a regra "valor de variável lido como .git" que a escrita aplica (`hooks/conformidade.py:983`). Por isso `d=.git; ln "$d"/config h` e `ln "$d"/HEAD h` passam no head, no `cddc8915` e na develop. Correção mínima: no link, a origem ou o destino com variável que o hook não resolve e cujo resto cai num nome do git recusa, como na escrita (com o falso positivo do A7). Cartão com prioridade. Esforço P. Dono: tech-lead.

**A1 da E20.29 (liberação) e A3.** A liberação da grafia comum está certa: as 6 fixtures `gitcomum-v3` passam, e com elas o par legítimo do `test_conformidade_verde`. A3: `builtin -iu X d=$(git rev-parse --git-dir); cp x $d` recusa. Em `env d=$(…) true; ln "$d"/HEAD h` o hook libera, e o bash expande `$d` vazio (`/HEAD`): sem efeito. A2: `test_hook_git_comum` está em `FORGE_CHECK` (`bin/forge-testes:99`).

**A4, A5, A7, A8, A9 e A10.** Sem mudança desde a E20.19, com as linhas do head (A5 em 1516, A8 em 1527). Correções mínimas como no parecer anterior (`0fc55eac`).

## Riscos aceitos e ferramentas
Nenhum risco aceito. CI do PR #507, run 43289298967 no head `3b3d7a67`: só `catraca`, `instalação (python 3.14)` e `árvore já provada na develop` passaram. `bateria (passos)` falhou no passo de pareceres (`R-REVIEW: PR toca bin/forge-testes … parecer … desatualizado`), e por isso as partes da suíte foram puladas. A bateria completa não rodou no head e a prova dela fica para o CI depois dos pareceres. Na máquina, um módulo por vez: `test_hook_git_comum` (1 OK, 16 s), `test_testes_tocados` (149 OK, 1 pulado), `test_conformidade_verde` (11 OK) e `test_hooks_volta_lancador` (22 OK, 25 pulados). Ferramentas: `forge-check parecer delta`, `git archive`, o montador de fixtures, `gh pr checks` e `gh run view`. Mutantes G20 a G26 e cobertura ficam com o QA (E20.32). `gitleaks`, `semgrep`, `zizmor` e `actionlint` não rodaram: o delta não toca workflow nem segredo, e nada foi instalado (`R-CUSTO`).
