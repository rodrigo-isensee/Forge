---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-ci-rapido
commit: 0237a1bcdad85dca462d34aa0426a328f6af78c0
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-15
---
# Review: v047 (CI-RAPIDO, revalidação por delta, E1.311)

Revalidação por delta do parecer anterior (reprovado no head 5b632a48, E1.298, por A1). Li só `forge-check parecer delta docs/reviews/v047-ci-rapido.md` (rc=0). O intervalo é `5b632a48..0237a1bc`, no domínio de código e testes, com um commit de código (0237a1bc, E1.310). Os arquivos são `docs/engineering/achados-recorrentes.md`, `skills/ci-cd/SKILL.md`, `stacks/node-react/pronto.md` e `tests/test_suite_partes.py`. Os commits 1f1214be e d9cd6707 só trazem pareceres e ficam fora do domínio.

## Achados
- A1 (recomendado) tests/test_suite_partes.py:570 · Vem do A4 anterior, que segue aberto: o agregador da develop é conferido pelo texto do YAML. Levar o caso push na develop ao scripts/ci-local numa etapa própria. Não bloqueia: não há defeito provado.

## Sondas

## Parecer
**Aprovado.** O delta muda só texto: três linhas de documentação e uma docstring. Não mexe em guarda nem em caminho executável, então não pede mutante novo.

O que o delta resolve, conferido no diff:
- **A1 anterior (bloqueante):** `stacks/node-react/pronto.md:65` agora diz que o `vitest --shard` divide por arquivo de teste, em partes de contagem igual e sem pesos. Para dividir por unidade de teste, o texto manda quebrar o arquivo grande e conferir a duração de cada parte contra T, remetendo à skill `ci-cd`. Isso bate com a documentação do Vitest e com a regra da skill (linha 57), e "pesos regravados a cada release" saiu. Seguem a guarda de N único, o agregador com o nome do check e `R-CUSTO`.
- **A2 anterior:** a docstring de `tests/test_suite_partes.py:609` diz "as 5 partes", o mesmo que o teste afirma (`assertEqual(n, 5)`, linha 606). O AR-9 subiu para vezes: 4, com última nessa linha, como pedido.
- **A3 anterior:** `skills/ci-cd/SKILL.md:57` troca a medida do Forge por "meça o do seu projeto em `gh run view`". A skill ficou neutra (`R-NEUTRO`).
- Procurei em `tests/` e `scripts/` os trechos tirados ("por unidade de teste, não por arquivo" no Node, "medido: 36 s"). Nenhum teste os lia, então nenhum teste de presença ficou órfão.

Execuções deste review: só a leitura do delta e `forge-check docs`. O delta não tem teste novo nem mutante para rodar. A suíte inteira é do CI do PR (`R-REVIEW`), que ainda não existe, porque o brief é sem PR.
