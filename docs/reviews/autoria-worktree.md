---
tipo: review
contrato: 1
pedido: autoria-worktree
branch: melhoria/autoria-worktree
commit: 02cb437
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-15
---
# Review: autoria de parecer gravado em outra worktree

Escopo: `git diff develop..02cb437`, com `hooks/conformidade.py` (`raiz_do_parecer`, `autoria`), `CHANGELOG.md` e os fixtures `tests/hooks/conformidade/autoria-worktree-registra.json` e `autoria-outro-repositorio-nao-registra.json`. Também li `docs/hooks.md`, só a parte de autoria (linhas 30, 52 e 81).

Parecer: **reprovado** (commit revisado 02cb437). A correção funciona para a worktree que fica fora da raiz da sessão. A worktree aninhada continua sem registro: é o layout do próprio Claude Code, em `.claude/worktrees/`, que o `docs/hooks.md` já cita. O resto é recomendado.

## Ferramentas
- Suíte completa, uma vez (`env -u FORGE_ABERTURA_FEITA python3 -m unittest discover -s tests`): `Ran 561 tests`, `OK`.
- Falha antes e passa depois: o `tests.test_hooks` com o `hooks/conformidade.py` da `develop` sobre os fixtures novos dá `ERROR` só em `autoria-worktree-registra`, por falta do `autoria.jsonl`. Com o 02cb437 passa. O fixture do outro repositório passa nas duas versões, porque é um teste de não-regressão.

## Sondagem (cópia descartável com fixtures temporários, fora da branch)
| Caso | Resultado | Leitura |
|---|---|---|
| Worktree aninhada `proj/.claude/worktrees/x`, Write em `docs/qa/p1.md` | **sem registro** | `raiz in p.parents` é verdadeiro e devolve a raiz da sessão. O `rel` vira `.claude/worktrees/x/docs/qa/p1.md` e não casa com o prefixo `docs/` |
| Caminho relativo `../wt-qa/docs/qa/p1.md` com `cwd` na raiz | registra | `guarda.resolver` faz o `realpath` contra o `cwd` |
| Pasta solta com um arquivo `.git` (`gitdir:` apontando para `.git/worktrees/wt-qa` da sessão) | registra | quem escreve um `.git` passa por worktree. Ver o item 3 |
| Repositório estranho (fixture do autor) | sem registro | o `--git-common-dir` é diferente |

## Pontos pedidos
- **Repositório estranho ou caminho forjado.** O repositório estranho é recusado, porque o `--git-common-dir` é comparado depois de `realpath` dos dois lados. Os symlinks também ficam resolvidos: `p` já sai de `realpath` pelo `resolver`, e `topo` e a raiz da sessão também passam por ele. O caminho relativo é resolvido contra o `cwd` da chamada. Uma pasta qualquer com um arquivo `.git` que aponta para a gitdir de uma worktree real se passa por worktree. O registro, porém, continua verdadeiro sobre quem gravou: `papel` e `agente` vêm da sessão, não do caminho, e o `forge-check pr` confere o hash do texto atual. Esse forjamento não dá a um papel a autoria de outro. Fica como limite documentado, e o parecer de segurança paralelo (`docs/security/autoria-worktree.md`) é quem decide se precisa de mais.
- **Custo de git por Write.** São 3 `git rev-parse` por Write ou Edit de `.md` fora da raiz da sessão, de qualquer pasta (inclusive `$TMPDIR` e `~`), mesmo quando o caminho não tem `docs/reviews|qa|devops|security`. Dentro da raiz, o retorno antecipado evita o git. Cada chamada leva alguns milissegundos. No pior caso, o limite de 5 s por chamada (`GIT_TIMEOUT_S`) somado três vezes passa dos 10 s do hook. Ver o item 2.
- **Cobertura dos fixtures.** Cobrem o caso feliz da worktree irmã e o repositório estranho. Faltam a worktree aninhada (bloqueante, item 1), o `.md` fora de `docs/<pasta de parecer>/` numa worktree (sem registro) e o caminho relativo.
- **`docs/hooks.md`.** Precisa de ajuste curto. A linha 30 diz "depois de gravar um `.md` em `docs/reviews/` ..." sem dizer que vale para qualquer worktree do mesmo repositório e não para outro. A linha 81 (limites) deve registrar o forjamento por arquivo `.git`. A linha 52 (estado na cópia principal) já está certa.

## Ajustes
1. **bloqueia** · `hooks/conformidade.py:996` · `if raiz in p.parents: return raiz` dispara antes de olhar a worktree. Por isso uma worktree dentro da raiz da sessão (`.claude/worktrees/<nome>`, do Claude Code) continua sem registro, que é o mesmo sintoma do cartão. **Sugestão:** achar primeiro a cópia de trabalho mais próxima só pelo disco, com `Guarda.raiz_git(p.parent)`, que já existe e procura o `.git` subindo as pastas. Se ela for a raiz da sessão, devolver sem git. Senão, conferir o `--git-common-dir` como hoje e usar essa pasta como raiz. Adicionar o fixture `autoria-worktree-aninhada-registra` com `{"worktree": "proj/.claude/worktrees/x", ...}`, que falha no 02cb437.
2. **recomendado** · `hooks/conformidade.py:1012` · só chamar o git quando o caminho tiver um segmento `docs/reviews|qa|devops|security` e o `.git` mais próximo (item 1) não for o da sessão. Assim um `.md` qualquer fora da raiz não custa git. Guardar o `--git-common-dir` da sessão uma vez por chamada do hook, e não uma vez por alvo.
3. **recomendado** · `docs/hooks.md:30` e `:81` · dizer que vale "em qualquer worktree do mesmo repositório (outro repositório não conta)" e registrar o limite: "uma pasta com arquivo `.git` apontando para uma worktree do repositório conta como ela; o registro continua sendo de quem gravou".
4. **recomendado** · fixtures · somar os casos da cobertura que faltam: `.md` fora de `docs/<pasta de parecer>/` na worktree não registra, e caminho relativo registra.
5. **nit** · `hooks/conformidade.py:1015` · `p.suffix != ".md" or not p.is_file()` repete o filtro da linha 1012. Basta `if raiz not in p.parents`.

## Fora do código
- `CHANGELOG.md`: a linha está em `## [Não publicado]`, seção `### Corrigido`, com o aviso de `afrouxa-regra`. Está correta. Depois do item 1, vale citar a worktree aninhada.
- Commit: `fix(hooks): ...` é um commit só e coerente, e a mensagem está clara.
- `R-NEUTRO` e `R-CUSTO`: nada específico de projeto e nada pago.
- O parecer de segurança é próprio (`docs/security/autoria-worktree.md`, em paralelo) e não foi refeito aqui.
