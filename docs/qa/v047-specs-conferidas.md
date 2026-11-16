---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-specs-conferidas
commit: 48e5741594135d899e5a4d668eaf6a947aa5e09e
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-16
---
# QA: v047 specs de mutante conferidas (E2.215, AR-12; parecer E2.283)

Item: `forge-mutante --conferir --todas` e o alinhamento das specs de `tests/mutantes/` ao `de` da fonte atual. Sem especificação de UX nem contrato de API; as obrigações vêm do E2.215 do pedido e da mensagem do commit (CO-1 a CO-5 abaixo). Passada única no head 0064a82e (`R-QA`); a suíte inteira é o check-run `bateria` do mesmo sha no CI do PR, não rodada aqui.

## Achados
- A1 (recomendado) .githooks/pre-push:587 · M9 de lote-m8-hook sobrevive: sem `-I` na listagem do plano, o teste de módulo falso em bin/ continua verde. Guarda de isolamento sem prova; abrir cartão para o autor do pre-push (R-QA).
- A2 (recomendado) hooks/conformidade.py:2813 · M5 de fix-037-uniao-seg sobrevive: tirar o barrar da prova da suíte em palavras do Bash não derruba test_pasta_fora_de_projeto_tambem_recusa. Lacuna de teste em guarda de segurança; cartão (R-QA).
- A3 (recomendado) bin/forge-mutante:809 · M7 de vel-p1p10 sobrevive: `0 if valido else 2` virar `0` não derruba o teste de equivalente com trecho ausente ou repetido; o rc 2 do equivalente inválido fica sem prova. Cartão.
- A4 (recomendado) bin/forge-check:685 · M17 de pr-verde-lote-check-3 sobrevive: sem a guarda `desatualiza`, conflito em arquivo livre no merge simulado passa no test_conflito_em_arquivo_livre_nao_invalida. Cartão.
- A5 (recomendado) bin/forge-check:2183 · M10 e M16 de t6t3-mensagem sobrevivem (:2183 e :2186): filtrar só `conferida` e pegar a primeira linha em vez da última não quebram o teste do Desde. O teste não separa as duas linhas. Cartão.
- A6 (recomendado) bin/forge_governanca.py:766 · I155 de v0433-integracao-10 sobrevive: inverter o `tokens=-` na linha da negada não derruba tests.test_governanca; só a linha dos itens (468-469) é afirmada. Cartão.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| CO-1 `--conferir --todas` lê todas as specs do rev, não o diff; spec que envelheceu sai 1, alinhada sai 0 | ConferirTodas.test_spec_antiga_fora_do_diff_que_envelheceu_sai_1_e_a_alinhada_sai_0 (mutante T3) | trecho com 0 e com 2 ocorrências | passou |
| CO-2 entrada inválida sai 2: sem spec, rev que não é commit, spec inválida | ConferirTodas.test_sem_spec_rev_que_nao_e_commit_ou_spec_invalida_saem_2 (T1, T2) | vazio (sem spec), rev inexistente | passou |
| CO-3 `--todas` só com `--conferir`, sem `--base`, SPEC nem `--cobertura` | ConferirTodas.test_todas_vem_so_com_conferir_e_sem_base_spec_nem_cobertura (4 subcasos) | combinação proibida | passou |
| CO-4 catraca: spec fora do lugar só pode ser das pendentes; a lista só encolhe (AR-12) | ConferirTodas.test_toda_spec_do_forge_confere_com_a_fonte_fora_as_pendentes (T4 a T7) | mínimo de 400 specs (guarda contra suíte vazia); diferença nos dois sentidos | passou |
| CO-5 as specs alinhadas apontam o `de` que existe na fonte | `forge-mutante --conferir --todas` (abaixo) | trecho repetido (2 a 4 vezes) | 44 pendentes declaradas, 0 fora da lista |

## Cenários e resultado real
- Testes do item: `python3 -m unittest tests.test_forge_mutante.ConferirTodas` na raiz do clone: `Ran 4 tests ... OK`.
- Conferência real no head: `bin/forge-mutante --conferir --todas` sai rc 1 com 44 linhas, todas `o trecho aparece N vezes` (nenhuma `0 vezes`, ou seja nenhuma spec com trecho ausente). Batem com `tests/fixtures/mutantes-pendentes.txt` (52 linhas, 8 de comentário, 44 de mutante: 29 de trecho repetido e 15 das specs da `melhoria/v047-mutantes-velhos`). O teste da catraca confirma a igualdade.
- Mutantes declarados do item: `bin/forge-mutante tests/mutantes/v047-specs-conferidas.json`, rc 0, `T1` a `T7` `morreu` (bin/forge-mutante:693, 696, 708, 720, 724, 969, 970). A lista cobre as guardas novas do diff (`--todas`, sem spec, rev inválido, `isentas` zeradas, mensagem do print, exclusividade de opções).
- Vermelho antes do verde: `bin/forge-testes --vermelho e13aed85` (módulos tocados) estourou o prazo (rc 124, sem veredito; também com `--modulos test_forge_mutante --prazo 450`), e sem veredito não vale como vermelho. Substituto manual, numa cópia em `$TMPDIR`: `git archive 0064a82e` com o `bin/forge-mutante` da base e13aed85: `unittest tests.test_forge_mutante.ConferirTodas` deu `Ran 4 tests ... FAILED (failures=7)` (`unrecognized arguments: --todas`); no head, `OK`. O autor deve colar o veredito oficial do `forge-testes --vermelho` se o tiver.
- Os 7 sobreviventes do relatório (specs reduzidas ao mutante, mesma rev, `forge-mutante` direto): todos reproduzidos `sobreviveu`: lote-m8-hook:M9, vel-p1p10:M7, fix-037-uniao-seg:M5, v0433-integracao-10:I155, pr-verde-lote-check-3:M17, t6t3-mensagem:M10 e M16.
- Avaliação dos 7 (a pergunta do brief): não bloqueiam este item. O item só alinhou o `de` ao código atual; as specs antigas tinham o trecho ausente e provavam nada. O diff não toca o código dessas guardas nem seus testes, então não há regressão do item, e `R-REVIEW` reserva o bloqueio a defeito provado do diff. Os sobreviventes são lacuna de teste dos pedidos de origem, agora visível: viram cartão (A1 a A6; ordem sugerida A2, A1, A6 por serem guardas de segurança, isolamento e contagem). Aviso: depois deste alinhamento a spec afirma `testes` que não matam o mutante; até o cartão fechar, o placar por versão vai mostrá-los.
- Fora do que bloqueia: o E2.215 fala em alinhar ou retirar as specs velhas; 44 mutantes seguem pendentes por declaração, travados pela catraca (só encolhe). Aceitável como entrega parcial declarada.
- `forge-check docs`: ver Provas do relatório.

## Revalidação por delta (head 48e57415, E2.362)
`forge-check parecer delta` (0064a82e..48e57415, sem o que veio da develop) listou no domínio: `tests/fixtures/mutantes-pendentes.txt` e 3 specs (pr-verde-lote-check M8, v0442-mensagem M4, v047-hook-erro-libera-4 M28). Reteste:
- Spec a spec (o `forge-mutante` recusa pedidos diferentes numa rodada): pr-verde-lote-check M5 a M8 `morreu` rc 0; v0442-mensagem M4 a M7 `morreu` rc 0; v047-hook-erro-libera-4 até M32 `morreu` rc 0 (M28 `morreu` em tests/catraca.py:315). O `de` novo existe na fonte atual.
- `python3 -m unittest tests.test_forge_mutante.ConferirTodas`: `Ran 4 tests ... OK`.
- `bin/forge-mutante --conferir --todas`: rc 1, 31 linhas, igual às 31 de mutante da fixture (encolheu de 44 para 31: saíram as 15 de `melhoria/v047-mutantes-velhos`, entraram `hooks-corpus-rapido` M2 e M5, ambos `0 vezes` e declarados pendentes). Nenhuma spec fora da lista.
- A1 a A6 seguem abertos como cartão (recomendado), sem mudança: o delta não toca o código dessas guardas.
- Junção com a develop (589dc3f7, 0bf8603c): o remoto é ancestral do head, sem rebase.
Parecer mantido: aprovado.
