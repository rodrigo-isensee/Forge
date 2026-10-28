---
tipo: review
contrato: 1
pedido: release-0.30.5
branch: melhoria/release-0.30.5
commit: d7e0c9f030ecbe9adefacad7884e3d58c715ef2a
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-28
---
# Review: release-0.30.5

## Achados

## Parecer
Aprovado. Delta sobre a develop a83de9e: um commit de release (d7e0c9f), 9 arquivos, nenhum de código ou teste (teto M14: 0 linhas contadas).

- CHANGELOG: seção `[0.30.5] - 2026-10-28` com as seis entradas dos fragmentos (guarda-sem-mutante em Adicionado; rel-dec em Alterado; hook-ansi-c, lote-ti, pr-verde-lote-check e release-timeout em Corrigido), texto idêntico ao dos fragmentos removidos, sem perda nem duplicata; `[Não publicado]` fica vazio.
- `changelog.d/` não existe mais na árvore (os seis fragmentos apagados).
- Versão 0.30.5 em `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json`; nenhuma ocorrência de 0.30.4 restante em JSON.
- Numeração 0.30.5 conforme a decisão do dono de 2026-10-24 ("C"). Sem mexer em código, `tests/config.json`, hooks ou branches protegidas.
- achados-recorrentes.md (PA-7) conferido: sem linha AR, nada se aplica ao diff.
- Segurança e pipeline: sem mudança de superfície; sem parecer próprio necessário.
