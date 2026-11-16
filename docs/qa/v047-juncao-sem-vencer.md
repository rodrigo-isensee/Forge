---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-juncao-sem-vencer
commit: 7babe7b84c382dc4ecba5ca59bfac38e3e210995
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-16
---
# QA: v047 (E2.201, junção que não vence parecer)

Código testado no head 7babe7b8 (o commit seguinte, f35176b2, só traz o parecer de segurança, trazido por merge). Sem especificação de UX: as obrigações são a E2.201 do pedido e a regra E7 (trazer a base por merge limpo não vence parecer por arquivo que a branch não mudou).

## Achados
- A1 (recomendado) bin/forge-check:1328 · o termo `base_do_delta(raiz, "develop", ref)[0]` não tem mutante: trocado por `True`, sobrevive (mutante Q1, rodado por mim). Sem develop ou com o head nela, o stdout e o rc são os mesmos; só mudam avisos no stderr. Declarar como `equivalente`.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| `pr` sem `--base` numa branch de trabalho: merge limpo da develop não vence o parecer | `JuncaoSemBase.test_merge_limpo_da_develop_nao_vence` | `.github/workflows/ci.yml` vindo da develop, branch sem mudá-lo | passou; falha na base |
| O que a branch mudou depois do parecer segue vencendo | `JuncaoSemBase.test_mudado_pela_branch_depois_do_parecer_vence` | `bin/a` mudado pela branch | passou; falha na base |
| Branch de integração (`main`) segue o diff literal | `JuncaoSemBase.test_branch_de_integracao_segue_o_diff_literal` | `main` sem `--base` não ganha develop | passou |
| Mensagem do teste existente passa a citar a base | `TesteEParecerSeparados` (3 testes) | linha com `(base origin/develop ...)` | passou |

## Cenários e resultado real
- Diff `4138445e..7babe7b8`: `bin/forge-check` (+8/-2, 3 linhas de guarda 1326-1328), 1 teste editado, 3 testes novos, spec de 3 mutantes, fragmento do changelog. Escopo bate com a E2.201.
- Mutantes: M1, M2 e M3 morreram; `--cobertura --base 4138445e` lista as três condições como `coberta`, nenhuma sem mutante. Q1 (A1) sobreviveu e é equivalente no veredito; não bloqueia.
- Os 13 testes de `test_forge_check_base_igual` e os 3 de `TesteEParecerSeparados` passam no head. A suíte inteira roda no CI do PR (sem PR ainda, sem check-run `bateria` do sha); o `forge-testes --vermelho` sem `--modulos` passou do prazo de 560 s aqui, por isso restringi a `test_forge_check_base_igual`, o módulo dos testes novos.
- Sem bug novo; nenhuma classe repetida (PA-7 conferido: AR-1 e AR-2 não se repetem, a lista de mutantes cobre as linhas mudadas).

## Provas
```
vermelho: base=4138445e23bd head=f35176b27d36 módulos=test_forge_check_base_igual (restrito por --modulos)
revertidos à base: bin/forge-check, changelog.d/v047-juncao-sem-vencer.md, docs/security/v047-juncao-sem-vencer.md
JuncaoSemBase.test_merge_limpo_da_develop_nao_vence · H=ok · B=falha · prova (asserção)
JuncaoSemBase.test_mudado_pela_branch_depois_do_parecer_vence · H=ok · B=falha · prova (asserção)
contagem: não prova (passa na base)=11; prova (asserção)=2
rc=0
```
```
forge-mutante: pedido=v047-juncao-sem-vencer rev=7babe7b84c38
M1 · morreu · bin/forge-check:1326
M2 · morreu · bin/forge-check:1328
M3 · morreu · bin/forge-check:1327
```
