---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-g2-1-publicar
commit: 939e4d22a8040dcf65b47201c97c6d7a17ed795e
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-26
---
# Review de segurança: v0481 (E6.34, #878, G2.1 `forge-check parecer publicar`), volta por delta

Revalidação por delta da rodada aprovada em dc6bc47e (E6.28; texto no git). Delta lido: `git diff dc6bc47e..939e4d22`. Ele traz só a develop até 34ab6714 (#885, G4 F1 `modo_por_grupo`, já revisada no PR de origem) e a resolução do conflito em `docs/hooks-fixtures.md`, o índice gerado.

Gatilhos: controles-do-forge, autorizacao, ci-cd.

Conferência do patch do item: comparei as linhas mudadas (`git diff -U0`, sem contexto) de `6cc4cd5a..dc6bc47e` (a develop do último merge até o head aprovado) com as de `34ab6714..939e4d22`. Fora de `docs/hooks-fixtures.md`, as duas listas são iguais linha a linha, nos mesmos 31 arquivos. A única diferença está nos três pareceres (`docs/qa`, `docs/reviews`, `docs/security`), regravados depois de dc6bc47e. A lógica do item (`hooks/conformidade.py`, `bin/forge-check`, `bin/forge_pareceres.py`, fixtures, mutantes) não mudou. Nenhuma linha de teste da develop nem da branch saiu.

O que aperta, o que é neutro, o que afrouxa:
- Aperta: nada novo neste delta. As travas do item continuam as aprovadas em dc6bc47e.
- Neutro: `docs/hooks-fixtures.md`, regenerado. O total passa de 3583, o da develop, para 3592 (+9 `contrib-publicar-*` da branch), com `conformidade` de 2709 para 2718 e `contrib-*` de 144 para 153. O `tests.test_indice_fixtures` confere que o índice está em dia (7 testes, OK). O código da develop (#885) entra como veio e não é escopo desta volta.
- Afrouxa: nada. Nenhuma fixture, asserção ou mutante foi retirado. No head mesclado, com o `modo_por_grupo` da develop (todos os grupos em barrar), as 9 fixtures do publicar seguem barrando e liberando como antes.

## Achados anteriores
- A1 da E6.24 (`ultima_raiz` lia depois do `--`): segue fechado. A guarda foi para `hooks/conformidade.py:1389` (as linhas andaram com a develop) e o M37 morre aqui.
- A1 do review E6.18 e A1/A2 da E6.16: seguem fechados, porque o delta não toca o código do item.

## Suíte e CI
Rodei aqui, no 939e4d22, só os módulos tocados. `tests.test_hooks.Hooks.test_fixtures_do_publicar` e `tests.test_forge_pareceres` passam (36 testes, OK), e `tests.test_indice_fixtures` também (7, OK). Rodei `bin/forge-mutante --processos 2 tests/mutantes/v0481-g2-1-publicar-6.json` (`rev=939e4d22a804`): M31 a M37 morreram (`hooks/conformidade.py:2646`, `:2649`, `:2649`, `:1391`, `:1393`, `:1392`, `:1389`), sem sobrevivente.

O run 45732216497 (CI, `headSha` 939e4d22) deu `success` em `bateria (passos)`, `bateria (verificações longas)`, `bateria (python 3.14)`, nas 10 partes da suíte (3.12 e 3.14), nos dois `teto de pulados`, em `instalação (python 3.14)` e em `árvore já provada na develop`. Falha `bateria (pareceres)`, porque o log diz R-REVIEW com o parecer `commit:` desatualizado por `docs/hooks-fixtures.md` e espera os pareceres deste head. `bateria` falha só como agregador dela. O run 45732216156 (Catraca) falha com R-CONFORMIDADE porque o item muda `bin/forge-check` e `hooks/conformidade.py`, e só o rótulo do dono libera. Nenhuma das duas falhas é de teste.
- ci: 939e4d22a8040dcf65b47201c97c6d7a17ed795e verde

## Riscos aceitos e ferramentas
Nenhum risco aceito. `gitleaks`, `semgrep`, `zizmor`, `actionlint` e `osv-scanner` não estão no PATH: fica a lacuna registrada e nada foi instalado (`R-CUSTO`). A revisão foi estática, sem nenhuma chamada de escrita à API.
