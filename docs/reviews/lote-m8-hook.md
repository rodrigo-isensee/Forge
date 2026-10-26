---
tipo: review
contrato: 1
pedido: lote-m8-hook
branch: melhoria/lote-m8-hook
commit: 0ff73965e955912d52fc078fa03d219a6f43e0a6
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-26
---
# Review: lote-m8-hook

Este é o PR 2 do M8. O pre-push de `melhoria/*` roda só os testes afetados pelo `bin/forge-testes` quando o envio é simples e dirigido; fora desse caso, roda a suíte inteira. Base `35057a2` (a `develop` com o PR 1, #328). Revisor independente: não fui o autor do lote. A conferência PA-7 (`docs/engineering/achados-recorrentes.md`) não tem item registrado.

## Revalidação por delta (volta 1, `0ff7396`)
- **Delta lido** (`bin/forge-check delta --parecer docs/reviews/lote-m8-hook.md`, intervalo `0e64acb..0ff7396`, commits `4877566` e `0ff7396`): `.githooks/pre-push` l.240-241, 252, 266 e 276; `changelog.d/lote-m8-hook.md` l.3; `tests/mutantes/lote-m8-hook.json` l.4 e 46-82; `tests/test_pre_push_afetados.py` l.182-223. Os pareceres de QA e de segurança no intervalo não são código e não os revisei.
- **Já lido na rodada 1 e fora do delta:** o resto de `.githooks/pre-push` (`dirigido()`, `so_parecer`, laço dos bloqueios, anotação da árvore verde), o resto de `tests/test_pre_push_afetados.py`, `tests/test_testes_tocados.py` (`NaoEPortao`) e a linha 2 do fragmento.
- **A1 (rodada 1), fechado.** `.githooks/pre-push:266` (plano) e `:276` (execução dirigida) chamam `python3 -I bin/forge-testes`. Com o `-I`, o `bin/` da branch não entra no sys.path e as variáveis `PYTHON*` são ignoradas. O `bin/forge-testes` só importa a biblioteca padrão (l.30-43), então o `-I` não quebra nada. O processo que roda os testes (`sys.executable -m unittest`, l.537) põe a raiz no sys.path, não o `bin/`. Isso é o mesmo que a suíte inteira já faz, e não é uma regressão. Os dois testes novos matam um mutante cada. `test_modulo_falso_em_bin_nao_decide_o_plano_nem_a_execucao` (M9) mostra que, sem o `-I` no plano, o `bin/json.py` falso faria o hook anunciar o dirigido. `test_modulo_falso_ja_na_base_nao_zera_a_execucao_dirigida` (M10) põe o falso na base, fora do diff, e mostra que, sem o `-I` na execução, o dirigido rodaria zero testes. As outras chamadas `python3` do hook (l.195, 197, 272, 279 e 282) rodam a suíte, não decidem o plano. O juízo final sobre elas é da segurança (decisão técnica de 20:28) e não o refaço.
- **A2 (rodada 1), fechado.** `.githooks/pre-push:252` passou a aceitar só `refs/heads/melhoria/*`, como diz a decisão do dono de 2026-10-24. `test_dirigido_so_vale_para_melhoria` cobre `feature/x`, `fix/x` e `chore/x` (subTest) e confere que esses envios rodam a suíte inteira, sem o aviso do dirigido. Ele também mata o M11.
- **Teste da âncora (A1 do QA).** `test_ancora_e_a_base_comum_com_a_develop_nao_a_ponta_da_develop` monta uma `develop` que andou depois da saída da branch e grava nela um `tests/config.json` (o commit `0ff7396` corrige o teste para gravar o arquivo de fato). Com a âncora na ponta da `develop`, o diff vigiado mostraria o arquivo e o envio cairia na suíte inteira. Com o `merge-base`, o envio segue dirigido. O teste mata o M12.
- **Spec de mutantes.** M1, M2, M3 e M8 (árvore limpa, ferramenta como link, HEAD igual ao enviado, um único ref) saíram, e entraram M9 a M12. A spec fica em 8, que é o teto de `MAXIMO_DE_MUTANTES` (`bin/forge-mutante:43`). As quatro guardas que perderam o mutante continuam no código e com teste próprio: `test_arvore_suja_com_arquivo_mapeado_nao_vira_envio_dirigido`, `test_ferramenta_que_e_link_roda_a_suite_inteira`, `test_commit_enviado_diferente_do_head_roda_a_suite_inteira` e `test_varias_refs_rodam_a_suite_inteira`. A troca troca guardas antigas por guardas mudadas nesta volta, o que atende ao "uma por guarda mudada" do pedido dentro do teto. Não abro achado. A mutação em si é do QA.
- **Teto M14.** `git diff --numstat --no-renames 35057a2...0ff7396` dá 42+3 (`.githooks/pre-push`), 267 (`tests/test_pre_push_afetados.py`) e 11+5 (`tests/test_testes_tocados.py`), ou seja, 328 linhas de 400. A spec, o fragmento e os pareceres ficam fora da conta. Não há linha `teto:` e ela não é necessária. Nenhum arquivo de `hooks/` está no diff.
- **Commits do delta.** `fix(pre-push)` e `test(pre-push)` seguem Conventional Commits em português, um por mudança coerente. O fragmento ganhou uma linha que descreve o `-I` e o filtro.

## Achados
- A3 (recomendado) README.md:68 · README.md:68, docs/economia-de-tokens.md:10 e agents/tech-lead.md:22 ainda dizem que o pre-push roda a suíte inteira; ficaram para o cartão DOCS-REGRA5-PREPUSH (proposta m8-caminho, riscos), que precisa entrar antes da próxima release
- A4 (recomendado) tests/test_pre_push_afetados.py:100 · vírgula dobrada na mensagem ("cita,, não roda"); `NaoEPortao.test_pre_push_recua_para_a_suite_inteira` (tests/test_testes_tocados.py:414) repete a asserção de `NaoRecuaDoHook` (:221); basta uma das duas

## Parecer
**Aprovado.** O A1 e o A2 da rodada 1 estão fechados. O A3 e o A4 continuam como recomendações e, pela decisão técnica de 20:11, ficam fora desta volta. Não achei defeito de comportamento provado, requisito descumprido nem problema de segurança com gatilho no delta.

Regras de ferramenta (cito a saída, não refiz):
- `python3 -m unittest tests.test_pre_push_afetados tests.test_testes_tocados.NaoEPortao` na worktree em `0ff7396` deu `Ran 25 tests ... OK`.
- A suíte completa não rodou aqui, por instrução do brief. Ela roda no pre-push e no CI do PR.

Risco para o PR: `.githooks/` está em `PROTEGIDOS` (`tests/catraca.py:43`). O PR só passa com o rótulo do dono aplicado depois do último push (`R-CONFORMIDADE`).

## Rodada 1 (`0e64acb`, parecer `7d6a9e2`)
Achados da rodada 1: A1 (`-I` em :264 e :274) e A2 (dirigido para qualquer `refs/heads/*`), os dois fechados acima; A3 e A4, mantidos acima.

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
