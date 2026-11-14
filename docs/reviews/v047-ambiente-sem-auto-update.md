---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-ambiente-sem-auto-update
commit: 413a922444228ca83ac7842f1cdcab8db66bf75c
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-14
---
# Review: v047 (AMBIENTE-SEM-AUTO-UPDATE, E1.104)

## Achados
- A1 (recomendado) bin/forge-testes:104 · a linha da tupla foi quebrada; nada a fazer (resolvido no delta)

## Sondas

## Parecer
Aprovado no head baf1bee6. Delta lido: 93deca84..baf1bee6 (bin/forge-testes, changelog.d, skills/trabalho-em-paralelo/SKILL.md, tests/test_ambiente_sem_auto_update.py).

Resolvidos os bloqueantes anteriores (A1 "(serializam)" e A2 "traz a `develop` uma vez") e os recomendados A3, A4 e A5: a skill `trabalho-em-paralelo` ficou idêntica à da `develop` (`git diff afba389e HEAD -- skills` vazio), então nenhum texto existente foi apagado ou resumido. A retomada saiu da entrega e espera a decisão do dono; o teste e o fragmento de changelog acompanham a saída. Fica só a orientação ao dono (README e modelo de projeto).

Provas rodadas aqui (sem PR, só afetados): test_ambiente_sem_auto_update OK; test_achado_teto_doc OK; test_medidas_m14b OK; test_sobreposicao_quadro 61 testes, 1 falha (`Fila.test_t4_excedentes_do_teto_esperam`, teto adaptativo sob carga da máquina) que falha igual na base afba389e: não vem desta branch; o CI do PR decide. Sem guarda de código mudada: sem mutante a declarar. Tamanho: 24 linhas de código e teste contra a base.

## Revalidação (E1.111)
Aprovado no head 4baba3c5. Delta lido: `forge-check parecer delta` baf1bee6..4baba3c5, no domínio só `README.md` e `templates/projeto/CLAUDE.md` (a junção da `develop` fica fora do escopo): sai a frase "Se a sessão cair, o Jarvis retoma os agentes em curso" das duas orientações ao dono (A4 do QA), sem outra mudança; nenhum teste procura essa frase (`grep` em `tests/`). `tests/test_ambiente_sem_auto_update.py` OK. Sem guarda de código mudada: sem mutante. Tamanho: 24 linhas de código e teste contra a base.

CI do PR #545 no 4baba3c5: `bateria (pareceres)` falha só por este parecer estar desatualizado (resolvido por este commit); `suíte parte 3/3` (3.12 e 3.14) falha e não consegui ler o log (host de logs fora da rede do sandbox); o delta é só texto de README e modelo, então não vem dele, mas o CI decide e a falha precisa ser lida antes do merge.

## Revalidação (E1.150)
Aprovado no head 413a9224, por instância que não fez a entrega. Delta lido: `forge-check parecer delta` 4baba3c5..413a9224, no domínio só `tests/test_reval_delta.py`: entra em `CITACOES_CONHECIDAS` o par (`tests/test_ambiente_sem_auto_update.py`, `README.md`) com 1 linha e motivo `teste-le`, que bate com a única leitura do README no teste (linha 13). `test_reval_delta` 10 testes OK; mutante (sem a entrada) reprova `test_caminho_de_texto_so_e_citado_como_a_lista_conhece` com "1 linhas, a lista diz 0". Sem guarda de código mudada: sem mutante a declarar. CI do PR #545: suíte 3.12 e 3.14 (partes 1 a 3) verdes; `bateria (pareceres)` vermelha só por este parecer e pelo do QA. Tamanho: 27 linhas de código e teste contra a develop.
