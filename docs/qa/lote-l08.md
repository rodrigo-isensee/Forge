---
tipo: qa
contrato: 1
pedido: versao-033
branch: melhoria/lote-l08
commit: 1ab191ac8a892d03f6a0d2cc308a95070fccd503
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 2
aceite_usuario: sim
data: 2026-11-04
---
# QA: lote L08 (E7, E10, E12, E16, E19)

Código testado: 874c89ec82a86840262c5c4a5b93eba48554eb5c. O `commit:` é o do teste novo do QA (tests/test_qa_lote_l08.py, commit separado do parecer, pelo E16), que só acrescenta teste ao código revisado.

## Achados
- A1 (recomendado) bin/forge-check:907 · L08-1: o portão do E7 aceita linha negada (NÃO conferida) por usar CONFERIDA sem ancorar "entrega"
- A2 (recomendado) bin/forge-check:904 · L08-2: ato-github não valida o tipo da PQ; (SHA) em maiúscula não conta como prova de commit

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E7 pr só aprova com conferida cobrindo o head | QaE7ConferenciaNoHead (ciclo, ref origin, linhas inválidas) | código depois da conferida; sha abreviado | passou |
| E7 x E16 teste do QA depois da conferida | test_commit_de_teste_do_qa_depois_da_conferida_exige_nova_conferencia | commit de teste fora de pareceres | passou (exige nova conferência; ver nota) |
| E10 pr --pr no head mesclado | QaE10PrMesclado (squash, parecer reprovado, número hostil) | branch apagada; número gigante | passou |
| E12 Desde da própria branch | QaE12DesdePorBranch (gerar --volta, entrega) | conferida de outra branch por último | passou |
| E16 teste e parecer separados | QaE16TesteEParecer (cita commit anterior, nome com ESC) | parecer em commit separado que cita o anterior | passou |
| E19 entrega ato-github | QaE19AtoGithub (merge/run, 2 briefs, PQ de commit, branch real) | nunca "nada a conferir" | passou |

## Cenários e resultado real
- 7 módulos tocados: test_forge 507, test_mensagem_conferente 15, test_volta_por_delta 67, test_conferencia_base_dono 33, test_erros_no_brief 42, test_etapa_do_brief 65, test_isencoes 5: todos OK. Arquivo novo do QA: 15 testes OK.
- `bin/forge-mutante tests/mutantes/lote-l08-*.json`: 45 mortos, 0 sobreviventes, rc=0.
- `forge-mutante --cobertura --base 4f53bde` listou condições sem mutante; somei 5 mutantes do QA (spec fora do repositório): Q1 a Q4 mortos (ato-github filtro e rc, --pr ref e motivo); Q5 (bin/forge-check:5573, `squash = False`) sobreviveu e é equivalente: com origem base o escolhido[0] já é o Base-sha.
- Vermelho antes do verde: `forge-testes --vermelho 4f53bde` estourou o prazo (rc 124, sem veredito, não vale). Manual: o arquivo novo sobre a base 4f53bde falha 13 verificações em 15 testes; os que passam na base guardam fronteira (E16, número hostil, entrega do E12).
- Nota E7 x E16: com o fluxo do E16, o commit de teste do QA fica fora de "só pareceres e quadro", então o `pr` exige nova linha de conferida do head antes do merge; é o texto de R-PROVA, registrado para o Jarvis planejar a ordem.
- Bugs: docs/qa/bugs/L08-1-conferida-aceita-negacao.md e docs/qa/bugs/L08-2-ato-github-tipo-de-pq-sem-validar.md (baixa, contorno simples).
