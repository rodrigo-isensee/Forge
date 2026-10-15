---
tipo: qa
contrato: 1
pedido: autoria-worktree
branch: melhoria/autoria-worktree
commit: 531b131c9c8503b4d4de1328d1fbc86da373f97a
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-15
---
# QA - autoria de parecer gravado em outra worktree (hook `conformidade`)

Links: `docs/reviews/autoria-worktree.md`, `docs/security/autoria-worktree.md`, `docs/hooks.md` (Autoria dos pareceres). Não há UX nem API; a obrigação é a do pedido: o hook registra a autoria do parecer gravado em worktree do mesmo repositório, inclusive aninhada em `.claude/worktrees/`, e só nelas. Offline, só disco local (`R-CUSTO`). Código testado: 531b131 (HEAD 3f1258c só acrescenta pareceres de review e segurança).

## Resultados
| ID | Cenário | Fronteira protegida | Resultado |
|---|---|---|---|
| CT-01 | Parecer em `docs/qa/` de worktree irmã (fora da raiz da sessão) | worktree fora da raiz | Passou: registra `docs/qa/p1.md`, 1 linha |
| CT-02 | Parecer em worktree aninhada `<raiz>/.claude/worktrees/x` | worktree dentro da raiz | Passou: registra `docs/qa/p2.md` relativo a ela |
| CT-03 | Parecer em repositório estranho (outro `git init`) | outro repositório | Passou: 0 linhas |
| CT-04 | `.md` fora de `docs/{reviews,qa,devops,security}` numa worktree irmã | fora de docs | Passou: 0 linhas |
| CT-05 | Suíte `env -u FORGE_ABERTURA_FEITA python3 -m unittest discover -s tests` | n/a | Passou: 561 testes, OK (144 s; `uptime` antes: carga 0,56) |
| CT-06 | `scripts/validar-plugin.sh` | n/a | Passou: `Validation passed` (a rede para api.anthropic.com é negada pelo sandbox; não afeta o resultado) |
| CT-07 | `forge-check pr autoria-worktree --base develop` | n/a | Antes deste parecer: recusa só por falta do parecer de QA (esperado); rodado de novo após gravá-lo, ver "Provas" do relatório |

CT-01 a CT-04 rodaram com `qa-autoria.sh` (em `$TMPDIR`): repositório temporário real fora dos fixtures, worktrees criadas com `git worktree add`, o hook chamado como PostToolUse de Write com `CLAUDE_PROJECT_DIR` na raiz. O hook é o do diff; os fixtures do autor (9 novos, incluindo `.git` forjado, link simbólico, `GIT_DIR` no ambiente e gitdir relativo) rodam dentro da suíte (CT-05).

## Vermelho antes do verde
Mesmo script contra os `hooks/` extraídos da `develop` (`git archive develop hooks`, `HOOK=<pasta>/hooks/conformidade.py bash qa-autoria.sh`): casos 1 e 2 falham (`registra -> nao`, 0 linhas); 3 e 4 passam nos dois lados (são guardas de não-regressão). Os testes novos detectam, portanto, a ausência da correção. Mutação: sem ferramenta gratuita na stack do Forge; não executada.

## Achado novo, fora do pedido (não reprova)
Gitdir relativo (`git worktree add --relative-paths`, R1 do re-review): fica como cartão 16d, decisão técnica do time (`R-DECISAO`). O fixture `autoria-worktree-relativo-registra` cobre o caso que o hook já resolve; o que o cartão trata não é regressão frente à `develop`, onde nenhuma worktree fora da raiz registrava.

## Bugs
Nenhum aberto.

## Veredito
Aprovado em 531b131. Zero críticos, altos, médios e baixos. A release rápida e o merge da base (a `develop` remota andou: #125, #126, #129) seguem como etapas do `tech-lead`.
