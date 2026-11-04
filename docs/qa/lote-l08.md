---
tipo: qa
contrato: 1
pedido: versao-033
branch: melhoria/lote-l08
commit: 318a4374a16a4662fcb1504565535f0caf92dcf4
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-04
---
# QA: lote L08 (E7, E10, E12, E16, E19)

Código testado: a46eab7891b4f0c233e547b303dfa9ff6feee35b (revalidado duas vezes; a segunda sobre 79256408521daeb3c1ca57261b690614b1e12699; a primeira rodada foi sobre 874c89ec82a86840262c5c4a5b93eba48554eb5c). O `commit:` é o do teste novo do QA (tests/test_qa_lote_l08.py, commit separado do parecer, pelo E16), que só acrescenta teste ao código revisado.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E7 pr só aprova com conferida cobrindo o head | QaE7ConferenciaNoHead (ciclo, ref origin, linhas inválidas) | código depois da conferida; sha abreviado | passou |
| E7 x E16 teste do QA depois da conferida | test_commit_de_teste_do_qa_depois_da_conferida_exige_nova_conferencia | commit de teste fora de pareceres | passou (exige nova conferência; ver nota) |
| E10 pr --pr no head mesclado | QaE10PrMesclado (squash, parecer reprovado, número hostil) | branch apagada; número gigante | passou |
| E12 Desde da própria branch | QaE12DesdePorBranch (gerar --volta, entrega) | conferida de outra branch por último | passou |
| E16 teste e parecer separados | QaE16TesteEParecer (cita commit anterior, nome com ESC) | parecer em commit separado que cita o anterior | passou |
| E19 entrega ato-github | QaE19AtoGithub (merge/run, 2 briefs, PQ de commit, branch real) | nunca "nada a conferir" | passou |
| E7 volta 1 (falha fechada, branch pelo sha) | QaE7ConferenciaNoHead.test_ref_por_sha..., QaE7FecharReal | pedido ausente, sem Histórico, duas branches no mesmo sha | passou |
| L08-1 negação da conferida | test_linha_conferida_sem_marcador... (7 variantes) | linha negada, sem hora | passou |
| L08-2 tipo da PQ | test_pq_de_commit_em_maiuscula_reprova | (SHA) | passou |
| A9 promoção não cobra a conferência do head; branch de trabalho segue cobrada | QaA9Promocao (promover-homolog.py real) | pedido de release ausente; --base main e homolog | passou |

## Cenários e resultado real
- 7 módulos tocados: test_forge 507, test_mensagem_conferente 15, test_volta_por_delta 67, test_conferencia_base_dono 33, test_erros_no_brief 42, test_etapa_do_brief 65, test_isencoes 5: todos OK. Arquivo novo do QA: 15 testes OK.
- `bin/forge-mutante tests/mutantes/lote-l08-*.json`: 45 mortos, 0 sobreviventes, rc=0.
- `forge-mutante --cobertura --base 4f53bde` listou condições sem mutante; somei 5 mutantes do QA (spec fora do repositório): Q1 a Q4 mortos (ato-github filtro e rc, --pr ref e motivo); Q5 (bin/forge-check:5573, `squash = False`) sobreviveu e é equivalente: com origem base o escolhido[0] já é o Base-sha.
- Vermelho antes do verde: `forge-testes --vermelho 4f53bde` estourou o prazo (rc 124, sem veredito, não vale). Manual: o arquivo novo sobre a base 4f53bde falha 13 verificações em 15 testes; os que passam na base guardam fronteira (E16, número hostil, entrega do E12).
- Nota E7 x E16: com o fluxo do E16, o commit de teste do QA fica fora de "só pareceres e quadro", então o `pr` exige nova linha de conferida do head antes do merge; é o texto de R-PROVA, registrado para o Jarvis planejar a ordem.
- Bugs: docs/qa/bugs/L08-1-conferida-aceita-negacao.md e docs/qa/bugs/L08-2-ato-github-tipo-de-pq-sem-validar.md (baixa, contorno simples).

## Revalidação
Delta 874c89e..7925640, sobre o head 7925640 (teste e parecer trazidos por cherry-pick para a lote-l08).
- L08-1 fechado: o portão do E7 usa `ENTREGA_CONFERIDA` (data e hora, `entrega conferida`); "NÃO conferida", "- não: entrega conferida", "conferência não cumpriu; conferida" e data sem hora reprovam (7 variantes).
- L08-2 fechado: `(SHA)` reprova como prova de commit.
- E7: o `pr` por sha acha a branch única do sha; duas branches no mesmo sha, pedido ausente e pedido sem Histórico reprovam (falha fechada), também com o forge-fechar real (para no passo 1, sem `gh pr create` nem merge). O arquivo do QA ganhou 4 testes (19 no total) e passou a gravar o pedido no HOME (fixture nova).
- Módulos, um por vez: test_forge 509, test_mensagem_conferente 15, test_volta_por_delta 67, test_conferencia_base_dono 33, test_erros_no_brief 42, test_etapa_do_brief 65, test_isencoes 5, test_fechar 91, test_qa_lote_l08 19: todos OK.
- `bin/forge-mutante tests/mutantes/lote-l08-*.json`: 49 mortos, rc=0. Mutantes do QA sobre o delta (spec fora do repositório): R1 (ambiguidade, :728), R2 (regex, :708) e R3 (minúsculas, :1400) mortos; R4 (`[] if cod`) equivalente.
- Bugs L08-1 e L08-2: fechados.

## Revalidação (A9 do review, a46eab7)
Delta 7925640..a46eab7 (a promoção com head igual à ponta de `origin/develop` ou `origin/homolog` não é cobrada pela conferência do head). Teste novo do QA em commit próprio, 318a437 (E16), e o parecer cita esse commit.
- Cenário 1: `scripts/promover-homolog.py` real, com o `forge-check` real, num repositório descartável sem pedido algum no HOME: `--dry-run` e execução passam (rc 0, "valem contra a main", `pr create --base homolog --head develop`), sem conferida.
- Cenário 2: branch de trabalho (`melhoria/y`, fora da ponta da integração) com `--base main` e `--base homolog`: rc 1, `conferência: sem o pedido`, sem mensagem de promoção.
- Vermelho: o mesmo teste sobre c8dba87 (antes do fix) falha, com `pr: conferência: sem o pedido de "release-0.2.0"` na promoção; sobre a46eab7 passa.
- `-p test_promover_homolog.py` e `-p test_qa_lote_l08.py` juntos: 57 testes OK (36 e 21).
- `bin/forge-mutante tests/mutantes/lote-l08-*.json`, numa worktree limpa no head 3839cf9: 52 mortos, rc=0 (a rodada na worktree com o parecer do review ainda sem commit foi descartada pela ferramenta, "árvore mudou").
- Bugs abertos: nenhum. Parecer segue aprovado.
