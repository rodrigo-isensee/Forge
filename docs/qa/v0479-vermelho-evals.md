---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-vermelho-evals
commit: 8b5d4a5f52add0af2856af46e95e748cb069f301
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-20
---
# QA: v0478 E48.4 (VERMELHO-TESTS-EVALS)

Escopo: `bin/forge-testes --vermelho` aceita módulo de pacote de `tests/` (`evals.test_x`) e caminho de arquivo (`tests/evals/test_x.py`); a suíte do `--vermelho` inclui os módulos de pacote.

## Achados
- A1 (bloqueante) tests/test_testes_tocados.py:1310 · `forge-testes --vermelho` dá rc=2 (sem veredito): dois testes novos caem na base com erro, não asserção (B=erro): ...aceita_modulo_de_pacote_e_caminho... e ...aceita_o_caminho_de_teste_da_raiz (:1347). R-QA: sem veredito não vale vermelho.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Módulo de pacote sem `--modulos` entra no diff | `test_vermelho_sem_modulos_roda_o_modulo_de_pacote_do_diff` | pacote aninhado | prova (asserção); mutantes M4, M6 morrem |
| `evals.test_x`, `tests.evals.test_x` e caminho dão o mesmo veredito | `test_vermelho_aceita_modulo_de_pacote_e_caminho_com_o_mesmo_veredito` | três grafias | passa no HEAD; na base B=erro (sem veredito); M1, M3, M5 morrem |
| Herdada da base em módulo de pacote | `test_vermelho_de_modulo_de_pacote_marca_herdada...` | chave do setUpClass | prova (asserção); M8, M9 morrem |
| Grafia torta e módulo sem arquivo recusados | `test_vermelho_recusa_modulo_de_pacote_sem_arquivo_e_grafia_torta` | `tests.tests.`, `Evals.`, `evals/` | prova (asserção); M1, M2 morrem |
| Caminho de teste da raiz | `test_vermelho_aceita_o_caminho_de_teste_da_raiz` | `tests/test_x.py` | passa no HEAD; na base B=erro (sem veredito); M3 morre |

## Cenários e resultado real
- Módulo tocado, local (TMPDIR): `python3 -I -m unittest discover -s tests -p test_testes_tocados.py -k Vermelho` → `Ran 48 tests ... OK`.
- Cobertura: `forge-mutante --cobertura --base 004ce869…` lista as 4 condições mudadas como `coberta` (M3, M8, M10, M11) e duas `isenta` com motivo, sem `isenta velha` nem `não coberto`. Linhas de guarda do diff têm mutante.
- `forge-mutante --processos 2 tests/mutantes/vermelho-tests-evals.json`: M1 a M11 todos `morreu` (M3 e M11 com `(erro)` sob mutante, controle verde); sem sobrevivente.
- `forge-testes --vermelho 004ce869… --modulos test_testes_tocados --prazo 600`: `vermelho: base=004ce869d641 head=8b5d4a5f52ad`; `contagem: não prova (passa na base)=163; prova (asserção)=3; pulado=1; sem veredito=2`; rc=2. Os dois sem veredito são os de A1; os mutantes provam que caem sem o código, mas a ferramenta não os aceita como vermelho. Correção sugerida ao autor: afirmar o `returncode` antes de ler a saída (`modulos_do_vermelho` estoura `StopIteration` na base), para a falha ser de asserção.
- Suíte inteira: não rodada (máquina carregada, ordem do brief); vale o check-run `bateria` do CI do PR.

## Achados fora do domínio
Nenhum.
