---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-meta-notas
commit: 870159838c177a81663725861816f6c14914b512
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-18
---
# QA: v0479-meta-notas (v0478 E25.4)

Escopo: só os testes do diff (`tests/test_meta.py`, classe `NotasEntreFerramentas`; `tests/evals/test_erros_por_papel.py` sem o `expectedFailure`; fixture `tests/hooks/meta/notas-entre-ferramentas-em-ingles-acusa.json`) e os 14 mutantes. Sem suíte local: a suíte inteira é o check-run `bateria` do CI do PR.

## Achados
- A1 (bloqueante) tests/test_meta.py:350 · R-QA: o vermelho sai rc=2 (sem veredito): 8 dos 11 testes novos dão KeyError (erro) na base por `linha["notas_em_outro_idioma"]`, em vez de falhar por asserção. Use `.get(...)` para a base dar falha e o vermelho dar rc 0.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Nota em outro idioma na rodada acusa | `test_nota_em_outro_idioma_na_rodada_acusa`, fixture, eval `test_nota_entre_ferramentas_em_ingles_e_acusada` | nota única | passou |
| Controle: notas no idioma do dono | `test_controle_notas_no_idioma_do_dono_nao_acusam` | n/a | passou |
| A fala do dono fecha a rodada | `test_nota_de_rodada_anterior_nao_conta` | limite da rodada | passou |
| Subagente não conta | `test_nota_de_subagente_nao_conta` | isSidechain | passou |
| Mensagem final não é nota | `test_mensagem_final_no_transcrito_nao_conta_como_nota` | duplicata da final | passou |
| Nota curta/mista sem idioma | `test_nota_curta_fica_sem_idioma_e_nao_conta` | texto curto | passou |
| Linha ilegível / fora da forma | `test_linha_ilegivel_...`, `test_registro_fora_da_forma_...` | JSON quebrado, tipos errados | passou |
| Sem lista do idioma do dono | `test_dono_sem_lista_nao_mede_notas` | idioma sem lista | passou |
| Custo: resultado de ferramenta não decodifica | `test_resultado_de_ferramenta_nem_se_decodifica` | linha maior | passou |
| Teto da medida | `test_notas_param_no_teto_da_medida` | 30+30+10 = 70 | passou |

## Cenários e resultado real
- `python3 -I -m unittest discover -s tests -p test_meta.py`: 43 testes, OK. `tests/evals/test_erros_por_papel.py`: 18 testes, OK (expected failures=3, os que sobraram não são o tirado).
- Vermelho (`forge-testes --vermelho 0c47762a --modulos test_meta --prazo 150`), cabeçalho: `vermelho: base=0c47762a6a9d head=870159838c17 módulos=test_meta`; revertidos à base: `hooks/meta.py` e outros 3. Contagem: `não prova (passa na base)=32; prova (API ausente)=3; sem veredito=8`, rc=2. Os 8 sem veredito são os testes da classe que passam por `medir` (B=erro, KeyError): ver A1. O eval do hook (`test_erros_por_papel`) não é módulo aceito pelo `--modulos` (fica em tests/evals).
- Mutação (`bin/forge-mutante --processos 4 tests/mutantes/v0478-meta-notas.json tests/mutantes/v0478-meta-notas-2.json`): `pedido=v0478 rev=870159838c17`, M1 a M14 `morreu`, rc=0, nenhum sobrevivente (M11 a M14 morrem por erro do teste declarado, o que o `forge-mutante` anota). Condições mudadas em `hooks/meta.py` (linhas 269, 271, 277, 279, 281 a 284, 287, 294, 297, 318): todas `coberta` no `--cobertura --base 0c47762a`; sem condição sem mutante.
- Guarda de suíte vazia: os testes percorrem listas fixas pequenas e afirmam o conteúdo exato; sem glob.

## Resultado
Reprovado só por A1 (vermelho sem veredito). Os testes e a mutação estão bons; o conserto é de uma linha no teste, do autor.
