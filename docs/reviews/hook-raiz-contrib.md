---
tipo: review
contrato: 1
pedido: hook-raiz-contrib
branch: melhoria/hook-raiz-contrib
commit: 1fa594650a77002bc0f4e638719951147a01a3d4
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-23
---
# Review: hook-raiz-contrib

Pedido HOOK-RAIZ-CONTRIB (E1), revisado no pedido HOOK-RAIZ-CONTRIB-REV (E1.1). Diff `139a3b4...1fa5946`, 2 commits: `196906c` (teste vermelho) e `1fa5946` (proteção). 8 arquivos, 99 inserções, 3 remoções.

## Achados

## Parecer
**Aprovado.** A mudança fecha o controle pedido, só acrescenta proteção e não mexe em nenhuma entrada antiga.

O que conferi:

- **O `*` em `casa()` vale por uma pasta só** (`hooks/conformidade.py:265-271`). Cada parte é passada por `re.escape` e as partes são unidas por `[^/]+`, com `re.match` ancorado no início. Num diretório, a comparação usa `rel + "/"` sem âncora no fim (mesma semântica de prefixo do `startswith` de hoje); num arquivo, usa `$`. Como o caminho já chega resolvido (`realpath`, sem `..`), o `[^/]+` não sobe nem atravessa níveis. As sondas abaixo confirmam: `~/.forge-contrib/wt/a/docs/pedidos/` (dois níveis) não casa, e `docs/pedidosX/` também não.
- **Nenhuma entrada nova da política se abre.** Só as duas entradas novas (`hooks/conformidade.json:50` e `:53`) têm `*`, as duas com `~/` e `quem: ["jarvis"]`. Elas passam pelo ramo `home` de `caminho_barrado` e não chegam ao `em_qualquer_lugar` (que só roda para entrada relativa com `quem` vazio). Nenhuma lista de `escrita_permitida` usa `*`. A mudança em `_citacoes` (`hooks/conformidade.py:1095`) usa o sufixo depois do último `*` (`/docs/pedidos`, `/docs/briefs`) como filtro de `pode_ser_protegido`. Esse filtro já incluía `docs/pedidos` e `docs/briefs` (vindos das entradas relativas), então nada novo fica de fora.
- **Nenhuma entrada antiga mudou.** O diff de `hooks/conformidade.json` é só `+2`. As entradas `~/.forge-contrib/docs/pedidos/` e `.../briefs/` continuam onde estavam, e a sonda s4 segue recusada nos dois commits.
- **As fixtures cobrem os quatro casos**: `tests/hooks/conformidade/pasta-contrib-{pedido,brief}-{tech-lead-bloqueia,jarvis-libera}.json`, com tech-lead recusado (rc 2, stderr com o motivo da entrada) e jarvis aceito (rc 0, sem `agent_type`) em pedidos e em briefs, e `HOME` isolado em `{tmp}/home`.
- **`docs/hooks.md:35` diz o mesmo que o código**: "as cópias em `~/.forge-contrib/docs/` e em `~/.forge-contrib/<pasta>/docs/`", só o `jarvis`. `<pasta>` no singular corresponde ao `*` de um nível.
- **Fragmento** `changelog.d/hook-raiz-contrib.md` (`### Corrigido`). O `CHANGELOG.md` não foi editado (ADR 0006).
- **Commits**: Conventional Commits em português, com vermelho antes de verde (`R-REVIEW`, bug com teste que falha antes).
- `R-NEUTRO`, `R-CUSTO`: nada específico de projeto e nada pago. `tests/config.json` não foi tocado.

Evidência de execução (HOME em `$TMPDIR/tech-lead-hookraiz/`, nunca na área real):

- `python3 -m unittest tests.test_hooks` em `1fa5946`: `Ran 43 tests in 80.706s` / `OK` (log `$TMPDIR/tech-lead-hookraiz/test_hooks-1fa5946.log`).
- Sondas diretas no hook (`rodar` de `tests/test_hooks.py`, num projeto com `.forge/versao`) em `1fa5946`:
  - recusadas (rc 2): s1 tech-lead Write `forge/docs/pedidos/`; s3 dev Write `estudo/docs/briefs/`; s4 entrada antiga; s7 `echo > ~/.forge-contrib/forge/docs/briefs/y.md`; s8 `rm -r .../forge/docs/pedidos`; s9 `tee .../p/docs/pedidos/z.md`; s11 `docs/docs/pedidos/`; s12 qa; s13 pasta oculta `.oculta/`; s14 `mv` para `briefs/`.
  - aceitas (rc 0): s2 jarvis; s5 `wt/a/docs/pedidos/` (dois níveis, fora do escopo); s6 `pedidosX/`; s10 `docs/reviews/`.
- As mesmas sondas em `196906c` (sem a proteção): s1, s3 e s7 dão rc 0 e s4 dá rc 2. A falha existia e a correção a fecha.

Regras de ferramenta: o Forge não tem `docs/engineering/praticas.md` com "decidida por". Por isso não há saída de comando de regra para citar. A bateria completa roda no pre-push deste envio e no CI do PR.

Recomendações fora do bloco, porque não bloqueiam e o parecer é aprovado:

1. O `*` de um nível deixa sem proteção uma worktree aninhada (`~/.forge-contrib/wt/<nome>/docs/pedidos/`, sonda s5). Hoje o Forge não versiona `docs/pedidos/` nem `docs/briefs/` (0 arquivos em `git ls-files`), e o escopo diz `<pasta>`. Se um dia a área de trabalho do Jarvis morar em `wt/<nome>/`, isso vira cartão.
2. `casa()` agora aceita `*` em qualquer entrada, mas `em_qualquer_lugar` (entrada relativa com `quem` vazio) compara o texto literal. Quem puser `*` numa entrada desse tipo terá uma proteção pela metade. Uma frase no docstring ou em `docs/hooks.md` restringindo o `*` às entradas `~/` evita isso.

Segurança (`R-SEGURANCA`, controle do Forge) e QA têm parecer próprio (E2.1 e E3.1 do pedido HOOK-RAIZ-CONTRIB-REV). Não os refiz.
