---
tipo: revisao-seguranca
contrato: 1
pedido: bp-1
branch: melhoria/bp-1
commit: 95a1140b65db1cccc053cdeb627c1f6b830400c1
parecer: reprovado
revisor: forge:security-engineer
data: 2026-10-17
---
# Review de segurança: bp-1

Escopo: `git diff f636d27c95bd1fdc9137baa830e0f53905863eaf...95a1140b65db1cccc053cdeb627c1f6b830400c1`, 17 arquivos (+370 / -8): `hooks/_comum.py`, `hooks/conformidade.py`, `hooks/vigia.py`, fixtures novas, `tests/test_hooks.py`, ADR 0009 e `docs/hooks.md`. O commit seguinte da branch (`8d8ff69`) só acrescenta `docs/reviews/bp-1.md`, então o código revisado é o mesmo. Revisão estática, com os hooks rodados sobre fixtures descartáveis numa cópia (`git archive`) em `$TMPDIR`, fora da worktree. Não escrevi esta branch.

## Gatilhos
`R-SEGURANCA`: a entrega muda controles do Forge, os hooks `conformidade` e `vigia` e a falha fechada comum (`executar`). Ela corrige o achado 1 (alta) de `docs/security/incidente-bypass-1.md`.

## Veredito
**Reprovado.** As reproduções literais do achado 1 estão fechadas, mas o achado continua aberto: **uma linha ainda desliga todos os hooks e cala o `vigia`** (achado A). O motivo é que a marca que deveria fazer a falha fechar fica em `.forge/run/`, uma pasta que o próprio git apaga. Pela mesma razão, a falha fechada não protege contra as formas de `git rm` que a conferência de caminhos deixa passar (achado B). A marca em `.forge/run/` saiu da proposta P1 do meu parecer do incidente. A falha é do desenho que eu propus, não da implementação.

## O que foi verificado (fechado)
A guarda nova (`hooks/conformidade.py:813-834`) dá rc=2 para:
- `git rm .forge/versao`, `git rm -q --cached .forge/versao` e `git rm -r .forge`;
- `git mv .forge/versao .forge/v` e `git mv .forge .f`;
- `git checkout HEAD~0 -- .forge`, `git checkout HEAD .forge/versao` (sem `--`), `git restore -s HEAD~1 .forge` e `git restore --source=HEAD -- .forge/versao`;
- `git -C .forge rm versao`, `git -C sub rm ../.forge/versao`, `git rm sub/../.forge/versao` e, com cwd em `sub/`, `git rm ../.forge/versao`;
- os curingas que o `glob` do Python alcança: `'.forge/vers*'`, `'.f*/versao'` e `-r '.*'`;
- `':/.forge/versao'`, que o `em_qualquer_lugar` pega.

A marca também não se apaga pelo caminho direto: `rm .forge/run/projeto` dá rc=2 (`.forge/run/` está protegido, `hooks/conformidade.json:32`). Com a marca presente e o `.forge/versao` apagado, `git push --force origin main` dá rc=2 ("sumiu") e o `vigia` avisa `versao-sumiu` no `Stop` (cenário conferido de ponta a ponta).

Falso positivo, sem regressão nos comandos comuns: `git checkout -- src/app.js`, `git restore src/app.js`, `git checkout -- .`, `git restore .`, `git checkout main`, `git checkout -`, `git switch -`, `git checkout -b nova`, `git rm src/app.js` e `git mv src/app.js src/b.js` dão rc=0.

## Achados

### A. A marca em `.forge/run/` é apagada pelo git: uma linha ainda desliga tudo · alta
- **Evidência:** `hooks/_comum.py:91-93`: a marca é `.forge/run/projeto`, e `marcar_projeto` grava `.forge/run/.gitignore` com `*`, então a marca é arquivo ignorado. `hooks/_comum.py:111-116` (`versao_sumiu`): sem a marca, nada falha fechado. A fixture `tests/hooks/conformidade/versao-sumiu-sem-marca-libera.json` confirma esse comportamento. O `git` não passa pela conferência de caminhos nos subcomandos `sparse-checkout`, `clean` e `stash` (`CAMINHOS_NO_GIT`, `hooks/conformidade.py:84`).
- **Reprodução** (cópia descartável, git 2.55.0, depois do `SessionStart` do `vigia` gravar a marca):
  - `git sparse-checkout set src`: o hook dá rc=0 (`conformidade` e `parecer`) e o comando apaga `.forge/versao` **e** `.forge/run/projeto`. Em seguida `git push --force origin main` dá rc=0 nos dois hooks, e o `vigia` no `Stop` dá rc=0 sem aviso.
  - Em duas linhas: `git clean -fdX` (rc=0, apaga a marca e mantém o `.forge/versao`) e depois `git rm '*/versao'` (rc=0, achado B). O resultado é o mesmo: push com rc=0 e `vigia` mudo.
  - `git stash -a` e `git clean -fdx .forge/run` também apagam a marca com rc=0.
- **Caminho de ataque:** o mesmo do achado 1 do incidente. Um agente no projeto, depois de um bloqueio ou levado por conteúdo injetado, roda uma linha que parece inofensiva ("reduzir a cópia de trabalho", "limpar ignorados"). Desse ponto em diante nenhum hook do Forge age e o usuário não recebe aviso.
- **Correção mínima:** gravar a marca onde nenhum comando de cópia de trabalho do git alcance, por exemplo `$(git rev-parse --git-common-dir)/forge/projeto`. Nem `clean`, nem `sparse-checkout`, nem `stash`, nem `reset` mexem em `.git/`. Acrescentar esse caminho a `caminhos` em `hooks/conformidade.json` com `quem: []`, como já acontece com `.git/config` e `.git/hooks/`. Fixtures: `sparse-checkout-sem-versao-bloqueia` (a marca sobrevive e o push dá rc=2), `git-clean-X-mantem-marca` e `vigia` avisando depois do `sparse-checkout`. Resolvido isso, toda forma de sumir com o arquivo que a guarda não vê (`sparse-checkout`, `reset --hard`, `read-tree -mu`, `switch`, `restore -s <ref> .`, `checkout --no-overlay <ref> -- .`, todas conferidas com rc=0 e o arquivo apagado) cai no cenário que já funciona: ação crítica com rc=2 e o `vigia` avisando. · Esforço P · Dono: `tech-lead`.

### B. A conferência de caminhos não segue a semântica de pathspec do git · média (alta enquanto A estiver aberto)
- **Evidência:** `hooks/conformidade.py:821,826`: palavra com `-` é descartada, então `--pathspec-from-file` passa. `hooks/conformidade.py:831`: o curinga vai para `glob.glob`, que não casa arquivo oculto com `*` nem atravessa `/`. Para o git, `*` atravessa `/` e casa ponto inicial.
- **Reprodução** (rc=0 no hook, e o `git` real apaga `.forge/versao`): `git rm '*/versao'`, `git rm '*versao'`, `git rm -r '*'`, `git rm ':(top).forge/versao'`, `git rm ':(glob)**/versao'`, `git rm '\.forge/versao'`, `git rm --pathspec-from-file=lista`, `echo .forge/versao | git rm --pathspec-from-file=-`, `git rm -r .` e `git rm -r :/`.
- **Caminho de ataque:** igual ao do A. Hoje a marca segura esses casos (cenário conferido: push com rc=2 e o `vigia` avisa). Combinados com o A, porém, desligam tudo.
- **Correção mínima:** para `rm`/`mv` e para `checkout`/`restore` com origem (`-s`, `<ref> --`, `--no-overlay`), deixar o próprio git resolver os caminhos com `git -C <pasta> ls-files -z -- <pathspecs>` e conferir cada resultado, no lugar do `glob.glob`. É leitura e não roda programa. Também recusar `--pathspec-from-file`, porque o hook não lê o arquivo nem o stdin. Para `checkout -- .` e `restore .` sem origem, deixar como está: o arquivo só muda se já diferir do índice, e isso o `vigia` (`em-vigor`) vê. Fixtures: `git-rm-curinga-oculto-bloqueia` (`'*/versao'`), `git-rm-pathspec-magica-bloqueia`, `git-rm-pathspec-from-file-bloqueia`. · Esforço P · Dono: `tech-lead`.

### C. `git restore --staged <caminho em vigor>` passou a perguntar ou barrar · informativa
- **Evidência:** `git restore --staged .claude/settings.json` dá rc=2. O comando só mexe no índice e não muda o arquivo em disco.
- **Avaliação:** é falso positivo raro (tirar do índice um arquivo em vigor) e não tem custo de segurança. Aceitável como está. Se incomodar, isentar `--staged` sem `--worktree` em `restore`. · Dono: `tech-lead`.

## O que fica aberto e quem cobre
- `git -c alias.x=rm x .forge/versao` dá rc=0 e apaga o arquivo. Isso é o achado 2 do incidente, coberto pela **BP-2** (recusar `-c alias.*` e `--config-env`). Com o achado A corrigido, a marca segura o efeito até lá.
- Ação **não crítica** sem `.forge/versao` passa (limite documentado na ADR 0009, item 2). A marca apagável por quem escreve fora do hook (Bash sem sandbox) depende do sandbox, coberto pela **BP-5** (P5, sandbox obrigatório nos projetos).
- Os achados A e B são desta entrega (escopo E1 da BP-1) e nenhuma BP posterior os cobre. Têm de ser corrigidos aqui.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: só os hooks da própria branch, executados com `python3` sobre uma cópia `git archive` em `$TMPDIR`, e `git` 2.55.0 local para conferir o efeito real de cada comando em repositórios descartáveis. Nenhum remoto foi tocado. `gitleaks`, `zizmor` e `actionlint` não se aplicam: a entrega não mexe em workflow nem traz segredo.
