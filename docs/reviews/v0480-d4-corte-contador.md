---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-d4-corte-contador
commit: bf598d2f872df03c42fc799367453eea98b558e9
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Code review: forge-fechar --corte, o corte da versão pelo contador (D4, CORTE-PELO-CONTADOR)

Escopo: pedido v0478, etapa E174.19, PR #869 (`R-REVIEW`), rodada 1. Li o diff inteiro de `aabc476c..bf598d2f`: 2 commits, 13 arquivos, 757 linhas a mais e 7 a menos. Não havia parecer anterior desta branch. O QA e a segurança têm pareceres próprios e não os refaço.

## Achados
- A1 (bloqueante) bin/forge-fechar:1484 · `[ -n "$v_dev" ] && [ -n "$v_hom" ] && [ -n "$v_main" ] || die` tem a forma `A && B || C` (SC2015), que test_fechar.Fechar.test_fechar_sem_a_e_b_ou_c_solto recusa; a suíte do CI, parte 5/5, ficou vermelha no head. Agrupe em `{ ...; } || die` ou troque por um `if`.
- A2 (bloqueante) tests/test_fechar_corte.py:58 · cita `README.md` em 2 linhas (58 e 105) sem entrada na CITACOES_CONHECIDAS (tests/test_reval_delta.py:124); o test_caminho_de_texto_so_e_citado_como_a_lista_conhece falha (CI, parte 4/5). Registre `(2, "teste-le")` na lista, com o parecer de segurança, ou tire o literal.
- A3 (recomendado) bin/forge-fechar:1499 · o V3 só procura o PR homolog -> main aberto. Se o dono fechar o PR sem mesclar, toda volta do --laco que termina com 0 roda o --corte e abre o PR de novo. Antes de criar, procure também um PR fechado com o título `release <v>` e pare nesse caso.

## Sondas
- S1 · `python3 -m unittest test_fechar.Fechar.test_fechar_sem_a_e_b_ou_c_solto` em tests/ no head bf598d2f · espera: OK · obtido: FAIL, `1484: [ -n "$v_dev" ] && [ -n "$v_hom" ]...`
- S2 · `python3 -m unittest test_reval_delta.Guarda.test_caminho_de_texto_so_e_citado_como_a_lista_conhece` em tests/ no head bf598d2f · espera: OK · obtido: FAIL, `(a) tests/test_fechar_corte.py · README.md: 2 linhas, a lista diz 0`

## Parecer
Reprovado por A1 e A2. O CI do PR (run 45478706012) ficou vermelho nas partes 4/5 e 5/5 da suíte, nas duas versões do Python, com exatamente essas duas falhas. Rodei os dois testes localmente e as duas falhas se repetiram. O `bateria (pareceres)` vermelho é a falta dos pareceres e não conta como achado. As duas correções são pequenas e não mudam o comportamento.

O que conferi e está correto:
- **Nunca mescla na main (`R-MAIN`).** O código novo não tem nenhum `gh pr merge`; o único merge do script continua sendo o `mesclar_direto`, que recusa a base `main`. O `--corte` toca a `main` só de dois jeitos. O V1 faz o `git fetch` da `main` e lê a versão do `plugin.json` dela. O V3 roda `gh pr create --base main --head homolog`, que só abre o PR; o merge fica com o dono. O push do V5 vai para `refs/heads/melhoria/marca-<v>`, e `<v>` só aceita dígitos (é o regex do contador). A promoção para a `homolog` sai pelo `--promover`, que já existia, com os portões dele.
- **Com o PR da main aberto, nada é promovido nem reaberto.** Rodei os mutantes M13 (espera o dono, `bin/forge-fechar:1490`) e M20 (PR da main aberto uma vez só, `:1499`), com `forge-mutante --processos 1`; os dois morreram.
- **O teste novo passa.** test_fechar_corte (18 testes) e `test_volta_sem_pendencia_roda_o_corte_no_fim` passaram localmente, com o ambiente limpo. O teste usa o `forge-contador` e o `forge-changelog` reais, e o falso do `gh` confere o prefixo exato do `pr create`.
- **A recusa de opções está fechada.** `--corte` com item, `--ref`, `--laco`, `--limpar` ou `--promover` é recusado, e o laço só corta quando a volta termina com 0. O `-G'"version"'` sem `--first-parent` está correto, porque a `develop` mescla por squash (linha 216).
- **Tamanho e documentação.** O `bin/forge-fechar` ganhou 86 linhas, dentro do teto H1. A documentação, o fragmento de changelog, o critério de reversão e a medida estão em `docs/fechamento-integrador.md`. Os mutantes estão declarados (M1 a M34, sem o M7).
