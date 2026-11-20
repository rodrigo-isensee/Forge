---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-quarentena-s1
commit: 1c0c1e9e81d306e5745a9a6c54ed92946a53b2dd
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: v0479-quarentena-s1

Gatilhos: teste que prova controle de hook pulado (afrouxa a proteção de teste, `R-CONFORMIDADE`), `teto_pulados` (sobe de 1 para 2 na revalidação 04e7293b).

Escopo: o diff `aa16e1a7..a2cc7fb2` (um `@unittest.skip` em `tests/test_hooks.py:1315` e o fragmento do changelog). Nenhum hook, fixture, spec de mutante nem `tests/config.json` muda.

## Confirmação pedida pelo dono
Confirmo por escrito: com a sonda S1 pulada, nenhum controle fica sem teste. O controle é o critério `carga_explica_a_recusa` (`tests/prova_de_carga.py:60-71`), que não deixa o tempo a mais causado por sono passar como carga. Cada parte dele tem outro teste que continua rodando (nenhum é pulado):
- Tabela do critério, com a linha S1 (`tests/test_hooks.py:1249`, medida real: parede 8,34 s, CPU 0,13 s, sono 4 s, referência 0,36): `test_carga_explica_a_recusa_so_pelo_vigia_do_prazo_longo_com_disputa_provada`, verde no head (saída `ok`).
- Mutantes: `bin/forge-mutante tests/mutantes/v0478-testes-prazo.json` no head, M5 a M8 morreram (`prova_de_carga.py:64,66,68,70`). M8 (`>= APROVEITAMENTO_MINIMO` vira `>= 0`) é a guarda da S1, e o teste que a mata é a tabela, não a sonda; a sonda não consta em `testes` de nenhum mutante (M9 e M10 em `v0478-testes-prazo-2.json` também não).
- A ligação medida do `liberar_ou_provar_a_carga` com o critério: `test_liberar_ou_provar_a_carga_aceita_so_a_recusa_explicada_pela_carga` (relógio e CPU falsos; um caso reprova só pela parcela, aproveitamento 0,72). Provas por mutação no fluxo, numa cópia em `$TMPDIR` (apagada): sono trocado por 0 (`:1211`) morreu; parcela trocada por constante (`:1212`) morreu; critério sempre verdadeiro morreu (4 falhas). Nada disso fica no repositório.
- O hook que recusa de verdade em 8 s, com sono real de 9 s: fixture `tests/hooks/parecer/v0455-merge-com-git-muito-lento-recusa-em-8s.json`, rodada por `test_prazo_do_merge`, verde no head (26,6 s).
- A referência da CPU: `test_referencia_da_cpu_mede_a_parcela_do_relogio`, verde.
- Os 4 testes do critério no head: `OK (skipped=1)`, só a S1 pulada.

Lacuna que sobra: a combinação ao vivo (sono real a mais, relógio real, referência real, na mesma execução) fica sem teste durante a quarentena. Cada elo dela tem teste próprio, como acima; é risco residual aceitável, temporário e restrito à confiabilidade do teste, sem caminho de ataque.

## Rótulo `afrouxa-regra`
Pode valer nas condições do dono. A catraca barra a mudança: `regra_testes_enfraquecidos` (`tests/catraca.py:556-565`) conta os pulos em `tests/` e dá 37 na base e 39 no head (a decoração é contada duas vezes: como chamada e como decorador); executei a regra e ela devolve a violação `R-CONFORMIDADE`. A saída prevista é o rótulo do dono (`rodrigo-isensee`, `tests/config.json:2`), posto depois do último push. Condições atendidas: (1) controle coberto, acima; (2) saída declarada (PR #701, 10 rodadas verdes) e cartão `TESTE-SONDA-S1-RELOGIO`; (3) `teto_pulados` continua 1 (`tests/config.json:930`), sem subir; o `@unittest.skip` não aparece em `PODEM_PULAR`, e no CI vira 1 pulado, que cabe no teto. Sem o rótulo, o PR fica barrado; quem o põe é o dono, não os agentes (`R-DECISAO`).

## Achados
- A1 (recomendado) changelog.d/v0479-quarentena-s1.md:2 · O fragmento agora declara a vaga única do teto, mas a subida da catraca (pulos 37 para 39) e o pedido do `afrouxa-regra` ainda vão ao corpo do PR; é o que resta do A1.
- A2 (recomendado) changelog.d/v0479-quarentena-s1.md:2 · Resolvido no repositório: prazo 2026-11-26 no skip e no fragmento. Falta só o mesmo prazo e o dono no cartão `TESTE-SONDA-S1-RELOGIO` (fora do repositório, não verificável aqui).
- A3 (recomendado) tests/mutantes/v0478-develop-relogio.json:12 · O M1 dessa spec só nomeia a S1 e agora dá "sem veredito" (teste pulado). A mesma mutação (`prova_de_carga.py:70`) morre na tabela do critério (M8 de v0478-testes-prazo.json); listar a tabela em `testes` do M1 ou retirar a spec.

- A4 (recomendado) tests/quarentenas.py:22 · Resolvido no head 968bc3ff para as três formas da S1 (função solta, `if False`, classe sem TestCase): contagem só de skip vivo, com prazo e OK do dono no motivo. Sobra o A5.
- A5 (recomendado) tests/quarentenas.py:70 · Resto aceito: o decorador, método sombreado, classe aninhada e fora do carregador agora contam pelo `unittest`; só o `skipTest` morto no corpo (após `return`/`raise`, `while False`, `if not True`, `else` de `if True`) ainda conta a mais; o teto continua pedindo o rótulo do dono.

## Detalhe dos achados
A1: evidência acima; caminho de ataque não há (higiene do registro); severidade baixa; correção: duas linhas no corpo do PR; esforço P; dono: `tech-lead`. A2: a quarentena sem prazo vira esquecimento; severidade baixa; correção: data no cartão; esforço P; dono: autor do pedido. A3: severidade baixa; a spec fica sem veredito até a S1 voltar; correção: uma linha em `testes`; esforço P; dono: autor do pedido.

## Revalidação no head ba6f6a03 (delta a2cc7fb2..ba6f6a03)
Lido: `forge-check parecer delta` (no domínio, só `tests/test_hooks.py`; o changelog fica fora do domínio e foi lido como evidência dos A1 e A2). A rodada anterior fica no git; aqui só o delta.
- Junção com a develop (#701): o teste da S1 injeta relógio (8,34 s), CPU (0,13 s) e parcela (0,36), as medidas do review (constantes em `tests/test_hooks.py:109`), e a tabela do critério usa as mesmas constantes (`:1258`). Nenhum hook nem `prova_de_carga.py` muda. A S1 ganhou asserções sobre a recusa real do vigia (returncode 2, mensagem do prazo longo).
- Skip com motivo novo: falha no CI sob carga mesmo com o #701; volta com o desenho da BP1 e 10 rodadas verdes no CI; cartão `TESTE-SONDA-S1-RELOGIO`; prazo 2026-11-26. `teto_pulados` segue 1 (`tests/config.json:930`, fora do delta).
- Changelog: cobre o prazo (A2) e a vaga do teto (parte do A1); catraca e rótulo ficam para o corpo do PR.
- Catraca: executei `regra_testes_enfraquecidos` entre a base ef186de8 e o head: "subiram de 37 para 39", violação `R-CONFORMIDADE`; a saída prevista é o rótulo `afrouxa-regra` posto pelo dono depois do último push (`R-DECISAO`). Inalterado.

### Reconfirmação por escrito: nenhum controle fica sem teste durante a quarentena
Reconfirmo, com a versão do #701 do teste e da tabela. No head, os 4 testes do critério dão `OK (skipped=1)`, só a S1 pulada: a tabela com a linha S1 (`test_carga_explica_a_recusa_so_pelo_vigia_do_prazo_longo_com_disputa_provada`), `test_liberar_ou_provar_a_carga_aceita_so_a_recusa_explicada_pela_carga` e `test_referencia_da_cpu_mede_a_parcela_do_relogio`, todos verdes. `bin/forge-mutante tests/mutantes/v0478-testes-prazo.json`: M1 a M8 morreram, inclusive M8 (`prova_de_carga.py:70`, a guarda da S1), morta pela tabela e não pela sonda. Como a S1 já injetava relógio e CPU, ela só testava a ligação do hook real com o critério; essa ligação tem o teste da recusa explicada pela carga e a fixture `v0455-merge-com-git-muito-lento-recusa-em-8s` (`test_prazo_do_merge`). Ressalva nova (A3): a spec `v0478-develop-relogio.json` dá "sem veredito" no M1, porque o teste declarado está pulado; o controle segue provado pela outra spec. Lacuna residual igual à anterior: a combinação ao vivo, sem caminho de ataque, temporária (até 2026-11-26).

Parecer mantido: aprovado.

## Revalidação no head 04e7293b (delta ba6f6a03..04e7293b)
Lido: `forge-check parecer delta` (no domínio: `tests/config.json` e `tests/test_catraca.py`; `tests/quarentenas.py`, as specs de mutante e o changelog ficam fora do domínio e foram lidos como evidência). A rodada anterior fica no git; achados A1 a A3 sem mudança de estado.
- `teto_pulados` de 1 para 2 (`tests/config.json:930`), com o OK do dono, só enquanto durar a quarentena da S1. A catraca (`regra_teto_pulados`, `TetoDePulados.test_teto_que_sobe_barra_e_que_cai_passa`) continua barrando a subida sem o rótulo `afrouxa-regra` do dono: é a trava principal e não muda.
- Novo `TetoDaQuarentena` (`tests/test_catraca.py:873`): no Forge `quarentenas_abertas(tests)` dá 1 (o skip real de `tests/test_hooks.py:1324`) e o teto 2 não passa de 1+1; sem quarentena o teto 2 reprova; teto 3 com uma quarentena reprova. Rodei `TetoDaQuarentena` e `TetoDePulados`: 8 testes, OK.
- Mutantes: `bin/forge-mutante tests/mutantes/v0479-quarentena-s1.json` no head: M1 a M6 morreram (M4 e M5 por erro do teste declarado sob o mutante, que passa sem ele; vale como morte).

### A contagem pode ser enganada?
Sondas em pasta de `$TMPDIR` (apagada), `quarentenas_abertas` sobre ela:
- S1 · três quarentenas mortas: `unittest.skip("quarentena")` numa função auxiliar nunca chamada, `self.skipTest("quarentena: falso")` em `if False`, `@unittest.skip("quarentena: ...")` em classe que não é `TestCase` · espera: 0 (nada pulado de verdade) · obtido: 3. Cada uma sobe o teto permitido sem gastar vaga de pulado no CI: é a brecha (A4).
- Não enganam: motivo em variável (`@unittest.skip(X)`), skip em arquivo que não é `test_*.py` e `print("quarentena: ...")`; a contagem fica abaixo, o que é seguro. Skip falso que de fato roda (decorador de teste coletado) gasta uma vaga no CI, então não ganha teto líquido.
- Não bloqueia: quem sobe o teto de verdade ainda passa pela catraca e pelo rótulo do dono; o skip morto precisa entrar num PR revisado, e o `TetoDaQuarentena` só vale como segunda trava. Nem o prazo nem o "OK do dono" são exigidos no motivo: o prazo 2026-11-26 só vive no texto do skip. Severidade baixa; correção mínima: contar só decorador de função `test_*` e `skipTest` dentro de método `test_*` de classe `TestCase`; esforço P; dono: autor do pedido.

### Nenhum controle fica sem teste
Confirmo por escrito: o controle novo (`quarentenas_abertas`, `teto_passa_da_quarentena`) tem testes e mutantes (acima); a S1 pulada segue coberta como na rodada anterior (tabela do critério, M8, ligação medida e fixture de 8 s); `teto_pulados` 2 está coberto pela catraca e pelo `TetoDaQuarentena`. Lacuna residual igual (combinação ao vivo da S1 até 2026-11-26). Devolução: o PR que tira a quarentena zera as abertas e o teste reprova teto 2, então o teto volta a 1.

Parecer mantido: aprovado.

## Revalidação no head 968bc3ff (delta 04e7293b..968bc3ff)
Lido: `forge-check parecer delta` (no domínio, só `tests/test_catraca.py`; `tests/quarentenas.py` e as três specs de mutante ficam fora do domínio e foram lidos como evidência). A1 a A3 sem mudança de estado; A4 resolvido (acima); A5 novo.
- Contagem nova (`tests/quarentenas.py:36-64`): só `@unittest.skip(...)` em `test_*` de classe `TestCase` e `skipTest(...)` vivo no corpo de `test_*`; motivo que começa com "quarentena" exige data AAAA-MM-DD e "OK do dono", senão `ValueError`. Motivo que não é quarentena não exige nada.
- Rodei `TetoDaQuarentena` e `TetoDePulados`: 12 testes, OK. No Forge `quarentenas_abertas(tests)` dá 1 e `teto_pulados` é 2 (`tests/config.json:930`), igual a 1+1. `bin/forge-mutante` nas três specs `v0479-quarentena-s1*.json`: M1, M4 a M22 morreram, nenhum sobreviveu.

### Sondas refeitas
- S1 (as três formas mortas) · `@unittest.skip("quarentena...")` em função solta e em método de classe sem base, `skipTest` em `if False`/`elif 0`, skip em método `auxiliar` · espera: 0 · obtido: 0. Confere com `test_skip_morto_da_sonda_s1_nao_conta`.
- Quarentena sem prazo, sem "OK do dono", data 26/11 ou "ok do dono" minúsculo · espera: `ValueError` · obtido: `ValueError` (teste `test_quarentena_sem_prazo_ou_sem_ok_do_dono_e_recusada`).
- Não enganam (subcontam, seguro): motivo em variável, f-string, `reason=` por palavra-chave, `skipIf`, skip de classe, `async def`.

### Outras formas de enganar a contagem (A5)
Em pasta de `$TMPDIR` (apagada), skip com motivo válido, em código que nunca roda, conta como aberto: `return` ou `raise` antes do `skipTest`, `assert False`, `while False`, `if not True`, `if 1 > 2`, `if None`, `else` de `if True`, `except` que não dispara: 8 contados onde o esperado era 0. Método sombreado (`test_a = None`, ou segundo `def test_b`), classe aninhada em função, classe em `if False` e classe repetida: 4 contados onde o esperado era 0. Arquivo `test_*.py` em pasta que o `unittest` não descobre também conta. Cada um sobe o teto permitido em 1 sem gastar vaga real de pulado.
Não bloqueia: nenhuma análise estática fecha todas as formas, e a subida do `teto_pulados` continua barrada pela catraca (`regra_teto_pulados`) até o rótulo do dono (`R-DECISAO`); o skip morto precisa entrar em PR revisado. O prazo vencido também não é conferido (só o formato). Severidade baixa; correção mínima: no CI, exigir que o número de pulados reais da suíte seja igual a `quarentenas_abertas` ou, no mínimo, que `teto_pulados` não passe do pulado real; esforço P; dono: autor do pedido.

### Nenhum controle fica sem teste
Reconfirmo por escrito: o controle novo (a contagem viva, a exigência de prazo e OK do dono, `teto_passa_da_quarentena`) tem testes (`TetoDaQuarentena`, 12 verdes com `TetoDePulados`) e 22 mutantes mortos; a S1 pulada segue coberta como nas rodadas anteriores (tabela do critério, M8, ligação medida, fixture de 8 s); `teto_pulados` 2 está coberto pela catraca e por `TetoDaQuarentena`. Lacuna residual igual (combinação ao vivo da S1 até 2026-11-26) mais o A5, sem caminho de ataque fora de PR revisado.

Parecer mantido: aprovado.

## Revalidação no head 1c0c1e9e (delta 968bc3ff..1c0c1e9e)
Lido: `forge-check parecer delta` (no domínio, só `tests/test_catraca.py`; `tests/quarentenas.py` e as cinco specs de mutante ficam fora do domínio e `tests/quarentenas.py`, que é o controle, foi relido inteiro). A1 a A4 sem mudança de estado; A5 reduzido (acima).
- Contagem nova (`tests/quarentenas.py:60-108`): o decorador, a classe e o método sombreado passam a ser o que o `unittest` carrega (`discover`, `__unittest_skip__`); `skipTest` segue lido no texto do corpo do método real. Prazo vencido é recusado (`:93`); pasta que não carrega é recusada (`:80`); `sys.path` e módulos voltam (`:83-86`).
- Rodei `TetoDaQuarentena` e `TetoDePulados`: 19 testes, OK. `bin/forge-mutante` nas cinco specs `v0479-quarentena-s1*.json`: 41 mutantes listados (M1, M4 a M7, M9 a M12, M16 a M19, M21, M23 a M41), todos morreram, nenhum sobreviveu, rodados com a árvore parada.

### Julgamento do resto do A5
Aceitável como recomendação. O que sobra é só contar a mais (nunca a menos) o `skipTest` literal em código morto do corpo. Ganho do atacante: 1 vaga de teto por skip morto. Para usá-la ele precisa (1) pôr o `skipTest` morto num PR revisado, onde o `tech-lead` e este parecer o leem, e (2) subir `teto_pulados` em `tests/config.json`, o que a catraca (`regra_teto_pulados`) barra sem o rótulo `afrouxa-regra` do dono (`R-DECISAO`); o motivo ainda exige prazo futuro e "OK do dono" (`:89-94`). A vaga a mais gasta nada no CI e só afrouxa o teto em 1 até o prazo. Sem caminho de ataque fora de PR revisado e aceito pelo dono: não bloqueia. Correção que fecharia: contar `skipTest` pelo pulado real do CI.

### Sondas refeitas
- S1 · pasta com seis `def` com `skipTest("quarentena (OK do dono): x; prazo 2099-01-01")` literal: `return` antes, `while False`, `if not True`, `else` de `if True`, `raise` antes, e um vivo · espera: 1 (só o vivo pula) · obtido: 6 (o `unittest` real pulou 1). Resto do A5, aceito.
- S2 · decorador `@unittest.skip` com motivo em variável (`skip(M)`) e `skipTest(M)` com variável · espera: não conta ou conta pelo valor · obtido: o decorador conta pelo valor real (3 contados na pasta de sondas), o `skipTest` com variável não conta (subconta, seguro).
- S3 · quarentena com prazo `2000-01-01` · espera: `ValueError` · obtido: `ValueError` "quarentena vencida em 2000-01-01".
- S4 · método sombreado (`test_9 = None`) e classe aninhada, em `if False` ou repetida · espera: 0 · obtido: 0 (cobertos por `test_formas_da_sonda_a5_que_o_unittest_nao_pula_nao_contam`).

### Nenhum controle fica sem teste
Reconfirmo por escrito: cada controle do head tem teste que roda e mutante morto. A contagem pelo carregador (`TetoDaQuarentena.test_conta_o_pulo_real_e_o_skiptest_vivo`, `test_skip_de_classe_conta_um_por_teste_sem_somar_o_corpo`, `test_subpasta_conta_so_se_o_unittest_a_descobre`, `test_formas_da_sonda_a5_que_o_unittest_nao_pula_nao_contam`); a recusa de prazo vencido (`test_quarentena_vencida_e_recusada_e_a_do_dia_passa`, `test_sem_data_dada_o_prazo_e_comparado_com_hoje`); a recusa sem prazo ou OK do dono (`test_quarentena_sem_prazo_ou_sem_ok_do_dono_e_recusada`); a pasta que não carrega (`test_pasta_que_o_unittest_nao_carrega_e_recusada`); a restauração de `sys.path` e módulos (`test_a_contagem_devolve_o_caminho_e_os_modulos`); `teto_passa_da_quarentena` e `teto_pulados` 2 (`TetoDaQuarentena`, `TetoDePulados`, catraca). A S1 pulada segue coberta como nas rodadas anteriores. Lacuna residual: a combinação ao vivo da S1 até 2026-11-26, mais o resto do A5, sem caminho de ataque fora de PR revisado.

Parecer mantido: aprovado.

## Riscos aceitos e ferramentas
Nenhum risco aceito por este parecer. Só ferramentas locais (`unittest`, `forge-mutante`, `catraca`); nenhuma faltou. A suíte inteira fica para o CI do PR.
