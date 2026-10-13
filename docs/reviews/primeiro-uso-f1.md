---
tipo: review
contrato: 1
pedido: primeiro-uso-f1
branch: melhoria/primeiro-uso
commit: 23c255f
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

# Review independente

Revisor: `forge:tech-lead`, sobre `origin/melhoria/primeiro-uso` em `23c255f` (inclui o ajuste de CA-5). Parecer: **aprovado**, com 1 recomendação média e 3 baixas.

## Verificação
- `python3 -m unittest discover -s tests`: 297 testes, OK. `shellcheck bin/forge bin/forge-novo-projeto`: limpo.
- Token: o script não chama `gh auth token`; o teste confere; o estado (`~/.local/state/forge/novo-projeto/<nome>.json` e a cópia ignorada pelo git) guarda só nome, pasta, dono e etapas. A skill proíbe pedir segredo no chat.
- Repositório sempre `--private` (teste confere). Dono vem de `gh api user`; nada fixo na conta do dono do Forge.
- CA-5: pergunta "Confirma? [s/N]" antes de `gh repo create`; Enter ou "n" recusa e nada é criado (testado); `--sim` só pula, de forma explícita.
- Commit inicial na `main` uma vez (etapa `commit_inicial`, `git add` explícito); reexecução com tudo pronto só reabre o Claude (testado).
- Nome: regex `^[A-Za-z0-9._-]{1,100}$` sem `.` e `..`; espaços, `/`, `../`, `;` são recusados e o laço pergunta de novo. O nome só aparece entre aspas e em argumentos, sem `eval`.
- Testes: HOME, `GIT_CONFIG_GLOBAL`, PATH e estado em diretório temporário; `git config` só no clone temporário; sem rede.
- Modo iniciante e Jarvis claros (perfil lido em uma linha, ausente = normal, decisão técnica é do time, credenciais só pelo terminal). Neutralidade: sem nome de projeto ou conta.

## Achados
1. **Média (recomendado)** · `bin/forge-novo-projeto`, bloco `repo_criado`: se a pessoa recusar a confirmação (estado salvo, sem `repo_criado`) e depois existir no GitHub um repositório com esse nome que não é do script, a retomada pula o teste de nome existente, diz "já foi criado antes; sigo com ele", marca `repo_criado` e empurra `main`, `develop` e `homolog` nele. Quebra a garantia "nunca escreve em repositório existente" e não confere visibilidade. Sem `--force`, então não destrói histórico. Sugestão: só aceitar repositório existente sem `repo_criado` se estiver vazio e privado (`gh repo view --json isPrivate,...`); senão pedir outro nome. Teste novo para a recusa seguida de repositório criado por fora.
2. **Baixa** · nome ou e-mail de commit vazios são aceitos (`ler` sem padrão) e o commit inicial falha depois; sugestão: repetir a pergunta até não vazio.
3. **Baixa** · o estado guarda `dono`, mas a retomada usa o `gh api user` atual; se a conta mudou entre execuções, o estado diverge. Sugestão: parar com mensagem clara.
4. **Baixa (docs)** · o parecer de autor acima, em "Desvios e limites", ainda diz que não há confirmação antes de `gh repo create`; o commit `23c255f` a adicionou. Atualizar o texto.
