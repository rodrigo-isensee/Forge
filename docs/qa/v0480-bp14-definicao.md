---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-bp14-definicao
commit: 0f921872cf4e8f854bfc7ccefab316da3fd046e3
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-24
---
# QA: v0480-bp14-definicao (E163.3)

Diff `998e2e45..0f921872`: uma linha de comentário HTML igual nos dois modelos de retrospectiva (`docs/retrospectivas/_modelo.md`, `templates/projeto/docs/retrospectivas/_modelo.md`) e o fragmento `changelog.d/v0480-bp14-definicao.md`. Só texto de comentário: define "pedido parado" (aberto, sem movimento no quadro há 7 dias ou mais). Sem código nem teste novo; vermelho antes do verde e mutação não se aplicam. Sem suíte local: a inteira é o `bateria` do CI do PR.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Os dois modelos seguem iguais | `test_retro_pendentes.test_modelo_preenchido_cobre_e_os_dois_modelos_sao_iguais` | igualdade fábrica × projeto | passou |
| Modelo só com comentário não cobre | `test_retro_pendentes.test_retro_so_com_o_cabecalho_do_modelo_nao_cobre` | corpo vazio (comentário HTML não conta) | passou |
| Seção 1 vazia segue sem cobrir (sonda) | sonda abaixo | seção vazia | passou |
| Texto das métricas dentro do teto | `test_metricas_texto` (2) | teto de caracteres | passou |
| Medidas | `test_medidas_m14b` (73) | n/a | passou |

## Execução
Comando: `python3 -I -m unittest discover -s tests -p <módulo>.py`.
- `test_retro_pendentes`: Ran 20, OK. `test_metricas_texto`: Ran 2, OK. `test_medidas_m14b`: Ran 73, OK.
- Sonda: modelo novo com todo comentário trocado por `texto.`, menos a seção 1 (vazia), `Cobre: v0.1.0, v0.2.0`. Saída: `(1, [... 'retro: pendentes=2'], ['retro: aviso: "p.md": secao sem corpo: dados do pedido; nao cobre'])`. A seção 1 vazia continua sem cobrir; a nova redação do comentário não mudou isso.
