---
tipo: review
contrato: 1
pedido: jarvis-forge-ao-abrir
branch: melhoria/jarvis-forge-ao-abrir
commit: 8b08053
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-14
---
# Parecer de autor: `jarvis-forge` atualiza a cópia vigente e consulta a fonte de harness ao abrir

Escopo: `origin/develop..55f8be6` (1 commit): `scripts/jarvis-forge`, `bin/forge-check` (subcomando `fontes`), `tests/test_forge.py`, ADR 0009 (ajuste), README, `docs/fontes-de-praticas.md` e `CHANGELOG.md`. O autor é o próprio `tech-lead`: parecer de autoria; `bin/forge-check` é protegido, então o PR exige o rótulo `afrouxa-regra` do dono, que é o portão independente.

## O que muda
- Atualização automática só por `fetch` + `merge --ff-only` na cópia vigente, nunca `reset`. Recusa com aviso de uma linha (e abre com a cópia atual) se houver mudança local, commit local, branch diferente da `develop` ou falta de rede. Não atualiza sob sessão tmux já aberta (`FORGE_ABERTURA_FEITA` evita repetir dentro do tmux). `--dev` não atualiza.
- `forge-check fontes` lê `~/.forge-contrib/fontes/fontes.json`, usa `git ls-remote -- <url> HEAD`, compara por prefixo com `commit_revisado`; sem registro, silêncio; sem resposta, saída 3 (o `jarvis-forge` não grava o cache e tenta na abertura seguinte). URL começando com `-` é ignorada. Nome e URL da fonte não entram no repositório (`R-NEUTRO`).

## Verificação
- Testes novos escritos antes e falhando sem a mudança: fast-forward, mudança local, commit local, sem rede, cache diário, `fontes` com versão nova, sem novidade, sem registro e fonte inalcançável. Repositórios bare locais e HOME temporário, sem rede.
- Um teste existente foi ajustado: a segunda abertura agora toca a cópia vigente (só fetch e merge), mas continua sem clone nem reset.
- Suíte completa, `shellcheck scripts/jarvis-forge` e `scripts/validar-plugin.sh` passam.

## Riscos e limites
- `R-CUSTO`: só `git ls-remote` e `git fetch`, sem API paga.
- O cache é por data local; arquivos `fontes-<data>` se acumulam (vazios, um por dia); o script não apaga nada.
- `ls-remote` consulta `HEAD` da fonte, não uma branch fixa: acompanha a branch padrão dela.

## Review independente

Revisor: `forge:tech-lead` (sessão independente da autoria). Escopo: `origin/develop..a5b3e3f` (2 commits), revisado como código de segurança (ADR 0009, seção 4, e `bin/forge-check`, protegido). Parecer: **reprovado** (2 itens bloqueiam).

### Bateria local (checkout `a5b3e3f`)
- `python3 -m unittest discover -s tests`: 319 testes, OK.
- `scripts/validar-plugin.sh`: passou. `shellcheck scripts/jarvis-forge`: sem achados.
- `tests/catraca.py --base <merge-base>` (regras): falha só por `bin/forge-check` (pede o rótulo `afrouxa-regra`, esperado). `--modo pareceres`: OK. `--modo pr-texto` com o corpo do PR: OK.
- Versão e changelog: `plugin.json` sem mudança; linha nova em `## [Não publicado]`: OK.

### Achados
1. **`scripts/jarvis-forge` (`atualizar_ao_abrir`, `rev-list`/`merge --ff-only origin/develop`) · bloqueia.** O nome curto `origin/develop` é ambíguo: o git resolve `refs/tags/origin/develop` antes de `refs/remotes/origin/develop`. Uma tag `origin/develop` publicada na origin apontando para um commit de `melhoria/*` é trazida pelo `fetch` (auto-follow, porque o commit vem com a branch) e o `merge --ff-only` avança a cópia vigente para código não revisado. Reproduzido em repositório local: a cópia vigente passou a ter o conteúdo da branch `melhoria/x`; o aviso `refname 'origin/develop' is ambiguous` some no `2>/dev/null`. O envio de tag não é barrado (`hooks/conformidade.py` libera `git push --tags`; o `pre-push` só barra mover tag existente). Isso quebra a garantia da ADR 0009, seção 4 ("nenhuma branch `melhoria/*` entra em uso"), e agora sem ação do dono, a cada abertura. O mesmo vetor existe, antes deste PR, no `--atualizar-vigente` (`reset --hard origin/develop`). Sugestão: `git -C "$vigente" fetch --quiet --no-tags origin +refs/heads/develop:refs/remotes/origin/develop`; usar `refs/remotes/origin/develop` por extenso no `rev-list`, no `merge --ff-only` e no `reset --hard` do `--atualizar-vigente`; depois do merge, conferir `HEAD == $(git rev-parse refs/remotes/origin/develop)`. Teste novo: tag `origin/develop` na origin apontando para fora da `develop`, e a cópia vigente não pode sair da `develop`.
2. **`bin/forge-check` (`cmd_fontes`, `git ls-remote -- url HEAD`) · bloqueia.** Qualquer URL do registro é aceita. O registro fica em `~/.forge-contrib/fontes/`, que o sandbox dos agentes pode gravar, e o `jarvis-forge` roda o `fontes` fora do sandbox. O `ext::` só está bloqueado pelo padrão do git: com `protocol.ext.allow=always` na configuração do usuário, `git ls-remote -- 'ext::sh -c touch% /caminho' HEAD` executou o comando (reproduzido com `-c protocol.ext.allow=always`). Caminho local, `file://` e `ssh` também passam. Sugestão: aceitar só `https://` com regex estrita (sem espaço nem caracteres de controle) e reforçar no próprio comando: `git -c protocol.allow=never -c protocol.https.allow=always ls-remote -- <url> HEAD`. Os testes passam a cobrir a recusa (`ext::`, `file://`, caminho local, URL com `;`, sem chamar o git) e o caminho feliz com um `git` falso no `PATH`, em vez de repositório bare local.
3. **`bin/forge-check` (`cmd_fontes`, linhas impressas) · recomendado.** `codigo` vem do registro gravável pelos agentes e `topo`, da rede; os dois vão para o terminal do dono sem filtro. Validar `topo` como 40 hexadecimais e `codigo` como `[A-Za-z0-9_-]+` (ou descartar caracteres de controle).
4. **`tests/test_forge.py` · recomendado.** Faltam testes para branch diferente da `develop`, sessão tmux já aberta (não atualiza) e `--dev` (não atualiza), comportamentos prometidos na ADR.
5. **`scripts/jarvis-forge` (`consultar_fontes`) · recomendado.** `XDG_STATE_HOME` relativo não é recusado, ao contrário do `XDG_DATA_HOME`.

### Conferido sem achado
- Só fast-forward na abertura; recusa com mudança local, commit local e fora da `develop`; sem `reset --hard` no caminho novo.
- Não atualiza com a sessão `jarvis-Forge` aberta; `FORGE_ABERTURA_FEITA` evita repetir dentro do tmux.
- Sem rede: `timeout 30` no `fetch`, uma linha de aviso, e a sessão abre.
- `fontes` não grava URL no repositório (`R-NEUTRO`) e usa só `git ls-remote` (`R-CUSTO`); registro malformado (JSON inválido, não-objeto, campos ausentes, URL começando com `-`) é tratado.
- Cache diário: fica em `~/.local/state`, fora da escrita do sandbox. Forjá-lo só esconde o aviso de versão nova da fonte, que não é controle de segurança.
- Teste antigo ajustado (`test_cria_a_copia_vigente_uma_vez_e_nao_toca_depois`): a mudança acompanha o comportamento novo (`fetch` e `merge` passam a ser esperados) e o teste continua barrando `clone`, `reset` e `checkout`. Não perdeu força no que protege.

## Re-review independente

Revisor: `forge:tech-lead` (sessão independente da autoria e da review anterior). Escopo: `9b20cab..06b3826` (1 commit, `fix(jarvis-forge): ref da develop sem ambiguidade e fontes só por https`), revisado como código de segurança. Parecer: **reprovado** (2 itens bloqueiam; os dois bloqueios anteriores estão corrigidos).

### Os dois ataques da review anterior, no head novo
- **Tag `origin/develop` ambígua: corrigido.** Com git real e origem local, foi publicada uma tag `origin/develop` apontando para um commit de `melhoria/x`. O script do `9b20cab` levou a cópia vigente para esse conteúdo; o do `06b3826` ficou na `develop`, tanto ao abrir quanto no `--atualizar-vigente`. Também ficou na `develop` com a tag já presente na cópia vigente, trazida por uma busca antiga. Usa `fetch --no-tags` com refspec explícito e `refs/remotes/origin/develop` por extenso.
- **`ext::` no registro: corrigido.** Com `protocol.ext.allow=always` no `~/.gitconfig` de um HOME temporário, `ext::sh -c touch% ...` é recusado antes de chamar o git ("URL recusada"). O comando não roda.

### Desvios novos procurados
- **Redirecionamento de https para outro protocolo: barrado.** Um servidor https local responde 302 para `http://`. Com a trava, o git falha com `Protocol "http" not supported or disabled in libcurl`. Sem a trava, segue o redirecionamento.
- **URL com credenciais (`https://user:senha@host/...`): recusada** pela regex, que não aceita `@`.
- **`insteadOf` reescrevendo https para `ext::`.** Sozinho, é barrado pelo `protocol.allow=never` (`transport 'ext' not allowed`). **Não é barrado** quando a mesma configuração traz também `protocol.ext.allow=always`: a regra por protocolo prevalece sobre `protocol.allow`, em qualquer nível de configuração. Ver achado 1.
- **Testes antigos ajustados: não ficaram mais fracos.** O `JFV` da atualização passou a exigir `reset --hard refs/remotes/origin/develop`, o que é mais estrito. O teste de commits locais deixou de proibir o `fetch`, que agora vem antes, para comparar com a origem atual: ele só atualiza `refs/remotes/origin/develop` com refspec explícito. O teste continua proibindo o `reset`, que é o que descarta trabalho. Os testes de `fontes` trocaram o repositório bare por um `git` falso e ganharam a recusa de 11 URLs, a linha exata com a trava e o filtro de caracteres de controle. Os recomendados 3, 4 e 5 da review anterior foram atendidos.

### Bateria local (checkout `06b3826`)
- `python3 -m unittest discover -s tests`: 330 testes, OK.
- `scripts/validar-plugin.sh`: passou. `shellcheck scripts/jarvis-forge`: sem achados.
- `tests/catraca.py --base b5e5d3d` (script da base): falha só por `bin/forge-check`, que pede o rótulo `afrouxa-regra` (esperado). `--modo pareceres`: falha porque o último parecer não é aprovado (este). `--modo pr-texto` com o corpo do PR 107: OK.
- Versão e changelog: `plugin.json` continua em 0.12.0 e há uma linha nova em `## [Não publicado]`: OK.

### Achados
1. **`bin/forge-check` (`cmd_fontes`, `subprocess.run([... "ls-remote" ...])`) · bloqueia.** O `ls-remote` roda no cwd de quem chamou, e o `jarvis-forge` chama `consultar_fontes` antes do `cd "$HOME/Forge"`. Num diretório que os agentes podem gravar, como uma worktree em `~/.forge-contrib/wt/`, cujo arquivo `.git` também é gravável, um `gitdir:` apontando para uma configuração com `url."ext::sh -c ...".insteadOf = https://` e `protocol.ext.allow=always` faz o `forge-check fontes` executar o comando fora do sandbox, com uma URL https legítima no registro. Reproduzido com HOME temporário e `GIT_CONFIG_NOSYSTEM=1`: o arquivo foi criado e o código de saída foi 3. Por isso o "protocolo travado" do CHANGELOG não vale nesse caso. A mesma configuração local também pode trazer um `credential.helper=!cmd`. Sugestão:
   - rodar o `ls-remote` com `cwd="/"`, fora de qualquer repositório, e tirar `GIT_DIR`, `GIT_WORK_TREE`, `GIT_CONFIG_PARAMETERS` e `GIT_CONFIG_COUNT` do `env`;
   - negar por extenso `-c protocol.ext.allow=never -c protocol.file.allow=never -c protocol.ssh.allow=never -c protocol.git.allow=never -c protocol.http.allow=never`. A linha de comando prevalece sobre o `~/.gitconfig`. Conferido: cada uma das duas medidas, sozinha, já barra a reprodução.
   - Teste novo com git real e sem rede: cwd num diretório cujo `.git` aponta para essa configuração, URL `https://127.0.0.1:1/r.git`. O arquivo-alvo não pode existir.
2. **`relativo/forge/fontes-2026-10-13` · bloqueia.** Arquivo vazio commitado na raiz do repositório. É resto do `test_xdg_state_home_relativo_e_recusado` rodado antes da correção: o `jarvis-forge` herda o cwd do runner, que é a raiz do repo, e gravou o cache com o caminho relativo. Sugestão: remover o arquivo e rodar o `jarvis-forge` com `cwd=self.tmp` no `JarvisForgeAbrir.rodar`, para que uma regressão nunca suje o repositório.

### Conferido sem achado
- `XDG_STATE_HOME` relativo é recusado antes de qualquer ação, e um teste cobre isso.
- Não atualiza com branch diferente da `develop`, sessão tmux aberta ou `--dev` (testes novos com git real).
- `_imprimivel` tira ESC, BEL e CR do código; `topo` precisa ter 40 ou 64 hexadecimais (SHA-1 ou SHA-256), senão conta como falha (saída 3).
- Na abertura, os avisos do `fetch` e do `merge` deixaram de ser descartados (`2>/dev/null` removido), e um aviso de ambiguidade passaria a aparecer.

## Terceira review independente

Revisor: `forge:tech-lead` (sessão independente da autoria e das duas reviews anteriores). Escopo: `1572021..8b08053` (1 commit, `fix(jarvis-forge): consulta de fontes fora do cwd, sem config do usuário e com protocolos negados`), revisado como código de segurança. Parecer: **aprovado** (os dois bloqueios da re-review estão corrigidos; 1 item recomendado).

### Os dois bloqueios da re-review, no head novo
- **`.git` malicioso no cwd: corrigido.** O ataque foi reproduzido com git real 2.43. O `.git` tinha `url."ext::sh -c touch% <alvo>".insteadOf = https://127.0.0.1:1/r.git` e `protocol.ext.allow=always`. Primeiro, o controle: o git puro, nesse cwd, executa o comando. Com o `forge-check` do `1572021`, o alvo foi criado nos três casos testados: `.git` como diretório, cwd dentro do `.git` e `.git` como arquivo `gitdir:` (worktree). Com o do `8b08053`, o alvo não foi criado em nenhum dos três, e a saída foi 3. Há duas defesas, cada uma suficiente sozinha: o `ls-remote` roda num `TemporaryDirectory`, e a linha de comando nega `ext`, `file`, `ssh`, `git` e `http`.
- **Arquivo de lixo: removido.** `relativo/forge/fontes-2026-10-13` saiu do repositório. `JarvisForgeAbrir.rodar` agora usa `cwd=self.tmp`. Depois da bateria completa, `git status` ficou limpo.

### Outras fontes de configuração procuradas (git real, mesmo ataque, HOME temporário)
O `1572021` executou o comando em 8 dos 10 vetores. O `8b08053` não executou em nenhum dos 10:
- `GIT_CONFIG_COUNT`/`GIT_CONFIG_KEY_n`/`GIT_CONFIG_VALUE_n` herdados;
- `GIT_CONFIG_PARAMETERS`;
- `GIT_DIR` apontando para o `.git` malicioso;
- `$XDG_CONFIG_HOME/git/config`;
- `~/.config/git/config`;
- `~/.gitconfig`;
- `GIT_EXEC_PATH` com um `git-remote-https` falso;
- `GIT_SSH_COMMAND` com `insteadOf` para `ssh://`;
- `TMPDIR` dentro de um repositório malicioso.

Os herdados caem porque o `env` filtra todo `GIT_*`. O global e o XDG caem por `GIT_CONFIG_GLOBAL=/dev/null`, e o do sistema por `GIT_CONFIG_NOSYSTEM=1`. O vetor do `TMPDIR` é o único em que o repositório pai ainda é descoberto, e nele quem barra é a negação por extenso na linha de comando.
- **`git` falso no `PATH`: fora do escopo.** O comando é executado, como era esperado. O `PATH` é o do shell do dono, e o `jarvis-forge` não o altera. Quem controla o `PATH` do dono já executa qualquer coisa.
- O teste novo `test_git_do_cwd_malicioso_nao_executa_comando` usa git real, sem rede. Ele falha com o `forge-check` do `1572021` e passa com o do `8b08053`. O teste da linha exata passou a exigir as negações por extenso, o que é mais estrito.

### Bateria local (checkout `8b08053`)
- `python3 -m unittest discover -s tests`: 331 testes, OK. Depois deles, `git status` ficou limpo.
- `scripts/validar-plugin.sh`: passou. `shellcheck scripts/jarvis-forge`: sem achados.
- `tests/catraca.py --base origin/develop`, com o script da base: falha só por `bin/forge-check`, que pede o rótulo `afrouxa-regra` aplicado pelo dono depois do último push (esperado). `--modo pr-texto` com o corpo do PR 107: OK. `--modo pareceres`: rodado sobre o commit deste parecer.
- Versão e changelog: `plugin.json` continua em 0.12.0 e há uma linha nova em `## [Não publicado]`: OK.

### Achados
1. **`bin/forge-check` (`cmd_fontes`, `tempfile.TemporaryDirectory()`) · recomendado.** A pasta temporária nasce no `TMPDIR` do dono. Se esse `TMPDIR` ficar dentro de um repositório, o git descobre o repositório pai e lê a configuração local dele. Os protocolos estão negados na linha de comando, mas um `credential.helper=!cmd` ainda seria lido, e só rodaria se um servidor https respondesse 401. Não é explorável pelos agentes: o `TMPDIR` vem do shell do dono, e o sandbox não grava em `/tmp` (conferido). Como reforço barato, vale acrescentar ao `env` `GIT_CEILING_DIRECTORIES` com o pai da pasta temporária, ou `GIT_DIR` com um caminho inexistente. Pode ir num PR futuro.
