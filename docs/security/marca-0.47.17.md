---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/marca-0.47.17
commit: 8d9f51d3d8c3ae37afc68618fdd5521e069ee6bf
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-25
---
# Review de segurança: marca da 0.47.17 (#882, v0481 E12.5)

Gatilhos: nenhum de código; a marca de release passa pela segurança por exigência do processo (classe C).

Neutro: a marca não muda código, hook, workflow nem regra; só junta texto de changelog e sobe a versão. Nada aperta nem afrouxa.

## Escopo lido
Diff `7e8c9c19..8d9f51d3`: 23 arquivos. Só três modificados (`.claude-plugin/plugin.json`, `dev/.claude-plugin/plugin.json`, `CHANGELOG.md`) e 20 apagados, todos em `changelog.d/`. Nenhum arquivo de código, hook, workflow, teste ou agente tocado.

## Conferências
- Fragmentos: os 20 fragmentos apagados em `changelog.d/` foram lidos na base e cada linha não vazia de cada um aparece, idêntica (comparação de linha inteira), na seção `## [0.47.17] - 2026-11-25` de `CHANGELOG.md:7-31`. São 21 itens porque `v0480-graphql-ilegivel.md` tinha dois. Cada item está na seção do fragmento (Adicionado 12, Alterado 6, Corrigido 3). Sobra em `changelog.d/` só o `README.md`.
- Versão: `0.47.17` em `.claude-plugin/plugin.json:3` e `dev/.claude-plugin/plugin.json:3`; o `marketplace.json` não traz campo de versão, nem na base, então não há o que subir. Seção nova logo abaixo de `[Não publicado]`, acima da 0.47.16.
- Data: commit da marca em 2026-11-24T23:31:46-03:00, ou seja, 2026-11-25T02:31:46 UTC; a data `2026-11-25` da seção bate com o UTC.
- Segredos: o diff só cita nomes de variáveis de ambiente (texto já presente nos fragmentos), nenhum valor de credencial.
- CI do head `8d9f51d3`: bateria, suíte (3.12 e 3.14, 5 partes), catraca, instalação e teto de pulados verdes; os jobs só de push na develop saem pulados, como esperado num PR.

## Achados

## Sondas

## Riscos aceitos e ferramentas
Nenhum risco aceito. `gitleaks` e `osv-scanner` não estão no PATH (lacuna registrada); a varredura de segredos do diff foi feita por leitura e busca de padrões.
