---
tipo: review
contrato: 1
pedido: pn6-base-recusada
branch: melhoria/pn6-base-recusada
commit: fab197c47dabb6714cd86b45a93a62b0962f87ce
parecer: aprovado
revisor: forge:tech-lead (PN6-BASE-RECUSADA-REV E1.1)
data: 2026-10-29
---
# Review: PN6-BASE-RECUSADA (E1.1 do PN6-BASE-RECUSADA-REV)

Code review (R-REVIEW) da branch inteira, `31257c14c8d245d66e7806edb7cd65e22b3aeb04...fab197c47dabb6714cd86b45a93a62b0962f87ce`: 5 commits, 4 arquivos (`bin/forge-check` +45 -12, `tests/test_conferencia_base_dono.py` +34, `tests/mutantes/pn6-base-recusada.json` +116, `changelog.d/pn6-base-recusada.md` +2). Li o diff inteiro contra o escopo E1 e E2 do pedido `PN6-BASE-RECUSADA` e a DECISÃO TÉCNICA de 22:32 (função única do Desde). Segurança é da E2.1 (`docs/security/`) e QA da E3.1; não os refaço.

Ferramenta: o Forge não tem `docs/engineering/praticas.md`; a suíte fica com o QA e o pre-push. Rodei só o do item, na worktree em `fab197c`: `python3 -m unittest tests.test_conferencia_base_dono` 31 testes OK; `bin/forge-mutante tests/mutantes/pn6-base-recusada.json` M1 a M11 "morreu", rc 0; `bin/forge-mutante --cobertura --base 31257c1` rc 1, com toda condição nova `coberta` e uma `apagada · bin/forge-check:1084(base) · desde is not None` (ver A2).

## Conferência dos pontos do brief
- **Função única, sem condição duplicada:** `veredito_do_desde` (`bin/forge-check:854`) concentra `desde_e_a_base`, `desde_valido` e `pedido_na_entrega`; `cmd_entrega` (`:1103`) e `recusa_do_desde` (`:1415`) só a chamam. `ref_da_base` (`:849`) é a única conta de `origin/<base>` ou local, usada pelos dois. Nenhum dos dois chamadores repete uma condição do Desde.
- **A guarda só mudou de lugar (`:1084(base)`):** na base, `if desde_e_a_base(...)` / `elif desde is not None:` / corpo. Na `fab197c`, `if desde_e_a_base(...): return` / `if desde is None: return` (`:860`) / o mesmo corpo. Como o primeiro ramo retorna, o `if desde is None: return` é exatamente a negação do `elif`; os valores devolvidos (valido e origem None nos ramos que reprovam, a linha e o `reprova`) são os que o `cmd_entrega` gravava antes. M11 mata a troca dessa guarda. É mudança de lugar, sem mudança de comportamento do `entrega`.
- **A guarda `pedido_na_entrega` no brief gerar:** chega pelo `veredito_do_desde`; `test_base_gravada_na_propria_entrega_recusa_como_no_entrega` prova a recusa com `(escopo: --desde gravado na própria entrega)` e confere que o `entrega` dá rc 1 no mesmo caso (M8, M9).
- **Mensagem:** traz a base, a origem (dono ou conferida), a ref, o Base-sha, o motivo (a linha `escopo:` do `entrega`) e o que fazer (gravar a `conferida <sha40>` ou pedir a base ao dono), termina em "nada gerado (P-N6)"; rc 1, sem `## Entregar` na saída.
- **Escopo:** só o `brief gerar --volta`, que é quem monta o `--desde` da prova a partir de `bases[-1]`; o `brief mensagem --entrega` ficou fora, como a DECISÃO TÉCNICA de 22:32 manda. O `entrega` não muda o que aceita (fora do escopo, P-N1).
- **Teto M14:** 91 linhas de código e teste (`bin/forge-check` 57, `tests/test_conferencia_base_dono.py` 34; spec de mutantes e fragmento fora da conta), um comportamento, sem `hooks/` nem caminho de `PROTEGIDOS`.
- **Commits e changelog:** Conventional Commits em português; fragmento `changelog.d/pn6-base-recusada.md` em `### Alterado`.
- **Achados recorrentes (PA-7):** conferi AR-1 a AR-10. AR-2 (ramo de falha sem teste): os três ramos da recusa têm teste. AR-4, AR-5, AR-6, AR-8, AR-10: não se aplicam (sem shell, sem ambiente herdado, sem hook). A2 é da classe do AR-1 (lista de mutantes incompleta, R-QA); sem linha AR nova nesta rodada, pela DECISÃO TÉCNICA 2026-10-29 15:28 do pedido T1-CONF-ESCOPO-REV.

## Achados
- A1 (recomendado) bin/forge-check:1419 · a recusa usa o head de agora (a ref); a regra do dono igual ao head (:830) não é monotônica: a base do dono igual à ref é recusada no gerar, mas o entrega da volta, com commits novos, a aceitaria; diga isso na mensagem ou não aplique essa guarda no gerar
- A2 (recomendado) tests/mutantes/pn6-base-recusada.json:1 · o --cobertura sai rc 1 com a condição apagada bin/forge-check:1084(base) `desde is not None`, que só mudou para :860 (M11); declare-a em `isentas` com esse motivo para o --cobertura do autor dar rc 0

## Parecer
**Aprovado.** A P-N6 faz o que o E1 pede: o `brief gerar --volta` decide a base de Desde pela mesma função do `forge-check entrega` e recusa na hora, com motivo e o que fazer, em vez de gerar uma prova que o `entrega` reprovaria. A refatoração do `cmd_entrega` preserva o comportamento (guarda movida, verificada linha a linha acima) e os testes do item e os 11 mutantes passam.

- A1 · `bin/forge-check:1419` · o `veredito_do_desde` roda com `head = ref`, o head da entrega revisada. Das condições, só `not (o == "dono" and c == head)` muda quando a volta acrescenta commits: a base do dono igual à ref é recusada agora e passaria no `entrega` que o autor roda depois da volta. O caso é estreito (a ref da volta costuma ter commits de parecer depois do head conferido) e o `test_base_que_o_entrega_recusa_para_o_gerar_sem_brief` fixa o comportamento atual de propósito, por isso não é defeito provado contra o E1, que não diz com qual head comparar. Sugestão: nomear esse caso na mensagem ("a base do dono igual à ref só vale depois de commit novo") ou decidir, com DECISÃO TÉCNICA, que o gerar não aplica essa guarda. Severidade: recomendado.
- A2 · `tests/mutantes/pn6-base-recusada.json:1` · a guarda só mudou de lugar, então não há buraco de teste, mas o verificador do autor (V2) fica vermelho e a prova `--cobertura` que o `brief gerar --volta` põe no Pronto quando sairia rc 1 numa volta. Sugestão: uma entrada `isentas` com o trecho `desde is not None` e o motivo "guarda movida para veredito_do_desde, coberta por M11". Classe AR-1. Severidade: recomendado.
