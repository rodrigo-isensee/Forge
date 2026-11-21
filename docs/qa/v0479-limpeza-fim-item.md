---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-limpeza-fim-item
commit: 011d6e1b9db4f44d236988740619d1776b8922aa
parecer: aprovado
escopo: incremental
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

## Revalidação (E68.10, head 9aa1e723, delta desde 71996730)
Delta lido por `forge-check parecer delta`: `bin/forge-copia` (A1: PR de fork, `isCrossRepository`, não encerra o item; A2: limpeza conferida de novo antes de apagar, função `sujeira`), 2 módulos de teste, spec `-4` e fragmento. Escopo e critérios iguais; sem achado novo.
- Local, só os arquivos tocados: `test_forge_copia.py` 57 testes OK; `test_forge_fechar.py` 29 testes OK. Suíte completa no CI do PR (`bateria` do mesmo sha).
- Vermelho: `forge-testes --vermelho 71996730… --modulos test_forge_copia,test_forge_fechar`: `contagem: não prova (passa na base)=78; prova (asserção)=8`; nenhum teste cai no HEAD.
- Mutação do delta: `bin/forge-mutante tests/mutantes/v0479-limpeza-fim-item-4.json --base 71996730…`: `base=71996730… rev=8767adfe3aff`; M25 (fork), M26 (reconferência), M27 (suja antes do gh) todos `morreu`, saída 0.

## Revalidação (E68.15, head 70115210, delta desde 9aa1e723)
Delta lido por `forge-check parecer delta`: `bin/forge-fechar` (função `fim_sem_merge`: só PR CLOSED do próprio repositório ou `vazio: sim` libera a limpeza sem merge; o contrato antigo do `--limpar` fica quando não há prova), `tests/test_forge_fechar.py`, spec `-5` e fragmento. Escopo e critérios iguais; sem achado novo.
- Local, só os arquivos tocados: `test_fechar.py` 111 testes OK (1 skip já existente, não introduzido pelo delta); `test_forge_fechar.py` 34 testes OK; `test_forge_copia.py` 57 testes OK. Suíte completa no CI do PR (`bateria` do mesmo sha).
- Vermelho: `forge-testes --vermelho 9aa1e723… --modulos test_forge_fechar`: `contagem: não prova (passa na base)=30; prova (asserção)=4`; nenhum teste cai no HEAD.
- Mutação do delta: `bin/forge-mutante tests/mutantes/v0479-limpeza-fim-item-5.json --base 9aa1e723…`: `base=9aa1e723… mb=9aa1e723… rev=8c3538ed…`; M28, M29, M30, M31 todos `morreu`, saída 0. Um mutante por linha de guarda mudada (linhas 798 a 800 e 1311).

## Revalidação (E68.20, head 011d6e1b, delta desde 70115210)
Delta lido por `forge-check parecer delta`: merge da develop sem conflito (fora do domínio) e o comando completo `forge-fechar <pedido> --ref <branch> --limpar` em `skills/trabalho-em-paralelo/ritmo-e-corte.md:44` (mais as citações das linhas 22 e 31). Sem código nem teste no delta; critérios iguais; sem achado novo.
- Local, só os arquivos tocados, com TMPDIR: `test_comando_pronto` 3 testes OK; `test_metricas_texto` 2 testes OK. Suíte completa no CI do PR (`bateria` do mesmo sha).
- Vermelho e mutação: não se aplicam, pois o delta é só texto de skill, sem regra de código.
