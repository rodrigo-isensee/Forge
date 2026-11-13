---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/release-0.47.0
commit: 51c51139b04881506718924895678cecb0a55453
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-13
---
# Review de segurança: marca da release 0.47.0

Escopo: delta `afba389e..51c51139` (26 arquivos): versão nos dois `plugin.json`, entrada 0.47.0 do `CHANGELOG.md`, remoção de 22 fragmentos de `changelog.d/` e uma linha em `docs/engineering/placar-mutacao.md`. Nenhum código de produção, hook, workflow ou dependência muda neste delta (o código da release já tem parecer próprio por item).

## Gatilhos
`R-SEGURANCA`: a marca de release publica a versão que todos os projetos instalam (manifesto do plugin, texto distribuído).

## Achados
- A1 (recomendado) docs/engineering/placar-mutacao.md:20 · a linha `specs=9` inclui a spec envio-leve.json, que saiu rc=2 sem contar; o placar subconta mortos. Medida, não portão: registrar o rc=2 na nota da linha ou remedir na 0.48.0.

## Sondas

## Detalhe dos achados
Verificações (estáticas, locais):
- Versão: `.claude-plugin/plugin.json:3` e `dev/.claude-plugin/plugin.json:3` em 0.47.0, JSON válido, só o campo `version` muda no diff.
- CHANGELOG: 22 fragmentos removidos com 23 linhas `- ` somadas, e 23 linhas `+- ` na entrada 0.47.0; nenhuma perde conteúdo. Varredura por caminho pessoal e termos de segredo (token, secret, password, chave) na entrada: sem ocorrência de segredo; as duas correspondências a "secret/token" do filtro são texto de processo (diretrizes, economia de tokens), sem credencial.
- Placar (A1): `tests/mutantes/envio-leve.json` não é spec nova desde a v0.46.0 (não consta do `--diff-filter=A`); rodada isolada aqui, `forge-mutante -- tests/mutantes/envio-leve.json` saiu rc=0 com M1 a M5 `morreu`. O rc=2 do placar da release foi, portanto, falha da medição (carga ~17 em 12 CPUs), não guarda quebrada. Não bloqueia: o placar não é portão e não toca segurança. Severidade informativa, dono `tech-lead`, esforço P.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Lacuna: `gitleaks` ausente do PATH; substituído pela leitura do diff do delta (sem segredo). CI do PR: não há PR aberto neste momento; sem código no delta, a suíte inteira roda no CI do PR da release.
