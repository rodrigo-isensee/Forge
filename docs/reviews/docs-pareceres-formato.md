---
tipo: review
contrato: 1
pedido: v046
branch: melhoria/docs-pareceres-formato
commit: c0acddcf3690bee21f69de4ff48ac236816f63e1
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-12
---
# Review: docs-pareceres-formato (v046, E24.4)

Escopo: `git diff a1318e88...c0acddcf` (3 commits, classe T, só documentação): `docs/security/guarda-conferente.md`, `docs/security/anti-alucinacao-portao.md`, `docs/security/v046-forge-pesado-m12.md`, `docs/reviews/hk3-parecer-texto.md` e o fragmento `changelog.d/docs-pareceres-formato.md`. Revisor que não escreveu nenhuma parte da branch, lendo numa worktree destacada no head.

## Achados
- A1 (recomendado) docs/security/anti-alucinacao-portao.md:82 · os achados citam `S1, parecer rc 0` e `(S1, rc 2)` (linha 85) pelo rótulo antigo; com a renumeração, `S1` agora é `gh pr create` rc 2 e o rc 0 está em S7. O `## Método das sondas` explica os colchetes, mas a citação ficou ambígua; trocar por `[S1]` ou pelos números novos.

## Sondas

## Parecer
Aprovado. Conferi cada um dos quatro pareceres contra a base:

- **Frontmatter, veredito e `commit:`:** nenhum hunk toca as linhas 1 a 15 de nenhum arquivo; frontmatter, `parecer:`, `commit:` e o parágrafo do veredito ficaram iguais.
- **guarda-conferente:** as 9 linhas da tabela viraram S1 a S9 com o mesmo cenário, resultado e leitura; a prosa foi para `## Método das sondas`. O `espera: passa (ver R1)` da S6 é coerente com o R1 (recusa da saída oficial é o defeito).
- **anti-alucinacao-portao:** as 21 linhas da tabela viraram S1 a S21, com o rótulo original entre colchetes e os rc antes → agora preservados; os `espera:` novos de S7 e S16 seguem o sentido de A2 e A1. Só a citação nos achados ficou ambígua (A1 acima, recomendado: não muda veredito nem sentido).
- **v046-forge-pesado-m12:** o A1 foi encurtado para caber nos 300 caracteres e o texto original foi para o detalhe, palavra por palavra; severidade (recomendado/baixa) igual.
- **hk3-parecer-texto:** as cinco formas viraram S1 a S5, o `read`/`mapfile` virou S6 e a comparação com a base virou S7; o A2 foi encurtado e o texto inteiro está, idêntico ao original, em `## Detalhe dos achados`. Classe AR-10 citada igual.
- **Changelog:** fragmento em `changelog.d/`, `CHANGELOG.md` intocado.

Ferramentas: `forge-check docs` no head c0acddcf, rc 0; `bin/forge-testes` com os arquivos tocados (27 módulos dirigidos), `Ran 1219 tests ... OK`. O repositório do Forge não tem `docs/engineering/praticas.md`; o checklist da skill `engineering-practices` foi lido nos itens que alcançam documentação (1, 2, 3, 9, 11). Tamanho (M14): só `.md` e `changelog.d/`, fora da contagem.

## AR (PA-7)
Conferi as 12 linhas de `docs/engineering/achados-recorrentes.md`: todas são de código, teste, mutante ou hook (AR-1 a AR-12); nenhuma alcança esta entrega só de texto. O A1 acima não repete classe registrada; sem linha AR nova.
