---
tipo: qa
contrato: 1
pedido: versao-033
branch: melhoria/prepush-so-docs
commit: 0ba1a876f9176c74d9dae97ca208805c3f652e43
parecer: aprovado
revisor: forge:qa-engineer
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-03
---
# QA: prepush-so-docs (versao-033, L03, E18 PREPUSH-SO-DOCS)

QA (`R-QA`) por `forge:qa-engineer`, que não é autor nem revisor (D-ETAPAS-INST = A). Testado em `0ea34e0a791fd104871514b75b5ddb05409e8b26` (código em `0ba1a87`, o resto são pareceres). Base `928e61b66015f7ee2a2e585dc8178e07dc16be39`. Os recomendados dos pareceres de review, segurança e devops (submódulo com `diff.ignoreSubmodules`, testes de modo, symlink e submódulo, A1 a A3 do review) não se repetem.

## Achados
- A1 (recomendado) tests/test_hooks_volta_propriedades.py:207 · teste de tempo falhou uma vez na suíte paralela (2 != 0, vigia de 3 s) sob carga e passou 3 de 3 isolado e no módulo; hooks/ não mudou no diff; cartão de estabilidade, não devolve este item.

## Critério → teste → resultado
Obrigações da seção E18 do modelo de ameaças (sem `CA-n`: é controle do Forge). Prova de ponta a ponta feita por mim, num repositório descartável com remoto bare, `core.hooksPath` apontando o hook do modelo e um `pre-push.local` que grava marca; envio real com `git push` ou stdin direto no hook.

| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| C-1 diff dos commits enviados, todas as refs | duas refs (docs e código) no mesmo `git push` | várias refs | roda tudo, passou |
| C-2 branch nova, tag, apagar, git que falha, diff vazio, saída sem NUL | `git push` de ref nova, `v1`, `:nova`; git falso com `diff` saindo 1 e com saída sem NUL; `feat feat` | sha zerado, falha do git, vazio | roda tudo em todos, passou |
| C-3 nome literal | docs/a.md, README.md, docs/sub/x.ts, src/a.md, docs/com espaco.md, docs/a\nb.ts, remoção de md: pulam. .github/x.md, .github/x.yml, src/a.ts, a.MD, a.md.ts, docsx/a.md, renome src para docs, src\nx.ts, symlink em src, modo: rodam | caixa, prefixo, renome, espaço, quebra de linha | passou (docsx/a.md pulou por ser `.md`, como manda o critério "termina em .md") |
| C-4 stdin intacto, aviso do pulo, `pre-push.local` que falha | pulo imprime a linha do modelo; só docs com local exit 3: rc 0; código com local exit 3: rc 1 | falha do hook local | passou |
| R-VERIFY e main rodam sempre | `feat:main` recusado; não fast-forward recusado; objeto remoto ausente recusado; nada roda o local | main, histórico reescrito | passou |
| T-1 a T-4 | leitura do diff: sem variável, opção, arquivo nem mudança em CI, `.githooks/pre-push` do Forge ou checagens do template | n/a | passou |
| Vermelho antes do verde | cópia da entrega com o hook da base | n/a | 7 falhas de 27 na base (abaixo) |

## Execução real
- Suíte inteira (`.githooks/pre-push --suite`, 4 processos, esperou a vez da trava): 2516 testes, 1064 s, `FAILED (failures=1, skipped=28)`, rc=1. A falha: `test_hooks_volta_propriedades ... test_t_vigia_de_prazo_recusa_com_marcador_e_libera_sem` (2 != 0), teste de tempo do vigia dos hooks, rodando ao lado de testes de CPU pesada; `hooks/` e `scripts/` não mudam no diff. Reexecutado isolado: 3 vezes OK (12,5 s). O módulo inteiro mais `test_prepush_so_docs`: 36 testes OK. Os 27 testes do item passaram na suíte (processo 2, rc 0). Nenhum teste foi pulado por mim.
- `scripts/validar-plugin.sh`: `Validation passed`, rc=0. `bin/forge-check docs`: rc=0.
- `shellcheck` não existe nesta máquina; fica com o CI do PR (o `test_pre_push_shellcheck` roda no CI).
- Vermelho: `bin/forge-testes --vermelho 928e61b…` caiu na suíte completa (o diff muda `bin/forge-testes`) e estourou 480 s sem veredito (rc=124, não vale). Prova alternativa: cópia do HEAD com o `pre-push` do modelo da base, `python3 -m unittest tests.test_prepush_so_docs`, `Ran 27 tests, FAILED (failures=7)`; com o hook da entrega, 27 OK.
- Mutantes declarados: não aplicável, o diff não toca `bin/` de decisão, `hooks/`, `.githooks/` do Forge nem `tests/catraca.py` (o `bin/forge-testes` só ganha uma linha de mapa).
- PA-7 (`docs/engineering/achados-recorrentes.md`): AR-3 (a lista de nomes do teste é negativa, já é A1 do review), AR-4 (o teste não herda `GIT_*`; minhas sondas rodaram com `GIT_CONFIG_*` nulos), AR-5 (sem Python no hook), AR-6 (o `2>/dev/null` do diff não esconde falha: a falha roda tudo, provado com git falso), AR-7 (o hook limpa `GIT_DIR` antes do primeiro git novo) conferidos.

## Parecer
Aprovado. O hook cumpre o limite exato e os controles C-1 a C-5 de ponta a ponta, sem mudança proibida, e as checagens R-VERIFY e da `main` seguem intactas. A única falha da suíte é um teste de tempo fora do diff, não reproduzido, registrado como recomendado.
