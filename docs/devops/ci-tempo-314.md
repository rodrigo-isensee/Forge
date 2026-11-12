---
tipo: revisao-devops
contrato: 1
pedido: v0457
branch: melhoria/ci-tempo-314
commit: 65f402e7c65349036c36c9c769c77f6a09b0ffff
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-11-12
---
# Review de devops: ci-tempo-314

## Achados
- A1 (recomendado) .github/workflows/ci.yml:37 · o comentário diz "13-20 min (3.12) e 17-20+ min (3.14)", mas a medida é 3.12 em 12,7 a 15,7 min e 3.14 em 15,8 e 16,5 min quando termina; ajuste os números, o teto de 30 não muda.

## Detalhes
Aprovado. O diff d3453407..65f402e7 só troca `timeout-minutes` de `rapida` (ci.yml:37) e `rapida-quatorze` (ci.yml:79) de 20 para 30, a asserção da lista de tetos em tests/test_catraca.py:3322 (["30","30","45",...]) e o fragmento changelog.d/ci-tempo-314.md. Nome de job, `if`, passos e permissões ficam iguais; nenhum teste ou portão foi tirado (R-VERIFY).

Medida conferida com `gh run view --json jobs`:
- 43206261879: 3.14 cancelada em 20,0 min (passo "Testes do Forge" 11:06:54 a 11:26:57); 3.12 falhou em 15,7 min (falha de teste, não de tempo).
- 43212986502: 3.14 cancelada em 20,3 min; 3.12 falhou em 12,9 min.
- 43219346032: 3.14 cancelada em 20,3 min; 3.12 passou em 15,1 min.
- Anteriores, sem cancelamento: 43099085052 (3.12 15,8 min, 3.14 16,2 min) e 43080466112 (3.12 13,4 min, 3.14 16,5 min).
O autor está certo de que a 3.14 batia no teto de 20. Mas a duração real dela nesses três runs é desconhecida (cancelada, só se sabe que passa de 20), e o histórico dos dois runs verdes dá 16 a 17 min. O salto de 16 para mais de 20 min é variação de runner, não de conteúdo. 30 min dá 50% de folga sobre o normal e 10 min sobre o pior visto; é plausível, mas não provado até um run da 3.14 terminar sob carga. Sugestão: o checkpoint de tempo da release (`gh run list`) confere a duração da 3.14; se passar de 25 min, abre cartão.

Dividir o job não é necessário agora. Se for preciso depois, o `scripts/arvore-testada.py:29` (JOBS_DE_PROVA) lê o job pelo nome exato ("checagem rápida (push na develop)" e "... python 3.14") e `prova_valida` (linha 64 em diante) exige `name` igual e `conclusion: success` num único job por versão. Dividir em dois jobs exigiria que JOBS_DE_PROVA aceitasse uma lista de nomes por versão com todos em success, mais o teste dele e os de tests/test_catraca.py (lista de tetos, linha 3322); ou um job agregador com o nome atual (`needs`, `if: always()`), como já existe nos agregadores de 5 min, o que mantém a prova intacta. Fora deste escopo.

Custo e minutos: o teto só vale quando o job passa dos 20 min; o runner público é gratuito (R-CUSTO), então não há gasto novo. Pior caso por push: +10 min por job em dois jobs em paralelo, dentro da franquia. Cancelar no teto desperdiça os 20 min já gastos e reprova o push; 30 min reduz esse desperdício.

Ferramentas: `actionlint` não rodado (diff só altera inteiros e um comentário; sem pesado); `gh run view`/`gh run list` usados. Revisão de segurança do workflow: sem mudança em permissions, SHA de ações, gatilhos ou segredos.

## Custo e rollback
Sem recurso novo nem minutos pagos. Rollback: reverter o commit (volta os dois tetos e a asserção para 20); mudança em `.github/` pede o envio pelo dono (token sem escopo `workflow`) e vale o rótulo `afrouxa-regra` se a catraca o exigir (o teto sobe, o que afrouxa limite de tempo); avisar o tech-lead.
