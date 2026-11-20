---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-quarentena-s1
commit: 1c0c1e9e81d306e5745a9a6c54ed92946a53b2dd
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
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

## Revalidação 2 (head 0f7e405b)
Head `0f7e405b960f0328109a83039e6a806e3ee7bec4` (de `ba6f6a03`), pelo `forge-check parecer delta`. Delta lido, uma linha: em `tests/mutantes/v0478-develop-relogio.json`, a lista `testes` do M1 ganhou `tests.test_hooks.Hooks.test_carga_explica_a_recusa_so_pelo_vigia_do_prazo_longo_com_disputa_provada`. Nada mais foi relido.
1. Teste novo existe (`tests/test_hooks.py:1229`) e passa no head: `OK (skipped=1)` nos dois testes do M1, o do skip da S1 e o novo.
2. Mutante M1 (`>= APROVEITAMENTO_MINIMO` trocado por `>= 0` em `tests/prova_de_carga.py`), aplicado numa cópia temporária do head: o teste novo reprova (`AssertionError: True is not false`). O teste mata o mutante, então a lista do M1 está correta.
3. A1 segue valendo (o delta não toca o skip nem o teto). Aprovado.

## Revalidação 3 (head 04e7293b)
Head `04e7293b3c89ea21b6575a2f848b81a540af52f7` (de `0f7e405b`), pelo `forge-check parecer delta`. Domínio lido: `changelog.d/v0479-quarentena-s1.md`, `tests/config.json`, `tests/quarentenas.py`, `tests/test_catraca.py` e `tests/mutantes/v0479-quarentena-s1.json`. Aprovado.
1. `teto_pulados` de 1 para 2 (`tests/config.json:930`), com o OK do dono de 19/11; o fragmento de changelog registra a devolução a 1 no PR que tirar a quarentena.
2. `TetoDaQuarentena` (`tests/test_catraca.py`) e `tests/quarentenas.py`: o teto passa só até 1 mais as quarentenas abertas (skip cujo motivo começa com "quarentena"); o motivo do skip da S1 (`tests/test_hooks.py:1324`) começa assim, então conta 1 e o teto 2 passa. Rodado: 4 testes `OK`.
3. Guardas: `quarentenas.py` tem 6 linhas de decisão, M1 a M6, um mutante por linha. Rodados numa cópia: M1 (`+ 1` no teto) reprova 2 testes; M6 (sem `startswith("quarentena")`) reprova 3. M2 a M5 vão pelo teste de contagem, que cobre skipIf, skipTest, subpasta, skip sem motivo e motivo não literal.
4. A1 segue valendo (rótulo `afrouxa-regra` e destaque no título; agora também pelo teto de 1 para 2).

## Revalidação 4 (head 968bc3ff)
Head `968bc3ff91e44c220723b0bbb4dbc8a62c1a1516` (de `04e7293b`), pelo `forge-check parecer delta`. Domínio lido: `tests/quarentenas.py`, `tests/test_catraca.py` e as specs `tests/mutantes/v0479-quarentena-s1.json`, `-2.json` e `-3.json`. Aprovado.
1. `quarentenas_abertas` conta só skip vivo: `@unittest.skip` em `test_*` de classe TestCase e `skipTest` no corpo, sem função aninhada, lambda, `if False`/`if 0` nem função solta. Exige data AAAA-MM-DD e "OK do dono" no motivo (ValueError sem eles).
2. A S1 continua contando 1: `quarentenas_abertas('tests')` no head dá 1; o motivo do skip (`tests/test_hooks.py:1324`) traz "OK do dono 19/11 18:12" e "prazo 2026-11-26". Teto 2 segue passando.
3. Rodado: `tests.test_catraca.TetoDaQuarentena`, 8 testes `OK`. Mutantes M1 a M22 (`forge-mutante` nas 3 specs): todos morreram; os que morreram por erro (M4 a M7, M14, M15, M19, M21) quebram o teste declarado, que passa sem o mutante.
4. A1 segue valendo (rótulo `afrouxa-regra` e destaque no título; teto 1 para 2).

## Revalidação 5 (head 1c0c1e9e)
Head `1c0c1e9e81d306e5745a9a6c54ed92946a53b2dd` (de `968bc3ff`), pelo `forge-check parecer delta`. Domínio lido: `tests/quarentenas.py`, `tests/test_catraca.py` e as 5 specs `tests/mutantes/v0479-quarentena-s1*.json`. Aprovado.
1. Contagem pelo carregador: `_motivos_carregados` usa `unittest.TestLoader().discover` e lê o `__unittest_skip__`/`__unittest_skip_why__` da classe ou do método real; pasta que o unittest não carrega vira ValueError, e `sys.path` e os módulos voltam (testes `..._nao_carrega_e_recusada` e `a_contagem_devolve_o_caminho_e_os_modulos`).
2. `skipTest` no corpo: lido no texto só dos métodos que o carregador devolveu (`_definicoes`, pela primeira linha do código); função solta, método sombreado, classe aninhada ou em `if False` não contam (`test_formas_da_sonda_a5...`).
3. Prazo vencido recusado (`_confere_quarentena`, `prazo < hoje`); o do dia passa; sem data dada compara com hoje. O prazo da S1 é 2026-11-26: depois dele a suíte recusa a quarentena, de propósito.
4. A S1 continua contando 1: `quarentenas_abertas('tests')` no head dá `1`. Rodado: `tests.test_catraca.TetoDaQuarentena`, 15 testes `OK`.
5. Mutantes: `forge-mutante --processos 1` nas 5 specs, 33 declarados (M1 a M41, 8+8+8+8+1), 33 `morreu`; os marcados `(erro)` quebram o teste declarado, que passa sem o mutante. Guardas novas com mutante (M23 a M41) e mais de 8 por arquivo repartidos em `-2` a `-5`.
6. A1 segue valendo (rótulo `afrouxa-regra` e destaque no título; teto 1 para 2).
