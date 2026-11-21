---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-k165-e2e-incremental
commit: f700354c98e71c6d50ecb54ff47d8677c672fb9a
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: v0478 (E73.3, K165)

Diff lido: `8caa7f3d..f700354c` (3 arquivos: `skills/qa-testing/SKILL.md`, `tests/config.json`, fragmento `changelog.d/`). Sem código executável; muda texto de regra de QA e acrescenta uma invariante.

## Gatilhos
Gatilhos: texto de regra de QA protegido por invariante (`tests/config.json`), dado de teste gravado em disco do projeto.

## Achados
- A1 (recomendado) skills/qa-testing/SKILL.md:61 · "(no `.gitignore`)" descreve, não manda: nada inclui `relatorios/` no `.gitignore` (o `bin/forge-init:214` só ignora `.forge/run/` e afins); o JSON do E2E, com mensagem de erro e dado de teste, pode ir ao git. Torne imperativo ou use pasta já ignorada.

## Sondas

## Detalhe dos achados
**A1.** Evidência: `skills/qa-testing/SKILL.md:61` e `bin/forge-init:214` (lista `ignorados` sem `relatorios/`); o modelo do projeto não traz `.gitignore`. Caminho: o QA grava `relatorios/<rodada>/<caso>.json` num projeto onde a pasta não está ignorada; o relatório JSON do executor E2E carrega mensagem de erro, URL, saída do processo e, às vezes, cabeçalho ou dado de semente; um `git add .` posterior leva isso ao remoto, legível por quem lê o repositório. Severidade: baixa (depende de dado sensível no ambiente de teste e de um commit descuidado). Correção mínima (dono: autor da branch, texto da skill e a invariante junto): trocar "(no `.gitignore`)" por "(acrescente `relatorios/` ao `.gitignore` antes da rodada)", ou gravar em `.forge/run/relatorios/<rodada>/`, já ignorado pelo `forge-init`; ajustar o padrão da invariante em `tests/config.json:579` e `:878` ao texto novo. Esforço: P.

**Cortes de texto conferidos (nenhuma regra afrouxou):**
- "(independência)" e "a escrita do plano ... saem do caminho crítico": a regra fica ("sem ler o código do autor"; invariantes `## Plano antecipado` e `no mesmo head do review` seguem casando).
- "Cobertura de linhas não é meta": o mesmo princípio segue em "Cobertura se diz por obrigação, não em percentual" (seção "Teste nasce de obrigação").
- "Nunca use um clone sem as refs remotas": reescrito como condição com a mesma checagem obrigatória (`git rev-parse refs/remotes/origin/<base>`).
- "(só classe, ID da regra, contagem e `arquivo:linha`)": o "no formato dele" remete a `docs/engineering/achados-recorrentes.md` ("## Formato"), que mantém a restrição e proíbe texto livre, trecho de código e valor de segredo.
- "zero violações de acessibilidade críticas ou sérias" → "a acessibilidade aprovada": a seção "## Acessibilidade" mantém "Zero violações críticas ou sérias para aprovar"; mesmo critério.
- "é o inverso do usual": retórico; o significado da saída 0 fica.
- Nenhuma frase cortada era invariante: todos os 12 padrões de `invariantes["skills/qa-testing/SKILL.md"]` casam no texto do head (sonda local abaixo).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Sonda local: os 12 padrões de invariante da skill casam (`python3 -I`, `re.search` sobre `tests/config.json`). Suíte inteira não rodada (CI do PR); o CI do head não foi consultado: o `gh` não está disponível na sessão (lacuna).
