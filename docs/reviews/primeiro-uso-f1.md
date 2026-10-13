---
tipo: review
contrato: 1
pedido: primeiro-uso-f1
branch: melhoria/primeiro-uso
commit: 516c4a4
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-13
---
# Parecer de autor: primeiro uso do Forge, entrega F1

Escopo: `origin/develop..516c4a4`: `bin/forge`, `bin/forge-novo-projeto` (novos), `bin/forge-init` (ignora `.forge/perfil`, `.forge/novo-projeto.json` e `.forge/onboarding.md`), skills `novo-projeto` e `modo-iniciante`, uma seção em `agents/jarvis.md`, README, CHANGELOG, `tests/test_novo_projeto.py` e a especificação em `docs/propostas/primeiro-uso/`.

Não afrouxa regra: nenhum invariante nem hook mudou; `bin/forge-check`, `hooks/`, `tests/catraca.py` e `.github/` intocados. Os scripts novos ficam em `bin/`, que a catraca pode tratar como sensível: este parecer é o registro pedido.

## Decisões de implementação
- O script roda no terminal, antes do Claude (o sandbox não lê `~/.config/gh`). Nunca lê o token (o teste confere que `gh auth token` não é chamado); o estado em `~/.local/state/forge/novo-projeto/<nome>.json` (e cópia em `.forge/novo-projeto.json`, ignorada pelo git) guarda nome, pasta, dono e etapas.
- Etapas (`repo_criado`, `clonado`, `commit_inicial`, `branches`) são gravadas depois do efeito e conferem o estado real (repo existente da própria execução, clone presente, commit já feito, push idempotente): rodar de novo retoma e não recria nada. Repositório já existente com o nome pedido nunca recebe escrita; o script pede outro nome.
- O commit inicial (README e `.gitignore`, `git add` explícito) vai para a `main` como ato do usuário no terminal (`R-MAIN`). A identidade do git é lida da configuração da pessoa; se faltar, é gravada só no clone.
- O script não roda o `forge-init`: a adoção é o fim da skill `novo-projeto` (`iniciar-projeto`), e assim "sem `.forge/versao`" continua sendo o sinal de primeiro uso para o Jarvis.
- O efeito do modo iniciante vem da leitura do perfil pelo Jarvis (uma linha, sem custo para o experiente). A injeção pelo `vigia` fica para a F3, que mexe em `hooks/`.
- Dono nunca fixo: vem de `gh api user`.

## Desvios e limites (sem ocultar)
- Sem confirmação "sim/não" antes de `gh repo create` (CA-5 do roteiro): o comando é explícito, o script imprime conta, nome e visibilidade antes de criar, e o repositório é sempre privado. A confirmação existe na skill, antes do push e do PR.
- Reaproveitar a URL de um repositório vazio e a conferência do escopo `repo` do token ficam fora da F1 (nome existente pede outro nome).
- O job `shellcheck` do CI não lista os scripts novos (`.github/` é protegido, `R-CONFORMIDADE`); rodado localmente, passa. Pendência registrada no CHANGELOG.

## Checklist
1. Pedido atendido, sem extras: sim.
2. Regras: `R-CUSTO` (só `git`, `gh`, GitHub gratuito), `R-NEUTRO` (nada de conta ou projeto), `R-MAIN`, `R-VERIFY` (sem `--force` nem `--no-verify`), `R-DECISAO` (uma pergunta por vez).
3. Legível: funções pequenas, etapas lineares; `shellcheck` limpo em `bin/forge`, `bin/forge-novo-projeto` e `bin/forge-init`.
4. Entradas validadas: nome por `^[A-Za-z0-9._-]{1,100}$` (sem `.` nem `..`), subcomando do despachante por `^[a-z][a-z0-9-]*$`, pasta existente e não vazia recusada.
5. Segurança: sem segredo em tela, estado ou commit; teste confere.
6. Testes: escritos antes (commit `test(primeiro-uso)`). Vermelho: 15 falhas e erros em `tests/test_novo_projeto.py` (13 testes, sem o código). Verde: `python3 -m unittest discover -s tests`, 294 testes; `scripts/validar-plugin.sh` e `forge-check docs` passam. Cobertura: caminho feliz (ordem, `--private`, três branches, autor do commit, estado), sem `gh auth`, nome existente, nome inválido, retomada depois de falha no clone, reexecução com tudo pronto, despachante, `.gitignore`, skills e Jarvis.
7. Commits: especificação, testes (vermelho), código, parecer; `git add` explícito.
