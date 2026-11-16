---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-jargao-medida
commit: 95e7a6ad678839d3a2f5fe2a734e129a79401d68
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-16
---
# Code review: medida de jargão por classe na mensagem ao dono (E7.4; revisão E2.219, revalidação E2.245)

Escopo: o review completo (E2.219) cobriu `git diff e13aed85...b8d4cda8`; esta revalidação (E2.245) leu só o delta de `forge-check parecer delta docs/reviews/v047-jargao-medida.md`, intervalo `b8d4cda8..95e7a6ad`, no domínio: `hooks/meta.py`, `tests/test_meta.py`, a fixture `jargao-mensagem-de-200-kb-decide-e-mede-no-teto.json`, `docs/hooks-fixtures.md`, o fragmento de changelog e as specs `v047-jargao-medida.json`, `-3.json` e `-4.json` (commits 2009704c, 8235da2c e 95e7a6ad, da E2.237). O revisor não fez a entrega.

## Achados
- A1 (recomendado) hooks/meta.py:1 · o diff de código e teste soma 229 linhas (meta.py 79, test_meta.py 150), acima da orientação de 150 (M14); o corpo do PR precisa trazer `teto: excedido, 229 linhas, <motivo>` (um comportamento só, mais a correção do tempo da medida).

## Sondas

## Parecer
Aprovado no head 95e7a6ad. Os achados da rodada anterior foram resolvidos:
- A1 antigo (bloqueante, etapa no fim da frase): a guarda passou a `(?!\w|\.\w)` em `hooks/meta.py:142`. Sonda refeita: `classes_de_jargao("Terminei a E7.4.")` dá `{'etapa': 1}`, e `E7.4.1` continua sem contar; o teste `test_etapa_no_fim_da_frase_conta` cobre, e os mutantes da linha morrem.
- A2 antigo (cerca `~~~`): `fora_de_codigo_e_citacao` guarda a cerca que abriu e só a mesma a fecha; a sonda com `~~~`, `git push`, `~~~` e depois uma cerca de crases com `~~~` dentro dá `{}`. Teste `test_cerca_de_til_e_fechada_pela_mesma_cerca`, mutantes M17 a M20.
- A3 antigo (custo quadrático de `explicado`): o "o que é" é procurado numa janela de 200 caracteres antes do termo, e a medida inteira (tabela "Em vez de" e classes) lê só os primeiros 20.000 caracteres, com `cortado` na linha. A entrega fecha também os bloqueantes A1 a A3 da segurança: a classe cartão sem o `[A-Z]{2,}` ambíguo e a medida depois da decisão, num `finally` (o `sys.exit(2)` do `bloquear` passa por ele, e o teste `test_stop_bloqueado_ainda_mede_e_sai_com_2` prova). Sondas de tempo no teto, por classe e com entrada adversária, ficaram entre 0,006 s e 0,18 s.

Mudança de comportamento aceita: um "o que é" a mais de 200 caracteres antes do termo, na mesma frase, deixa de explicar (`test_o_que_e_longe_do_termo_nao_explica` fixa isso). É medida, não trava, e não pesa.

Verificadores, rodados no clone no head 95e7a6ad:
- `python3 -m unittest tests.test_meta`: 15 testes, OK.
- `bin/forge-mutante --processos 1` com as quatro specs: M1 a M28 morreram, rc=0.
- `bin/forge-mutante --cobertura --base b8d4cda8`: rc=0; as condições mudadas têm mutante (linhas 158, 160, 161, 162, 193 e 195) e as linhas 153 e 155 da base ficam isentas com motivo.

A suíte inteira fica para o CI do PR, que ainda não existe (o brief manda não abrir). Neutralidade (`R-NEUTRO`): nada de projeto entra. Os itens do Entregar da E2.237 têm commit. Conferi `docs/engineering/achados-recorrentes.md` (PA-7): AR-4 (os testes novos chamam as funções no processo, sem subprocesso herdando ambiente), AR-9 (o docstring e o fragmento citam o teto novo) e AR-12 (as specs foram editadas no mesmo item que mudou as linhas) não se repetem. Nenhuma linha AR é gravada.
