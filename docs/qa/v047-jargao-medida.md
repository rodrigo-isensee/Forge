---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-jargao-medida
commit: 95e7a6ad678839d3a2f5fe2a734e129a79401d68
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-16
---
# QA: v047 (E7.4, medida de jargão por classe no hook de fim de resposta, E2.221)

Escopo `e13aed85...b8d4cda8`: `hooks/meta.py` (S6), `tests/test_meta.py`, fixture `tests/hooks/meta/jargao-classes-da-mensagem-do-evento.json`, índice `docs/hooks-fixtures.md`, três specs de mutante. Não havia parecer anterior: completo. O pedido não traz `CA-n`; as obrigações são as da E7.4 (mede e nunca bloqueia, lê `last_assistant_message`, conta por classe fora de código e citação, nunca grava o termo) e `R-QA`. Sem PR e sem check-run `bateria` para o sha: a prova é a execução local dos cenários.

## Achados
- A1 (recomendado) hooks/meta.py:162 · `explicado` refaz `re.split` sobre `texto[:inicio]` a cada termo: custo quadrático. Medido: 4000 termos (cerca de 20 mil caracteres) levam 12 s; 500 levam 0,14 s. Abaixo do prazo do hook (300 s) em mensagem realista; não bloqueia.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Cada uma das 6 classes conta o termo e deixa passar o parecido | `JargaoPorClasse.test_cada_classe_conta_o_termo_e_deixa_passar_o_parecido` | hash só com dígitos ou só com letras, `R-2`, caminho sem extensão | passou |
| Termo explicado (parêntese ou "o que é") não conta; parêntese fora da frase não explica | `test_termo_explicado_nao_conta` | limite da frase | passou |
| Bloco de código e citação fora da conta; crase conta | `test_bloco_de_codigo_e_citacao_nao_contam_e_crase_conta` | cerca que fecha o bloco | passou |
| Mensagem do evento vence o transcrito; vazia cai no transcrito; termo nunca vai ao disco | `test_mensagem_do_evento_vence_o_transcrito_e_o_termo_nao_vai_ao_disco` | campo vazio | passou |
| S6 só mede e o Stop passa (integração do hook) | fixture `meta/jargao-classes-da-mensagem-do-evento` e `meta/mensagem-com-jargao-so-mede` | rc 0 | passou |
| Índice das fixtures em dia | `tests.test_indice_fixtures` (7 testes) | contagem 2466 | passou |

## Cenários e resultado real
- `python3 -m unittest tests.test_meta` na raiz do clone: 9 testes, OK.
- Fixtures (via `Hooks.executar_fixture`): as duas do `meta` com jargão, ok. `tests.test_hooks` inteiro estoura meu prazo local e fica para o CI do PR.
- `forge-check docs`: rc=0.
- Sondagem de entradas patológicas (regex): hash de 200 mil `a`, caminho e cartão de 100 mil caracteres, em 3 ms ou menos; só o laço por termo é quadrático (A1).

## Vermelho antes do verde
`forge-testes --vermelho e13aed85` não terminou no meu prazo (fila da trava da suíte); sem veredito, não conta como vermelho. Prova manual: `meta.py` da base (`e13aed85`) na árvore do head, `python3 -m unittest tests.test_meta` na cópia: `Ran 9 tests ... FAILED (errors=9)`: os 4 testes novos de `JargaoPorClasse` caem (9 erros contando as 6 subcasos de classe); os 5 antigos passam.

## Mutação (`forge-mutante`)
Lista conferida contra o diff com `forge-mutante --cobertura --base e13aed8588adb14f9c6b723bf0fee2ce30e7bcd3`: toda condição Python mudada tem mutante (`meta.py:153,154,155,163,169,171,177`), mais M9 a M15 nas expressões. Rodada, `--processos 2`:

```
forge-mutante: pedido=v047-jargao-medida rev=b8d4cda82594 (3 specs)
M1 a M17 · morreu (17 de 17)
rc=0
```

Nenhum sobrevivente, nenhum equivalente.

## Achados recorrentes (PA-7)
Conferidos AR-1 (lista de mutantes completa: sim), AR-2 (ramos de falha: o que cai para o transcrito tem teste), AR-12 (specs batem com o código do head: as 17 morreram). Nenhuma classe repetida; sem linha nova.

## Revalidação por delta até 95e7a6ad (E2.246)
Delta `b8d4cda8..95e7a6ad` (`forge-check parecer delta`): `hooks/meta.py`, `tests/test_meta.py`, fixture nova `meta/jargao-mensagem-de-200-kb-decide-e-mede-no-teto`, `docs/hooks-fixtures.md`, três specs de mutante, fragmento de changelog. O A1 do parecer anterior (custo quadrático em `explicado`) está fechado: janela de `JANELA_DA_FRASE` e leitura de `TETO_DA_MEDIDA` caracteres (`cortado` na linha); a medida roda depois da decisão do Stop (`finally`), e o exit 2 continua saindo. Escopo da E7.4 inalterado: o plano vale. Sem check-run `bateria` citado; a prova é local.

- `python3 -m unittest tests.test_meta`: 15 testes, OK (6,5 s); `tests.test_indice_fixtures`: 7 testes, OK.
- Vermelho (cópia do head com `hooks/meta.py` da base `b8d4cda8`): `forge-testes --vermelho b8d4cda8` estourou o prazo (rc=124, sem veredito, não vale). Manual: os testes de etapa com ponto final, `~~~`, "o que é" longe e corte da medida caem (3 FAIL, 1 ERROR); o teste da mensagem adversária de 200 KB passa de 150 s na base (prazo), contra menos de 5 s no head. `test_stop_bloqueado_ainda_mede_e_sai_com_2` passa também na base: não distingue a ordem; quem a guarda é o teste da ordem em `Jargao` e os mutantes M25 a M28.
- Mutação, `forge-mutante --base b8d4cda8` com as 3 specs: `base=b8d4cda82594978d6edd6f309721a742848a3b81 mb=b8d4cda82594978d6edd6f309721a742848a3b81 rev=95e7a6ad678839d3a2f5fe2a734e129a79401d68`; M1 a M8 e M17 a M28 `morreu`, rc=0; sem sobrevivente nem equivalente.
- `forge-check docs`: rc=0.

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Etapa no fim da frase conta; versão de 3 números não | `test_etapa_no_fim_da_frase_conta` | ponto final, `E7.4.1` | passou |
| Cerca `~~~` abre bloco e só ela fecha | `test_cerca_de_til_e_fechada_pela_mesma_cerca` | cerca mista | passou |
| "o que é" só vale na janela | `test_o_que_e_longe_do_termo_nao_explica` | 200 caracteres | passou |
| Medida lê só o teto e marca `cortado` | `test_medida_le_so_o_teto_e_marca_cortado` | TETO_DA_MEDIDA | passou |
| Mensagem de 200 KB mede em tempo limitado | `test_mensagem_adversaria_de_200_kb_mede_em_tempo_limitado` e a fixture nova | 5 s de CPU | passou |
| Decisão do Stop antes da medida; falha da medida não escapa | `Jargao` (ordem) e `test_stop_bloqueado_ainda_mede_e_sai_com_2` | exit 2 | passou |

PA-7: AR-1 (um mutante por guarda mudada: sim), AR-2, AR-12 (specs batem com o head: 28 de 28 morrem): nenhuma classe repetida, sem linha nova.

Parecer: aprovado. Nenhum achado aberto.
