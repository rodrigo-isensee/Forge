---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-mutantes-sobreviventes
commit: 94cbaa1b43de3e468c11f9360893d5c592c01ebc
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-16
---
# Review: v047 (E2.505, mutantes sobreviventes)

Parecer completo (não havia parecer anterior nesta branch), sobre o head 007cd931, contra a develop (86ac0fcb). Instância que não fez a entrega.

## Escopo lido
- Diff contra `origin/develop`: 4 testes (+33 linhas em `tests/*.py`, dentro do teto M14), 2 specs em `tests/mutantes/` e o fragmento do changelog. Um comportamento: matar mutantes sobreviventes.
- O Forge não tem `docs/engineering/praticas.md`; segui o checklist da skill `engineering-practices` e `achados-recorrentes.md` (PA-7).

## Verificação
- Testes dos arquivos tocados, no clone, sem `-I`: `test_conformidade_verde` 11 OK; `test_forge_mutante` 124 OK; `test_governanca` 50 OK; `test_mensagem_conferente` 18 OK. Suíte inteira: CI do PR.
- `bin/forge-mutante --conferir --base 86ac0fcb`: "conferidas: o trecho de cada spec do diff está no lugar".
- `t6t3-mensagem.json`: 16 de 16 morreram.
- `pr-verde-lote-check.json`: M8 **sobreviveu** (`bin/forge-check:1494`).
- Prova da regressão: a spec da develop (`de` terminando em `# D4`) roda M8 e ele morre em `bin/forge-check:1785`. O `de` novo, terminando em `# E1g; E2.252`, só casa a linha 1494 (a de 1785 termina em `# D4; E1g; E2.252`), onde o teste `test_d4_so_o_fragmento...` não observa o efeito.
- Os outros testes novos: lidos; cada um tem ramo de falha com comportamento (sem leitura de texto da fonte). `test_desde_real...` usa repositório real e comandos git com `cwd`.

## Achados
- A1 (bloqueante) tests/mutantes/pr-verde-lote-check.json:79 · [resolvido no 94cbaa1b] M8 retargeteado para a linha 1494 e sobrevive; na develop o `de` casava a linha 1785 e o mutante morria. A "correção" criou o sobrevivente. Volte ao `de`/`para` que casa 1785 (use `# D4; E1g; E2.252`) e rode a spec; AR-12.
- A2 (recomendado) tests/mutantes/t6t3-mensagem.json:103 · lista de dois testes em uma só linha, fora do formato das outras specs (um por linha); separe.

## Revalidação (delta 007cd931..94cbaa1b)
- Delta lido com `forge-check parecer delta`: `tests/mutantes/pr-verde-lote-check.json` (M8 volta a `# D4; E1g; E2.252`) e `docs/engineering/achados-recorrentes.md` (AR-12, 5 vezes).
- `bin/forge-mutante tests/mutantes/pr-verde-lote-check.json`: M1 a M8 morreram; M8 em `bin/forge-check:1785`.
- `--conferir --base 86ac0fcb`: trecho de cada spec no lugar. `tests.test_portao_diff_proprio` 19 OK; `tests.test_forge_mutante` 124 OK (ConferirTodas 4 OK), sem `-I`.
- A2 segue recomendado, não bloqueia.

## Parecer
Aprovado no head 94cbaa1b: A1 corrigido e provado pela spec.
