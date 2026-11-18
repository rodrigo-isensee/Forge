---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0478-devops-lote
commit: d50b9cd0783da93d77709cdba273c1f45ce053b2
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-18
---
# Review: v0478 (E6.3, lote de devops)

## Achados
- A1 (bloqueante) agents/devops-engineer.md:16 · a linha do **CI pago** perdeu "junte os commits" e "comando local verde" (R-CUSTO); tests.test_textos_ci_custo falha no head e passa na base. Restaure as duas partes e encurte outra frase se o teto de texto apertar.
- A2 (recomendado) skills/ci-cd/SKILL.md:30 · o item 10 ainda diz "se já instalados"; alinhe com o agente: ferramenta ausente é achado do parecer e quem instala é scripts/preparar-estacao.sh.
- A3 (recomendado) tests/test_ferramentas_portoes.py:80 · o teste do modo container lê o texto da fonte; troque por comportamento (rodar --container --simular com curl falso que acusa chamada).
- A4 (recomendado) scripts/preparar-estacao.sh:104 · zizmor e semgrep entram por pipx sem versão fixada, ao contrário dos binários; fixe a versão (pipx install zizmor==X) ou registre o motivo. Parecer de segurança decide o peso.

## Sondas

## Parecer
Reprovado por A1: defeito provado, regra protegida por teste removida do agente de devops.

Escopo (E6.1, E6.2): os dois cartões estão nos commits 4b4ef58b (regra do ensaio em alvo descartável no agente, na skill ci-cd e como ameaça fixa no método da skill cyber-security; `--ferramentas` no preparar-estacao.sh com sha256 da release conferido, falha de uma ferramenta vira `falta:`, container não baixa binário) e 71a84aaf/d50b9cd0 (mapa do forge-testes e peso). Nada em hooks/, bin/forge-check nem bin/forge-fechar. O `imprimir_resultado` repete o padrão já usado depois do `garantir_gh`.

Provas lidas e rodadas no clone (head d50b9cd0, base 4182a6b9):
- `python3 -m unittest tests.test_textos_ci_custo tests.test_ferramentas_portoes`: 11 testes, 1 falha (A1: `'junte os commits' not found` em agents/devops-engineer.md); os 6 testes novos passam.
- Ressalva do autor, `tests.test_forge.ForgeCheck.test_raiz_depois_do_subcomando_e_git_isolado`: falha igual no head e na base (gh sem rede na estação); não é do diff.
- `python3 -I tests/catraca.py --base 4182a6b9`: rc=0, sem saída.
- `bash -n scripts/preparar-estacao.sh`: ok. shellcheck: ausente na estação (pendência, como o autor declarou); o CI do PR roda a bateria.
- Instalação real das ferramentas: não rodada (rede e custo de estação); coberta pelos falsos de curl e pipx do teste novo.

Suíte inteira: só no CI do PR (ainda sem PR).
