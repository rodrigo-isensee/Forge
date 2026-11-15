---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-ci-rapido
commit: 88fe9ff40c95a8cae5565c6ea7105117f0a8f4dc
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-14
---
# Review: v047 (CI-RAPIDO, implementação, E1.257)

Intervalo `origin/develop..88fe9ff4` (merge-base 067b2a9f, igual ao Base-sha): 3 commits (desenho E1.242, parecer de segurança do desenho E1.247, implementação E1.248). Revisei o código da E1.248: `.github/workflows/ci.yml`, `scripts/suite-partes.py`, `scripts/pesos-do-ci.py`, os testes, os mutantes declarados, o README e o texto do modelo de projeto. Os pesos de `tests/pesos-d4.json` não foram recalibrados, por desenho (etapa própria depois do primeiro CI).

## Achados
- A1 (bloqueante) README.md:69 · README passou a dizer 5 partes, mas tests/test_forge.py:335 exige o trecho "3 partes paralelas por versão de Python": test_readme_diz_baratas_antes_da_fila_afetados_e_suite_inteira_no_ci reprova no head (reproduzido). Atualizar o teste para o texto novo.
- A2 (recomendado) docs/economia-de-tokens.md:10 · Ainda diz que a bateria roda "em 3 partes paralelas por versão de Python"; agora são 5 por unidade, também na develop. Atualizar na mesma entrega (definição de pronto, documentação afetada).
- A3 (recomendado) scripts/suite-partes.py:134 · dividir, pesos_por_modulo (:123) e esperado_da_parte (:90) ficaram sem chamador de produção desde que --parte usa dividir_por_unidade; só os testes os chamam. Remover com os testes deles ou dizer no código por que ficam.
- A4 (recomendado) scripts/pesos-do-ci.py:85 · math.isfinite é redundante com 0 <= seg <= TETO_S (inf e NaN já falham a comparação); por isso o mutante M20 sobrevive, equivalente. Tirar o isfinite e o M20, ou marcar o M20 como equivalente na spec.
- A5 (recomendado) tests/test_suite_partes.py:570 · S1 do desenho pede teste de comportamento do agregador da develop (perna vermelha, pulada, cancelada); o teste lê o texto do YAML. O scripts/ci-local só simula pull_request; levar o caso push na develop a ele numa etapa própria.
- A6 (recomendado) skills/ci-cd/SKILL.md:55 · O desenho (2.4) põe o orçamento de tempo e a guarda de completude também na skill ci-cd e nos stacks/*/pronto.md; o head só mudou templates/projeto/docs/engineering/protecao-de-branch.md. Fazer ou registrar no PR que fica para outra etapa.

## Sondas

## Parecer
**Reprovado** por A1: o head deixa a suíte vermelha. A troca de "3 partes" por "5 partes" no README quebra uma asserção de texto em `tests/test_forge.py:335`, que continua pedindo o trecho antigo. Reproduzido com `python3 -m unittest discover -s tests -p test_forge.py -k test_readme_diz_baratas_antes_da_fila`: `AssertionError: '3 partes paralelas por versão de Python' not found`. Correção mínima: trocar o trecho esperado por "5 partes paralelas por versão de Python". É defeito provado (`R-REVIEW`): o CI do PR reprovaria no `bateria`. Os outros achados são recomendados e não devolvem.

O que está certo, conferido no código:
- **Prova da promoção (S1, A1 da segurança):** os agregadores `rapida` e `rapida-quatorze` mantêm os nomes exatos de `JOBS_DE_PROVA` (`scripts/arvore-testada.py:29`), com `if: always()` e a restrição de push na develop. Eles só leem `needs.*.result` e exigem `success` da matriz e do teto. Não fazem checkout nem rodam script. As pernas levam "parte K/5" no nome e não colidem com eles.
- **N único (S2, A3):** `test_o_n_das_matrizes_e_o_mesmo_nos_tres_lugares` confere as 4 matrizes, `--parte K/N`, `--somar-pulados N` e o nome. O teto de pulados é um job próprio no `needs` do agregador, o que fecha o caso da matriz `[1,2,3,4]` com `/5`.
- **Pulados (S5, A4):** o download só lê o run corrente, sem `run-id` nem token, e há teste que confere essa ausência.
- **Divisão por unidade (S9):** `completude_da_divisao` confere por ID do discover; `rodar` repete a conferência de completude sobre o que executou. A falha é fechada.
- **Anotação (S6):** só sai o alfabeto `[A-Za-z0-9_.]` com segundos finitos, e o dado é escapado. O título não leva `,` nem `:`.
- **`pesos-do-ci.py` (A2):** filtra a execução como o `arvore-testada` (push, develop, ci.yml, repositório e head_repository, success) e aceita só pernas em `success` do mesmo run, num conjunto 1..N completo. Unidade fora do plano, segundo fora de [0, 900] ou anotação fora do formato é descartada inteira. O script nunca grava no repositório e o erro sai sem o token.
- **`R-CUSTO`:** sem dependência nova, sem cache novo e só runner gratuito. **`R-VERIFY`:** sem `continue-on-error`, sem `[skip ci]` e sem teste pulado.

Execuções deste review, no head 88fe9ff4:
- `tests/test_forge.py` (o módulo inteiro, por causa de A1): 610 testes e 1 falha, só a de A1.
- `tests/test_suite_partes.py`: 44 OK. `tests/test_pesos_do_ci.py`: 16 OK. `test_ci_local`, `test_arvore_testada`, `test_suite_partes_paralelas`, `test_suite_reuso`, `test_pesos_teto` e `test_modelos_projeto`: OK.
- `bin/forge-mutante --processos 1` nas 3 specs: 33 de 34 mortos (M1 a M19 e M21 a M34). M20 sobrevive e é equivalente (A4).
- A suíte inteira é do CI do PR. Ainda não há PR nem CI neste head, e não a rerrodei (`R-REVIEW`).

Tamanho (M14): cerca de 1110 linhas de código e teste (`ci.yml` 201, `suite-partes.py` 140, `pesos-do-ci.py` 209 e os testes 564). O corpo do PR deve trazer `teto: excedido, <n> linhas, <motivo>`. Vale o motivo de ser um comportamento só (a divisão em 5 partes por unidade e a prova da develop), sem mexer em `hooks/`.

Na volta: corrigir A1. O A2 é barato e vai junto. A revalidação é por delta (`forge-check parecer delta docs/reviews/v047-ci-rapido.md`).
