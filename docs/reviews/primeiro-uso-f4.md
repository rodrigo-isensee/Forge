---
tipo: review
contrato: 1
pedido: primeiro-uso-f4
branch: melhoria/primeiro-uso-f4
commit: cb4249f
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-14
---
# Parecer de autor: primeiro uso F4 (instalação intocável e travas)

- **Mudança:** `hooks/conformidade.py` (travas do `git`, do `gh` e do `claude`, `checar_remocao`, confirmação `ask`), `Hook.iniciante()` e `copia_principal()` em `hooks/_comum.py`, `tests/test_hooks.py` (aceita `esperado.pergunta`), 100 fixtures `trava-*` em `tests/hooks/conformidade/`, invariantes novos em `tests/config.json`, `docs/hooks.md`, `skills/modo-iniciante`, uma linha no `agents/jarvis.md`, `CHANGELOG.md`.
- **Já coberto antes (só ganhou fixture e a mensagem simples):** `push --force`, `-f`, `+refspec`, push e merge na `main`, push para `develop`/`homolog` (inclusive `--delete` e `:ref`), caminhos em vigor (`.claude/`, `.githooks/`, `.forge/versao|config.json|run/`, `~/.claude/*`).
- **Acrescentado (recusa para todos):** `gh repo delete`, `gh api -X DELETE repos/<dono>/<repo>` e GraphQL `deleteRepository`; `gh repo edit --visibility public`, `gh api` com `private=false` ou `visibility=public`; `git push --mirror`; `filter-branch`, `filter-repo`, `rebase` com `main`/`develop`/`homolog` em uso e `branch -D|-d|--delete` delas; `claude plugin uninstall|remove|disable|update` e `marketplace add|remove`, `claude config set|add|remove`; `rm`/`mv` de pasta que contém caminho em vigor (`rm -rf .forge`), sem alcançar a raiz do projeto nem as pastas acima dela (limpeza de worktree segue livre).
- **Perfil iniciante (`.forge/perfil`, lido da cópia ou da principal):** a recusa troca o texto técnico pela consequência em linguagem simples e o caminho (site do GitHub, `forge desfazer`, sugestão ao Forge). `reset --hard`, `clean -f`, `checkout -- .`, `restore .`, `gh repo archive` e `rebase` de branch já enviada respondem `permissionDecision: "ask"` (saída 0); se a mesma linha tiver uma recusa, ela vence. No perfil padrão esses cinco ficam como estavam (nada novo para quem programa).
- **Instalação intocável:** a recusa de caminho em vigor passa a sugerir registrar como sugestão ao Forge; o Jarvis e a skill `modo-iniciante` mandam guardar o pedido em `~/.local/state/forge/sugestoes/` (a F6 envia).
- **Pendência documentada (`docs/hooks.md`, `CHANGELOG.md`):** o comando assistido com backup (`forge config`, `forge perfil`) não existe. `.forge/perfil` ficou de fora de `caminhos`: a skill `novo-projeto` o grava hoje e proteger agora quebraria o primeiro uso; entra quando o comando existir.
- **Vermelho antes:** as fixtures e a asserção `pergunta` foram escritas antes do código; sem a mudança falharam 58 fixtures e 7 deram erro. **Verde depois:** 404 testes (`python3 -m unittest discover -s tests`) e `scripts/validar-plugin.sh` passam. Fixtures sem rede (`R-CUSTO`) e sem termo de projeto (`R-NEUTRO`).
- **Atenção ao dono:** toca `hooks/` e `tests/hooks/`: o PR precisa do rótulo `afrouxa-regra`. Nenhuma fixture existente mudou de resultado; nada foi afrouxado (só se acrescentam recusas e confirmações). Atenção de review: o `branch -d/-D` de `develop`/`homolog` e o `rm` de pasta são recusas novas para todos os papéis. Sem mudança de versão (ADR 0006). Depende do #103 e do #102.

Parecer de autor, feito pelo mesmo agente que escreveu a mudança; o review independente fica a cargo do `tech-lead` no PR.
