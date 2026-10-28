---
tipo: qa
contrato: 1
pedido: lote-ti
branch: melhoria/lote-ti
commit: 98991ed1ae89eb2e94612acaad29201582aec83e
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-28
---
# QA: lote-ti (testes instáveis de hooks, E1 a E4)

Parecer do pedido LOTE-TI-REV (E3.1), sobre o head `98991ed`, base `ed7fbd8`. O lote só toca testes (`tests/`) e o fragmento do changelog; nenhum arquivo de produção (`hooks/`, `bin/`) mudou, então não há spec de mutantes declarados (`tests/mutantes/`) a conferir.

## Achados
- A1 (recomendado) bin/forge-testes:188 · o `forge-testes --vermelho` sai rc=2 (sem veredito) para os testes do E3 (TypeError "unexpected keyword argument 'semente'" não está em ERROS_DE_API); a falha na base foi provada à mão (abaixo), mas o autor deveria somar TypeError ao classificador ou entregar a prova manual
- A2 (recomendado) tests/test_hooks_volta_lancador.py:167 · o teste da semente não prende o deslocamento de cada passo: trocar `desl_posicoes` ou `desl_env` por 0 em apoio_volta_unica.py (mutantes M1 e M2) sobrevive; comparar os deslocamentos por passo em amostras de corpos de mais de 97 palavras fecharia

## Critério → teste → resultado
O pedido não tem especificação de UX com `CA-n`; as obrigações são os itens E1 a E4 do pedido e a decisão D3 (2026-10-27 20:13).

| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1 (falha fechada no sandbox) | `test_apoio_pathlib_312_faz_o_caminho_longo_demais_levantar` (pré-condição, ENAMETOOLONG em toda versão) + `test_erro_interno_com_lista_de_permissao_falha_fechado` e fixtures `contrib-falha-fechada-*` (já existentes) | caminho de 300 caracteres | passou; os 3 testes passam também na base neste sandbox (a falha do cartão não reproduz hoje), o teste novo é diagnóstico e não muda o que eles provam |
| E2 (FLAKY-G1-CARGA) | `test_t9b_bash_que_passa_do_prazo_e_falha_do_arnes`; `test_g1_esta_na_classe`, `test_divisao_esta_na_classe` | prazo estourado vira falha do arnês com causa (texto `while :`) | passou 5 de 5 sob carga; vermelho: na base o teste novo dá erro (API ausente), `forge-testes` classifica "prova (API ausente)" |
| E3 (PROP-AMOSTRA) | `test_amostra_da_propriedade_desloca_com_a_semente`; propriedade com `FORGE_PROP_SEMENTE` e a semente na nota da falha | sem semente = deslocamento 0; `0 <= d < passo`; amostra ⊂ conjunto inteiro; sementes distintas, amostras distintas | passou; vermelho manual: TypeError na base (A1); mutantes M3 e M4 morrem, M1 e M2 sobrevivem (A2) |
| E4 / D3 (tempo em CPU) | `test_guarda_mede_cpu_e_nao_relogio`, `test_tempo_do_teto_das_leituras_do_lancador`, propriedade (120 s de CPU) | limite 15 ms e 10 ms (teto K); 120 s | passou; `test_guarda_mede_cpu_e_nao_relogio` cai na base (prova asserção); mutante `perf_counter` morre |

## Cenários e resultado real
Carga: 5 módulos tocados em paralelo na mesma máquina (12 núcleos).
- `tests.test_testes_tocados` 81 OK (19 s); `tests.test_hooks` 52 OK (99 s); `tests.test_hooks_volta_corpus` 16 OK (50 s); `tests.test_hooks_volta_lancador` 22 OK (66 s); `tests.test_hooks_volta_propriedades` 8 OK (58 s). Nenhum pulado, nenhuma falha.
- Repetição 5 vezes, em paralelo e com 10 laços de CPU ocupando a máquina: `test_g1_esta_na_classe`, `test_divisao_esta_na_classe`, `test_t9b_bash_que_passa_do_prazo_e_falha_do_arnes`, `test_tempo_do_teto_das_leituras_do_lancador`, `test_guarda_mede_cpu_e_nao_relogio`: 5 de 5 OK (cada rodada ~19 s).
- Vermelho (`forge-testes --vermelho ed7fbd8 --modulos test_hooks_volta_lancador`, rc=2): `test_guarda_mede_cpu_e_nao_relogio` prova (asserção); `test_amostra_da_propriedade_desloca_com_a_semente` e `test_propriedade_sem_marcador_...` "sem veredito" (B=erro). Prova manual na base com o teste do HEAD: `TypeError: BaseVoltaUnica.textos_sem_marcador() got an unexpected keyword argument 'semente'`. Na execução completa o resultado foi o mesmo (2161 não prova, 1 API ausente, 1 asserção, 1 pulado, 2 sem veredito); as não-provas são testes que o lote não escreveu.
- Mutação à mão (só no apoio, testes do E3/E4): M1 `k % passo_posicoes == 0` sobrevive; M2 `k % passo == 0` (env/outros) sobrevive; M3 deslocamento sempre 0 morre; M4 `randrange(passo+1)` morre; M5 `perf_counter` no driver morre.

## Limites contra a regra D3 (CPU, 2x o p95 de 10 execuções no runner)
- Os limites do commit vêm de medida no sandbox; não há medida no runner, que sai do CI do PR. Aqui: teto K, 10 execuções de 20 decisões, pior máximo 6,0 ms e pior médio 3,6 ms (o commit anotou p95 6,9 e 4,9); limites 15 ms e 10 ms = 2,5x e 2,8x do pior medido por mim. Cabem na regra D3 com folga se o runner for até ~2x mais lento que o sandbox (o runner foi visto a ~1,5x no relógio da propriedade).
- Propriedade sem marcador: 6 sementes, CPU 33,9 a 34,3 s (17 936 a 18 048 formas, acima do piso de 10 000); o commit anota p95 de 42,3 s em outra máquina, de 19,6 a 42,3 s. O limite de 120 s é 2,8x esse p95, acima dos 2x literais da D3, mas já era o da decisão de 19:13 e a D3 só cobre a propriedade "se ainda não estiver nos 120 s". Cabe na regra se o p95 do runner for até 60 s de CPU; o runner foi medido em 62 s de relógio com o limite antigo, e a CPU não passa do relógio.
- Veredito dos limites: cabem, condicionados à medida do CI do PR (10 execuções no runner); se o p95 do runner ultrapassar 60 s de CPU na propriedade ou 7,5 ms no teto K, o limite deixa de ser 2x e volta a ser decisão do dono.

## Riscos
- E1 não tem defeito observável hoje (os 3 testes passam na base neste sandbox): o item entrega só a pré-condição diagnóstica.
- `test_guarda_mede_cpu_e_nao_relogio` confere texto do driver (estrutural); a prova de comportamento é o teto K em milissegundos de CPU.
