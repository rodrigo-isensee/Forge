---
tipo: qa
contrato: 1
pedido: v048
branch: melhoria/v048-dono-pesos
commit: ca3c07bb5c4eebe23e849d0031dd9822c5aed05f
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-28
---
# QA: v048 dono dos pesos (#959, DONO-DA-GERACAO-DOS-TEMPOS, classe C)

- ci: pendente no momento do parecer (head ca3c07bb): suíte 3/5 e 5/5 verdes, 1/5, 2/5 e 4/5 em andamento; `catraca` e `catraca (conferência)` vermelhas (esperam parecer ou rótulo). Sem a linha `ci: <sha40> verde` o `forge-check pr` recusa o aprovado; regravar quando as partes fecharem.

## Achados
- A1 (recomendado) tests/test_pesos_do_ci.py:261 · `forge-testes --vermelho` dá "sem veredito" para 3 testes novos (B=erro, API ausente na base: conferir, perna, pesos_velhos) e "passa na base" para 2 negativos; a prova real é a mutação M1-M13 (asserção), não o vermelho.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E6.1 execução de PR mesclado na develop entra | DepoisDoF6.test_pr_mesclado_na_develop_entra | PR mesclado, head igual | passou; M5 morreu |
| E6.1 não mesclado, fork, outra base, sha antigo não entram | test_pr_nao_mesclado_de_fork_de_outra_base_ou_de_outro_sha_nao_entra | 4 limites fora | passou; M1 M10 mortos |
| E6.1 perna de push x perna de PR | test_perna_de_push_nao_vale_em_execucao_de_pr_e_a_de_pr_nao_vale_em_push | nome da perna | passou; M4 morto |
| E6.1 teto 2x limite | test_teto_de_execucoes_conta_as_de_pr_ate_2_vezes_o_limite | máximo | passou; M6 morto |
| Falha fechada com dado malformado | test_execucao_de_pr_malformada_nao_quebra_nem_entra | não objeto, 2 PRs, sem PR, sem número, número string | passou; M7 M8 M9 mortos |
| E6.2 `--conferir` acusa pesos velhos | test_pesos_velhos_sao_acusados, test_conferir_sai_1_com_pesos_velhos_e_0_com_pesos_em_dia | chave fantasma, mais de 25% sem peso | passou; M2 M3 M11 M13 mortos |
| `--conferir` com arquivo que não é objeto | test_conferir_com_pesos_que_nao_sao_objeto_sai_1 | lista com as mesmas chaves | passou; M12 morto |
| E6.3 dono no passo de ritmo-e-corte.md | leitura do diff (texto, sem teste) | n/a | conferido |
| Specs v047 realinhados (-2, -4, -5) | bin/forge-mutante nos 3 | M16 M17 e demais | todos morreram; 1 equivalente declarado (M20) |

## Cenários e resultado real
- Testes do módulo: `python3 -m unittest tests.test_pesos_do_ci`: 24 testes, OK.
- Mutantes (`bin/forge-mutante tests/mutantes/v048-dono-pesos.json`, head ca3c07bb): M1 a M13 `morreu`, nenhum `(erro)`, ou seja, todos pela asserção.
- v047-ci-rapido-2, -4, -5: todos `morreu` (vários com `(erro)`, comportamento anterior da spec, controle verde); M20 equivalente declarado.
- `--cobertura --base ae194fa9`: as 13 condições mudadas cobertas por M1 a M13.
- Vermelho (`forge-testes --vermelho ae194fa9 --modulos test_pesos_do_ci`): `base=ae194fa9ca00 head=ca3c07bb5c4e`; prova (asserção)=2, prova (API ausente)=1, sem veredito=3, não prova (passa na base)=18 (inclui 2 negativos novos, vácuos na base por natureza, mortos pelos mutantes). Ver A1.
- Falha fechada: dado malformado da API não chama `pulls/N` nem levanta; `--conferir` com arquivo não objeto sai 1; `--conferir` nos pesos reais do repositório sai 0.
- Não verificado: leitura real da API do GitHub (só dublê, R-CUSTO); valores não numéricos em `pesos-d4.json` não são conferidos pelo `--conferir`.
