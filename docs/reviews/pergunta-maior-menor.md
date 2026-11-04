---
tipo: review
contrato: 1
pedido: versao-033
branch: melhoria/pergunta-maior-menor
commit: 88c82dd4d4c97f004e0d273ef70c142f443e5c18
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-04
---
# Review: pergunta-maior-menor (pedido versao-033, frente 0.34)

Revalidação por delta da leitura do lote textos-034 (parecer 77a422eebe94e998f2d8881b215d46bf8d8a3f21, branch rev-textos-034), que dividiu o lote em um PR por cartão (A1 de lá). Delta lido: `git diff f7fe80b melhoria/pergunta-maior-menor` nos arquivos de texto, `tests/config.json`, o teste novo e o fragmento do changelog. Já lido no 77a422e: `docs/regras/R-DECISAO.md`, que é igual, e o resto da skill.

## Delta
- `skills/modo-iniciante/SKILL.md:41`: troca "das três" por "das duas com número", o que atende o A3 do 77a422e.
- `tests/config.json`: um trecho a mais na invariante de `docs/regras/R-DECISAO.md` ("se esse custo fica maior ou menor que o das outras opções"). Só acrescenta, nada sai nem afrouxa, e atende o A2 do 77a422e. O JSON é válido.
- `tests/test_pergunta_maior_menor.py` confere a nova redação; `changelog.d/pergunta-maior-menor.md` traz só a linha deste cartão.

## Comandos (head 88c82dd)
- `python3 -I -m unittest discover -s tests -p test_pergunta_maior_menor.py`: OK.
- `python3 -I -m unittest discover -s tests -p test_comportamento.py`: OK.
- `python3 -I tests/neutralidade.py`: rc=0.
- `python3 -I -m unittest discover -s tests -p test_forge.py`: 491 testes em 392 s, OK (inclui as invariantes de `tests/config.json`).
- M14: 23 linhas (22 de teste e 1 de `tests/config.json`), um cartão; abaixo de 150. `tests/config.json` não está em `PROTEGIDOS`, e a catraca do CI decide se o acréscimo pede rótulo.

## Gatilhos e outros pareceres
Há gatilho de segurança: `docs/regras/` e `tests/config.json` estão em `CONTROLES_DO_FORGE` (`bin/forge-check:167`). Este PR precisa do parecer de segurança (`R-SEGURANCA`), que não é refeito aqui. Sem pipeline: não há parecer de devops.

## Achados

## Parecer
Aprovado. O A2 e o A3 do lote foram atendidos. Falta o parecer de segurança antes do QA.
