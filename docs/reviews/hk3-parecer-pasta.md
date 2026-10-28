---
tipo: review
contrato: 1
pedido: hk3-parecer-pasta
branch: melhoria/hk3-parecer-pasta
commit: 212203a39fd4419c45dd797ea0737b7d05001d19
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-28
---
# Review: o hook parecer resolve a pasta do git como o git e o bash (HK3-PARECER, PR A, E1 e E3)

Escopo: `ff3936ae4011a95f25c37280fe32e4fa5ced0d95...212203a39fd4419c45dd797ea0737b7d05001d19` (3 commits: `46d48cf` fix, `87853c8` test, `212203a` test). Rodada 1, leitura da branch inteira (sem parecer anterior, sem delta).

Veredito: **reprovado** por 3 achados bloqueantes, os três da mesma classe (variável que o bash lê por conta própria, reescrita na linha, não é seguida pelo hook), todos provados por sonda com rc=0 onde o modelo de ameaças exige recusa. Um achado recomendado.

## Ferramentas (citadas, não refeitas)
- `python3 -m unittest tests.test_hooks_parecer_pasta tests.test_testes_tocados`: `Ran 82 tests in 14.016s` / `OK`.
- `bin/forge-testes --listar hooks/parecer.py`: dirigido, 14 módulos, inclui `test_hooks_parecer_pasta`; com `bin/forge-testes` no diff, suíte completa (fica no CI do PR, decisão M8).
- `tests/config.json`: fora do diff.
- Mutantes: 4 specs em `tests/mutantes/hk3-parecer-pasta-{1..4}.json` (29 mutantes, pelo commit `87853c8`); não reexecutados aqui.

## Conferência dos pontos do brief
| Ponto | Resultado |
|---|---|
| `-C` em ordem, relativo ao anterior | ok: `pastas_do_git` junta todos os `-C` das opções globais e `pasta_do_git` os compõe (`hooks/parecer.py:234-255`); opção depois do subcomando não conta (fixture `pasta-passa-opcao-depois-do-subcomando-nao-e-global`) |
| `cd` | ok, salvo A1 e A3: um argumento só, `cd` sozinho vai ao HOME, opção ou argumento a mais é desconhecido (`hooks/parecer.py:224-231`) |
| `~` | parcial: `~` e `~/` usam o HOME do processo do hook, não o da linha (A3) |
| Variável só de atribuição literal solta | ok: `soltos` fecha em subshell, if/for, `\|\|`, pipeline e segundo plano, e o fechamento é pegajoso até o fim da linha (lado seguro); prefixo, `export`, `+=` e `read` tornam a variável desconhecida; 12 fixtures `pasta-barra-atribuicao-*` |
| Lado seguro para pasta desconhecida | ok para merge e pull (`hooks/parecer.py:555-560` recusa com o conserto no texto); para o `gh` a pasta desconhecida cai na da sessão (A4, fora da regra, recomendado) |
| `pull --rebase` da própria branch com push | ok: `pasta-passa-cd-literal-pull-rebase-e-push` e `pasta-passa-pull-rebase-da-propria-branch-sem-cd` passam; com HEAD de integração recusa (`pasta-barra-pull-rebase-na-integracao`, `pasta-barra-pull-na-integracao-com-push`) |
| Mapa do `forge-testes` e teste de contagem | ok: o módulo novo importa `test_hooks`, que roda o `bin/forge-check`, então entra em `FORGE_CHECK` e na regra de `hooks/` (`bin/forge-testes:72,101-102`); a contagem 27 → 28 (`tests/test_testes_tocados.py:61`) é a consequência direta, não escopo novo (decisão técnica de 2026-10-28 11:30 conferida) |
| `analisar()` inalterado para `conformidade.py:904` | ok: `analisar` está fora do diff; `hooks/conformidade.py:904` segue lendo a mesma tupla (`'cd', dir`, `'branch', dir, nome`); a resolução nova mora só em `conferir` |
| Teto M14 | ok: 213 linhas de código e teste (`bin/forge-testes` 5, `hooks/parecer.py` 173, `tests/test_hooks_parecer_pasta.py` 33, `tests/test_testes_tocados.py` 2); corpus `tests/hooks/`, `tests/mutantes/` e `changelog.d/` ficam fora; uma classe de comportamento em `hooks/` (a pasta do git), com corpus próprio |
| Teste de pasta afirma mínimo | ok: `minimo(..., 50, ...)` e os dois lados (`tests/test_hooks_parecer_pasta.py:25-27`) |
| Fragmento de changelog | ok: `changelog.d/hk3-parecer-pasta.md` |
| Achados recorrentes (PA-7) | lista vazia; nada a conferir; a classe dos achados abaixo é nova, sem linha `AR-<n>` nesta rodada |

## Sondas (prova dos bloqueantes)
Fixtures no formato do corpus, rodadas pela mesma máquina do `tests/test_hooks.py` contra o `hooks/parecer.py` de `212203a`, em `$TMPDIR/tech-lead-hk3-parecer-pasta/sonda/parecer/`. Montagem: `{raiz}` = `proj` em `develop`, worktree `home/proj` em `melhoria/x`, `HOME={tmp}/home`. Todas esperavam rc=2.
- controle `cd {raiz} && git merge melhoria/x` (cwd na worktree): rc=2 (a montagem barra o merge na integração).
- s1 `HOME={raiz}; cd ~ && git merge melhoria/x` (cwd na worktree): rc=0.
- s2 `HOME={raiz}; cd && git merge melhoria/x`: rc=0.
- s3 `HOME={raiz}; git -C ~ merge melhoria/x`: rc=0.
- s5 `export CDPATH={tmp}; cd proj && git merge melhoria/x` (cwd `{tmp}/home`, onde `proj` é a worktree de trabalho): rc=0; o bash vai a `{tmp}/proj` (develop).
- s6 `CDPATH={tmp} cd proj && git merge melhoria/x` (mesmo cwd): rc=0.
- s7 `printf -v GIT_DIR %s {raiz}/.git; export GIT_DIR; git merge melhoria/x` (cwd na worktree): rc=0; o git mescla no repositório de `{raiz}`.

## Achados
- A1 (bloqueante) hooks/parecer.py:228 · requisito (regra do modelo: CDPATH com cd relativo recusa): CDPATH por export ou prefixo vira desconhecido e cai no os.environ, que não o tem; o cd relativo é julgado pela pasta atual (sondas s5 e s6, rc=0)
- A2 (bloqueante) hooks/parecer.py:526 · requisito (regra do modelo: GIT_DIR por export na linha recusa): printf -v, read ou mapfile seguido de export GIT_DIR não marca o desvio; `todas` limpa as variáveis mas não liga `desviado` (sonda s7, rc=0)
- A3 (bloqueante) hooks/parecer.py:189 · segurança com gatilho (merge na integração sem parecer): `com_til` e o cd sozinho usam o HOME do processo do hook; HOME=<integração> na linha leva o bash a outra pasta que o hook não vê (sondas s1, s2 e s3, rc=0)
- A4 (recomendado) hooks/parecer.py:533 · gh pr create, ready e merge com pasta desconhecida (pushd, cd $UNK) são julgados pela pasta da sessão; fora da regra do modelo (só merge e pull), mas o docstring diz que o desconhecido nunca vale pela sessão

## Parecer
Reprovado. A estrutura está boa: a resolução mora só em `conferir`, `analisar` ficou intacto para o `conformidade`, o fechamento de `soltos` é pegajoso (erra para o lado seguro), o corpus cobre as linhas P e B do modelo e o PR fica numa classe em `hooks/`, dentro do teto. Os três bloqueantes são a mesma lacuna: o hook segue as variáveis que a linha cita (`$NOME`), mas não as que o bash e o git leem sozinhos (`HOME` no `~` e no `cd` sem argumento, `CDPATH` no `cd` relativo, `GIT_DIR`/`GIT_WORK_TREE`/`GIT_COMMON_DIR` exportados sem `=` na palavra).

- A1 · `hooks/parecer.py:227-229` · o teste é `variaveis.get("CDPATH") or os.environ.get("CDPATH")`; `export CDPATH=...` e `CDPATH=... cd` põem CDPATH em `ruins` e o tiram de `variaveis`, e o hook trata "desconhecido" como "vazio". Sugestão: guardar no ambiente o conjunto de nomes que a linha tocou (`ruins`, `todas`) e tratar CDPATH tocado e não fixo como "pode estar ligado" (cd relativo vira None). Fixtures: as duas sondas s5 e s6. Severidade: bloqueia.
- A2 · `hooks/parecer.py:526-531` · `todas` (read, printf, mapfile, declare sem `=`, source, eval) apaga as variáveis, mas não liga `desviado`; e `export GIT_DIR` sem `=` não entra em `ruins`. Sugestão: `desviado |= todas` (ou: export/declare de um nome de `DESVIOS`, com ou sem `=`, liga o desvio). Fixture: s7 e a variante com `read GIT_DIR`. Severidade: bloqueia.
- A3 · `hooks/parecer.py:187-189` e `:539` (o `cd` sozinho) · `com_til` e o `cd` sem argumento usam `os.path.expanduser("~")`; com `HOME` fixo na linha, o bash usa o novo; com `HOME` tocado e não fixo, o hook não sabe. Sugestão: `com_til` recebe `variaveis` e o conjunto tocado: HOME fixo vale o valor fixo, HOME tocado e não fixo dá None. Fixtures: s1, s2 e s3. Severidade: bloqueia.
- A4 · `hooks/parecer.py:533` · `raiz_gh = pasta or hook.cwd()`: depois de `pushd <outra worktree>` ou `cd $UNK`, o `gh pr create` sem `--head` num projeto infere a head da branch da sessão. A fixture `pasta-passa-gh-depois-de-pushd-vale-a-pasta-da-sessao` fixa o comportamento com `--draft`, e o comportamento é o de antes do PR. Sugestão: registrar como limitação no docstring (hoje ele diz "nunca é julgado pela pasta da sessão") ou recusar o `gh pr` não rascunho com pasta desconhecida, num cartão próprio. Severidade: recomendado.

Achado de segurança (A1 a A3 são contorno do portão R-REVIEW): vai como cartão ao `security-engineer`, que dá o parecer próprio em paralelo (E2.1); este review não o refaz.
