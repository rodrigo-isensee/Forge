---
tipo: qa
contrato: 1
pedido: k164-mesma-base
branch: melhoria/k164-intervalo
commit: 91f798c7177f794da79a66b3b97cd9e385efc0a0
parecer: aprovado
revisor: forge:qa-engineer
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-31
---
# QA: k164-mesma-base (E2, branch melhoria/k164-intervalo)

Escopo: `git diff 8c07b4448aec..91f798c7177f`. Código: 2 linhas em bin/forge-check (gramática do achado e ramo do intervalo invertido), 15 de teste em tests/test_forge.py; spec de mutação, fragmento e pareceres de review e segurança. Pedido de correção sem especificação de UX: a obrigação vem da E2 do pedido (o achado aceita `arquivo:a-b`; invertido ou malformado segue recusado).

## Achados
- A1 (recomendado) bin/forge-check:1283 · intervalo `5-5` aceito (provado) mas sem teste: trocar `>` por `>=` sobrevive à suíte e à spec; somar `5-5` aceito ao teste e um mutante M5 (mesma proposta do review R2)
- A2 (recomendado) bin/forge-check:1283 · int() sem teto de dígitos: `1-` seguido de 5000 noves dá ValueError (traceback), falha fechada; limitar dígitos na regex (mesmo achado A1 da segurança)

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E2: intervalo a-b aceito e copiado inteiro no brief | VoltaComRecomendacao.test_achado_com_intervalo_de_linhas_e_aceito_e_copiado_inteiro | intervalo válido 3-5 e 10-12 | passou (vermelho na base) |
| E2: invertido recusado | VoltaComRecomendacao.test_intervalo_malformado_ou_invertido_e_recusado (9-3) | início maior que fim | passou (M2 e M3 morrem) |
| E2: malformado recusado | idem (`3-`, `-3`, `3-5-7`, `3--5`, `a-b`) | um hífen só, dois números | passou (M4 morre) |
| E2: forma antiga `arquivo:n` segue valendo | 78 testes de VoltaComRecomendacao e test_volta_por_delta | uma linha só | passou |
| Borda `5-5`, dígitos longos | execução manual do analisador | igualdade; tamanho | `5-5` aceito; dígitos longos: ValueError (A2) |

## Cenários e resultado real
- Vermelho antes do verde (`bin/forge-testes --vermelho 8c07b44`, rc 0): `vermelho: base=8c07b4448aec head=91f798c7177f`; revertidos à base: bin/forge-check, changelog.d/k164-intervalo.md, docs/reviews/k164-mesma-base.md, docs/security/k164-mesma-base.md. Linhas: `test_achado_com_intervalo_de_linhas_e_aceito_e_copiado_inteiro · H=ok · B=falha · prova (asserção)`; `test_intervalo_malformado_ou_invertido_e_recusado · H=ok · B=ok · não prova (passa na base)`; contagem: prova=1, não prova=2312, pulado=28. O segundo teste só guarda regressão (a base já recusava esses casos); quem o prova são M2 a M4.
- Suíte do escopo: `python3 -m unittest tests.test_forge.VoltaComRecomendacao tests.test_volta_por_delta`: 78 testes, OK (duas rodadas).
- Mutação: `bin/forge-mutante tests/mutantes/k164-intervalo.json` (rev 91f798c7177f): M1 morreu (1251), M2 morreu (1283), M3 morreu (1283), M4 morreu (1251), rc 0. `--cobertura --base 8c07b444`: rc 0, `coberta · bin/forge-check:1283 · M2, M3`. Conferência da lista contra o diff: as duas linhas de guarda mudadas (1251 gramática, 1283 ramo) têm mutante; o único furo é a fronteira de igualdade (A1, recomendado: o requisito não a exige).
- Sem shell nem hook tocados; sem interface, acessibilidade não se aplica.

## Parecer
Aprovado. Cumpre a M14 (agents/tech-lead.md:19): um comportamento só (o intervalo no achado), 21 linhas de código e teste, nada em hooks/. Nenhum bug aberto; A1 e A2 são recomendações que não devolvem (R-REVIEW).
