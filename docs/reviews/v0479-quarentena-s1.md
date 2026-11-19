---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-quarentena-s1
commit: ba6f6a0366ed1d0c1280bc9f43e402d25d830e57
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-19
---
# Review: v0478 (E37.4, quarentena da sonda S1)

## Achados
- A1 (recomendado) tests/test_hooks.py:1315 · a catraca barra o skip novo (R-CONFORMIDADE, 37 para 39 e módulo de controle 4 para 6 pulos); o PR precisa do rótulo `afrouxa-regra` do dono, depois do último push, e do destaque no título.

## Parecer
Aprovado. Diff de 4 linhas em 2 arquivos (`git diff aa16e1a7 a2cc7fb2 --stat`).
1. Corpo do teste intacto: o diff só acrescenta o decorador `@unittest.skip` com motivo, OK do dono (19/11 18:12), PR #701 e cartão `TESTE-SONDA-S1-RELOGIO`; nenhuma linha removida.
2. `teto_pulados` segue 1 (`tests/config.json:930`, sem diff contra a base).
3. Soma dos pulados: pelo código, os pulos incondicionais da suíte são só este (os 4 `expectedFailure` de `tests/evals/test_erros_por_papel.py` não entram em `pulados_ids`); os condicionais (`sys.monitoring` em 3.12 e 3.14, `flock`, `bash`, `env`) não disparam no runner Linux. Soma esperada 1, igual ao teto: não estoura, mas fica sem folga; outro pulado novo reprova o CI até o #701 devolver o teste. Localmente `test_cobertura` e `test_fila_ocupacao` rodaram 23 testes sem pulo e a S1 deu `OK (skipped=1)`. Os logs do CI não puderam ser lidos (rede do sandbox); o job "teto de pulados" (3.12 e 3.14) passou no run 44617762561 (PR guardas-parecer, sem a quarentena), o que prova só soma <= 1 na base. A soma real das 5 partes sai no CI deste PR.
Sem suíte local, como o brief manda.

## Revalidação
Head `ba6f6a0366ed1d0c1280bc9f43e402d25d830e57` (de `a2cc7fb2`), pelo `forge-check parecer delta`; domínio lido: `changelog.d/v0479-quarentena-s1.md` e `tests/test_hooks.py`. Aprovado.
1. Junção com a develop (`5c883b8d`, trouxe o #701): fora do domínio do delta (veio da base), sem releitura.
2. Corpo do teste igual ao da develop: `diff` da função `test_liberar_ou_provar_a_carga_recusa_a_sonda_s1` entre `origin/develop` (`ef186de8`) e o head sai vazio; `git diff origin/develop HEAD -- tests/test_hooks.py` traz só 3 linhas, o decorador `@unittest.skip`.
3. Motivo novo do skip: cita o OK do dono (19/11 18:12), a falha no CI sob carga mesmo com o #701, o desenho da BP1, o cartão `TESTE-SONDA-S1-RELOGIO` e o prazo 2026-11-26. O fragmento de changelog diz o mesmo.
4. Teto de pulados: `teto_pulados` é 1 na develop e no head (`tests/config.json`, sem diff); o único `@unittest.skip` em `tests/` é este. Rodado: `OK (skipped=1)`.
5. A1 (rótulo `afrouxa-regra` e destaque no título) segue valendo e vai ao PR.
