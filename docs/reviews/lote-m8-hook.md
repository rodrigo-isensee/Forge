---
tipo: review
contrato: 1
pedido: lote-m8-hook
branch: melhoria/lote-m8-hook
commit: 0e64acb2341f43de138ebfdfe405edb264617d11
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-26
---
# Review: lote-m8-hook

Este é o PR 2 do M8. O pre-push de branch roda só os testes afetados pelo `bin/forge-testes` quando o envio é simples e dirigido; fora desse caso, roda a suíte inteira. O diff vai de `35057a2` (a `develop` já com o PR 1, #328) a `0e64acb`: três commits do autor e o merge da `develop`. Ele mexe em `.githooks/pre-push`, `tests/test_pre_push_afetados.py`, `tests/test_testes_tocados.py` (`NaoEPortao`), na spec `tests/mutantes/lote-m8-hook.json` e no fragmento `changelog.d/lote-m8-hook.md`. Sou um revisor independente e não fui o autor do lote. A conferência PA-7 (`docs/engineering/achados-recorrentes.md`) não tem item registrado.

## Achados
- A1 (recomendado) .githooks/pre-push:264 · `python3 bin/forge-testes` põe `bin/` no topo do sys.path: um `bin/argparse.py` da branch toma o plano (sonda: imprimiu "forge-testes: dirigido (test_a)" com rc 0) e o diff vigiado não o vê; usar `python3 -I` aqui e em :274; cartão ao security-engineer
- A2 (recomendado) .githooks/pre-push:250 · o envio dirigido aceita qualquer refs/heads/*; a decisão do dono fala do pre-push de melhoria/*; restringir a `refs/heads/melhoria/*` (o resto cai na suíte inteira) deixa o código igual à decisão
- A3 (recomendado) README.md:68 · README.md:68, docs/economia-de-tokens.md:10 e agents/tech-lead.md:22 ainda dizem que o pre-push roda a suíte inteira; ficaram para o cartão DOCS-REGRA5-PREPUSH (proposta m8-caminho, riscos), que precisa entrar antes da próxima release
- A4 (recomendado) tests/test_pre_push_afetados.py:100 · vírgula dobrada na mensagem ("cita,, não roda"); `NaoEPortao.test_pre_push_recua_para_a_suite_inteira` (tests/test_testes_tocados.py:414) repete a asserção de `NaoRecuaDoHook` (:221); basta uma das duas

## Parecer
**Aprovado.** Não achei defeito de comportamento provado, requisito da decisão do dono descumprido nem problema de segurança com gatilho. Os quatro achados são recomendações e não devolvem a entrega.

Pontos que o brief pede para conferir:
- **Condições do envio dirigido** (`dirigido()`, `.githooks/pre-push:247-267`):
  - um único ref (`n_refs -eq 1`);
  - destino `refs/heads/*`;
  - sha local hexadecimal e diferente de zero;
  - `bin/forge-testes` como arquivo comum, sem link;
  - `HEAD` igual ao sha enviado;
  - árvore limpa, com os arquivos não versionados incluídos;
  - base `refs/remotes/origin/develop^{commit}`, resolvida uma vez para um sha. O plano (`--listar --base`) e a execução (`--base`) usam esse mesmo sha, como pedia o A2 do review do `lote-m8-prepush`;
  - nenhum caminho de `bin/forge-testes`, `tests/config.json` ou `.githooks/` no diff a partir de `merge-base(base, HEAD)`.

  Todas as condições falham fechado (`|| return 1`). O plano só vale se a saída começar com `forge-testes: dirigido (`. Isso exclui "nada alterado; nada a rodar." e "suíte completa (...)", que levam à suíte inteira. Os bloqueios de conteúdo (main, homolog, develop, envio não fast-forward) valem antes, no laço de leitura (:106-132), e `test_bloqueios_de_conteudo_valem_antes_do_filtro` exercita os quatro. O `.forge/run/testes.log` que o `forge-testes` grava está no `.gitignore` (`/.forge`), então o envio dirigido não suja a árvore do push seguinte.
- **Opção C.** Um módulo de teste no diff não tem regra no `MAPA`, por isso cai em `completo`. O hook não precisa de regra própria para isso. `test_so_modulo_de_teste_mudado_roda_a_suite_inteira_e_anota` prova o item 6 do critério de fim da proposta.
- **Recuo para a suíte inteira.** Se `dirigido()` falha, a ordem é `scripts/suite-paralela.py` e, sem ele, `unittest discover`, como antes (:275-281). `so_parecer` continua antes de `dirigido`, sem mudança.
- **Só a suíte inteira anota a árvore verde.** `completa=0` só no ramo dirigido (:272), e a anotação exige `completa = 1` (:305). O caminho `so_parecer` segue anotando, como antes, e o comentário (:241-242) diz que essa anotação é herdada. Esse ponto não mudou neste PR.
- **Os 16 testes de `tests/test_pre_push_afetados.py`** (15 em `PrePushAfetados` e 1 em `NaoRecuaDoHook`). Eles rodam o hook de verdade num repositório descartável, com módulos falsos (`test_a`, `test_sugerir`, `test_forge`) e `bin/forge-sugerir` como caminho mapeado de `bin/`. Cada condição do envio dirigido tem o seu caso, inclusive a ferramenta como link, a branch local `origin/develop` ambígua e o filtro permissivo que se auto-julgaria (controle positivo mais os três caminhos vigiados). A falha no módulo afetado barra o envio, e a falha num módulo não afetado não barra. A guarda de árvore limpa tem um caso com o arquivo mapeado sujo, em que o plano seria o mesmo, então o que prova a guarda é o caminho tomado.
- **`NaoEPortao`** (`tests/test_testes_tocados.py:392-416`). `.githooks` sai da lista de portões que não podem citar o script, e o mínimo de arquivos cai de 5 para 4. Entra `test_so_o_pre_push_cita_o_script_em_githooks`, que exige exatamente `{".githooks/pre-push"}`. O recuo para `discover -s tests` continua exigido. A docstring registra a decisão de 2026-10-24 que substitui a anterior. Com isso, o A1 do review do `lote-m8-mapa` está resolvido.
- **Spec de mutantes.** São 8 mutantes, um por guarda mudada (M1 a M8), cada um apontando o teste que o mata. O registro do autor no pedido diz que todos morreram. Não rodei a mutação: ela é do QA.
- **Teto M14.** `git diff --numstat --no-renames 35057a2...0e64acb` dá 40+3 (`.githooks/pre-push`), 225 (`tests/test_pre_push_afetados.py`) e 11+5 (`tests/test_testes_tocados.py`), ou seja, 284 linhas de 400. A spec em `tests/mutantes/` e o fragmento ficam fora da conta. Não há linha `teto:` e ela não é necessária. Nenhum arquivo de `hooks/` está no diff.
- **Commits.** Seguem Conventional Commits em português, um por mudança coerente, mais o merge da `develop` antes do review (`R-FLUXO`). O fragmento `changelog.d/lote-m8-hook.md` tem o nome da branch.

Sobre o A1: o risco não é novo em classe, porque a suíte inteira também executa código da branch e um `unittest.py` na raiz já faria sombra no `-m unittest`. Mesmo assim, essa sombra contorna a guarda "quem muda o filtro não pode se auto-julgar" que o próprio hook declara (:259-260). Uma sombra acidental tende a quebrar o `forge-testes`, e o hook então cai na suíte inteira. O gatilho exige um arquivo feito de propósito, e o CI do PR roda tudo. Por isso o classifiquei como recomendado e o encaminho como cartão para o `security-engineer`, que faz o parecer próprio deste PR (`R-SEGURANCA`, controle do Forge).

Risco para o PR: `.githooks/` está em `PROTEGIDOS` (`tests/catraca.py:43`). O PR só passa com o rótulo do dono aplicado depois do último push (`R-CONFORMIDADE`).

Regras de ferramenta (cito a saída, não refiz):
- `python3 -m unittest tests.test_pre_push_afetados tests.test_testes_tocados.NaoEPortao` na worktree em `0e64acb` deu `Ran 21 tests ... OK`.
- Sonda de sombra (em `$TMPDIR`): `bin/argparse.py` ao lado de uma cópia do `bin/forge-testes`, e `python3 bin/forge-testes --listar` imprimiu o plano da sombra com rc 0.
- A suíte completa não rodou aqui, por instrução do brief. O pedido registra o pre-push da entrega com `1985 OK`.
