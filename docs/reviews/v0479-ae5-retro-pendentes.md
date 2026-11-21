---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-ae5-retro-pendentes
commit: 600bbecf622bd734806ae351276e844f9a55cc10
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-21
---
# Review: v0478 (E58.63, AE5.1 `forge-check retro --pendentes` e o campo `Cobre:`)

Intervalo lido: `821db42e..600bbecf` (3 commits). Desenho: `docs/propostas/v0479-melhorias-anti-erro.md`, AE5 (a).

## Achados
- A1 (recomendado) bin/forge-check:5835 · Comentário HTML de várias linhas conta como corpo: seção só com `<!--`, `lead`, `-->` cobre a versão (sonda: rc 0, pendentes=0). O modelo usa comentário de uma linha; ignorar o miolo até `-->` fecha a brecha.

## Parecer
Aprovado. Faz o que o AE5 (a) pede, nem mais: lista as tags `vX.Y.Z` alcançáveis da main com mais de 24 h sem retro que as cubra, e a retro declara `Cobre:` no cabeçalho, várias versões por retro. O relógio é argumento (`--agora`), sem leitura da hora; entrada ilegível sai 2; `--main` aceita só ref sem opção (`REF_DA_MAIN` exige primeiro caractere alfanumérico); link, pasta, arquivo acima do teto e pasta de retros que é link não cobrem. As retros vêm do `--raiz-pedidos` quando dado (pasta de controle) e as tags do git de `--raiz`. A exigência das quatro seções com corpo vai além do texto do desenho, mas serve ao objetivo (retro vazia não quita a cobrança) e está documentada no modelo. A integração com a auditoria (AE6) e o recibo das 8h fica para o item do AE6.

Tamanho (H1): cerca de 70 linhas de código em `bin/forge-check`, um comportamento. Modelo igual em `docs/retrospectivas/_modelo.md` e `templates/projeto/docs/retrospectivas/_modelo.md`, com teste de igualdade. `test_retro_pendentes` entrou no mapa do `bin/forge-testes` (FORGE_CHECK e LEITORES_DE_TEXTO) e nos pesos D4; fragmento em `changelog.d/`.

Execução no head 600bbecf:
- `python3 -m unittest tests.test_retro_pendentes`: 18 testes, OK. Os subprocessos limpam o ambiente e chamam Python com `-I`.
- `bin/forge-mutante` nos três arquivos `tests/mutantes/v0478-ae5-retro-pendentes*.json`: 24 de 24 morreram (8 por arquivo), uma guarda por mutante.
- `python3 -m unittest tests.test_forge.Neutralidade`: 3 testes, OK (`R-NEUTRO`).
- Nomes de função de módulo do `bin/forge-check`: `grep -oP '^def \K\w+' | sort | uniq -d` vazio. Constantes repetidas no módulo: só `ETAPAS_DE_PARECER` e `ID_DE_PEDIDO`, que já se repetem na base `821db42e`; nenhuma vem deste diff.
- Suíte completa: fica no CI do PR (`R-REVIEW`); a branch ainda não tem PR, então não há CI a citar.

A1 é recomendado: não há gatilho no modelo nem no fluxo atual (as retros seguem o modelo de comentário de uma linha), e vira cartão depois do merge.

## Sondas
