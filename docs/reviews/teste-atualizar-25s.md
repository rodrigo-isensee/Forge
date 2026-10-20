---
tipo: review
contrato: 1
pedido: teste-atualizar-25s
branch: melhoria/teste-atualizar-25s
commit: 4057d257490c53589ba2858cf4e06415773713f7
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-20
---
# Review: teste do forge atualizar sem falha por relógio

Escopo: `bd204b8..4057d25`, 3 arquivos (`tests/test_atualizar.py`, `changelog.d/teste-atualizar-25s.md`, este parecer). Quem revisa não é o autor. Veredito: **aprovado**, sem achados bloqueantes.

## Ferramentas (saída citada)
- `python3 -m unittest tests.test_atualizar.EsperaDoTerminal -v`: `Ran 2 tests in 14.513s` / `OK`. A suíte completa fica com o QA e o CI.
- `forge-check docs`: sem saída de erro.

## Conferência do pedido
- E1: `rodar` com respostas espera o fim do processo ou da saída até `limite` (120 s) e só mata quem fica sem saída por `ocioso` (20 s); a marca "[TRAVOU esperando resposta]" foi mantida. Quando o processo sai, o pty devolve EOF/OSError e o laço termina na hora, sem esperar o ocioso.
- E2: dois testes novos em `EsperaDoTerminal`: processo lento (total acima do ocioso, nunca um intervalo ocioso inteiro sem saída) termina com código 0 e sem a marca; pergunta sem resposta continua marcada e com código diferente de 0.
- E3: fragmento `changelog.d/teste-atualizar-25s.md` presente, com o nome da branch.

## R-QA
Nenhuma asserção saiu nem ficou mais frouxa: o diff em `tests/test_atualizar.py` só mexe em `rodar` (parâmetros, laço) e acrescenta a classe nova; as asserções dos testes existentes ficam intactas. A pergunta sem resposta continua falhando (teste 2, e o vermelho antes do verde registrado pelo autor). O prazo de detecção passou de 25 s fixos para 20 s sem saída, que é mais estrito para quem trava.

## Peso na suíte
Os testes novos somam cerca de 10 s (7,5 s + 2 s, mais a preparação). Aceitável para provar os dois lados.

## Segurança, devops
Só código de teste; sem gatilho de segurança, sem pipeline.

## Achados

## Detalhe dos achados
- Recomendação (não bloqueia): `tests/test_atualizar.py`, teste do processo lento: dá para reduzir o total de 7,5 s (por exemplo, passos de 1 s e ocioso de 2 s) sem perder a prova. Opcional.
- Recomendação (não bloqueia): `limite` e `ocioso` são parâmetros do `rodar`, mas o ocioso de 20 s ainda é fixo para os demais testes; se o FLAKY-1 mostrar lentidão maior que isso entre linhas, vale torná-lo configurável por ambiente.
