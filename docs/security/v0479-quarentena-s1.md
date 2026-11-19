---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-quarentena-s1
commit: a2cc7fb24092f8f51378775a42efec62e21998d2
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-19
---
# Review de segurança: v0479-quarentena-s1

Gatilhos: teste que prova controle de hook pulado (afrouxa a proteção de teste, `R-CONFORMIDADE`), `teto_pulados`.

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
- A1 (recomendado) changelog.d/v0479-quarentena-s1.md:2 · O fragmento não diz que a catraca sobe (pulos 37 para 39) nem pede o `afrouxa-regra`; declarar a violação e a decisão do dono no corpo do PR. O pulado ocupa a única vaga do teto (1): outro pulo no CI reprova.
- A2 (recomendado) changelog.d/v0479-quarentena-s1.md:2 · A quarentena não tem data limite: se o PR #701 parar, o pulo fica. Pôr no cartão `TESTE-SONDA-S1-RELOGIO` uma data de revisão e o dono.

## Detalhe dos achados
A1: evidência acima; caminho de ataque não há (higiene do registro); severidade baixa; correção: duas linhas no corpo do PR; esforço P; dono: `tech-lead`. A2: a quarentena sem prazo vira esquecimento; severidade baixa; correção: data no cartão; esforço P; dono: autor do pedido.

## Riscos aceitos e ferramentas
Nenhum risco aceito por este parecer. Só ferramentas locais (`unittest`, `forge-mutante`, `catraca`); nenhuma faltou. A suíte inteira fica para o CI do PR.
