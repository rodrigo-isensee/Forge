---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-bp2-i1-conserto
commit: d816262d85319c97fed47261d3179f485df5bf08
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Code review: `forge-fechar --conserto` (BP2 I1, E38.5)

Escopo lido: `git diff 004ce869..d816262d` (`bin/forge-fechar`, `docs/fechamento-integrador.md`, `changelog.d/`, a classe `Conserto` de `tests/test_fechar.py` e o formato de `tests/mutantes/fechar-conserto*.json`), mais o que o C4 lê do CI (`scripts/falhas-no-resumo.py`, `scripts/suite-paralela.py:322`).

## Achados
- A1 (bloqueante) bin/forge-fechar:1089 · C4 falha aberto: o sed descarta a anotação de subteste cujo parâmetro tem `)` (`test_b.Caso.test_um (entrada='f()'): ...`); com outro teste anotado, esse nunca é conferido nos pulados (S1). Tome o id até o primeiro espaço ou `:`, sem casar o parêntese.
- A2 (recomendado) tests/test_fechar.py:1345 · o gh falso do C4 aceita qualquer `--commit`; o mutante `--commit "$conserto_topo"` na linha 1099 do script passa os 38 testes da classe (S2). Confira no falso o sha igual ao head do PR (checklist 12).

## Sondas
- S1 · anotações `tests/test_b.py<TAB>test_b.Caso.test_um (entrada='f()'): AssertionError` e `tests/test_c.py<TAB>test_c.K.test_dois: AssertionError` no sed de bin/forge-fechar:1089 · espera: os dois ids · obtido: só test_c.K.test_dois
- S2 · bin/forge-fechar:1099 com `--commit "$conserto_topo"` e `python3 -m unittest test_fechar.Conserto` · espera: algum teste vermelho · obtido: Ran 38 tests, OK

## Parecer
Reprovado pelo A1 (R-REVIEW: requisito C4 com defeito provado, mesma classe do A1 da segurança em `docs/security/v0479-bp2-i1-conserto.md`). O formato vem de `scripts/falhas-no-resumo.py` (`CABECALHO` com o subteste guloso e `teste + " (sub)"`), e o `unittest` gera `(entrada='f()')` para `subTest(entrada="f()")`: a anotação real tem o `)` interno. Sozinho, o teste perdido deixa `ids` vazio e o C4 para (falha fechada); com outro teste anotado no mesmo run, o perdido sai da conferência. Correção mínima: na linha 1089, capturar `^([^\t]*)\t([A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)+)[ :]`, com um caso em `Conserto` e o mutante que volta ao padrão de hoje. Na mesma volta entra o A1 da segurança (pulado por `setUpClass` e por módulo); este parecer só o cita, sem refazer.

Conferido sem achado: o código segue o desenho C1 a C7 e as decisões D2 e D5 do dono; falha fechada em toda leitura (cada `ler` com `die`); o C3 prende o head trazido pelo 2b ao merge-tree do revisado com o topo; o passo 6 relê o topo antes do merge; `--conserto` recusa `--lote` e `--armar`; o fixture limpa a marca e o head do pai herdados (AR-4, d816262d). Tamanho (H1): 104 linhas de código novas em `bin/forge-fechar`, fora comentários, testes e docs, um comportamento só. Reversão escrita em `docs/fechamento-integrador.md` ("Reversão"). Commits em Conventional Commits, com `afrouxa-regra` no título do commit da mudança.

Ferramentas: `shellcheck` fora do PATH desta estação (o CI do PR o roda; sem instalação, `R-CUSTO`). Suíte: não rodada (brief; o CI do PR é o portão). Rodados aqui: `tests.test_fechar.Conserto`, 38 testes OK em 74,6 s no head d816262d, e a sonda S2. Os mutantes declarados (6 arquivos) não foram rodados: são do QA (E38.7).
