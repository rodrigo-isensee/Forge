---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-vermelho-evals
commit: bdc7eb53e6388924e889f249e55b728ec221412b
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-20
---
# QA: v0478 E48.4 (VERMELHO-TESTS-EVALS)

Escopo: `bin/forge-testes --vermelho` aceita módulo de pacote de `tests/` (`evals.test_x`) e caminho de arquivo (`tests/evals/test_x.py`); a suíte do `--vermelho` inclui os módulos de pacote.

## Achados

A1 da rodada anterior (rc=2, dois testes sem veredito) fechado no delta `8b5d4a5f..bdc7eb53` (só `tests/test_testes_tocados.py`): `modulos_do_vermelho` afirma a linha do plano e `returncode` antes de ler; o teste de revertidos afirma a linha única. Na base a falha agora é de asserção.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Módulo de pacote sem `--modulos` entra no diff | `test_vermelho_sem_modulos_roda_o_modulo_de_pacote_do_diff` | pacote aninhado | prova (asserção); mutantes M4, M6 morrem |
| `evals.test_x`, `tests.evals.test_x` e caminho dão o mesmo veredito | `test_vermelho_aceita_modulo_de_pacote_e_caminho_com_o_mesmo_veredito` | três grafias | prova (asserção); M1, M3, M5 morrem |
| Herdada da base em módulo de pacote | `test_vermelho_de_modulo_de_pacote_marca_herdada...` | chave do setUpClass | prova (asserção); M8, M9 morrem |
| Grafia torta e módulo sem arquivo recusados | `test_vermelho_recusa_modulo_de_pacote_sem_arquivo_e_grafia_torta` | `tests.tests.`, `Evals.`, `evals/` | prova (asserção); M1, M2 morrem |
| Caminho de teste da raiz | `test_vermelho_aceita_o_caminho_de_teste_da_raiz` | `tests/test_x.py` | prova (asserção); M3 morre |

## Cenários e resultado real
- Módulo tocado, local (TMPDIR): `python3 -I -m unittest discover -s tests -p test_testes_tocados.py -k Vermelho` → `Ran 48 tests ... OK`.
- Cobertura: `forge-mutante --cobertura --base 004ce869…` lista as 4 condições mudadas como `coberta` (M3, M8, M10, M11) e duas `isenta` com motivo, sem `isenta velha` nem `não coberto`. Linhas de guarda do diff têm mutante.
- `forge-mutante --processos 2 tests/mutantes/vermelho-tests-evals.json`: M1 a M11 todos `morreu` (M3 e M11 com `(erro)` sob mutante, controle verde); sem sobrevivente.
- `forge-testes --vermelho 004ce869d641ca62394d705c4453d8a014002f15 --modulos test_testes_tocados --prazo 900` (rc=0, 155 s): `vermelho: base=004ce869d641 head=bdc7eb53e638 módulos=test_testes_tocados (restrito por --modulos)`; `mantidos no HEAD: tests/mutantes/vermelho-tests-evals.json, tests/test_testes_tocados.py`; `contagem: não prova (passa na base)=163; prova (asserção)=5; pulado=1`, sem sem-veredito nem falha no HEAD. Os cinco testes novos, incluindo os dois do A1, saem `H=ok · B=falha · prova (asserção)`.
- Delta: `forge-check parecer delta` lista só `tests/test_testes_tocados.py` (aviso de merge 7adf831 fora da origin/develop local, sem rede de fetch aqui). Mutantes M1 a M11 da rodada anterior seguem válidos: o delta não toca `bin/` nem a spec.
- Suíte inteira: não rodada (máquina carregada, ordem do brief); vale o check-run `bateria` do CI do PR.

## Achados fora do domínio
Nenhum.
