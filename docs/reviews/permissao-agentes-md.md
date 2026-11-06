---
tipo: review
contrato: 1
pedido: versao-033
branch: melhoria/permissao-agentes-md
commit: ce082b2864ee78172fc3b5bd1e2f1b2e822b4e17
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-04
---
# Review: permissao-agentes-md (pedido versao-033, frente 0.34)

Revalidação por delta da leitura do lote textos-034 (parecer 77a422eebe94e998f2d8881b215d46bf8d8a3f21, branch rev-textos-034), que dividiu o lote em um PR por cartão (A1 de lá). Delta lido: `git diff` dos arquivos de texto entre o commit do cartão no lote e o head desta branch, o teste novo e o fragmento do changelog. Já lido no 77a422e: o restante do texto, que é igual.

## Delta
- `skills/trabalho-em-paralelo/SKILL.md:15`: o aviso ao dono agora só vale quando a regra de permissão de `agents/**` não está configurada; com a regra aplicada, o dono não é interrompido. Isso atende o A5 do 77a422e e a D11 = A. O agente recusado continua sem contornar (`R-CONFORMIDADE`).
- `tests/test_permissao_agentes_md.py` confere a condição; `changelog.d/permissao-agentes-md.md` traz só a linha deste cartão.

## Comandos (head ce082b2)
- `python3 -I -m unittest discover -s tests -p test_permissao_agentes_md.py`: OK.
- `python3 -I tests/neutralidade.py`: rc=0.
- M14: 21 linhas de teste, um cartão; abaixo de 150. A skill tem 17 linhas, dentro de `limite_linhas`.

Gatilho: nenhum.

## Achados

## Parecer
Aprovado.
