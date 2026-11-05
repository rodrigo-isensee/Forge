---
tipo: review
contrato: 1
pedido: versao-033
branch: melhoria/lote-fechar2-guardas-v2
commit: b822d22cc790e7f01882e632ebb3c932d925bd54
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-04
---
# Code review: testes do ramo de falha das guardas do forge-fechar (LOTE-FECHAR2, v2)

Escopo: `git diff origin/develop...HEAD`, um commit (`b822d22`), 4 arquivos: 6 testes em `tests/test_fechar_base_andou.py` (mais um `mktemp` falso e o falso de `merge-base --all`), 2 em `tests/test_fechar_espera_catraca.py`, a spec `tests/mutantes/lote-fechar2-5.json` e o fragmento de changelog. `bin/` não muda. Fecha os achados A1 e A2 do `docs/qa/lote-fechar2.md`. QA e segurança não são refeitos aqui (sem gatilho de segurança: só teste).

## Achados
- A1 (recomendado) tests/test_fechar_base_andou.py:466 · o teste A1 troca o `mkdir` por um falso que sempre sai 0 e prende a prova ao `-d`; é intencional, mas vale citar o `mkdir` falso no cabeçalho do módulo

## Verificação
- Mutantes: `bin/forge-mutante tests/mutantes/lote-fechar2-5.json` deu G1 a G7 `morreu` (forge-fechar:180, 346, 859, 617, 598, 599, 601). Cada mutante tem o `de` exato e aponta o teste que o mata.
- Testes: `test_fechar_base_andou.py` Ran 40 OK; `test_fechar_espera_catraca.py` Ran 17 OK.
- Fragilidade: sem relógio nem rede; os de espera usam `--espera 2|4` com `FORGE_FECHAR_INTERVALO=1`, o mesmo padrão dos vizinhos, e afirmam contagem de leituras (`>2`), não tempo. Ordem não importa: cada teste monta o próprio estado. O `subTest` do A3 limpa os arquivos de estado a cada caso.
- Falsos: o `mktemp` falso falha só com `-d` sem outros argumentos (o do log segue real); `merge-base --all` falso cobre erro com saída parcial e saída vazia com rc 0, os dois ramos de `die`.
- Teto M14: 69 + 18 = 87 linhas de teste (a spec e o fragmento ficam fora), abaixo de 150. Um comportamento só (testes de guardas).
- Commit: Conventional Commits em português, só teste, spec e fragmento. Sem TODO nem depuração.
