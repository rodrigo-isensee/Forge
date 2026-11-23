---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-ordens-hook
commit: 35211762d50aec616625d3e7bd90ed88c7bb7f47
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-23
---
# Review de segurança: v0478 (E123.21, volta de CI do hook ordens)

Revalidação por delta (`forge-check parecer delta`, intervalo fe14fb1e..35211762, sem o merge da develop 51cb434d). No domínio: `hooks/conformidade.py:3602` (`entrada_valida`) e `tests/test_hooks.py:1790` (casos novos de política malformada). Fora do domínio, lidos por conferência: `tests/mutantes/v0479-conformidade-trilha-7.json` (U6 só atualiza o texto citado de `CONTROLE_NO_TEXTO`, já com `ordens`) e `tests/mutantes/v0480-ordens-hook-6.json` (M32 a M37). A rodada anterior (fb8a25f4, no head fe14fb1e) fica no git.

Gatilhos: hook de controle (validação da política de conformidade, que falha fechada).

**Só aperta, por escrito:** a mudança de `entrada_valida` é equivalente na decisão (nem aperta nem afrouxa a política): a função interna `texto(v)` (`isinstance(v, str) and bool(v)`) virou a comparação inline `isinstance(v, str) and v != ""`, idêntica para `str` (o JSON só produz `str`); a precedência de `"branch" not in e or isinstance(...) and ... != ""` é `A or (B and C)`, a mesma de antes; o `return False` antecipado para não objeto é o `isinstance(e, dict) and ...` de antes. O teste ganha 5 casos recusados (caminho vazio, caminho não texto, motivo vazio, `quem` com item não texto, branch vazia) e 6 mutantes: só aperta a cobertura. O item, no delta, só aperta.

Estado dos achados anteriores: A1 a A4 seguem resolvidos (o código fora de `entrada_valida` não mudou no delta). O cartão CONFORMIDADE-CURINGA-PASTA segue aberto, da base, sem relação com este delta.

## Sondas
- S1 · diferencial de `entrada_valida` fe14fb1e contra 35211762: 17 valores (ausente, None, vazio, textos, números, booleanos, listas, objetos) nos 5 campos, mais 7 não objetos · espera: 0 divergências · obtido: 1419864 casos, 0 divergências

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Ferramentas: leitura do delta; a sonda S1 (funções extraídas por `git show` de cada commit, fora do repositório); `python3 -m unittest tests.test_hooks.Hooks.test_politica_de_conformidade_malformada_bloqueia` no head: 1 teste, OK. A suíte inteira não foi rodada (brief: sem suíte local); vale o CI do PR.
