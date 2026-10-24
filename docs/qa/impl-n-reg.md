---
tipo: qa
contrato: 1
pedido: impl-n-reg
branch: melhoria/impl-n-reg
commit: eaa30f89d08afa9431935a7d2469831842743aeb
parecer: aprovado
revisor: forge:qa-engineer
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-22
---
# QA: impl-n-reg (E1.4)

QA (R-QA) da entrega `38c58247..eaa30f89` (só `docs/` e `changelog.d/`), sobre o HEAD `20202bc` (a entrega mais o parecer de review). Sem gatilho de R-SEGURANCA (decisão técnica do Histórico do pedido): sem casos de abuso. O pedido não tem especificação de UX nem contrato de API; os critérios são o E1 e o E2 do pedido. A E2 não faz parte desta entrega (espera a P-REG-1).

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1: pareceres de branches mescladas chegam à develop, com a origem citada | CT-01 a CT-03 (blob a blob) | conteúdo byte a byte igual ao da origem | passou |
| E1: PR só de docs, no padrão da 0.27.0 | CT-04 (`git diff --stat`) | nenhum arquivo fora de `docs/` e `changelog.d/` | passou |
| E1: a varredura não deixou parecer final de PR mesclado de fora | CT-05 | branch com PR mesclado e parecer ainda não registrado | passou |
| E2: lista para a limpeza, sem apagar nada | CT-06 | nenhuma branch removida; `--merged` vazio | passou |
| R-NEUTRO e demais regras lidas pela bateria | CT-07 | nome de ferramenta de stack no núcleo; trecho de regra copiado | passou |
| Versão e changelog: fragmento e CHANGELOG intocado | CT-08 | um fragmento, seção válida | passou |

## Cenários e resultado real
- CT-01 a CT-03: blob de cada parecer no HEAD contra o commit de origem. `conformidade-leitura.md` `bcf12f7` = `e77dbd0`; `forge-check-lote.md` `41723e3` = `b3b165c`; `suite-paralela-d4.md` `858e4da` = `ad65236`. Os três commits de cópia (c405785, cac4500, 8282f00) tocam um arquivo cada e se revertem sozinhos.
- CT-04: 5 arquivos, +72 −11: os 3 pareceres, `docs/kanban/limpeza-0.28.0.md` e `changelog.d/impl-n-reg.md`.
- CT-05: para cada ponta, `git diff --name-only <head do PR> <ponta>` toca só o parecer registrado (445e769..e77dbd0, b69dbe9..b3b165c, b578714..ad65236). As pontas no remoto agora continuam as mesmas da lista (e77dbd0, b3b165c, ad65236).
- CT-06: `git branch -r --merged origin/develop` lista só `origin/develop`, como diz o kanban. `origin/develop` segue em 38c5824 (`ls-remote` confere). Nenhum ref foi apagado.
- CT-07 e CT-08: cópia limpa por `git clone` em `$TMPDIR` no HEAD `20202bc`, `python3 -m unittest tests.test_forge`: 419 testes, OK (inclui neutralidade, a regra só na fonte e changelog). `forge-check docs`: rc=0. Uma primeira tentativa com `git archive` (sem `.git`) deu 2 erros de `git ls-files`; é limitação da cópia, não da entrega, e sumiu no clone.
- Vermelho antes do verde e mutação: não se aplicam (sem código de produção nem teste novo no diff).

## Coerência de `docs/kanban/limpeza-0.28.0.md` com o remoto de agora
- Tabela de propostas e as 3 pontas: confere.
- `impl-n-cat1` (224dd54) e a branch do postinstall: existem, sem PR; não mexidas.
- Linha de `impl-n-fechar-b` (`:24`, "sem parecer"): velha. A ponta é `c97e2cc` e a branch tem `docs/reviews/impl-n-fechar-b.md` e `docs/security/impl-n-fechar-b.md` que a develop não tem. A classificação "Não apagar" segue certa.
- O texto "Proposta" e a nota de que a E2.1 depende de confirmação batem com a P-REG-1 aberta.

## Recomendações (fora do bloco de achados)
- Com a recomendação do review (`20202bc`): quem executar a E2.1 relê a linha da `impl-n-fechar-b` e reconfere os blobs e as pontas na hora, pois branches de agentes em voo mudam.
- A E2.1 só começa depois da resposta do dono à P-REG-1. O critério por PR mesclado não foi decidido por este parecer.

## Parecer
Aprovado. Sem bug aberto, nada apagado, bateria verde na cópia limpa.
