---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-mutantes-sobreviventes
commit: f39e95a6ee8b80067bcc90141c1a04802a0f0a0a
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-16
---
# QA: v047 (E2.547, mutantes sobreviventes)

Parecer completo (a branch não tinha parecer de QA), contra a develop (4068c807). Código testado no `Revisar-sha` f39e95a6; o head e7f1c2e4 só acrescenta o ajuste de formato do parecer de review (`git diff f39e95a6 HEAD`: um arquivo em `docs/reviews/`). Sem especificação de UX: as obrigações são as do E2.304 (matar os mutantes sobreviventes fix-037-uniao-seg:M5, vel-p1p10:M7, v0433-integracao-10:I155, pr-verde-lote-check-3:M17, t6t3-mensagem:M10 e M16), mais o conserto do M8 de pr-verde-lote-check (E2.530).

## Achados
- A1 (recomendado) tests/mutantes/vel-p1p10.json:33 · M3 (controle vermelho, rc 2): o teste citado, `ValidacaoDaSpec.test_equivalente_sem_justificativa_ou_com_testes_e_invalido`, foi renomeado (hoje `..._com_testes_mal_formados_e_invalido`, test_forge_mutante.py:139). Igual na develop; fora do diff. Vira cartão (AR-12).
- A2 (recomendado) tests/mutantes/fix-037-uniao-seg.json:74 · M8 sobrevive no head e na develop (hooks/conformidade.py:2811); não é um dos seis do item. Vira cartão.
- A3 (recomendado) tests/mutantes/v0433-integracao-10.json:6 · I145 e I158 sobrevivem (iguais na develop) e vários outros saem inválidos (erro de carga); não são do item. Vira cartão.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| fix-037-uniao-seg:M5 morre | `test_conformidade_verde.ProvaDaSuite` (linha que o hook não lê, com e sem a prova, tech-lead e sem papel) | linha ilegível com a prova recusa, sem a prova libera | passou; M5 sobrevivia na develop, morre no head (M6 também) |
| vel-p1p10:M7 morre | `Execucao.test_equivalente_com_o_trecho_ausente_ou_repetido_sai_2` (com mutante que morre + equivalente inválido) | `de` ausente e `de` repetido | passou; M7 morreu |
| v0433-integracao-10:I155 morre | `EsperaPorPortaoETokens` (tokens do pedido, com e sem fonte) | tokens=40 vs tracinho (não None) | passou; I155 sobrevivia na develop, morreu no head |
| pr-verde-lote-check-3:M17 morre | `PrAposMergeDaBase.test_conflito_em_arquivo_livre_nao_invalida` (fixture com `src/x.txt` fundindo limpo) | conflito só no arquivo livre, merge simulado roda | passou; M17 e M18 morreram |
| t6t3-mensagem:M10 e M16 morrem | `MensagemPelaEtapaDoBrief.test_desde_real_e_a_linha_mais_recente_valida_com_commits_da_branch` | 2 conferidas, dono depois/antes da conferida, só dono | passou; M10 e M16 morreram (16 de 16) |
| E2.530: M8 de pr-verde-lote-check volta a casar a linha que o mata | `test_portao_diff_proprio...test_d4_so_o_fragmento...` | `de` com `# D4; E1g; E2.252` casa 1 vez | passou; M8 morreu em bin/forge-check:1785 |

## Cenários e resultado real
- Diff `origin/develop..HEAD`: 5 arquivos de teste (+39 linhas), 2 specs de mutantes, fragmento do changelog e AR-12. Nenhum arquivo de produção mudou: o escopo bate com o E2.304 e o E2.530.
- Testes dos arquivos tocados, no clone, sem `-I`: `test_conformidade_verde` 11 OK; `test_forge_mutante` 124 OK; `test_governanca` 50 OK; `test_mensagem_conferente` 18 OK; `test_forge.PrAposMergeDaBase` 12 OK. Suíte inteira: CI do PR (sem PR ainda, sem check-run `bateria`).
- Especificação conferida: `bin/forge-mutante --conferir --base 4068c807`: "conferidas: o trecho de cada spec do diff está no lugar" (rev e7f1c2e4).
- Mutantes das duas specs do diff: `pr-verde-lote-check` M1 a M8 morreram, rc=0 (M8 em bin/forge-check:1785); `t6t3-mensagem` M1 a M16 morreram, rc=0. `pr-verde-lote-check-3` M17 e M18 morreram, rc=0.
- Vermelho antes do verde: o item só adiciona testes a código que não muda, então o "vermelho" é o mutante vivo na develop. Prova: na develop (cópia de `git archive 4068c807`), `fix-037-uniao-seg` M5, M6 e `v0433-integracao-10` I155 **sobrevivem**; no head, M5, M6 e I155 **morrem**. `forge-testes --vermelho 4068c807` estourou o prazo de 580 s (rc=124, sem veredito: não vale como vermelho); a prova acima o substitui.
- Fora do item (develop igual): ver A1 a A3.

## Provas
```
bin/forge-mutante --conferir --base 4068c807136bfa5b9ad9eeb05f25113d948c2680
base=4068c807136bfa5b9ad9eeb05f25113d948c2680 mb=4068c807136bfa5b9ad9eeb05f25113d948c2680 rev=e7f1c2e410765057e93662d87fd73062f52cd70f
conferidas: o trecho de cada spec do diff está no lugar

forge-mutante: pedido=pr-verde-lote-check rev=e7f1c2e41076 -> M1..M8 morreu (M8 · bin/forge-check:1785), rc=0
forge-mutante: pedido=t6t3-mensagem rev=e7f1c2e41076 -> M1..M16 morreu (M10 · bin/forge-check:2191, M16 · bin/forge-check:2194), rc=0
forge-mutante: pedido=pr-verde-lote-check (spec -3) -> M17 · morreu · bin/forge-check:687; M18 · morreu · bin/forge-check:3027, rc=0
head:    fix-037-uniao-seg M5 morreu (conformidade.py:2813), M6 morreu (2819); v0433-integracao I155 morreu (forge_governanca.py:766)
develop: fix-037-uniao-seg M5 sobreviveu, M6 sobreviveu, M8 sobreviveu; v0433-integracao I155 sobreviveu, I145 sobreviveu, I158 sobreviveu
```
