---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-f5-tamanho-1
commit: 473004fedf0cbbd2a4618452b28ba6fc6802daa0
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-27
---
# QA: v0481 F5.1 (aviso de tamanho com o corte sugerido, #933)

- ci: 473004fedf0cbbd2a4618452b28ba6fc6802daa0 verde

Fonte dos critérios: `docs/arquitetura/f5-tamanho-pela-ferramenta.md`, F5.1 e "Testes previstos" (sem especificação de UX; é ferramenta). Classe C. Plano escrito da lista de testes previstos do desenho, conferido depois contra o diff (76 linhas de código: `bin/forge_tamanho.py` +46, `bin/forge-check` +30; a skill ganha 2 linhas de texto).

## Critério → teste → resultado
| Critério (desenho F5.1) | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| 150 passa, 151 recusa | `NaAbertura.test_fronteira_150_passa_e_151_recusa`, `CorteSugerido.test_recusa_de_abertura` | teto 150 / 151; exceção `teto: excedido` com o total certo | passou |
| só testes, `.md` e `tests/mutantes/` não contam; `tests/catraca.py` conta; binário fora | `NaAbertura.test_so_testes_md_e_mutantes_nao_contam_e_o_modulo_do_portao_conta`, `test_arquivo_grande_divide_por_funcao_e_binario_fica_fora` | 500 linhas sem código passam; binário | passou |
| 90+50+40 dá dois PRs (140 e 40); 100+100 dá dois | `CorteSugerido.test_agrupa_o_maior_primeiro_no_primeiro_pr_em_que_cabe`, `test_cabe_ate_o_teto_inclusive` | soma igual ao teto cabe | passou |
| arquivo de 200 com `def a` 120 e `def b` 80 vira dois PRs por função | `NaAbertura.test_arquivo_grande_divide_por_funcao_e_binario_fica_fora`, `CorteSugerido.test_linhas_por_funcao_do_cabecalho` | cabeçalho `@@` sem contagem, `,0`, sem contexto | passou |
| arquivo de 200 sem contexto vira PR próprio "cortar à mão" | `NaAbertura.test_arquivo_grande_sem_contexto_vira_topo_para_cortar_a_mao`, `CorteSugerido.test_unidade_acima_do_teto_vira_pr_proprio_para_cortar_a_mao` | unidade acima do teto | passou |
| empate em ordem estável | `CorteSugerido.test_empate_em_ordem_estavel_pelo_nome` | entrada em duas ordens | passou |
| mais de 6 PRs corta em "e mais N" | `CorteSugerido.test_texto_com_ate_6_prs_e_e_mais_n` | 6 sem corte, 8 com "e mais 2" | passou |
| o aviso do `pr --previo` traz o corte | `NaAbertura.test_aviso_do_pr_previo_traz_o_corte` | n/a | passou |
| `tamanho_do_pr` com PR aberto igual | 11 testes `NoPr` sem mudança, verdes na base e no head | PR aberto, fechado, sem rede | passou |
| falha do git: não lê o diff recusa; `-U0` que falha recusa sem o corte | `NaAbertura.test_git_que_falha_recusa_e_o_corte_que_falha_sai_sem_ele` | git falha | passou |

## Vermelho antes do verde
```
vermelho: base=6716f239c755 head=473004fedf0c módulos=test_forge_tamanho (restrito por --modulos)
contagem: não prova (passa na base)=24; prova (API ausente)=13   (rc=0)
```
Os 13 testes novos falham na base por API ausente; nenhum teste cai no head. Os 24 que passam na base são os existentes.

## Mutantes (rodados por mim; o log do autor não vale)
`bin/forge-mutante tests/mutantes/v0481-f5-tamanho-1.json tests/mutantes/v0481-f5-tamanho-1-2.json tests/mutantes/v0481-f5-tamanho-1-3.json --processos 3` (rc=0, 18 s):
```
forge-mutante: pedido=v0481-f5-tamanho-1 rev=473004fedf0c
M1 a M12, M14, M15, M16 · morreu
M13 · morreu · bin/forge-check:1526 · (erro) o teste declarado deu erro sob o mutante e passa sem ele
M17 · morreu · bin/forge_tamanho.py:69 · (erro) o teste declarado deu erro sob o mutante e passa sem ele
```
17 de 17 mortos, nenhum sobrevivente, nenhum equivalente. `--cobertura --base 6716f239c755`: todas as linhas de guarda mudadas saem `coberta` (forge-check 1491, 1512, 1513, 1516, 1526; forge_tamanho 58, 59, 68, 69, 72, 82, 89, 91), sem `não coberto`.

Os dois mortos com `(erro)` morrem por erro do teste declarado sob o mutante, com o controle verde: valem como morte pela regra da ferramenta.

## Cenários e resultado real
- Suíte: não rerrodei; `gh pr checks 933` no head 473004fe: verdes `suíte` 1/5 a 5/5, `bateria (passos)`, `bateria (python 3.14)`, `bateria (verificações longas)`, `instalação`, `teto de pulados`, `árvore já provada`; `bateria`, `bateria (pareceres)` e `catraca` falham e esperam os pareceres (isentos por G3).
- Código sem chamador: `tamanho_na_abertura` só é usada pelos testes neste PR (o F5.2 e o F5.3 a consomem, conforme o desenho); não é achado.
- Nada de bug aberto; sem acessibilidade nem E2E de stack (ferramenta de linha de comando).
