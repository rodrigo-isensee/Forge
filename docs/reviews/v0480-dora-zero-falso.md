---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-dora-zero-falso
commit: 38d9c349c671dd76f5a71f30f3734bac2d0d64d3
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0478 · forge-check dora diz nao-medido sem o arquivo (FORGE-DORA-ZERO-FALSO), E160.2

PR #844, head 38d9c349, base develop 789fc141. Diff: `bin/forge_dora.py` (+30/-12, dentro do teto H1), `tests/test_forge_dora.py`, `tests/mutantes/v0480-dora-zero-falso.json` (novo), `tests/mutantes/v0457-dora.json` (sai o M7) e o fragmento `changelog.d/v0480-dora-zero-falso.md`. Sem suíte local (o CI do PR a roda; no momento da leitura, `bateria (pareceres)` falhava por falta deste parecer e a suíte estava pendente).

## Leitura
- Comportamento: `linhas_do_quadro` devolve `boas=None` quando `ler_texto` dá None (arquivo ausente ou pasta no lugar), `bin/forge_dora.py:68-70`; `vazao` (`:96`) e `falhas` (`:115`) propagam; `calcular` (`:160`) troca taxa e recuperação por `{"estado": "nao-medido", "motivo": ...}`. Arquivo existente e vazio segue 0. Faz o que o cartão pede, nem mais.
- A saída de texto (`linhas_de_texto`) já serializa qualquer dict por `campos`; o teste do comando confere a linha `vazao estado="nao-medido" motivo=...`. Nenhum outro consumidor do JSON de `forge_dora` no repositório (grep em `bin`, `hooks`, `skills`, `docs`, `agents`).
- Frequência e espera da mudança não dependem dos quadros e seguem medidas (o teste afirma `frequencia n=3` no caso ausente).

## M7 da v0457-dora e o teste que fixava 0 (não afrouxa)
- O M7 mutava `(ler_texto(arq) or "")`, trecho que não existe mais no head (só resta em `bin/forge_governanca.py:417`, outro arquivo, coberto pela `v0433-integracao-8`). A guarda que o substitui é `if texto is None:` (`:69`), com mutante próprio (M1 da spec nova), mais M2 a M4 nas três propagações: um por linha de guarda mudada.
- O teste antigo afirmava (a) ausente vale 0 e (b) ausente não gera recusado. (a) é o defeito corrigido; (b) segue afirmado no teste novo (`recusados == []`, `tests/test_forge_dora.py:137`). O "vazio vale 0" passou para `test_quadro_vazio_existente_segue_zero`, com arquivo existente. Nada que a guarda antiga protegia ficou sem teste.
- O teste `Brutos` ganhou um `escapes.md` vazio para continuar medindo `taxa_pct`; o limiar `MINIMO_PARA_RESUMO` segue coberto.

## Ferramentas (citadas, não refeitas)
- `bin/forge-mutante tests/mutantes/v0480-dora-zero-falso.json` no head: M1, M2, M3 e M4 morreram (M1 a M3 por erro do teste declarado sob o mutante, que é morte válida; M4 por asserção).
- `python3 -m unittest tests.test_forge_dora`: 17 testes, OK.

## Parecer
Aprovado. A correção é pequena, mantém o 0 para quadro existente e vazio, e a retirada do M7 acompanha a retirada da condição que ele mutava, com guarda nova mutada e testada no ramo de falha.
