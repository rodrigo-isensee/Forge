---
tipo: review
contrato: 1
pedido: primeiro-uso-f4
branch: melhoria/primeiro-uso-f4
commit: 3e91376
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-14
---
# Parecer de autor: primeiro uso F4 (instalação intocável e travas)

- **Mudança:** `hooks/conformidade.py` (travas do `git`, do `gh` e do `claude`, `checar_remocao`, confirmação `ask`), `Hook.iniciante()` e `copia_principal()` em `hooks/_comum.py`, `tests/test_hooks.py` (aceita `esperado.pergunta`), 105 fixtures `trava-*` em `tests/hooks/conformidade/`, invariantes novos em `tests/config.json`, `docs/hooks.md`, `skills/modo-iniciante`, uma linha no `agents/jarvis.md`, `CHANGELOG.md`.
- **Já coberto antes (só ganhou fixture e a mensagem simples):** `push --force`, `-f`, `+refspec`, push e merge na `main`, push para `develop`/`homolog` (inclusive `--delete` e `:ref`), caminhos em vigor (`.claude/`, `.githooks/`, `.forge/versao|config.json|run/`, `~/.claude/*`).
- **Acrescentado (recusa para todos):** `gh repo delete`, `gh api -X DELETE repos/<dono>/<repo>` e GraphQL `deleteRepository`; `gh repo edit --visibility public`, `gh api` com `private=false` ou `visibility=public`; `git push --mirror`; `filter-branch`, `filter-repo`, `rebase` com `main`/`develop`/`homolog` em uso e `branch -D|-d|--delete` delas; `claude plugin uninstall|remove|disable|update` e `marketplace add|remove`, `claude config set|add|remove`; `rm`/`mv` de pasta que contém caminho em vigor (`rm -rf .forge`), sem alcançar a raiz do projeto nem as pastas acima dela (limpeza de worktree segue livre).
- **Perfil iniciante (`.forge/perfil`, lido da cópia ou da principal):** a recusa troca o texto técnico pela consequência em linguagem simples e o caminho (site do GitHub, `forge desfazer`, sugestão ao Forge). `reset --hard`, `clean -f`, `checkout -- .`, `restore .`, `gh repo archive` e `rebase` de branch já enviada respondem `permissionDecision: "ask"` (saída 0); se a mesma linha tiver uma recusa, ela vence. No perfil padrão esses cinco ficam como estavam (nada novo para quem programa).
- **Instalação intocável:** a recusa de caminho em vigor passa a sugerir registrar como sugestão ao Forge; o Jarvis e a skill `modo-iniciante` mandam guardar o pedido em `~/.local/state/forge/sugestoes/` (a F6 envia).
- **Pendência documentada (`docs/hooks.md`, `CHANGELOG.md`):** o comando assistido com backup (`forge config`, `forge perfil`) não existe. `.forge/perfil` ficou de fora de `caminhos`: a skill `novo-projeto` o grava hoje e proteger agora quebraria o primeiro uso; entra quando o comando existir.
- **Vermelho antes:** as fixtures e a asserção `pergunta` foram escritas antes do código; sem a mudança falharam 58 fixtures e 7 deram erro. **Verde depois:** 404 testes (`python3 -m unittest discover -s tests`) e `scripts/validar-plugin.sh` passam. Fixtures sem rede (`R-CUSTO`) e sem termo de projeto (`R-NEUTRO`).
- **Atenção ao dono:** toca `hooks/` e `tests/hooks/`: o PR precisa do rótulo `afrouxa-regra`. Nenhuma fixture existente mudou de resultado; nada foi afrouxado (só se acrescentam recusas e confirmações). Atenção de review: o `branch -d/-D` de `develop`/`homolog` e o `rm` de pasta são recusas novas para todos os papéis. Sem mudança de versão (ADR 0006). Depende do #103 e do #102.

Parecer de autor, feito pelo mesmo agente que escreveu a mudança; o review independente fica a cargo do `tech-lead` no PR.

## Review independente (tech-lead, HEAD 3e91376)

Parecer: **reprovado**. Revisei o diff a partir de 279bab5 e sondei o hook com cerca de 90 comandos, nos perfis padrão e iniciante, num repositório de teste (papel `tech-lead`, branch `melhoria/x` publicada).

**Validação local** (cota do Actions esgotada): `python3 -m unittest discover -s tests` passou (404 testes, OK). `scripts/validar-plugin.sh` passou. `catraca.py --base origin/develop` (b5e5d3d), no modo `regras`, saiu com 1: só pede o rótulo `afrouxa-regra` para `hooks/_comum.py` e `hooks/conformidade.py`, como o esperado, e o rótulo ainda não foi aplicado. O modo `pareceres` (`--head HEAD --ramo=melhoria/primeiro-uso-f4 --base-ref develop`) passou, avaliado sobre o parecer de autor. O modo `pr-texto` passou. Versão 0.12.0 igual à da base, e há 3 linhas novas em `[Não publicado]` (F2, F3, F4): ok.

**Falsos positivos (fluxo legítimo)**
- Liberados, como deve ser: `git branch -d/-D/--delete melhoria/*`; `rm -rf` de `$TMPDIR`, `/tmp/...` e `../wt/...`; `git worktree remove [--force]`; `claude plugin validate|install|marketplace update`. `reset --hard`, `clean -fd`, `checkout .` e `restore .` continuam livres no perfil padrão. No iniciante, `restore --staged .` e `clean -n` ficam livres.
- `ask` sem TTY: o hook não lê o terminal nem espera resposta. Ele imprime o JSON e sai com 0 na hora (medido). Quem decide é o Claude Code: num subagente em segundo plano, ou com `-p` sem ferramenta de permissão, o que não está pré-aprovado é negado, e o agente recebe a recusa sem travar. Isso segue a documentação do Claude Code. Não reproduzi numa sessão real, porque o sandbox nega a API.

**Brechas**
- Fechadas: `gh api -X DELETE|delete|--method DELETE|--method=DELETE repos/o/r[/]` (também com `{owner}/{repo}` e com o `-X` depois do endpoint); GraphQL `deleteRepository`; `-f/-F/--field private=false|FALSE`, `visibility=public` e `-XPATCH`; `gh repo edit --visibility[=]public|PUBLIC`. No push: `+ref`, `+HEAD:ref`, `+main` com `-c`, `--force-with-lease[=...]`, `--force-if-includes` e `--mirror`. Apagar a `main`: `push origin --delete main`, `--delete origin main`, `-d main`, `:main` e `:refs/heads/main`. Apagar `.forge` por caminho: `rm -rf .forge`, `./.forge`, `.forge/`, `../.forge` (com `cd`), caminho absoluto literal, `mv .forge` e `rm -rf ~/.claude`. No rebase: `switch develop && rebase main`. Em `branch -D|-dr`: `develop` e `origin/main`.
- Ficam como limite aceito (o sandbox é a garantia real, `docs/hooks.md`): `D=.forge; rm -rf $D`, `rm -rf .fo*` e `find ... -exec rm`.

**Ajustes necessários**
1. `hooks/conformidade.py:320` (`claude`): `claude plugin update` é recusado. É assim que os projetos se atualizam: o `agents/jarvis.md:78`, a skill `contribuir-com-o-forge` e o `bin/forge-doutor:109` mandam rodar `claude plugin update forge@forge`. Atualizar o plugin não desinstala nem desliga a proteção. Sugestão: tirar `update` da lista e inverter as duas fixtures `trava-claude-plugin-update-*` para "libera". Severidade: **bloqueia**.
2. `hooks/conformidade.py:309` (`gh_trava`): `gh api -XDELETE repos/o/r` e `gh api -X=DELETE repos/o/r` apagam o repositório sem recusa. O `parecer.opcao` não lê a opção curta colada nem com `=`, embora o `metodo_mutante` leia (o `-XPATCH ... private=false` é recusado). Sugestão: ler o método do mesmo jeito que o `metodo_mutante` lê (`-XDELETE`, `-X=DELETE`, `--method=DELETE`), com fixtures das duas formas. Severidade: **bloqueia**.
3. `hooks/conformidade.py:347` (`checar_remocao`): `rm -rf $PWD/.forge`, `rm -rf "$CLAUDE_PROJECT_DIR"/.forge` e `rm -rf $PWD/.forge/` passam. Para arquivo, o mesmo prefixo é recusado (`rm "$PWD/.forge/versao"` cai em `em_qualquer_lugar`), e esses são os prefixos que um agente usa quando trabalha com caminho absoluto. Sugestão: aplicar à pasta o mesmo casamento em qualquer lugar do caminho que o `caminho_barrado` usa, comparando o fim do caminho com a pasta de um caminho protegido sem dono. Incluir fixtures com `$PWD` e `$CLAUDE_PROJECT_DIR`. Severidade: **bloqueia**.

**Recomendados** (podem virar cartão; não bloqueiam)
4. `.forge/perfil` fora de `caminhos`: `echo experiente > .forge/perfil` e `rm .forge/perfil` passam. Um agente que troca o perfil não ganha nada além do que o perfil padrão já permite, porque as recusas valem para todos os perfis. Mas some a confirmação da pessoa em `reset --hard`, `clean -f`, `checkout/restore .`, `gh repo archive` e `rebase` publicado, e somem também as mensagens simples. O risco é médio: é exatamente a proteção desenhada para o iniciante. Sugestão, sem esperar o `forge perfil`: recusar a escrita e a remoção de `.forge/perfil` quando o arquivo já existe com `iniciante`. A criação pela `novo-projeto` continua livre. Senão, abrir um cartão com prazo antes da F6.
5. `gh api -X PATCH repos/o/r --input body.json` (ou `--input -` com `{"private":false}`) torna o repositório público sem recusa. Sugestão: recusar `--input` em PATCH ou PUT no endpoint do repositório (`REPO_APAGAR`).
6. `ask` de `reset --hard` no iniciante também vale numa worktree temporária de review (o perfil é lido da cópia principal). Em segundo plano, a ação é negada. Nenhuma skill do Forge usa `reset --hard` hoje, então o impacto é baixo. Sugestão: dispensar a confirmação em worktree vinculada com HEAD solto.
7. Limites menores: `git update-ref -d refs/heads/develop` (só local, recuperável) e `git pull --rebase` sobre a branch de integração não são vistos.

Depois de corrigir os itens 1 a 3, com fixtures novas, peça um re-review. O rótulo `afrouxa-regra` continua sendo do dono, aplicado depois do último push.
