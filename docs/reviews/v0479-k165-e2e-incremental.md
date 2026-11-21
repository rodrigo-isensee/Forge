---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-k165-e2e-incremental
commit: f700354c98e71c6d50ecb54ff47d8677c672fb9a
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-21
---
# Review: v0478 (E73.2, K165 e2e incremental)

Diff `8caa7f3d..f700354c`: `skills/qa-testing/SKILL.md` (+1 regra, 6 frases encurtadas), `tests/config.json` (+1 invariante com `regra`/`porque`), fragmento em `changelog.d/`. Só documentação e configuração de teste: 0 linhas de código (H1 dentro do teto), sem guarda mudada, sem mutante a declarar.

## Achados
- A1 (recomendado) skills/qa-testing/SKILL.md:61 · "(no `.gitignore`)" lê como fato, mas o modelo `templates/projeto/` não traz `.gitignore`; trocar por "acrescente `relatorios/` ao `.gitignore`" deixa o passo explícito para o projeto novo.

## Sondas

## Parecer
Aprovado. A regra nova (K165) faz o que o pedido pede: JSON por caso ao terminar, fora de `/tmp`, fora do git, com exemplo neutro (`<executor-e2e>`, `R-NEUTRO`), e fica protegida pela invariante nova com `R-QA` e motivo.

Frases cortadas, conferidas uma a uma, sem regra perdida:
- "(independência)": a regra ("sem ler o código do autor") segue; saiu só o rótulo.
- "a escrita do plano ... saem do caminho crítico": repete o título da seção ("o plano sai do caminho crítico").
- "Cobertura de linhas não é meta": coberta em "Cobertura se diz por obrigação, não em percentual" (seção "Teste nasce de obrigação").
- "Nunca use um clone sem as refs remotas": reescrita mantém o risco (rc 0 com base errada) e a conferência `git rev-parse refs/remotes/origin/<base>`; o passo 1 da lista já exige as refs remotas.
- "Saída 0 é o inverso do usual": saiu só o comentário; o significado da saída 0 segue.
- Formato da linha `AR-<n>`: "no formato dele" aponta para `docs/engineering/achados-recorrentes.md`, que define o formato em `## Formato`.
- Critério de pronto "zero violações ... críticas ou sérias" → "a acessibilidade aprovada": a seção "Acessibilidade" segue com "Zero violações críticas ou sérias para aprovar"; o limiar não caiu.

Testes de texto que leem a skill, rodados no head (`python3 -I -m unittest discover -s tests`): `test_forge.py -k Skills -k RegrasInviolaveis -k TetoPorPr -k RodarUmModuloComIsolamento -k Neutralidade -k AntiDuplicacao` 20 OK; `test_forge_mutante.py -k TextoQueMandaUsarAFerramenta` 3 OK; `test_aq1_texto.py` 6 OK; `test_clareza.py` 9 OK. A invariante nova casa com o texto (RegrasInviolaveis verde). Suíte inteira: fica no CI do PR (`R-REVIEW`), não rodada aqui. Commit único, Conventional Commits em português, mensagem clara.
