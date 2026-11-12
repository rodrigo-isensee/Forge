---
tipo: qa
contrato: 1
pedido: v046
branch: melhoria/conformidade-curinga
commit: 9bd8340486854e946ad2bd810074a6dfaaf8e778
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-12
---
# QA: conformidade-curinga (volta 4, E20.38)

## Achados
- A1 (bloqueante) hooks/conformidade.py:1093 · mutante sobrevivente (R-QA): trocar `(git, topo and diretorio_comum(topo))` por `(git,)` e rodar tests.test_hook_git_comum dá OK. O ramo do diretório comum (worktree) não tem fixture nem mutante na spec -5.
- A2 (bloqueante) tests/mutantes/v046-conformidade-caminho-git-5.json:1 · linha de guarda sem mutante: `forge-mutante --cobertura` lista 1093 `topo and diretorio_comum(topo)` e `b and Path(b).is_dir()` como `sem mutante`. Declarar o mutante e a fixture de worktree (`ln "$(git rev-parse --git-common-dir)"/c?nfig h`).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Curinga na origem de rev-parse que alcança .git/config recusa | gitcomum-v3-curinga-config, -colchete-config-cp-l | glob em regra específica | passou (cai na base, passa no head) |
| Curinga com variável | gitcomum-v3-curinga-variavel, -chaves-variavel-cp-s | origem via variável | passou |
| Chaves recusam (falha fechada) | gitcomum-v3-chaves-config | chaves | passou |
| Prefixo do glob (`hook[s]/pre-push`) | gitcomum-v3-colchete-hooks-cp-s | cada prefixo | passou |
| Destino nunca se libera | gitcomum-v3-link-destino-rev-parse | último argumento | passou (já passava na base; guarda de regressão, morto por G27) |
| Sem falso positivo: `HEA?` segue livre | gitcomum-v3-curinga-head-libera | regra genérica | passou (libera na base e no head) |
| Origem no diretório comum de worktree com curinga | nenhum | worktree | NÃO COBERTO (A1) |

## Cenários e resultado real
- Vermelho à mão: worktree destacada na base c340c322, com as 8 fixtures novas copiadas: `python3 -m unittest tests.test_hook_git_comum` deu FAILED (failures=6): as 4 de bloqueio por curinga/colchete e as 2 de chaves/variável. As outras 2 (link-destino, head-libera) passam na base por desenho.
- Head 9bd83404: `python3 -m unittest tests.test_hook_git_comum` OK (72 fixtures, mínimo atualizado).
- `bin/forge-mutante tests/mutantes/v046-conformidade-caminho-git-5.json` (árvore limpa, em série): G27 a G33 morreram, rc 0. A spec -4 (G22 a G26) também morreu.
- Sonda minha (fixture descartável numa worktree, `ln "$(git rev-parse --git-common-dir)"/c?nfig h`): passa no head e falha com o ramo do diretório comum removido, o que prova que a fixture que falta mataria o mutante.
- A suíte inteira roda no CI do PR (`bateria`); não rodada aqui.
