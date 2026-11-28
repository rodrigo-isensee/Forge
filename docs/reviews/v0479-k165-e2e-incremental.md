---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-k165-e2e-incremental
commit: b4a5764717bf5d03815bf9071b9bf93aeabe47ad
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-21
---
# Review: v0478 (E73.7, revalidação; E73.2, K165 e2e incremental)

Diff `8caa7f3d..f700354c`: `skills/qa-testing/SKILL.md` (+1 regra, 6 frases encurtadas), `tests/config.json` (+1 invariante com `regra`/`porque`), fragmento em `changelog.d/`. Só documentação e configuração de teste: 0 linhas de código (H1 dentro do teto), sem guarda mudada, sem mutante a declarar.

## Revalidação (E73.7, head b4a57647)
Delta lido: `forge-check parecer delta docs/reviews/v0479-k165-e2e-incremental.md`, intervalo `f700354c..b4a57647`, no domínio `skills/qa-testing/SKILL.md` e `tests/config.json`.
- A1 da rodada anterior fechado: skills/qa-testing/SKILL.md:61 agora manda "acrescente `relatorios/` ao `.gitignore` antes da rodada", passo explícito para o projeto novo.
- Frase cortada para o teto: "se a sessão cair, o que rodou fica" sai do texto; o motivo segue no `porque` da invariante (`tests/config.json`, K165) e a regra (JSON por caso, ao terminar, fora de `/tmp`) fica inteira.
- Invariante mais estrita: o padrão passa a exigir também "que some" e a ordem do `.gitignore` antes da rodada; `regra`/`porque` atualizados no mesmo padrão.
- Rodados no head: `python3 -I -m unittest discover -s tests -p test_metricas_texto.py` 2 OK; `python3 -I -m unittest discover -k RegrasInviolaveis -s tests -p test_forge.py` 3 OK. Suíte inteira no CI do PR (`R-REVIEW`).

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
