---
tipo: qa
contrato: 1
pedido: versao-034
branch: melhoria/lote-estoque-c
commit: f11234dffd10cdf566a5a22d43210edf595229ad
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-05
---
# QA: lote C (ferramentas), junção E2.5 do versao-034

Base do parecer: o log da suíte inteira do push do lote, `/tmp/push-lote-c.log` (head enviado d1dd1add, que só acrescenta o parecer de review sobre f11234d), pela decisão do dono de 2026-11-05 14:59. A suíte não foi rodada de novo (R-TETO). Cada item já tem o próprio QA aprovado; aqui se julga a junção.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Suíte inteira verde sobre a junção | push do lote, 94 módulos | o conjunto dos 7 itens juntos | passou: `OK (skipped=30)` |
| Mapa de testes cobre o teste novo da junção (test_qa_doutor_034 executa `bin/forge-check`) | `MapaCobreOQueOsTestesLeem` e `Mapa.test_forge_check_roda_os_modulos_dele` (contagem 40) em `tests/test_testes_tocados.py` | módulo fora do mapa | passou |
| Fragmento de changelog único com o nome da branch | `tests.test_changelog` (`FragmentoTemONomeDaBranch`) | um só fragmento novo | passou |

## Cenários e resultado real
Resumo copiado do log da suíte inteira:

```
suite-paralela: 2648 testes em 94 módulos, 2 processos (carga alta (load 15.9 de 12 núcleos, 18.3 GB disponíveis)).
processo 1: rc 0, 986 testes, 2468.5 s, 51 módulos
processo 2: rc 0, 1662 testes, 1737.8 s, 43 módulos
Ran 2648 tests in 2468.763s (2 processos)
OK (skipped=30)
19:25:34 push_rc=0 lote-c
```

Falhas: nenhuma (nenhuma linha FAIL ou ERROR no log). Pulos: 30, todos de `unittest` (`s` nas linhas de pontos; o log não traz o motivo de cada um, só a contagem; o processo 1 mostra 1 e o processo 2 mostra 25 mais 4 isolados). Nenhum deles foi acrescentado por este QA nem marcado para a suíte passar. Linhas de aviso e de catraca no log, copiadas:

```
AVISO: job 'j' pulado por falta de suporte: condição sem suporte (token inesperado): __import__('os').system('touch /tmp/
AVISO: --confiar: o código do PR de fork de 'dona' vai rodar nesta máquina com o seu ambiente e com a credencial do gh em disco; ela fica exposta a esse código.
AVISO: j/lint pulado: actionlint ausente no PATH
catraca: a API do GitHub não respondeu por inteiro (KeyError); vale como sem rótulo.
catraca: a API do GitHub não respondeu por inteiro (OSError); vale como sem rótulo.
catraca: a API do GitHub não respondeu por inteiro (OSError); vale como sem rótulo.
```

Os avisos de `j`, `--confiar` e `actionlint` são saída esperada de testes que provam esses avisos; as três linhas de catraca são de testes com a API do GitHub simulada indisponível.

## O que mudou na junção e o teste que o cobre (por leitura)
Os 7 merges não tiveram conflito (`git show --remerge-diff` vazio nos 7). O que a junção acrescentou além dos itens: `e17d07a` (`bin/forge-testes:72`, `test_qa_doutor_034` no mapa FORGE_CHECK; `tests/test_testes_tocados.py:61`, contagem 40) e `f11234d` (só `changelog.d/`, um fragmento no lugar de oito).

| Item | Teste do que mudou | Nos 94 módulos do log |
|---|---|---|
| forge-testes-filtro-k | `test_k_filtra_os_testes_do_modulo` e `test_k_repetido_soma_os_padroes_e_nao_combina_com_vermelho` em `tests/test_testes_tocados.py` | sim |
| forge-testes-aviso-mapa | `test_teste_que_le_bin_fora_do_mapa_avisa_cedo`, `test_sem_aviso_quando_o_mapa_ja_leva_o_modulo_ou_so_cita_o_caminho`, `test_sem_aviso_quando_o_teste_passa_bin_x_como_argumento_ou_dado`, `test_aviso_vale_tambem_no_diff_sem_caminho` | sim |
| forge-testes-sem-mapa | `test_caminho_de_modulo_de_teste_roda_so_esse_modulo_e_avisa` e `test_caminho_de_modulo_inexistente_ou_misturado_com_outro_arquivo_segue_o_mapa` | sim |
| doutor-034 | `tests/test_doutor.py`, `tests/test_doutor_protecao_gh.py` e `tests/test_qa_doutor_034.py` | sim |
| doutor-f8-caminho | `tests/test_qa_doutor_f8.py` (roda o `bin/forge-doutor` completo) | sim |
| lote-fechar2-guardas-v2 | `tests/test_fechar_base_andou.py` e `tests/test_fechar_espera_catraca.py` | sim |
| hook-parecer-034 | `tests/test_hooks_parecer_pasta.py` | sim |
| ajuste da junção (`bin/forge-testes`, mapa) | `Mapa.test_forge_check_roda_os_modulos_dele` (conta 40) e `MapaCobreOQueOsTestesLeem`, que reprovaria o mapa sem `test_qa_doutor_034` | sim |

Lacuna por leitura: nenhuma. Os módulos novos que leem `bin/` fora do mapa (`test_qa_doutor_f8`, `test_fechar_base_andou`) rodam na suíte completa do push, que não usa o mapa, e a guarda `MapaCobreOQueOsTestesLeem` passou com eles. A coluna "Nos 94 módulos do log" foi conferida pelo nome de cada módulo no cabeçalho dos processos do log.

## Limites
Não rodei vermelho antes do verde nem mutação: cada item os tem no próprio parecer, e a junção não muda regra de código além do mapa. O mapa de testes dirigido do pre-push não roda a suíte completa, e a contagem 40 é checada por teste, não pelo log.
