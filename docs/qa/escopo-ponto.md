---
tipo: qa
contrato: 1
pedido: v0457
branch: melhoria/escopo-ponto
commit: ba35957368421e2e1803e48011839eaa83454463
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-12
---
# QA: escopo-ponto (E23.35)

Diff 8b5a44d5..ba359573: bin/forge-check (cinco defeitos da conferência de entrega, E23.17 a-c e E23.36 d-e), 2 módulos de teste e 3 specs de mutantes. Sem especificação de UX nem contrato de API: as obrigações são os cinco defeitos do pedido.

## Obrigação, teste, resultado
| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| (a) ponto inicial do caminho fica | PontoInicial.test_caminho_com_ponto_inicial_e_pontuacao_final | `.github/` com pontuação final | verde; vermelho na base |
| (b) volta herda o escopo dos briefs anteriores | VoltaNaMesmaBranch (5 testes) | outra branch, outro pedido, outra etapa não entram | verde; 2 provam na base, 3 negativos passam na base de propósito |
| (c) pareceres pelo pedido do brief | PareceresPeloPedido (3) | id diferente do nome do arquivo; outro pedido segue reprovando | verde; 2 provam na base |
| (d) parecer de portão da branch é anexo | ParecerDoPortao (5) | outra branch, outro pedido, sem frontmatter, sem commit revisado | verde; 1 prova na base; ver A1 |
| (e) intervalo parte do merge-base | MergeDaBaseDepoisDoBrief (4) | head já na develop, base fora da branch, arquivo da develop mudado | verde; 1 prova na base |

## Provas
- Classes rodadas uma por vez: PontoInicial 1 OK, VoltaNaMesmaBranch 5 OK, PareceresPeloPedido 3 OK, ParecerDoPortao 5 OK, MergeDaBaseDepoisDoBrief 4 OK.
- Vermelho: `forge-testes --vermelho 8b5a44d5 --modulos tests.test_selo_e_entrega,tests.test_conf_escopo --prazo 500` abre com `vermelho: base=8b5a44d5ffd5 head=ba3595736842`, bin/forge-check revertido à base; contagem: `não prova (passa na base)=59; prova (asserção)=7`; nenhum teste cai no HEAD. Os 7 que provam cobrem os 5 defeitos; os negativos passam na base por serem proteção do que não muda.
- Mutantes: `forge-mutante` das 3 specs, 17 mutantes (M1 a M17), todos `morreu`, rc=0. `--cobertura --base 8b5a44d5` lista as 11 linhas de condição mudadas como cobertas.
- Falha de ambiente: a primeira rodada de `--vermelho` sem `--modulos` estourou o prazo de 590 s sob load 14 a 22 (sem veredito, não vale como vermelho); repetida restrita aos dois módulos.

## Achados
- A1 (bloqueante) bin/forge-check:2325 · mutante sobrevivente: trocar `fm.get("tipo") == tipo` por True, ou `fm.get("parecer") in ("aprovado", "reprovado")` por True, mantém ParecerDoPortao 5/5 OK (cópia descartável); M11 só tira o `branch ==`. Falta teste e mutante para tipo e parecer.
