---
tipo: review
contrato: 1
pedido: release-0.30.1
branch: melhoria/release-0.30.1
commit: 7af2bd4f5207e3b49376751d3e07a524336f5715
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-24
---
# Review: release-0.30.1

## Achados

## Parecer
Aprovado, sem achados. Revisor diferente de quem fez o commit de release. Diff `cb653db...7af2bd4`: 5 arquivos, 8 adições e 6 remoções, nenhuma linha de código nem de teste (teto M14 não se aplica).

- CHANGELOG: `## [0.30.1] - 2026-10-24` traz os 2 itens, EST-030-L2 (Adicionado) e EST-030-L3 (Alterado), com o texto idêntico ao dos fragmentos apagados no mesmo diff; `## [Não publicado]` ficou vazio.
- `changelog.d/`: `est-030-l2.md` e `est-030-l3.md` removidos; nenhum fragmento restou na árvore do commit.
- Versão: `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json` passam de 0.30.0 para 0.30.1; nenhuma outra referência a 0.30.0 fora de CHANGELOG e pareceres históricos.
- Número: 0.30.1 segue a decisão do dono "C" (só o último número sobe até a 0.30 fechar, exceção ao SemVer do CLAUDE.md).
- Commit só da release: um commit, `chore(release): versão 0.30.1 (#311 e #313)`, Conventional Commits em português, com os trailers de atribuição.
- Achados recorrentes (PA-7): `docs/engineering/achados-recorrentes.md` sem linhas; nada a conferir. Segurança e pipeline: sem mudança de código, nada a citar.
