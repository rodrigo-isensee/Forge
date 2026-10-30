---
tipo: review
contrato: 1
pedido: pn5-espera-envio
branch: melhoria/pn5-espera-envio
commit: bb8a670fa24f0d64acfc641d8f3a6288cc30734f
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-29
---
# Review: pn5-espera-envio

Code review (`R-REVIEW`) do B1-2 da P-N5 (pedido PN5-ESPERA-ENVIO-REV, E1.1), diff `cfc2734...bb8a670` (3 commits: e58e1d7, 82d6bfd, bb8a670). Desenho: lote B1, seção 2, regra 4, de `docs/planos/2026-10-29-desenho-h1-b1.md`.

## Achados
- A1 (bloqueante) skills/esperar-estado/SKILL.md:38 · requisito e defeito provado: a regra 4 pede log de caminho literal; a linha usa "$TMPDIR/envio.log" e, com git push no lugar de <envio>, a conformidade recusa em projeto (rc 2). Use caminho literal no lançamento e no laço e teste a linha trocada pelos hooks

## Parecer
**Reprovado**, por um bloqueante (A1); o resto do diff está correto.

**A1, evidência de execução.** Sonda em `$TMPDIR/tech-lead-pn5-espera-envio/sonda_hooks.py`, sobre a fixture `BlocosPassamPelosHooks` do próprio módulo, rodando a saída de `lancamento().replace("<envio>", "git push origin melhoria/x")` pelos hooks `parecer` e `conformidade`, papel `forge:tech-lead`, nos dois ambientes do teste:
- `conformidade/projeto` (branch `feature/x`): código 2, `R-CONFORMIDADE: $TMPDIR com ação crítica: o hook não modela. Corrigir: branch literal, um comando por linha, sem # entre linhas, $, crase, chaves nem case`.
- Os outros três casos (parecer nos dois ambientes, conformidade no clone do Forge): código 0.
- A mesma linha com caminho literal (`/home/u/.forge-tmp/envio.log` no lugar de `"$TMPDIR/envio.log"`): os quatro casos saem 0.
- `bin/forge-fechar ... --espera 900` no lugar de `<envio>`, com `$TMPDIR`: os quatro casos saem 0 (o fechamento-integrador não é afetado; o defeito é o envio em projeto, que é o uso do tech-lead, linha 21 do agente).

O padrão da skill chega a todo projeto pelo plugin, e o envio do tech-lead em projeto é o caso principal da regra 4. Hoje o agente que copiar a linha é barrado. A regra 4 da própria skill (linha 14) já diz "log de caminho literal"; a linha 38 contradiz. Correção sugerida: no lançamento e no laço (linha 43), um caminho literal com marcador de troca (por exemplo, `<log>`, trocado pelo caminho absoluto da tarefa) e, em `LacoDoLog`, a linha de lançamento trocada (`<envio>` por `git push origin feature/x` e `<log>` por caminho literal) também passa por `BlocosPassamPelosHooks` nos dois ambientes; esse é o teste que falha antes e passa depois. Classe: a mesma do AR-10 (texto conferido numa forma, executado por outro caminho: o teste de hooks roda o modelo com `<envio>` e o bloco do laço, nunca a linha com o envio de verdade); sem linha AR nova nesta rodada (decisão técnica 2026-10-29 15:28 do T1-CONF-ESCOPO-REV).

**O que está correto (lido, não volta):**
- Regra 4 da skill (linha 14): lança com `run_in_background`, log que termina com `rc=`, espera no mesmo turno pelo laço da regra 2, nunca encerra o turno com processo pendente; segue o desenho.
- Laço do log (linha 43): 17 voltas de 30 s (540 s), sai no primeiro `rc=`, `fim=teto` com código 1; sem `sh -c`, `timeout`, `--watch` nem `run_in_background` (asserção de `TextoDaSkill`); sem palavra de marcador.
- Linha de lançamento com `<envio>` e o teste que a troca por um `git` falso (`tests/test_esperar_estado.py:97-122`): rc 0 sai na hora sem dormir, rc 1 sai e mostra, sem linha sai no teto depois de 17 voltas; `git` e `sleep` falsos, sem rede.
- `agents/tech-lead.md:21`: texto do desenho, mantém só leitura e worktree intocada durante a espera.
- `docs/fechamento-integrador.md:28`: cita a skill e o `rc=`, mantém a leitura de `log:` e `fim: código <n>`.
- `EsperaDoPushEVerificadores` (`tests/test_forge.py:5152-5157`): exige o texto novo e a ausência do antigo; a frase antiga não estava nos `invariantes` (sem rótulo). Nenhum outro texto do repositório traz "espere a notificação" (grep).
- Spec de mutantes `tests/mutantes/pn5-espera-envio.json` (M1 a M4) cobre saída na hora, `rc=1`, teto e a frase do tech-lead.

**Ferramentas (citadas, não refeitas):** `python3 -m unittest tests.test_esperar_estado tests.test_forge.EsperaDoPushEVerificadores` no HEAD revisado: 15 testes, OK. Mutação: entrega do autor, spec 4/4 (histórico do pedido).

**Teto M14:** `git diff --numstat --no-renames cfc2734...HEAD`: contam `tests/test_esperar_estado.py` (48) e `tests/test_forge.py` (5), 53 linhas; sem `hooks/` nem `PROTEGIDOS`; um comportamento (espera do envio pelo `rc=` do log). Dentro do teto.

**Regras:** `R-NEUTRO` sem termo de projeto; `R-CUSTO` sem nada pago; fragmento `changelog.d/pn5-espera-envio.md` presente. Sem ADR (desenho, seção 6, com critério de reversão).
