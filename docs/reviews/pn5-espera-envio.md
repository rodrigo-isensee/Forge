---
tipo: review
contrato: 1
pedido: pn5-espera-envio
branch: melhoria/pn5-espera-envio
commit: 8a7ad60d238af4a894901f28b96dd909bb910af6
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-29
---
# Review: pn5-espera-envio

Code review (`R-REVIEW`) do B1-2 da P-N5 (pedido PN5-ESPERA-ENVIO-REV, E1.1), volta 1: revalidação por delta do parecer anterior (a20d657, reprovado no head bb8a670 por A1). Head revisado 8a7ad60.

## Achados

## Parecer
**Aprovado.** O A1 da volta anterior está resolvido; o delta não trouxe achado novo.

**Delta lido** (`bin/forge-check delta --parecer docs/reviews/pn5-espera-envio.md`, intervalo `bb8a670..8a7ad60`, só o commit 8a7ad60):
- `skills/esperar-estado/SKILL.md:36,38,40,43`: o lançamento e o laço do log usam o marcador `<log>`, trocado pelo caminho absoluto escrito por extenso; o aviso da linha 36 diz por que (sem `$TMPDIR` nem `$?`, que a `conformidade` recusa ao lado do envio) e bate com a regra 4 (linha 14, "log de caminho literal"). A contradição apontada no A1 sumiu.
- `tests/test_esperar_estado.py:53-57,108-114`: `com_log` troca `<log>` como o agente faz; `LacoDoLog` deixa de depender de `TMPDIR` no ambiente e roda o lançamento e o laço com o caminho literal (rc 0, rc 1 e teto seguem cobertos).
- `tests/test_esperar_estado.py:169-183`: `BlocosPassamPelosHooks` passa a rodar, além dos blocos, a linha de lançamento com `git push origin <branch do ambiente>` e `<log>` literal, pelos hooks `parecer` e `conformidade`, nos dois ambientes (clone do Forge e projeto); a contagem de casos sobe para `4 * (len(BLOCOS) + 1)`. É o teste que falha antes e passa depois pedido no A1.
- `tests/mutantes/pn5-espera-envio.json:17,36-43`: M2 acompanha o texto novo; M5 volta o `$TMPDIR` ao lançamento e aponta `BlocosPassamPelosHooks`.

**Já lido (não relido):** o resto do diff `cfc2734...8a7ad60` (regra 4 da skill, laço do PR, `agents/tech-lead.md:21`, `docs/fechamento-integrador.md:28`, `EsperaDoPushEVerificadores`, M1, M3, M4, fragmento), aprovado como correto no parecer a20d657 e intocado pelo delta.

**A1, evidência de execução.** M5 aplicado à mão numa cópia do head (`$TMPDIR/tech-lead-pn5-espera-envio/m5`): `BlocosPassamPelosHooks` falha com `2 != 0 : R-CONFORMIDADE: $TMPDIR com ação crítica: o hook não modela`, o mesmo código 2 provado na volta anterior; sem o mutante, passa. O mutante morre pelo teste certo.

**Classe:** a do AR-10 (texto conferido numa forma, executado por outro caminho), agora coberta pelo teste que roda a linha com o envio de verdade; sem linha AR nova nesta rodada (decisão técnica 2026-10-29 15:28 do T1-CONF-ESCOPO-REV).

**Ferramentas (citadas, não refeitas):** `python3 -m unittest tests.test_esperar_estado tests.test_forge.EsperaDoPushEVerificadores` no head 8a7ad60: 15 testes, OK. Mutação da spec completa: entrega do autor.

**Teto M14:** `git diff --numstat --no-renames cfc2734...HEAD`: contam `tests/test_esperar_estado.py` (63) e `tests/test_forge.py` (5), 68 linhas; sem `hooks/` nem `PROTEGIDOS`; um comportamento. Dentro do teto.

**Regras:** `R-NEUTRO` sem termo de projeto (o caminho do teste é genérico); `R-CUSTO` sem nada pago; fragmento `changelog.d/pn5-espera-envio.md` presente.
