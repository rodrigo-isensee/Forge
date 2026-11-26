---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-release-04719-anexo
commit: 0157977e02dc38058c1b762b01d301985f85573f
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-26
---
# Review de segurança: v0481 (anexo da 0.47.19, E12.34, #907), volta por delta

Delta lido: `git diff da7b59be..0157977e`. Fora dos pareceres (`docs/reviews/`, `docs/qa/`, `docs/security/`, que são só os da rodada E12.28 a E12.30), toca só `CHANGELOG.md:24`, +1 −1 (commit `0157977e`, E12.31). A rodada anterior (aprovada em `da7b59be`) fica no git.

Gatilhos: nenhum

## Detalhe
- **A1 do review (CHANGELOG.md:24), resolvido:** a linha do anexo diz agora "os 8 itens" e lista #875, #878, #888, #901, #902, #903, #904 e #906, com "(v0481 E12.26, E12.27)". Bate com os 8 fragmentos juntados. A seção `[0.47.19]` não perde nenhuma linha: `git diff 8ae4d6c6 0157977e -- CHANGELOG.md` não tem nenhuma linha `-`.
- **O que aperta, o neutro e o que afrouxa (do delta):** o delta é **neutro**. É só texto de nota de versão e não mexe em nenhum controle, hook, teste, invariante nem manifesto. Nada aperta e nada afrouxa. A classificação dos 18 itens da versão está em `docs/security/release-0.47.19.md`.
- **Segredos:** os padrões de token do GitHub, chave da Anthropic, chave da AWS, chave privada e token do Slack dão 0 na linha nova.
- **Conferência no head:** `bin/forge-changelog conferir-release`: `ok: changelog.d/ sem fragmentos pendentes`. `python3 -m unittest tests.test_changelog`: 91 testes, OK.

## Riscos aceitos e ferramentas
Sem riscos aceitos. gitleaks, osv-scanner, semgrep, zizmor e actionlint estão fora do PATH (lacuna registrada). O delta é uma linha de texto, lida por inteiro.

CI no head `0157977e` (run 45826880513):
- verdes: `bateria (passos)`, `bateria (verificações longas)`, `instalação (python 3.14)`, `árvore já provada na develop` e Catraca (45826880490);
- `bateria (pareceres)` está vermelha. Causa, reproduzida com `tests/catraca.py --modo pareceres`: os pareceres de review e de QA da rodada anterior estão `reprovado` em `da7b59be`, e as voltas deles correm em paralelo a esta;
- as 10 partes da suíte ainda rodavam na leitura.

Por isso esta rodada não grava a linha `- ci:`.
