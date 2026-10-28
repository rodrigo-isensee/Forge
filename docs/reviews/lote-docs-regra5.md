---
tipo: review
contrato: 1
pedido: lote-docs-regra5
branch: melhoria/lote-docs-regra5
commit: 3802b9e581ca6fa52dc51f46227afb3e6918ada3
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-26
---
# Review: lote-docs-regra5 (DOCS-REGRA5-PREPUSH, pedido LOTE-DOCS-REGRA5-REV, E1.1)

Escopo: `edb5358...3802b9e`, dois commits (5c782de, 3802b9e), seis arquivos: README.md, agents/tech-lead.md, docs/economia-de-tokens.md, changelog.d/lote-docs-regra5.md, tests/test_forge.py, tests/test_testes_tocados.py. Sem mudança em código de produção.

## Garantido por ferramenta
- `python3 -m unittest tests.test_forge.PrePushSoOsAfetados tests.test_forge.EsperaDoPushEVerificadores tests.test_testes_tocados.NaoEPortao` em 3802b9e: `Ran 8 tests`, `OK`.
- Os mesmos testes de 3802b9e sobre a árvore de edb5358 (cópia em `$TMPDIR`): `FAILED (failures=3)`, caem `test_readme_e_tech_lead_dizem_so_os_afetados`, `test_v2_dirigida_e_na_fila` e `test_regra_5_cita_o_script_e_a_decisao_do_dono`. Os testes pegam o texto antigo.
- Teto M14: `git diff --numstat --no-renames edb5358...HEAD` dá 20 linhas de teste (`tests/test_forge.py` 13+1, `tests/test_testes_tocados.py` 4+1); o resto é `.md` e fragmento. Dentro do teto, sem `hooks/` nem `PROTEGIDOS`.
- A suíte completa não rodei (brief: só os testes do item); ela fica no CI do PR.

## Por leitura
- Comportamento conferido em `.githooks/pre-push` de edb5358: o caminho dirigido (`dirigido_ok`) vale só para `refs/heads/melhoria/*` (linha 252), cai na suíte inteira quando o plano do `--listar` não é dirigido (linhas 266-267, caminho sem regra) e fora de `melhoria/*`; `ci.yml` roda a bateria em todo `pull_request`. README.md:68, agents/tech-lead.md:22 e docs/economia-de-tokens.md:10 dizem isso e citam a decisão do dono M8 de 2026-10-24; a regra 5 registra que ela substitui a de 2026-10-15 e mantém os bloqueios de conteúdo.
- Testes: `test_regra_5_cita_o_script_e_a_decisao_do_dono` seguia cobrando a citação literal da decisão; agora cobra `bin/forge-testes`, `M8`, `2026-10-24`, `CI de todo PR` e a ausência da frase antiga. Não afrouxou: troca a decisão substituída pela vigente e acrescenta o teste de ausência (cada string aparece uma vez no arquivo, na regra 5). `test_v2_dirigida_e_na_fila` troca a frase antiga pela nova, mesma força. `PrePushSoOsAfetados` é novo, com ausência e presença em README e tech-lead; o alvo das ausências sumiu de fato (item 11 do checklist).
- Frase antiga em outro arquivo: `git grep` por "suíte inteira/completa" com "push" em agents, skills, docs/regras, stacks, templates, README, bin e scripts não acha outra afirmação de que o pre-push de `melhoria/*` roda a suíte inteira. Restam dois comentários fora do diff com imprecisão menor (A2, A3).
- Commits: Conventional Commits em português; o primeiro deixa `test_v2_dirigida_e_na_fila` vermelho e o segundo corrige, aceito por DECISÃO TÉCNICA do Jarvis (2026-10-26 21:06; o squash junta os dois).
- Changelog: fragmento em `### Corrigido`, CHANGELOG.md intocado. `R-NEUTRO` e `R-CUSTO` sem impacto. `docs/engineering/achados-recorrentes.md` sem linha (lista vazia).
- Segurança e pipeline: sem gatilho (só texto e testes de texto); nada a encaminhar ao `security-engineer` nem ao `devops-engineer`.

## Achados
- A1 (recomendado) README.md:68 · o texto omite dois casos do pre-push: diff que toca bin/forge-testes, tests/config.json ou .githooks/ cai na suíte inteira (pre-push:265) e o push só de pareceres roda só as classes curtas (pre-push:270); citar em meia frase num próximo cartão
- A2 (recomendado) bin/forge-testes:25 · a docstring cita só a decisão de 2026-10-23 e diz que review e QA rodam a suíte inteira; alinhar à M8 de 2026-10-24 e aos cortes da decisão ACELERA-RODADA (fora do diff, cartão próprio)
- A3 (recomendado) bin/forge-fechar:366 · o comentário diz que o pre-push roda a suíte no push que remove a branch remota, mas o envio só de remoção não roda a suíte (pre-push:144); corrigir o comentário (fora do diff, cartão próprio)
- A4 (recomendado) tests/test_testes_tocados.py:421 · `M8` e `2026-10-24` são cobrados soltos; cobrar o trecho `decisão do dono M8 (2026-10-24)` e `melhoria/*` deixaria o teste mais preciso contra edição futura da regra 5

## Parecer
Aprovado. Os três textos descrevem o pre-push da develop (dirigido só em `melhoria/*`, suíte inteira fora disso ou sem regra, bateria completa no CI de todo PR) e citam a M8 de 2026-10-24; os testes cobram o texto novo e caem sobre o antigo, sem perder cobrança. Os quatro achados são recomendações e não devolvem a entrega.
