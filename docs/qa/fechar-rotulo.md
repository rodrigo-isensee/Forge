---
tipo: qa
contrato: 1
pedido: fechar-rotulo
branch: melhoria/fechar-rotulo
commit: 32fb00871dc99c096d76469c54ff558eb3123def
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-20
---
# QA - forge-fechar: passo 5 por título e item marcado, aviso no `--dry-run`

Links: `~/.forge-contrib/docs/pedidos/fechar-rotulo.md`, `docs/reviews/fechar-rotulo.md`, `docs/security/fechar-rotulo.md`. Sem UX nem API; as obrigações são E1 a E3 e as duas decisões técnicas do Histórico. Código testado: `32fb008`; o HEAD `017f930` só acrescenta o parecer de segurança. Offline, gh e git falsos em `$TMPDIR` (`R-CUSTO`).

## Resultados
Suíte `python3 -m unittest discover -s tests -q`: 961 testes, OK (243 s, sem outra suíte concorrente). `scripts/validar-plugin.sh`: Validation passed. `tests.test_fechar`: 32 OK.

| Critério | Teste | Resultado | Fronteira protegida |
|---|---|---|---|
| Título que cita afrouxa-regra sem rótulo para no passo 5 | `test_titulo_que_cita_o_rotulo_sem_o_rotulo_aplicado_para` | passou | título é a primeira linha do texto |
| Corpo que só cita o nome não para (caso do #226) | `test_corpo_que_so_cita_o_nome_do_rotulo_nao_para` | passou | citação sem item marcado |
| Item marcado em `-`, `*`, `+`, `1.`, `1)` com `[x]`/`[X]` sem rótulo para | `test_recusa_quando_item_do_rotulo_marcado_...`, `test_item_marcado_com_mais_ou_lista_numerada_tambem_para`, `test_item_marcado_com_x_maiusculo_e_marcador_asterisco_tambem_para` | passaram | cada marcador e as duas caixas do x; item desmarcado não para |
| Com rótulo aplicado, passa (título e corpo) | `test_titulo_..._com_o_rotulo_aplicado_segue`, `test_rotulo_pedido_e_aplicado_pelo_dono_segue` | passaram | rótulo presente |
| `--dry-run` avisa quando o diff toca caminho protegido | `test_dry_run_avisa_quando_o_diff_toca_caminho_de_controle_da_catraca` | passou (`hooks/parecer.py`; nenhuma chamada a gh) | caminho protegido |
| `--dry-run` calado sem caminho protegido | `test_dry_run_nao_avisa_sem_caminho_de_controle` | passou | diff sem controle |
| `--dry-run` diz "não consegui conferir" quando o git diff falha | `test_dry_run_avisa_quando_nao_consegue_ler_o_diff` | passou | ref inexistente |
| Corpo gerado traz o item desmarcado | `test_corpo_gerado_traz_o_item_do_rotulo_desmarcado` | passou | nunca `[x]` |
| Lista de controles não é copiada no script (E3) | `test_lista_de_controles_vem_da_catraca_e_nao_e_copiada_no_script` | passou | mínimo de 5 itens em PROTEGIDOS |

## Vermelho antes do verde
Cópia do HEAD em `$TMPDIR/vermelho` com `bin/forge-fechar` de `50997b7` (develop): `python3 -m unittest tests.test_fechar -v` falha 5 de 32: `test_corpo_gerado_traz_o_item_do_rotulo_desmarcado`, `test_corpo_que_so_cita_o_nome_do_rotulo_nao_para`, `test_dry_run_avisa_quando_nao_consegue_ler_o_diff`, `test_dry_run_avisa_quando_o_diff_toca_caminho_de_controle_da_catraca`, `test_lista_de_controles_vem_da_catraca_e_nao_e_copiada_no_script`. Os testes de título e de marcadores passam também na develop (ela já parava em qualquer citação): são guardas contra regressão do estreitamento, não detectam o código antigo.

## Instabilidade
Nenhum teste falhou e passou de novo sem mudança.

## Achados
