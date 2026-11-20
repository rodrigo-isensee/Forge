---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-quarentena-s1
commit: 04e7293b3c89ea21b6575a2f848b81a540af52f7
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-19
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

- A4 (recomendado) tests/quarentenas.py:22 · A contagem aceita `skip`/`skipTest` com motivo "quarentena" mesmo morto (função não chamada, ramo `if False`, classe não coletada): sobe o teto em 1 sem gastar vaga real de pulado. Contar só decorador de teste e `skipTest` no corpo de teste.

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

## Riscos aceitos e ferramentas
Nenhum risco aceito por este parecer. Só ferramentas locais (`unittest`, `forge-mutante`, `catraca`); nenhuma faltou. A suíte inteira fica para o CI do PR.
