---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0478-devops-lote
commit: f00c3da26d6be9051f14ad0b1cfad212b41998b4
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-18
---
# Review: v0478 (E6.11, revalidação do lote de devops)

## Sondas

## Parecer
Aprovado. Revalidação E6.11 por delta (H3, R-REVIEW): li só `forge-check parecer delta docs/reviews/v0478-devops-lote.md`, intervalo f9356caf..f00c3da2, domínio código e testes: tests/mutantes/v0478-devops-lote.json, tests/test_ferramentas_portoes.py.

- A5 corrigido: test_falha_do_install_sem_tar_vira_falta_e_nao_grava_instalou roda o script com `install` falso que sai 1 no binário solto e afirma `falta:`, ausência de "instalou" e de arquivo (teste de comportamento, não lê a fonte); M5 (:98, `else ok=1`) e M6 (:99, `if true`) declarados, um por linha.

Provas rodadas no clone (head f00c3da2):
- `python3 -m unittest tests.test_ferramentas_portoes.FerramentasDosPortoes.test_falha_do_install_sem_tar_vira_falta_e_nao_grava_instalou`: 1 teste, OK.
- `bin/forge-mutante --processos 1 tests/mutantes/v0478-devops-lote.json`: M1 (:90), M2 (:92), M3 (:97), M4 (:112), M5 (:98), M6 (:99) morreram.

Suíte inteira: só no CI do PR (ainda sem PR).

### Revalidação anterior (E6.7, head f9356caf)
Revalidação por delta (H3, R-REVIEW): li só `forge-check parecer delta docs/reviews/v0478-devops-lote.md`, intervalo d50b9cd0..f9356caf, domínio código e testes: agents/devops-engineer.md, changelog.d/v0478-devops-lote.md, scripts/preparar-estacao.sh, skills/ci-cd/SKILL.md, tests/mutantes/v0478-devops-lote.json, tests/test_ferramentas_portoes.py.

Achados do parecer anterior (head d50b9cd0):
- A1 corrigido: agents/devops-engineer.md:16 volta a ter "junte os commits" e "comando local verde" (R-CUSTO); tests.test_textos_ci_custo passa.
- A2 corrigido: skills/ci-cd/SKILL.md:30 diz que ferramenta ausente é achado do parecer e quem instala é scripts/preparar-estacao.sh.
- A3 corrigido: test_modo_container_nao_baixa_ferramenta roda `--container --simular` com curl falso que registra chamada; não lê mais a fonte.
- A4 corrigido: zizmor 1.32.0 e semgrep 1.186.0 fixados (`pipx install "$1==$2"`), com teste e mutante M4. Além disso, os binários agora conferem também o sha256 fixado no script, e falha do tar vira `falta:`.

Provas rodadas no clone (head f9356caf):
- `python3 -m unittest tests.test_textos_ci_custo tests.test_ferramentas_portoes`: 14 testes, OK.
- `bin/forge-mutante --processos 1 tests/mutantes/v0478-devops-lote.json`: M1 (:90), M2 (:92), M3 (:97), M4 (:112) morreram.
- `bin/forge-mutante --cobertura --base d50b9cd0`: `não coberto: scripts/preparar-estacao.sh` (shell não se analisa, por desenho); conferido à mão, daí o A5.
- `python3 -I tests/catraca.py --base 4182a6b9`: rc=0, sem saída.
- shellcheck: ausente na estação (pendência); o CI do PR roda a bateria.

Suíte inteira: só no CI do PR (ainda sem PR).
