---
tipo: qa
contrato: 1
pedido: v046
branch: melhoria/conformidade-curinga
commit: abfccb7e24fb7ef005e53080d81d60c3896234cc
parecer: aprovado
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

## Revalidação por delta b283521c..abfccb7e (E20.42, volta 5)
Delta lido (3 commits: 15dfdc3a fix, f84306a6 mutantes, abfccb7e docs): hooks/conformidade.py (`COLCHETE_DE_DIGITO`, `sem_caixa`, `origem_so_generica`), 11 fixtures `gitcomum-v3-*` novas (mínimo atualizado), spec `-6` (G34 a G39), AR-13. Veredito: aprovado.
- A1 (mutante sobrevivente no ramo do diretório comum): fechou. Fixture `gitcomum-v3-worktree-comum-config-bloqueia`; G36 (`filter(None, (git,))`) morre em hooks/conformidade.py:1104.
- A2 (linha de guarda sem mutante): fechou. `forge-mutante --cobertura --base c340c322` sem nenhuma `sem mutante`, `não coberto` ou `só equivalente`; 1083 (G38), 1097 (G34, G39), 1104 (G37) cobertas.
- Delta sem achado novo. Sondei o colchete: `[[:digit:]]`, `[[=c=]]`, `[^x]`, `[0-9][a]` ficam com `[` depois de retirar o colchete de dígitos e recusam; `[0-9-]+` só admite dígito e hífen, sem letra, então o bash e o glob do Python leem igual. Desvio declarado (par `forge-suite-Xverde.[0-9]`) coberto por `gitcomum-v3-colchete-digito-libera` e G39.

## Provas (revalidação E20.42)
- PQ-1: `git log --format=%H -1 abfccb7e24fb7ef005e53080d81d60c3896234cc` -> abfccb7e24fb7ef005e53080d81d60c3896234cc
- Vermelho: worktree destacada na base do delta (b283521c) com as fixtures novas copiadas: `python3 -m unittest tests.test_hook_git_comum` FAILED (failures=6: classe-config, equivalencia-config, negacao-config, negacao-hooks, nocaseglob-config, ordenacao-config, todas recusa que a base libera). As outras 5 passam na base por desenho (guardas de regressão; mortas pelos mutantes G36 a G39).
- Head abfccb7e: `python3 -m unittest tests.test_hook_git_comum` Ran 1 test, OK.
- `bin/forge-mutante tests/mutantes/v046-conformidade-caminho-git-4.json` rc 0: G20 a G26 `morreu`.
- `bin/forge-mutante tests/mutantes/v046-conformidade-caminho-git-5.json` rc 0: G27 a G33 `morreu`.
- `bin/forge-mutante tests/mutantes/v046-conformidade-caminho-git-6.json` rc 0: G34, G39, G35, G36, G37, G38 `morreu` (conformidade.py:1097, 1097, 1103, 1104, 1104, 1083).
- `bin/forge-mutante --cobertura --base c340c322` rc 0, só linhas `coberta`.
- Suíte inteira: não rodei (R-TETO); vale o check-run `bateria` do sha no CI do PR.
