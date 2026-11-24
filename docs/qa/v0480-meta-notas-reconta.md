---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-meta-notas-reconta
commit: c947a0634110a0006d4ca4f6d63e446a2c2445d5
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-23
---
# QA: v0480-meta-notas-reconta (E137.17, PR #822)

## Achados
- A1 (bloqueante) hooks/meta.py:327 · mutante sobrevivente: trocar `vistas.pop(...)` por `vistas.get(...)` mantém os 54 testes verdes; a ordem de uso mais recente (quem sai quando passa de MARCAS_GUARDADAS) não tem teste nem mutante declarado.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E137.1: marca por transcrito, o Stop de outra sessão não apaga a minha | test_stop_de_outra_sessao_no_meio_nao_faz_recontar | duas sessões intercaladas | passou; vermelho na base (asserção) |
| E137.1: teto MARCAS_GUARDADAS, sai a mais velha | test_marcas_guardadas_param_no_teto_e_sai_a_mais_velha | teto + 1 | passou; vermelho na base (API ausente); só prova a saída por inserção, não por uso (A1) |
| E137.1: marca fora da forma é ignorada | test_marca_do_transcrito_fora_da_forma_e_ignorada | entrada não objeto | passou; passa na base (herdada), morre o mutante M2 |
| E137.1: nota cuja entrada traz `"type":"tool_result"` ainda conta | test_nota_cuja_entrada_traz_o_par_type_tool_result_ainda_conta | par dentro do input objeto | passou; vermelho na base (asserção) |
| Ordem de uso mais recente decide quem sai (comentário em meta.py:327) | nenhum | n/a | sem teste (A1) |

## Cenários e resultado real
- `python3 -m unittest tests.test_meta` (da raiz, sem -I): Ran 54 tests, OK.
- `bin/forge-testes --vermelho 0e59c446 --modulos test_meta`: `vermelho: base=0e59c44642a8 head=c947a0634110 módulos=test_meta (restrito por --modulos)`; `contagem: não prova (passa na base)=51; prova (API ausente)=1; prova (asserção)=2`.
- `forge-mutante` precisa de uma chamada por pedido (as duas specs têm pedidos diferentes), então rodei uma por spec, ambas com `--base 0e59c446`, rc 0:
  - v0478-meta-notas-3: `base=0e59c44642a8f388649cb794072fd347ebebd8aa mb=0e59c44642a8f388649cb794072fd347ebebd8aa rev=c947a0634110a0006d4ca4f6d63e446a2c2445d5`; M15, M16, M17, M18 morreram; M19, M20, M21, M22 morreram (erro).
  - v0480-meta-notas-reconta: mesma linha `base=`; M1 morreu (hooks/meta.py:285), M2 morreu (erro, :318), M3 morreu (:329), M4 morreu (:331).
- `forge-mutante --cobertura --base 0e59c446`: só linhas `coberta`, nenhuma `não coberta`. A cobertura não enxerga o `pop` do diff como condição, por isso o mutante manual abaixo.
- Mutante manual (QA) `vistas.pop(str(transcrito), {})` para `vistas.get(str(transcrito), {})`: 54 testes OK, sobrevive. Efeito: a sessão ativa mantém a posição de inserção e pode ser expulsa antes de uma ociosa, voltando ao recontar das notas. Corrige-se com um teste (sessão 0 volta a ser usada, depois mais MARCAS_GUARDADAS - 1 sessões, e a sessão 0 ainda tem marca) e um mutante declarado na spec.
- Árvore restaurada após o mutante manual (git status limpo).
- Suíte inteira: só no CI do PR; não rodada aqui.
