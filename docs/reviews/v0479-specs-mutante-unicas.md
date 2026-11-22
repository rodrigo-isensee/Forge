---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-specs-mutante-unicas
commit: 118dd80c997f24f9b8dd6764fb6da7854041401c
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-21
---
# Review: v0479-specs-mutante-unicas

Etapa E97.2, classe T, review como portão único. Base 27169ed1, head fa6deb89.

## Escopo lido
- `tests/mutantes/revisor-wt-e6a-1.json` M2, `tests/mutantes/acelera-e2b-diff-vazio.json` M7, `tests/mutantes/z075-uma-delegacao-por-branch.json` M3, M6 e M7: o `de` e o `para` ganharam o mesmo prefixo de contexto (a linha anterior ou o começo da linha); a troca da guarda segue idêntica (AR-12), sem mudar o efeito.
- `changelog.d/v0479-specs-mutante-unicas.md`: fragmento `### Corrigido` coerente com o diff.

## Provas
- `bin/forge-mutante --conferir --base 27169ed1`: `conferidas: o trecho de cada spec do diff está no lugar`, rc=0.
- `bin/forge-mutante --conferir --todas`: nenhum dos cinco mutantes aparece na lista de trechos ambíguos (a lista restante é de outras specs, fora do diff).
- `bin/forge-mutante --processos 1 ... --ids`: revisor-wt-e6a-1 M2 morreu (bin/forge-check:2014); acelera-e2b-diff-vazio M7 morreu (bin/forge-check:3878); z075-uma-delegacao-por-branch M3 morreu (hooks/agentes.py:960), M6 e M7 morreram (hooks/agentes.py:955).
- Suíte: só no CI do PR (`R-REVIEW`), não rerrodada aqui.

## Parecer
Aprovado. O diff faz só o que a etapa pede: cinco trechos `de` passam a ser únicos no arquivo, com a mesma mutação, e todos os cinco mutantes morrem com os testes declarados.

## Revalidação (E97.5, head 118dd80c)
- Delta lido: `forge-check parecer delta docs/reviews/v0479-specs-mutante-unicas.md`, intervalo fa6deb89..118dd80c sem a base; no domínio só `tests/fixtures/mutantes-pendentes.txt`. O merge da develop 9253a761 (4a7fecc8, varredura de dívida) fica fora do escopo.
- O 118dd80c tira das pendentes exatamente as cinco linhas dos mutantes corrigidos no fa6deb89 (revisor-wt-e6a-1 M2, acelera-e2b-diff-vazio M7, z075-uma-delegacao-por-branch M3, M6 e M7); era o que reprovava o ConferirTodas no CI do PR #782 (a catraca só encolhe, AR-12).
- `python3 -m unittest tests.test_forge_mutante`: `Ran 145 tests`, `OK`, incluindo o teste que confere toda spec contra as pendentes.
- Parecer mantido: aprovado.
