---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-limpeza-fim-item
commit: 71996730a3e485db4410e9e4a824fe4e113d4ace
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-21
---
# QA: v0479-limpeza-fim-item (E68.5)

Escopo: `forge-copia limpar` (apaga clone ou worktree de item acabado) e `forge-fechar --limpar` sem PR MERGED nem aberto, que passa as cópias ao `forge-copia limpar` (LIMPEZA-AO-FIM-DO-ITEM). Diff base..71996730 conferido: `bin/forge-copia`, `bin/forge-fechar`, 3 specs de mutantes, 2 módulos de teste, fragmento e uma linha em `ritmo-e-corte.md`.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Fim do item (PR MERGED/CLOSED sem OPEN; sem PR, `vazio: sim`) | `test_forge_copia` (limpar) | PR aberto, sem PR e não vazio | passou |
| Só cópia limpa, sem stash, sem commit fora da origem, sem worktree ligada | `test_forge_copia`, `LimparSemMerge.test_copia_suja_fica_com_codigo_3` | árvore suja, arquivo novo | passou |
| Destino fora de `~/.forge-contrib` ou a própria pasta recusado | `test_forge_copia` | `..`, link, raiz | passou |
| Branch local e remota ficam | `LimparSemMerge.test_pr_fechado_apaga_o_clone_limpo_e_a_branch_fica` | n/a | passou |
| `forge-fechar --limpar`: PR aberto para; sem cópia para como antes; outra branch intocada; a principal não é cópia | `LimparSemMerge.*` | PR aberto, outra branch | passou |

## Execução (local, só os arquivos tocados, com TMPDIR)
- `test_forge_copia.py`: 55 testes, OK. `test_forge_fechar.py`: 29 testes, OK. A suíte completa fica no CI do PR (`bateria` do mesmo sha).
- Vermelho antes do verde, `forge-testes --vermelho bead3e53… --modulos test_forge_copia,test_forge_fechar`:
  `vermelho: base=bead3e531280 head=71996730a3e4 módulos=test_forge_copia,test_forge_fechar (restrito por --modulos)`
  `contagem: não prova (passa na base)=59; prova (API ausente)=1; prova (asserção)=24` (nenhum teste cai no HEAD).
- Mutação: `bin/forge-mutante` nas 3 specs (24 mutantes: 16 em `forge-copia`, 8 em `forge-fechar`), saída 0, M1 a M24 todos `morreu`.
- `forge-mutante --cobertura --base bead3e53`: condições Python de `forge-copia` cobertas por mutante declarado (provado acima); `forge-fechar` é shell (`não coberto`), com 8 mutantes declarados à mão (linhas 803 a 818, 1300 e 1301), todos mortos.
