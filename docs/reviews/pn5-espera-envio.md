---
tipo: review
contrato: 1
pedido: pn5-espera-envio
branch: melhoria/pn5-espera-envio
commit: 07fd724471aa59537e7d4bc030bc8740e9949c94
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-29
---
# Review: pn5-espera-envio

Code review (`R-REVIEW`) do B1-2 da P-N5 (pedido PN5-ESPERA-ENVIO-REV, E1.1), volta 2: revalidação por delta do parecer anterior (9bf2d8e, aprovado no head 8a7ad60). Head revisado 07fd724. A volta 1 (8a7ad60) e a original (a20d657, reprovado por A1) seguem abaixo como histórico.

## Achados

## Parecer
**Volta 2 (head 07fd724): aprovado.** Sem achado novo.

**Delta lido** (`bin/forge-check delta --parecer docs/reviews/pn5-espera-envio.md`, intervalo `8a7ad60..07fd724`, só o commit 07fd724): `tests/test_esperar_estado.py:169`, `LOG` passa de um caminho sob o home do usuário a `/tmp/forge-tmp/envio.log`. O teste continua provando o mesmo: `com_log` (linha 53-55) só troca `<log>` pela string, e o hook recebe a linha como texto, sem criar nem ler o arquivo; o caminho segue literal e absoluto, sem `$TMPDIR`, que é o que a regra 4 da skill exige. `scripts/verificar-contribuicao.sh origin/develop`: rc=0 ("nenhum segredo nem caminho pessoal no diff contra origin/develop"); busca pelo caminho sob o home do usuário em `tests/test_esperar_estado.py` vazia.

**Já lido (não relido):** todo o resto do diff `cfc2734...07fd724`, aprovado no parecer 9bf2d8e e intocado pelo delta.

**Classe:** caminho pessoal em teste (`R-NEUTRO`, achado pela ferramenta `verificar-contribuicao.sh`, não pelo review); sem linha AR nova nesta rodada (decisão técnica 2026-10-29 15:28 do T1-CONF-ESCOPO-REV).

**Ferramentas (citadas, não refeitas):** `python3 -m unittest tests.test_esperar_estado` no head 07fd724: 13 testes, OK.

**Teto M14:** `git diff --numstat --no-renames origin/develop...HEAD`: `tests/test_esperar_estado.py` (63) e `tests/test_forge.py` (5), 68 linhas, igual à volta 1; dentro do teto.

### Volta 1 (head 8a7ad60)
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
