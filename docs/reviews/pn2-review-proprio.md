---
tipo: review
contrato: 1
pedido: pn2-review-proprio
branch: melhoria/pn2-review-proprio
commit: 8e7abd9e65ef4b5272ec4b19be2c04523b796955
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-30
---
# Review: pn2-review-proprio

Code review (`R-REVIEW`) do C3 da P-N2 parte 1 (pedido PN2-REVIEW-PROPRIO, revisão no PN2-REVIEW-PROPRIO-REV, E1.1): commits 4d58f72 e 8e7abd9 sobre a develop 042e5d8f73fc659615a4313c7213a661dfc32ce0.

## Achados
- A1 (recomendado) bin/forge-check:4611 · etapa de review escrita de outro jeito (`(tech-lead): review do delta`, 7 ocorrências nos pedidos, ou papel `forge:tech-lead`) não casa e gera aviso falso; só aviso, e no delta a branch já está no remoto. Se incomodar, aceitar `review` e normalizar o papel com `nome_do_papel`.
- A2 (recomendado) bin/forge-check:4622 · segundo `git ls-remote` da mesma branch no mesmo `forge-check brief` (o `estado_do_commit`, linha 4254, já consulta); com rede lenta dobra a espera. Sugestão: ler o remoto uma vez em `avaliar_brief` e passar adiante.
- A3 (recomendado) tests/test_etapa_do_brief.py:579 · três linhas em branco antes de `class ReviewProprio` (o resto do arquivo usa duas).

## Parecer
**Aprovado.** Sem bloqueante.

Checklist (leitura):
- **Escopo (E1, E2):** faz o que o pedido pede, nem mais nem menos. A linha é exatamente a do E1; o rc não muda (a tupla sai com `False`, mutante M5 morto); branch já no remoto, pedido com a etapa de review e brief sem `Branch:` não ganham a linha. Nada em `hooks/`, `tests/config.json` nem `agents/conferente.md` (fora do escopo respeitado).
- **Lugar da função:** `aviso_de_review_proprio` fica fora de `conferir_brief` e é chamada em `avaliar_brief` (bin/forge-check:4651), como registra a DECISÃO TÉCNICA 2026-10-30 02:20 do pedido: `conferir_brief` não recebe a raiz e o git precisa dela; a saída do `forge-check brief` é a mesma.
- **Critério da etapa de review:** papel `tech-lead` (lido por `ler_pedido_brief`, primeiro nome antes da vírgula, minúsculo) e `: code review` no texto da etapa. Nos pedidos atuais a forma `(tech-lead): code review` aparece 126 vezes e cobre o caso comum; o risco declarado de etapa escrita de outro jeito está no A1 e custa só um aviso a mais, nunca um portão.
- **Remoto e silêncio sem rede:** reusa `remoto_da_branch` (o mesmo `ls-remote` do `commit:`, sem duplicar lógica); com `conferido` falso (sem rede, sem `origin`, timeout) nada se imprime (M3 morto). O nome da branch sai por `caminho_impresso` (sem controle na saída) e entra no git como `refs/heads/<branch>` depois de `origin`, sem virar opção.
- **Testes:** `ReviewProprio` em tests/test_etapa_do_brief.py usa o remoto local nu de `QuatroDefeitosDoScript.com_remoto` (sem rede, git sem `GIT_*` herdado pelo `git()` do script, AR-4 não se aplica). Os quatro casos do E2 estão lá, mais o caso de code review de outro papel (M7). O teste sem rede compara o rc antes e depois do remoto. Rodado aqui: `python3 -m unittest tests.test_etapa_do_brief.ReviewProprio -v`, 4 testes, OK.
- **Mutação (ferramenta, citada):** `bin/forge-mutante tests/mutantes/pn2-review-proprio.json`: M1 a M7 `morreu`. `bin/forge-mutante --cobertura --base 042e5d8…`: as linhas 4618, 4620 e 4623 cobertas pela spec. Lista de mutantes completa para as guardas novas (classe AR-1 conferida, sem ocorrência).
- **Ajuda e changelog:** a frase entrou na ajuda do `brief` (docstring do módulo, bin/forge-check:53, junto das outras linhas que só avisam) e o fragmento `changelog.d/pn2-review-proprio.md` existe; `CHANGELOG.md` e versão intocados.
- **Teto por PR (decisão M14):** `git diff --numstat --no-renames 042e5d8...8e7abd9`: bin/forge-check 20+1, tests/test_etapa_do_brief.py 39 = 60 linhas de código e teste, de 150; fora da conta a spec em `tests/mutantes/` e o fragmento. Um comportamento só. Essa conta não tem relação com o TETO-60 de carga da máquina.
- **Achados recorrentes (PA-7):** AR-1 a AR-10 conferidos; nenhuma classe se repete neste diff. Sem linha AR nova nesta rodada (DECISÃO TÉCNICA 2026-10-29 15:28 do pedido T1-CONF-ESCOPO-REV); as recomendações acima são das classes "critério textual estreito" (A1), "chamada de rede repetida" (A2) e "formatação" (A3), nenhuma registrada antes.
- **Segurança:** sem gatilho (só uma linha de aviso, nada muda no que reprova); nada para o `security-engineer`. Sem custo (`R-CUSTO`), neutro (`R-NEUTRO`).
- **Commits:** dois, Conventional Commits em português, cada um coerente (comportamento com teste; spec de mutantes e fragmento).

`R-REVIEW` cumprido para o head 8e7abd9e65ef4b5272ec4b19be2c04523b796955. O QA (`docs/qa/pn2-review-proprio.md`) é de outra delegação e não é refeito aqui.
