---
tipo: review
contrato: 1
pedido: autoria-worktree
branch: melhoria/autoria-worktree
commit: 25c51e3
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-15
---
# Review: autoria de parecer gravado em outra worktree

## Revalidação após o merge da base (commit revisado 25c51e3)

Escopo: `git diff ca87905 25c51e3` (o que o PR entrega sobre a develop com #125, #126 e #129) e `git diff 531b131 25c51e3 -- hooks/conformidade.py`. Revisão independente do merge.

Parecer: **aprovado**, sem ajustes novos.
- Sobre a develop atual, `hooks/conformidade.py` tem um único hunk (`@@ -1138`): `diretorio_comum`, `raiz_do_parecer` e `autoria`, idênticos ao aprovado em 531b131 (filtro por caminho de parecer, hash lido antes de `raiz_do_parecer`, registro no `.forge/run/` comum). Nenhum outro trecho do hook diverge da develop.
- Sem interação com o que a develop trouxe: as mudanças do conferente e da catraca estão em outros hunks, e `raiz_git`, `resolver`, `hook.run` e `hook.trava` continuam como a função `autoria` os usa. A trava de carga (`hooks/agentes.py`, escape `FORGE_CARGA_LIVRE=1` só do dono) não é tocada pelo PR.
- `CHANGELOG.md` e `docs/hooks.md`: só a linha em `### Corrigido` e as duas linhas de `docs/hooks.md`, sem conflito com a develop.
- Gitdir relativo segue como o cartão 16d, decidido pelo time; não reprova.

Ferramentas (sobre 25c51e3, load 0.5): suíte `Ran 562 tests in 171.298s`, `OK`; `scripts/validar-plugin.sh`: `Validation passed`. Segurança e QA revalidam em pareceres próprios.

## Volta 2 (commit revisado 531b131)

Escopo: `git diff 504ef11..531b131`, com `hooks/conformidade.py` (`diretorio_comum`, `raiz_do_parecer`, `autoria`), os 7 fixtures novos `tests/hooks/conformidade/autoria-*`, `CHANGELOG.md` e as duas linhas alteradas de `docs/hooks.md`. A história foi reescrita só para trocar a identidade: o 02cb437 da volta 1 virou o 1d82a22. O parecer de segurança (`docs/security/autoria-worktree.md`) é próprio e não foi refeito aqui.

Parecer: **aprovado**. O bloqueante foi resolvido, e os 3 recomendados e o nit também. Sobra um recomendado novo, que não bloqueia: worktree criada com caminhos relativos (item R1 abaixo).

### Ferramentas (rodadas depois do rebase, sobre o 531b131)
- Suíte completa (`env -u FORGE_ABERTURA_FEITA python3 -m unittest discover -s tests`): `Ran 561 tests in 159.969s`, `OK`. A contagem é a mesma da volta 1 porque os fixtures são subtestes de `test_fixtures`.
- `scripts/validar-plugin.sh`: `✔ Validation passed`.
- Falha antes e passa depois: o `tests.test_hooks` com o `hooks/conformidade.py` do 1d82a22 sobre os fixtures do 531b131 dá `FAILED (failures=3, errors=1)`. O `ERROR` é o `autoria-worktree-aninhada-registra`, e os `FAIL` são `autoria-git-forjado-comum-nao-registra`, `autoria-git-forjado-nao-registra` e `autoria-git-symlink-nao-registra`. Com o 531b131 passa.

### Achados da volta 1
1. **bloqueia, resolvido.** A worktree aninhada (`.claude/worktrees/<n>`) registra. `raiz_do_parecer` acha primeiro a cópia mais próxima pelo disco (`Guarda.raiz_git`) e só devolve a raiz da sessão se o topo for ela (ou um ancestral, quando a sessão não está na raiz do git). Fixture `autoria-worktree-aninhada-registra`, que falha no 1d82a22.
2. **recomendado, resolvido.** Não há mais chamada git. O filtro por pares `("docs", reviews|qa|devops|security)` em `p.parts` vem antes de qualquer leitura do disco, e um `.md` qualquer fora dessas pastas não custa nada.
3. **recomendado, resolvido.** O `docs/hooks.md` diz "qualquer worktree do mesmo repositório, dentro ou fora da raiz da sessão (outro repositório não conta)", e a seção de limites registra o forjamento dos dois arquivos dentro do `.git`.
4. **recomendado, resolvido.** Entraram os fixtures `autoria-worktree-fora-de-docs-nao-registra` e `autoria-worktree-relativo-registra`. Também entraram `git-forjado`, `git-forjado-comum`, `git-symlink` e `git-dir-no-ambiente`.
5. **nit, resolvido.** O filtro repetido saiu; `rel` vazio quando `raiz` é None.

### `diretorio_comum` e `raiz_do_parecer`
- **Vínculo de volta.** O `.git` (arquivo) tem de começar com `gitdir:`, a pasta tem de estar em `<comum>/worktrees/<n>`, e o `gitdir` dela tem de apontar de volta para o mesmo `<topo>/.git`. Com isso, a pasta solta que aponta para uma worktree real e a que aponta para o `.git` comum são recusadas, cada uma com o seu fixture. Os submódulos (`.git/modules/<n>`) ficam fora, e está certo, porque são outro repositório.
- **Symlinks.** Um `.git` que é link é recusado (`is_symlink`), e o `raiz_git` não sobe para um `.git` mais acima, então não há desvio. Os topos e a raiz da sessão saem de `realpath`, e por isso a comparação `esperado == str(marca)` é feita entre caminhos reais.
- **Caminhos relativos.** O `file_path` relativo é resolvido contra o `cwd` (fixture). O `gitdir:` relativo do `.git` é resolvido contra `topo`, que está certo. O `gitdir` de volta relativo não: ver R1.
- **Filtro por pares.** Ele casa `docs/<pasta>` em qualquer altura do caminho absoluto. Um falso positivo, como `/x/docs/qa/proj/a.md`, só custa leituras de disco, e o `rel.startswith` relativo à cópia continua sendo o portão. Nenhum parecer legítimo é cortado pelo filtro.
- **Parecer legítimo que deixa de registrar.** Sondei pela chamada direta de `diretorio_comum` num repositório temporário: a cópia principal e a worktree com caminho absoluto devolvem `<proj>/.git`, e a worktree criada com `git worktree add --relative-paths` (git 2.55 local; também `worktree.useRelativePaths=true`) devolve `None`. É o R1. A worktree movida sem `git worktree repair` também não registra, mas aí o próprio git a considera quebrada. Está aceitável.
- **`sha` antes da conferência.** Ler o conteúdo antes das leituras do `.git` reduz a janela entre gravar e anotar. Concordo.
- **Cache por sessão descartado.** Concordo. Sem processo git, o custo por alvo são poucos `stat` e duas leituras de arquivos pequenos, só para caminhos de parecer. Um cache acrescentaria estado e invalidação sem ganho mensurável.

### Ajustes
- **R1, recomendado** · `hooks/conformidade.py:1009` · o `gitdir` de volta pode ser relativo à pasta `<comum>/worktrees/<n>` (git 2.48 ou mais novo, com `--relative-paths` ou `worktree.useRelativePaths`), e `os.path.realpath(os.path.dirname(volta))` o resolve contra o `cwd` do processo. Assim a worktree legítima fica sem registro, e o `forge-check pr` recusa o parecer quando o `autoria.jsonl` existe (falso bloqueio, não falsa autoria). Contra a `develop` não é regressão, porque lá nenhuma worktree registrava. **Sugestão:** `alvo = os.path.join(pasta, volta)` (absoluto continua absoluto), comparar `os.path.join(os.path.realpath(os.path.dirname(alvo)), os.path.basename(alvo))` e somar o fixture `autoria-worktree-gitdir-relativo-registra`. Pode entrar nesta branch ou num cartão próprio.

### Fora do código
- `CHANGELOG.md`: a linha de `### Corrigido` foi reescrita, cita a worktree aninhada e os casos recusados e mantém o aviso de `afrouxa-regra`. Está correta.
- Commit `fix(hooks): registra a autoria de worktree aninhada e valida o vínculo do .git`: um commit só, coerente, com mensagem clara.
- `R-NEUTRO` e `R-CUSTO`: nada específico de projeto e nada pago.

## Volta 1 (commit revisado 02cb437, hoje 1d82a22)

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
