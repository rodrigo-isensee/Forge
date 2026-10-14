---
tipo: review
contrato: 1
pedido: primeiro-uso-f5
branch: melhoria/primeiro-uso-f5
commit: 2604b50
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-14
---
# Parecer de autor: primeiro uso F5 (atualização segura com ponto de retorno)

Autor e revisor são o mesmo papel aqui: este parecer é de autor e não substitui a review independente do PR.

## O que foi conferido
- **Fixação de versão:** `claude plugin marketplace add --help` não documenta ref. Teste local: `https://<host>/<repo>.git#v1.0.0` é aceito como fonte (a CLI tenta clonar sem o fragmento; a falha é só de rede no sandbox) e caminho local com `#` é recusado. O checkout da tag não pôde ser observado sem rede, então a troca é `remove` + `add <endereço>#vX.Y.Z` + `update`/`install`, com devolução ao endereço anterior se falhar; a versão nova é descoberta pelas tags (`git ls-remote`), não pela marketplace. Pendência: confirmar o checkout da tag na primeira atualização real.
- **Defesas da consulta** (`bin/forge_versoes.py`): só https sem usuário, `GIT_ALLOW_PROTOCOL=https`, `protocol.allow=never`, cwd vazio e neutro, sem senha, sem configuração do git do usuário. Local só com `FORGE_PERMITE_LOCAL=1` (testes). Testado com um `git` falso que registra cwd, protocolo e argumentos.
- **Segurança do usuário:** exige terminal; `forge-upgrade --simular` roda da cópia da tag antes de qualquer mudança; plugin só troca depois da simulação; falha na troca devolve o plugin e descarta o ponto; nenhum `reset`, `--force`, `branch -D` nem `rm` no projeto (teste por texto). `voltar-versao` não apaga branch nem arquivo novo (só lista).
- **Testes:** 28 novos (`tests/test_atualizar.py`), escritos antes (20 falhas e 4 erros sem a mudança): caminho feliz, recusa, sem terminal, em dia, sem rede, árvore suja, simulação que falha, doutor que falha (voltar e não voltar), troca do plugin que falha, voltar (não mesclada, mesclada, sem ponto, recusa, duas vezes), defesas, aviso do doutor. Suíte completa 431 verde, `validar-plugin.sh` ok.

## Riscos e pendências
- Altera `hooks/doutor.py` (consulta de rede no Stop, 3 s, cache diário): o PR precisa do rótulo `afrouxa-regra` do dono. `hooks.json` não mudou.
- Doutor com problema antigo e sem relação oferece voltar depois da atualização (a mensagem avisa que pode não ter relação).
- `forge-check` e os demais hooks intocados.

## Review independente (head `a1c8e80`)

Bateria no checkout do PR (worktree destacada em `a1c8e80`, sem o Actions): `python3 -m unittest discover -s tests` 432 testes OK; `scripts/validar-plugin.sh` ok; `shellcheck` (lista do CI e `bin/forge`) limpo; `catraca.py --modo pareceres` e `--modo pr-texto` (corpo real do PR) saem 0; `catraca.py --base <merge-base com develop>` sai 1 por `hooks/_comum.py`, `conformidade.py` e `parecer.py` (o PR está empilhado sobre a F4, ainda fora da `develop`) e o PR não tem o rótulo `afrouxa-regra`; versão sem mudança e linha nova em `[Não publicado]`, ok.

### Bloqueia o merge
1. **`marketplace remove` reescreve o `.claude/settings.json` do projeto e trava o fluxo** (`bin/forge_versoes.py:160`). Sonda com a CLI real (`HOME` temporário, projeto com o `settings.json` do modelo, `cwd` no projeto): `claude plugin marketplace remove forge` (sem `--scope`, "remove de todos os escopos") tirou do arquivo versionado `extraKnownMarketplaces.forge`, `enabledPlugins` **e** `"agent": "forge:jarvis"`. O `add` seguinte vai para o escopo `user`, então o projeto fica sem o Jarvis e sem o plugin declarado. Encadeamento: a árvore fica suja, o `forge-upgrade` recusa ("a cópia de trabalho não está limpa"), o `forge atualizar` oferece voltar, e o `forge voltar-versao` recusa por "mudanças não salvas". Quem não programa fica com o plugin novo, o projeto alterado e nenhum caminho de volta. Os testes não pegam porque o `claude` é falso.
   Correção: `--scope user` no `remove` e no `add` (os dois aceitam), conferir `git status --porcelain` depois da troca (se sujou, devolver e parar) e um teste de integração com a CLI real num `HOME` temporário (o `remove` não usa rede). Alternativa para o arquiteto decidir: fixar pelo `ref` da fonte `github` em `extraKnownMarketplaces` do projeto, numa branch com PR (ADR 0005), sem `remove`.
2. **A restauração não é confiável.** O `remove` vem antes de qualquer garantia, e a "devolução" readiciona `https://...#v<antes>`, não a fonte original (`{"source": "github", "repo": ...}`, com o escopo dela). Se a falha foi de rede, a devolução falha igual e o usuário fica sem marketplace e sem plugin (o `remove` desinstala). A mensagem de refazer à mão repete o mesmo `add` que acabou de falhar. Correção: antes do `remove`, guardar no ponto a saída de `claude plugin marketplace list --json` (fonte e escopo), validar a cópia da tag (`claude plugin validate <forge_novo>`), e na falha restaurar exatamente a fonte guardada. A mensagem final deve dar o comando da fonte original.
3. **O ponto de retorno guarda e sobrescreve o `settings.local.json`** (`criar_ponto`, `restaurar_arquivos`). Esse arquivo não é versionado e pode ter `env` com chave. A cópia vai para `~/.local/state/forge/retorno/` com a permissão padrão, e na volta (caso mesclado) é escrita por cima da versão atual sem histórico, o que perde o trabalho feito depois da atualização. Correção: não copiar o `settings.local.json` (a atualização não mexe nele) ou, se for preciso, `chmod 700` na pasta do ponto e restaurar só com o arquivo idêntico ao do `depois`.

### Recomendado (não bloqueia)
- **Consulta de tags: `.git` no `cwd` está coberto, `.git` acima do `TMPDIR` não.** Sonda: `cwd` num repositório com `url.<x>.insteadOf` e `GIT_DIR` no ambiente, sem efeito. Com o `TMPDIR` dentro desse repositório, o `ls-remote` da pasta "neutra" (`bin/forge_versoes.py:78`) lê o `.git/config` dele e vai a `https://evil.invalid/...`. O `clone` não é afetado (não lê o repositório envolvente), então o efeito é um aviso falso de versão nova. Correção de uma linha: `GIT_CEILING_DIRECTORIES=<pai da pasta neutra>` no `env` (sonda: com ele, a URL não muda), mais uma fixture.
- **F4 e o Jarvis.** O hook `conformidade` vê a linha `forge atualizar`, não os `claude plugin marketplace remove|add|install` internos, então não recusa nada. A guarda é só `isatty`, e `printf 's\n' | script -qc 'forge atualizar' /dev/null` dá um terminal ao agente (o `--ja-confirmado` do `voltar-versao` também pula a pergunta). Isso contorna a intenção da F4 ("instalação intocável"). Recomendação: `forge atualizar`, `forge-atualizar`, `forge voltar-versao` e `forge-voltar-versao` entram na lista de recusa da F4 para agentes (no `iniciante`, com a frase "rode no seu terminal: forge atualizar"). O Jarvis só oferece e explica (o aviso diário já manda rodar no terminal), e `agents/jarvis.md` diz isso.
- **Falso alarme do doutor.** Hoje qualquer problema depois da atualização oferece voltar. Regra proposta: rodar `forge-doutor --rapido` da versão atual antes da troca, guardar no ponto e oferecer voltar só se aparecer problema **novo**. Os antigos são listados como "já existiam antes".
- `bin/forge-atualizar:44`: "Tudo bem, ficou como está" é impresso também depois de voltar. Deve ir para o `else`.
- `pasta_de_retornos` usa só `projeto.name`. Dois projetos com o mesmo nome compartilham os pontos, e o `voltar-versao` de um pode restaurar os arquivos do outro. Filtrar por `meta["projeto"] == str(projeto)` em `ultimo_ponto`.
- `ja_mesclada` trata "branch da atualização não existe" como mesclada. Se o `forge-upgrade` falhou antes de criar a branch, a volta cria `forge/voltar-*` sem necessidade. Distinguir pelo `head_antes`.

### Aviso diário: aprovado
Só no `Stop`, como `systemMessage` (nunca `additionalContext`), uma vez por dia pelo cache `.forge/run/versao-nova`, com a rede fora da trava e uma releitura do cache depois. São 3 s no máximo, há silêncio sem rede e `FORGE_VERIFICAR_VERSAO=0` desliga. O texto usa só números de versão, sem nada da saída remota.

Parecer: **reprovado**. Os bloqueantes 1 a 3 voltam ao autor, cada um com o teste que falha antes (o 1 com a CLI real em `HOME` temporário). Depois, o rótulo `afrouxa-regra` do dono continua obrigatório.

## Re-review independente (head `2604b50`)

Bateria no checkout do PR (worktree destacada em `2604b50`, sem o Actions): `python3 -m unittest discover -s tests` 444 testes OK; `scripts/validar-plugin.sh` ok; `shellcheck` (lista do CI e `bin/forge`) limpo; `catraca.py --modo pr-texto` (corpo real do PR) sai 0. `catraca.py --base <develop>` (script da base) sai 1 só por `hooks/_comum.py`, `conformidade.py` e `parecer.py`: falta o rótulo `afrouxa-regra` do dono. `catraca.py --modo pareceres` (argumentos do CI) sai 1 só porque o último parecer deste arquivo era o reprovado anterior; não há outro defeito. Versão igual à da `develop` (0.12.0) e linhas novas em `[Não publicado]`, ok.

Sondas com a CLI real (`claude` 2.1.299, `HOME` e `XDG_STATE_HOME` temporários, Forge local com as tags v0.12.0 e v0.13.0, `FORGE_PERMITE_LOCAL=1`, projeto com o `.claude/settings.json` do modelo, um `settings.local.json` com `env` e terminal por `script`):

### Bloqueios anteriores: corrigidos
1. **Escopo do projeto.** `claude plugin marketplace remove forge --scope user`, mesmo com o `cwd` no projeto, deixa o `git status` limpo. O código ainda roda o `claude` numa pasta neutra. Ok.
2. **Ordem e restauração.** A tag é confirmada (`ls-remote`) e a fonte original é lida antes do `remove`. Na sonda, o `add` da tag falhou de verdade (`Path does not exist: ...#v0.13.0`). O fluxo readicionou a fonte original (`directory`, escopo `user`), o `~/.claude/settings.json` ficou idêntico ao de antes, o plugin continuou instalado, o ponto e a marca foram descartados e o projeto não mudou. A mensagem manual agora usa a fonte original. Ok.
3. **Segredo no ponto.** O ponto guarda só os arquivos de `.forge/` que estão no git, sem `claude/` nem `settings.local.json`. As pastas `forge/`, `retorno/` e `retorno/<projeto>` ficam com 700. A volta nunca sobrescreve um arquivo não versionado. Ok.

As recomendações também foram atendidas: doutor antes e depois (só problema novo oferece voltar), `GIT_CEILING_DIRECTORIES`, a mensagem "ficou como está" no `else`, `ultimo_ponto` filtrado pelo projeto e o Jarvis só oferece.

### Recusa do hook para agentes: atende ao pedido
Sonda direta no `hooks/conformidade.py` (perfil `iniciante`, `agent_type: forge:jarvis`). Recusa com `R-CONFORMIDADE`: `forge atualizar` (e `--fixar`), `forge voltar-versao`, `env [-i ...]`, `script -qc '...'` (incluindo `forge-voltar-versao --ja-confirmado`), `bash -c`, `sh -c "cd ... && ..."`, `bash -lc forge-atualizar`, caminho absoluto do binário, `python3 bin/forge-atualizar`, `eval`, `timeout` e `nohup`. Libera o que só cita o comando: `echo`, `git commit -m '... forge atualizar'`, `forge salvar '...'` e `forge doutor`.

### Bloqueia o merge
1. **`forge atualizar --fixar` descarta trabalho não salvo** (`bin/forge-atualizar:76` e `bin/forge_versoes.py`, `restaurar_projeto`). O `--fixar` sai antes da checagem `git status --porcelain`. Além disso, `restaurar_projeto` roda `git checkout -- <arquivo>` em **todo** arquivo de `git diff --name-only`, tanto no caminho de sucesso quanto no de falha, sem saber se foi o `claude` que mexeu. Sonda com a CLI real: alterei `.forge/versao` e `.gitignore` sem salvar e rodei `forge atualizar --fixar`. As duas mudanças sumiram, sem stash nem cópia. A mensagem ainda culpa o Claude ("O Claude mexeu em arquivo do projeto e eu restaurei: .forge/versao, .gitignore"). É perda de trabalho de quem não programa, no comando que a própria saída manda rodar.
   Correção: (a) checar a árvore limpa também no `--fixar`, antes de qualquer chamada; (b) em `restaurar_projeto`, tirar a foto (`git status --porcelain` ou o hash de cada arquivo) antes da troca e só devolver o que mudou entre a foto e o depois. Como o `claude` agora roda em pasta neutra e no escopo `user`, a alternativa mais simples é trocar a restauração por uma checagem que só avisa e para. (c) Um teste que falha antes: árvore suja, `--fixar`, e a mudança continua lá.

### Recomendado (não bloqueia)
- **O hook não pega interpretador com código inline nem shell indireto.** Passam: `python3 -c "import pty; pty.spawn(['forge','atualizar'])"` (dá terminal), `python3 -c 'os.system("forge atualizar")'`, `node -e`, `perl -e`, `echo 'forge atualizar' | bash`, `bash <<< '...'`, `f=forge; $f atualizar` e `x=atualizar; forge $x`. Para isso o agente precisa contornar de propósito, e é o mesmo limite das outras travas da F4 por texto. Por isso é recomendação: para `-c`/`-e` de interpretador, procurar `forge-atualizar`, `forge-voltar-versao` e o par `forge` + `atualizar|voltar-versao` no texto inteiro do argumento, tirando `[],` das palavras, e recusar o pipe/here-string para shell que contenha esses termos. Cada caso com uma fixture.
- A sonda do caminho de sucesso com a CLI real não foi possível sem `https`: o `claude` não aceita `#ref` em fonte de pasta local. O sucesso fica coberto só pelo `claude` falso. Vale uma sonda manual com o endereço real antes da release.

Parecer: **reprovado**. O bloqueante 1 volta ao autor, com o teste que falha antes. O resto está pronto. Depois disso, o rótulo `afrouxa-regra` do dono continua obrigatório.
