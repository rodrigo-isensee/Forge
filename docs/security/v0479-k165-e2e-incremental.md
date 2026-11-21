---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-k165-e2e-incremental
commit: b4a5764717bf5d03815bf9071b9bf93aeabe47ad
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: v0478 (E73.6, K165, revalidação)

Volta por delta (`R-REVIEW`): a rodada anterior (parecer no head `f700354c`, commit `8a2e2696`) fica no git e não é recopiada.

## Gatilhos
Gatilhos: texto de regra de QA protegido por invariante (`tests/config.json`), dado de teste gravado em disco do projeto.

## Delta lido
`forge-check parecer delta`, intervalo `f700354c..b4a57647`, no domínio: `skills/qa-testing/SKILL.md` (linha 61) e `tests/config.json` (linhas 579 e 878). Já lido na rodada anterior: o resto do diff `8caa7f3d..f700354c`, sem mudança desde então.

## Sondas

## Detalhe dos achados
**A1 (recomendado, rodada anterior): fechado.** `skills/qa-testing/SKILL.md:61` agora manda "acrescente `relatorios/` ao `.gitignore` antes da rodada", imperativo e antes da gravação; a correção mínima proposta foi aplicada ao pé da letra. A invariante acompanha o texto novo em `tests/config.json:579` (padrão) e `:878` (motivo, `R-QA`), e o padrão exige a frase da ordem, de modo que removê-la quebra o teste `Invariantes`. Nenhum texto saiu do lugar além do parêntese descritivo trocado pela ordem; "nunca em `/tmp`" permanece.

Sem achado novo.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Sonda local (`python3`, `re.search`): o padrão novo de `invariantes["skills/qa-testing/SKILL.md"]` casa no texto do head (True). Suíte inteira não rodada (CI do PR); o CI do head não foi consultado: o `gh` não está disponível na sessão (lacuna).
