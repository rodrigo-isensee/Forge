---
tipo: review
contrato: 1
pedido: ta-3
branch: melhoria/ta-3-testes-tocados
commit: 98bd38a9f2bc11064942727d4838cadf7de47ad2
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-16
---
# Review independente: teste dirigido durante a iteração (TA-3)

Escopo: `6ebd201...98bd38a` (base 6ebd2016939293d451f3584a2d3ae3e6fde381bf; o autor não é este revisor). 4 arquivos, 2 commits (`e389b99` docs, `98bd38a` feat): `bin/forge-testes`, `tests/test_testes_tocados.py`, `docs/economia-de-tokens.md`, `changelog.d/ta-3-testes-tocados.md`.

Veredito (rodada 1, sobre `98bd38a`): **REPROVADO** por 1 achado que bloqueia: o mapa manda rodar módulos que não incluem o único módulo que exercita alguns caminhos mapeados. O resultado é um "dirigido verde" falso. Os outros 2 achados são recomendados. Tudo volta ao autor; este revisor não corrige o diff.

## Conferido e ok
- Falha fechada: caminho sem regra, `tests/config.json`, o próprio script (`ALTERA_O_MAPA`, bin/forge-testes:58), módulo mapeado sem arquivo (:91-93) e erro do git (:121-122) caem na suíte completa. Os testes cobrem cada caso (tests/test_testes_tocados.py:78-92, :162-165).
- Log em `.forge/run/testes.log`: `git check-ignore -v` responde `.gitignore:20:/.forge`. Teste em tests/test_testes_tocados.py:195-196.
- Não é portão: `grep -rn forge-testes .github .githooks hooks scripts` não acha nada. O teste percorre essas pastas e exige pelo menos 5 arquivos (tests/test_testes_tocados.py:176-184), e o pre-push continua com `python3 -m unittest discover -s tests` (:186-188).
- Regra 5 (docs/economia-de-tokens.md:10): cita o script e traz a frase literal do dono, "A, desde que para main rode tudo.". Diz que pre-push, review, QA, CI e o caminho para a main rodam a suíte inteira.
- `tests/config.json` não foi alterado (só acréscimo: nada). O texto é neutro (R-NEUTRO): nada de projeto, nome ou stack. O fragmento `changelog.d/ta-3-testes-tocados.md` tem o nome da branch. `bin/forge-testes` está no índice com modo 100755. Usa só a biblioteca padrão (R-CUSTO ok).
- Commits pequenos, Conventional Commits em português.
- Execução: `python3 -m unittest tests.test_testes_tocados -q` dá `Ran 21 tests in 0.843s OK`. Exemplo dirigido: `bin/forge-testes --base 6ebd201... --listar` dá `forge-testes: suíte completa (bin/forge-testes altera o mapa ou a configuração)`, como esperado para esta branch.
- Ferramentas (regra 5): não rodei a suíte completa nem o validar-plugin (fora do brief). Ficam para o QA e o CI.

## Achados

1. **bin/forge-testes:41, :47, :48, :52** · problema: `tests/test_atualizar.py` exercita o fluxo de atualização de verdade. Copia `bin/`, `migrations/`, `templates/` e `.claude-plugin/` do repositório (test_atualizar.py:116-117), roda `bin/forge-doutor` e `bin/forge` (:640, :674) e o hook `hooks/doutor.py` (:22, :473). Nenhuma dessas regras inclui `test_atualizar`. Saída real de `planejar`: `migrations/0.7.0/migrar` vai para CONTEUDO sem test_atualizar; `bin/forge-doutor` vai para `['test_doutor']`; `hooks/doutor.py` vai para hooks sem test_atualizar; `.claude-plugin/plugin.json` vai para CONTEUDO sem test_atualizar. Da mesma forma, `stacks/node-react/pesados.json` é lido por test_hooks.py:48, mas `stacks/` cai em CONTEUDO, que não inclui `test_hooks`. Nesses casos o autor recebe um verde dirigido que não rodou o módulo que testa a mudança. Isso contraria o próprio comentário do mapa ("Prefira ser largo a ser estreito", :33) e a promessa da docstring (rodar "os módulos de teste que cobrem esses caminhos"). Os portões continuam pegando o erro, mas tarde e com uma rodada a mais. · sugestão: incluir `test_atualizar` em `bin/forge-doutor`, `bin/forge`, `hooks/.*` (ou uma regra própria para `hooks/doutor.py`), e criar uma regra própria para `(migrations|templates|\.claude-plugin)/.*` com CONTEUDO + `test_atualizar`. Incluir `test_hooks` em `stacks/.*`. Fixar cada caso com teste em `Mapa` (por exemplo `migrations/0.7.0/migrar` contém `test_atualizar` e `stacks/x/pesados.json` contém `test_hooks`). Opcional, mais robusto: um teste que procura em cada `tests/test_*.py` os caminhos do repositório que ele lê via `RAIZ / "<pasta>"` e afirma que o plano dessa pasta inclui o módulo. · severidade: **bloqueia**.

2. **bin/forge-testes:72** · problema: `git diff --name-only` detecta renomeação por padrão (diff.renames) e lista só o nome novo. Se um arquivo mapeado for movido, os módulos do caminho antigo não entram no plano. · sugestão: `git("diff", "--name-only", "--no-renames", ancora)`, que lista os dois lados. Um teste com `git mv` no repositório de brinquedo. · severidade: recomendado.

3. **bin/forge-testes:56** · problema: a lista "Sem regra (de propósito)" não cita `tests/hooks/`, `tests/migracoes/` e `tests/transcricoes/` (fixtures), nem `CLAUDE.md`/`.gitignore` na raiz. Todos caem corretamente na completa, mas o comentário parece exaustivo e não é. · sugestão: escrever "por exemplo" ou completar a lista. · severidade: recomendado.

## Segurança, devops e QA
A segurança roda em paralelo (`docs/security/`), e este parecer não a refaz. O script não mexe em pipeline nem em CI, então não há parecer de devops. O QA vem depois deste parecer e do de segurança.
