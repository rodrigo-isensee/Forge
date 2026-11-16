---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-caminho-pessoal
commit: 700913201442a8d57dd0e021ca72d3944b7fa63f
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 1
data: 2026-11-13
---
# QA: v047 caminho pessoal (E5.4, head 70091320)

Branch `melhoria/v047-caminho-pessoal`, head `700913201442a8d57dd0e021ca72d3944b7fa63f`, base `9b2c6474`. Sem PR: rodei só o que é afetado (`R-QA`).

## Achados
- A1 (recomendado) scripts/verificar-contribuicao.sh:55 · a troca do home do runner por @ apaga a barra inicial: um caminho pessoal de home ou Users aninhado depois do home do runner passa (rc 0, reproduzido). Troque por marcador com barra. Baixo, vira cartão.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E5.4-a: home do runner do CI não reprova | `test_home_do_runner_passa_mas_nome_que_o_contem_ou_o_segue_falha` (linha com o home do runner) | segmento exato runner/ | passou |
| E5.4-b: nome que só começa com runner segue barrado | mesmo teste (runner2) | logo fora do limite | passou |
| E5.4-c: outro caminho pessoal na mesma linha segue barrado | mesmo teste (home do runner e depois home de outro nome) | duas ocorrências na linha | passou |
| E5.4-d: raiz de macOS com nome runner segue barrada | mesmo teste | outra raiz | passou |
| E5.4-e: `/root/` e `$HOME` não são acusados | mesmo teste | n/a | passou |
| E5.4-f: os 4 caminhos que a base já recusava seguem recusados | `VerificarContribuicao` inteira (15 testes) | n/a | passou |

## Cenários e resultado real
- `python3 -m unittest tests.test_forge.VerificarContribuicao`: 15 testes, OK no head.
- Vermelho antes do verde: `forge-testes --vermelho 9b2c6474` rodou todos os módulos e estourou o meu prazo de 500 s (rc 124, carga 16 em 12 CPUs): sem veredito, não vale como vermelho. Linha dele: `vermelho: base=9b2c6474cc1e head=700913201442 ... revertidos à base: changelog.d/v047-caminho-pessoal.md, scripts/verificar-contribuicao.sh; mantidos no HEAD: tests/mutantes/v047-caminho-pessoal.json, tests/test_forge.py`. Vermelho manual numa cópia em $TMPDIR, com o script da base e o teste do head: o teste novo cai (`AssertionError: 1 != 0 : n.md:1: caminho pessoal`, FAILED failures=1); com o script do head passa.
- Mutação: `bin/forge-mutante tests/mutantes/v047-caminho-pessoal.json`: CP-M1, CP-M2 e CP-M3 · morreu (scripts/verificar-contribuicao.sh:55). A mudança de guarda é uma linha (a 55) e tem 3 mutantes: sem linha de guarda descoberta.
- `forge-mutante --cobertura --base 9b2c6474`: `não coberto: scripts/verificar-contribuicao.sh`. Explicação: a checagem só lista condição Python; arquivo shell sai sempre como `não coberto`, uma vez por arquivo (regra de cobertura do `forge-mutante`). Não é lacuna: os 3 mutantes declarados à mão cobrem a linha mudada e morreram.
- Sondagem própria no head: o caso A1 acima passa quando deveria ser barrado (recomendação, não requisito do E5.4: o pedido pede outro caminho pessoal na mesma linha, e esse é recusado).
- Suíte inteira: não rodei local; vale o check-run `bateria` do PR quando houver.
