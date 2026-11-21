---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-k167-ato-do-dono
commit: b9974f7561240393a660c841699a65fee99064e4
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-21
---
# Review: v0479-k167-ato-do-dono

Code review do K167 (v0478 E74.2) no head b9974f75, base develop 8caa7f3d: 3 arquivos, 5+/3-, só texto de skill e o fragmento do changelog.

## Parecer
Aprovado.

- Escopo (E74, K167): `skills/modo-iniciante/SKILL.md:35` põe no passo 3 do formato de pergunta o ato do dono (merge na `main`, rótulo de PR da `main`, arquivo travado, configuração do GitHub): a opção diz que quem aplica é o dono, com comando ou tela, e nenhuma põe o agente para aplicá-lo, citando `R-MAIN` e `R-CONFORMIDADE` pelo ID. `skills/ci-cd/SKILL.md:32` soma à leitura da proteção os rulesets (`repos/<dono>/<repo>/rulesets` e `rules/branches/<b>`), endpoints reais da API do GitHub, mantendo a proibição de alterar por `gh api`.
- `skills/ci-cd/SKILL.md:8` encurta a abertura (sai "Princípios genéricos e o padrão da fábrica (GitHub Actions)") para caber no teto do texto sem subi-lo (Histórico, E74.1 11:00); nenhum conteúdo normativo sai, e nenhum teste procura a frase retirada.
- Neutralidade (`R-NEUTRO`): placeholders `<dono>/<repo>/<b>`, sem nome de projeto.
- Ferramentas: os 9 módulos de teste que leem as duas skills (`test_clareza`, `test_dependabot_modelo`, `test_doutor_protecao_gh`, `test_pergunta_maior_menor`, `test_modelo_ci`, `test_qa_doutor_f8`, `test_novo_projeto`, `test_skills_v0442`, `test_textos_034`): 116 testes, OK. `bin/forge-changelog conferir --base origin/develop`: "ok: 1 fragmento(s) novo(s)". `git diff --check`: limpo.
- Sem guarda de código no diff: sem mutante a declarar. Suíte inteira não rerrodada (brief); a prova é o CI do PR (`R-REVIEW`).
