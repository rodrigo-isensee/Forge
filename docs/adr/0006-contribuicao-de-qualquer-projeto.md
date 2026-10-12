# 0006 - Contribuição de qualquer projeto como colaborador

Estado: vigente. Data: 2026-10-12.
Propósito: definir como uma melhoria de fábrica descoberta em qualquer projeto chega ao Forge. Público: agentes de todos os projetos e quem mantém o Forge. Revisão: 2026-10-12.

## Contexto
Decisão do usuário: qualquer agente de qualquer projeto que perceber uma melhoria de fábrica abre PR na `develop` do Forge, como colaborador do GitHub; quanto mais o plugin é usado, mais ele melhora. Hoje o Jarvis manda trabalhar num clone fixo (`~/Forge`), o que traz dois problemas: com vários projetos em sessões paralelas, o mesmo clone troca de branch por baixo de outra sessão; e uma worktree de outro clone já vazou `GIT_DIR` e corrompeu o repositório real (CHANGELOG 0.3.0). Além disso, o CI exige versão nova em todo PR para a `develop`: dois contribuidores sobem a mesma versão e entram em conflito.

## Decisão
1. **Quem:** qualquer agente, em qualquer projeto, ao identificar melhoria de fábrica (classificação em "Fábrica × projeto" do Jarvis). Uma melhoria por PR.
2. **Onde trabalhar:** um clone próprio por projeto, fora do projeto: `~/.forge-contrib/<projeto>`. Nunca uma worktree de outro clone, nunca o cache do plugin.
3. **Acesso ao repositório:**
   - **com acesso de escrita** (`gh repo view --json viewerPermission` retorna `WRITE`, `MAINTAIN` ou `ADMIN`): branch `melhoria/<assunto>` a partir da `develop` atualizada, push no próprio repositório;
   - **sem acesso:** `gh repo fork`, push no fork e PR para a `develop` do Forge;
   - **sem `gh` autenticado:** registra a proposta em `docs/kanban/melhorias.md` do projeto e avisa o usuário.
4. **Antes do PR, no clone de contribuição:** testes do Forge verdes (inclui neutralidade, `R-NEUTRO`) e `claude plugin validate . --strict`; varredura de segredos no diff (padrões de chave, token, `.env`, e-mail e caminhos pessoais); nada de nome, regra de negócio, dado pessoal ou trecho de código do projeto de origem no diff.
5. **Texto do PR:** projeto de origem, situação observada, o que muda e como medir o efeito (`docs/melhoria-continua.md`).
6. **Versão:** PR para a `develop` **não** sobe mais a versão. Cada PR que muda a fábrica acrescenta uma linha em `## [Não publicado]` do `CHANGELOG.md`. O job `versao` do CI passa a: na `develop`, exigir entrada nova em `## [Não publicado]` quando arquivos da fábrica mudam; na `main` (PR `homolog` → `main`), exigir versão em `plugin.json` maior que a da `main` e a seção `[Não publicado]` convertida em `## [X.Y.Z] - data`. O `tech-lead` prepara essa conversão num PR de release na `develop` antes de promover para a `homolog`. O teste `test_changelog_tem_a_versao_atual` continua válido, porque procura a primeira entrada numerada.

## Alternativas consideradas
| Opção | Prós | Contras |
|---|---|---|
| Clone único `~/Forge` (hoje) | Simples | Sessões paralelas trocam a branch umas das outras |
| Worktree do clone do Forge por projeto | Economiza disco | Estado git compartilhado; foi a origem do vazamento da 0.3.0 |
| Fragmentos de changelog (`changelog.d/<branch>.md`) montados na release | Zero conflito entre PRs | Mais ferramenta; adotar se os conflitos em `[Não publicado]` ficarem frequentes |
| Manter a versão em cada PR | Já implementado | Conflito garantido entre contribuidores paralelos |

## Consequências
- Mais fácil: qualquer projeto contribui sem depender de uma sessão central; contribuidores não brigam pela versão.
- Mais difícil: a versão é decidida na release, não no PR; o `tech-lead` passa a classificar patch, minor ou major (ADR 0005) olhando o `[Não publicado]`.
- Segurança: PR de fork roda com `pull_request` (sem segredos, permissão de leitura); nunca usar `pull_request_target` com checkout do código do PR. O hook `.githooks/pre-push` é só do lado do cliente; com mais colaboradores com escrita, a proteção real da `develop`, `homolog` e `main` precisa ser a proteção de branch do GitHub.
- Risco: o texto do PR expor o projeto de origem se o repositório do Forge for público. O PR descreve a situação sem dados do projeto.
