---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-maq-i9
commit: ca3017805fcfb5c3c6321d65e587e2b58a942764
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-16
---
# QA: v047 (MAQ-I9, fatia 3: forge-testes na trava)

Escopo: `bin/forge-testes` (a suíte completa sem `-k` só roda por `.githooks/pre-push --suite` da própria cópia; R-TETO), testes em `tests/test_testes_tocados.py`, specs `tests/mutantes/v047-maq-i9.json` e `-2.json`. Sem especificação de UX nem contrato de API (ferramenta interna); as obrigações são as de C-1, C-4, C-5 e T-2 do desenho citados nos testes e no changelog.

## Achados
- A1 (bloqueante, corrigido em ca301780) tests/test_testes_tocados.py:1674 · `unlink(missing_ok=True)` aplicado; o vermelho agora dá veredito (rc 0).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| C-5 completa pedida passa pela trava (`execv` de `pre-push --suite`) | `TravaDoForgeTestes.test_completa_pedida_vira_o_pre_push_da_copia_com_suite` | argv fixo `--suite`, código 7 chega inteiro | passou; prova (asserção) |
| C-1 script de outra cópia sai 2 | `test_script_de_outra_copia_sai_2_no_completo` | raiz do script diferente da raiz do git | passou; prova (asserção) |
| C-1 pre-push sem `+x` ou ausente sai 2, sem recuo ao `discover` (T-2) | `test_pre_push_sem_x_ou_ausente_sai_2_sem_recuo_para_o_discover` | permissão, arquivo ausente | passou; prova (asserção) |
| C-4 plano completo só roda com `--status` 1 (0, 2, 3, sinal = ocupado) | `test_completo_por_plano_so_roda_com_o_status_livre` | código logo fora do livre, morte por sinal | passou no HEAD; prova (asserção) após A1 |
| `-k` e `--afetados` seguem como antes | `test_completa_com_k_segue_como_antes`, `test_afetados_nao_passa_pela_trava` | `-k`, plano que nunca é a completa | passou; neutros na base (esperado) |
| Sem mapa cai na completa e não a roda de outra cópia | `Execucao.test_sem_mapa_cai_na_completa_e_o_script_de_outra_copia_nao_a_roda`, `test_completa_pedida_e_listar_nao_roda_nada` | `--listar` não roda nada | passou; prova (asserção) |
| Medida da vaga segue com `-k` | `MedidaDaVagaPesada.rodar_com` | n/a | passou |

## Cenários e resultado real
- Módulo do item, `python3 -m unittest tests.test_testes_tocados` na raiz do clone: `Ran 157 tests in 48.038s`, `OK (skipped=1)`. O skip é `MedidaDaVagaPesada.test_conta_a_pesada_viva_sem_gravar_a_linha_de_comando_dela`, pulado também na base (H=pulado, B=pulado): condicional já existente, não do item.
- Vermelho: `bin/forge-testes --vermelho 4138445e --modulos test_testes_tocados` (cwd no clone, árvore limpa). Abre com `vermelho: base=4138445e23bd head=029b6456889d módulos=test_testes_tocados (restrito por --modulos)`; `revertidos à base: bin/forge-testes, changelog.d/v047-maq-i9.md`. Fecha com `contagem: não prova (passa na base)=148; prova (asserção)=7; pulado=1; sem veredito=1` e `sem veredito: volta ao autor; não vale como vermelho nem como já falhava.` Saída 2. Nada cai no HEAD (H=ok em todos). O sem veredito é o do A1.
- Mutantes: `bin/forge-mutante tests/mutantes/v047-maq-i9.json tests/mutantes/v047-maq-i9-2.json --processos 3`, saída 0, `spec=dc042588… spec=2ce1f27b…`, M1 a M9 `morreu` (bin/forge-testes:925, 799, 800, 803, 804, 807, 807, 808, 810).
- Cobertura de guardas: `forge-mutante --cobertura --base 4138445e` lista 799, 803, 807 e 925 como `coberta` (declarado, não provado); os 9 mutantes cobrem cada linha de guarda mudada no diff (`not pedida`, `!= 1`, `os.access`, raiz, `modo == "completo" and not args.filtros`). Sem achado de lista incompleta (AR-1).
- Revisão do diff: o `execv` troca o processo, então o código de saída do pre-push chega sem passar por `anotar`; o log deixa de anotar a completa (documentado na docstring). Sem outro defeito encontrado.
- Suíte inteira: não rodada localmente; fica para o check-run `bateria` do mesmo sha no CI do PR.
- Achados recorrentes (PA-7): AR-1 conferido (lista cobre o diff); AR-4 conferido (`LIMPO` tira `CI`, `FORGE_*`, `GIT_*` do ambiente dos testes novos); AR-5 conferido (`python -I` nos testes novos); sem classe repetida nova, sem linha `AR-<n>` a gravar.

## Revalidação (delta 029b6456..ca301780)
- `forge-check parecer delta`: só `tests/test_testes_tocados.py` (uma linha: `self.registro.unlink(missing_ok=True)`); sem mudança em `bin/`, logo mutantes e demais resultados anteriores seguem valendo.
- `bin/forge-testes --vermelho 4138445e --modulos test_testes_tocados`: `contagem: não prova (passa na base)=148; prova (asserção)=8; pulado=1`, sem veredito=0, nada cai no HEAD, rc=0 (antes: prova=7, sem veredito=1, rc=2).
- `python3 -m unittest tests.test_testes_tocados.TravaDoForgeTestes`: `Ran 6 tests`, `OK`.
- Suíte inteira: check-run `bateria` do mesmo sha no CI do PR.
