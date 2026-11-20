---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-recomendado-restos
commit: 985cf4e3dba073c6c6eaca14195a4ac94f4575da
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-20
---
# QA: v0479-recomendado-restos

Diff 004ce869..985cf4e3: 5 arquivos, só texto (agente devops, modelo devops, R-REVIEW, fragmento de changelog) e o teste `tests/test_achado_teto_doc.py`. Sem código de produção nem guarda executável; sem mutante a declarar.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Modelo e agente de devops dizem que o recomendado vira cartão | `RecomendadoViraCartao.test_cada_texto_que_decide_a_volta_traz_a_regra` | mínimo de 14 textos (guarda contra suíte vazia) | passou; cai na base |
| R-REVIEW: o `recomendado` de segurança volta ao autor | `test_nenhum_texto_manda_corrigir_antes_o_recomendado_de_review_ou_qa` | nenhum texto de review/QA manda corrigir antes | passou; cai na base |

## Cenários e resultado real
Módulo tocado, `python3 -I -m unittest discover -s tests -p test_achado_teto_doc.py`: 8 testes, OK. Suíte inteira: só no CI do PR, não rodada aqui.

Vermelho (`bin/forge-testes --vermelho 004ce869d641ca62394d705c4453d8a014002f15 --modulos test_achado_teto_doc`):
```
vermelho: base=004ce869d641 head=985cf4e3dba0 módulos=test_achado_teto_doc (restrito por --modulos)
revertidos à base: agents/devops-engineer.md, changelog.d/v0479-recomendado-restos.md, docs/regras/R-REVIEW.md, templates/projeto/docs/devops/_modelo.md
mantidos no HEAD: tests/test_achado_teto_doc.py
...test_cada_texto_que_decide_a_volta_traz_a_regra · H=ok · B=falha · prova (asserção)
...test_nenhum_texto_manda_corrigir_antes_o_recomendado_de_review_ou_qa · H=ok · B=falha · prova (asserção)
contagem: não prova (passa na base)=6; prova (asserção)=2
```
Os 6 que passam na base são testes antigos do módulo, não novos.
