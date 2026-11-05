---
tipo: qa
contrato: 1
pedido: versao-033
branch: melhoria/lote-l08
commit: df0a0e98d3d3b65efeea5086787ec328a9745081
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-05
---
# QA: lote L08 (E7, E10, E12, E16, E19)

Código testado: a46eab7891b4f0c233e547b303dfa9ff6feee35b (revalidado duas vezes; a segunda sobre 79256408521daeb3c1ca57261b690614b1e12699; a primeira rodada foi sobre 874c89ec82a86840262c5c4a5b93eba48554eb5c). O `commit:` é o último commit de código revisado (df0a0e9, o último commit de teste do QA, que só mexe em specs de mutantes sobre o código testado 3625656).

## Achados
- A1 (recomendado) docs/qa/lote-l08.md:1 · nenhum achado bloqueante aberto; o A1 antigo (spec e7b velha, L08-3) está fechado

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
| E7 e E11 pr só conta os pareceres da própria branch | QaPareceresDaBranch (3) | parecer alheio desatualizado ou reprovado; falta o próprio (revisão e QA) | passou |

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

## Revalidação (04437d1, módulo do forge-fechar real)
O autor moveu `FecharComOForgeCheckReal` para tests/test_fechar_forge_check_real.py e o tests/test_qa_lote_l08.py passou a importá-la dali (única mudança no arquivo do QA; por isso o `commit:` é 04437d1, que contém o arquivo de teste atual, regra E16). A classe movida não mudou além da referência ao cenário `Fechar` e ao caminho do `forge-check`, e os dois testes do QA que a usam (pedido sem Histórico e duas branches no mesmo sha, parada no passo 1) seguem cobrindo o mesmo. `-p test_qa_lote_l08.py` e `-p test_fechar_forge_check_real.py` juntos: 23 testes OK. Parecer segue aprovado, sem bugs abertos.

## Revalidação (083a959: pareceres só da própria branch)
Teste novo do QA em commit próprio, 5ac531f (E16), que o `commit:` cita; código testado 083a959.
- Cenário de ponta a ponta com o `forge-check` real num repositório descartável: branch com parecer próprio aprovado e pareceres alheios (de outra branch, mais recentes, desatualizados, aprovados ou reprovados): o `pr` da branch passa e não cita o alheio. Sem os pareceres próprios, ou sem só o de QA, reprova com `sem parecer da branch "melhoria/x" para o pedido p1`.
- Vermelho: sobre 04437d1 (antes do fix) 2 dos 3 testes falham (os de falta do parecer próprio); o terceiro guarda a fronteira.
- `-p test_qa_lote_l08.py`: 24 testes OK.
- `bin/forge-mutante tests/mutantes/lote-l08-*.json` numa worktree limpa em 5ac531f: 54 mortos e `M36 · controle vermelho`, rc=2. Defeito L08-3 (docs/qa/bugs/L08-3-spec-de-mutantes-e7b-velha.md): a spec lote-l08-e7b.json cita `tests.test_fechar.FecharComOForgeCheckReal`, movido por 04437d1 para tests/test_fechar_forge_check_real.py, e, com o caminho corrigido, M36 sobrevive porque o 1d50bea tornou redundante o `branch_do_sha` dentro de `conferencia_do_head`. A correção é do autor (spec); o parecer volta a aprovado quando a rodada der rc=0.

## Revalidação 3625656 (4 regressões do pre-push)
Head testado c4b582d (depois de 3625656 só há pareceres). Delta: `git diff 91d52dc 3625656` (bin/forge-check `conferir=False` só no escopo da merge-integracao, apoio_conferida, test_conf_escopo, test_estado_da_branch).
- Suíte inteira, `.githooks/pre-push --suite` (log /tmp/claude-0/suite.log): 2612 testes, 4 processos, `FAILED (failures=6, errors=1, skipped=30, guarda=2)`. Os 7 itens são de ambiente (pid namespace) em test_hooks (4 subtestes de test_fixtures `agentes/inicio-sem-par-grava-pid-da-sessao`, `reserva-grava-pid-e-sessao`, `inicio-casa-reserva-da-sessao-e-mantem-pid`, `inicio-so-casa-reserva-da-mesma-sessao`; `test_registro_de_agente_solta_so_com_prova_de_sessao_morta`) e test_atualizar (`test_ancestral_chamado_claude_recusa_mesmo_com_pty_e_sem_variavel`, forge-atualizar e forge-voltar-versao). Prova: `tests.test_hooks tests.test_atualizar` numa cópia de origin/develop (b45e40a) dão os mesmos 7 e mais um de tempo (`test_muitos_heredocs...`), `failures=7, errors=1`. Nenhum teste do L08 caiu; test_conf_escopo e test_estado_da_branch passaram. O contador `guarda=2` não traz detalhe no log.
- As 4 regressões: o escopo da merge-integracao lê só os pareceres (`conferir=False`, :1396), enquanto o `pr` da linha de comando, o `brief gerar` e o forge-fechar seguem cobrando a conferência (padrão True, :657); test_estado_da_branch grava a conferida do head; apoio_conferida usa `sem_manutencao`. O teste novo `test_escopo_le_so_os_pareceres_e_o_pr_segue_cobrando_a_conferencia` cobre as duas metades.
- Mutantes: spec nova tests/mutantes/lote-l08-escopo.json (M60 `conferir=False` do escopo e M61 padrão `conferir=True`, ambos mortos pelo teste novo). O fix mudou as linhas de M29 e M30 (tests/mutantes/lote-l08-e7.json), que saíram inválidas (rc=2); atualizei o trecho `de` (df0a0e9). `bin/forge-mutante tests/mutantes/lote-l08-*.json` no head df0a0e9: 57 mortos, M36 equivalente, rc=0. As linhas de guarda mudadas pelo fix (:657, :1396 e as duas de `conferir else []`, cobertas por M29 e M30) têm mutante.
- Vermelho antes do verde: não rodei `forge-testes --vermelho`; o review mutou o `conferir=False` e o teste novo caiu, e M60 e M61 mortos aqui valem como a prova de que o teste falha sem a implementação.
- Bugs abertos: nenhum (L08-1, L08-2 e L08-3 fechados). Veredito: aprovado.

## Revalidação df0a0e9 (spec de mutantes)
Delta `c4b582d..df0a0e9`, só tests/mutantes/: lote-l08-e7.json (M29 e M30 com o `conferir` do fix 3625656) e lote-l08-escopo.json (M60 e M61, sem o M62 duplicado). O `commit:` é o do último commit de teste (E16); depois dele só há pareceres (8df8e17, 12a5d19, 3991a93). Nenhum código de produção mudou.
- `bin/forge-mutante tests/mutantes/lote-l08-*.json` no head 3991a93, árvore limpa: rc=0, todos os mutantes mortos (M60 em bin/forge-check:1396 e M61 em :657 mortos pelo teste novo do escopo; M29 e M30 mortos), M36 equivalente declarado.
- Rodada do QA (forge-mutante, head 6455af7 com rev=6455af7c9c11, árvore limpa, rc=0), saída inteira:

```
forge-mutante: pedido=lote-l08 rev=6455af7c9c11 spec=14899b5332de77dd3da6bddcb45f33aaf20358e3016ff8e93519fc379d7c87b4 spec=814c0263fb9d68b6c2fb5e22280e206023883821f34c8d458757c7137fa7b350 spec=46e4e5e3530fe3dfdc7178a33b488786d44839e4b87b181b539f73bb0ac585d5 spec=a74640e2b035c0be6d8aae928d2025fb6f94502efddbb235c8fcd806a711758b spec=74148699a9764b20516e570080fabb6b262defe8eab30f7489d2db262168d8e2 spec=c288327e9d019aceb8ad602fa2f7dcf660db074c99ea9ae600e7ecc85074d023 spec=ca1925ddc1fc79542a738231d8b6400e8e2b739e20ef22b8e3b08d6e5ca59dda spec=3a2f30750c33e1d589e46c2edf761244120dfc7536524165d238a322aadf34df
M1 · morreu · bin/forge-check:878
M2 · morreu · bin/forge-check:876
M3 · morreu · bin/forge-check:876
M4 · morreu · bin/forge-check:876
M5 · morreu · bin/forge-check:880
M6 · morreu · bin/forge-check:869
M7 · morreu · bin/forge-check:860
M8 · morreu · bin/forge-check:6497
M9 · morreu · bin/forge-check:902
M10 · morreu · bin/forge-check:1117
M11 · morreu · bin/forge-check:1117
M12 · morreu · bin/forge-check:1126
M13 · morreu · bin/forge-check:1129
M14 · morreu · bin/forge-check:1850
M15 · morreu · bin/forge-check:1975
M16 · morreu · bin/forge-check:5625
M17 · morreu · bin/forge-check:1118
M18 · morreu · bin/forge-check:941
M19 · morreu · bin/forge-check:940
M20 · morreu · bin/forge-check:892
M38 · morreu · bin/forge-check:1436
M39 · morreu · bin/forge-check:1441
M40 · morreu · bin/forge-check:1455
M41 · morreu · bin/forge-check:1455
M42 · morreu · bin/forge-check:1455
M43 · morreu · bin/forge-check:1456
M44 · morreu · bin/forge-check:1462
M45 · morreu · bin/forge-check:1465
M46 · morreu · bin/forge-check:1484
M47 · morreu · bin/forge-check:6347
M48 · morreu · bin/forge-check:1426
M49 · morreu · bin/forge-check:1481
M21 · morreu · bin/forge-check:770
M22 · morreu · bin/forge-check:770
M23 · morreu · bin/forge-check:733
M24 · morreu · bin/forge-check:727
M25 · morreu · bin/forge-check:761
M26 · morreu · bin/forge-check:766
M27 · morreu · bin/forge-check:763
M28 · morreu · bin/forge-check:712
M29 · morreu · bin/forge-check:668
M30 · morreu · bin/forge-check:682
M31 · morreu · bin/forge-check:702
M32 · morreu · bin/forge-check:704
M33 · morreu · bin/forge-check:711
M34 · morreu · bin/forge-check:713
M35 · morreu · bin/forge-check:715
M36 · equivalente · bin/forge-check:758
M37 · morreu · bin/forge-check:745
M50 · morreu · bin/forge-check:678
M51 · morreu · bin/forge-check:690
M52 · morreu · bin/forge-check:691
M56 · morreu · bin/forge-check:667
M60 · morreu · bin/forge-check:1396
M61 · morreu · bin/forge-check:657
M53 · morreu · bin/forge-check:918
M54 · morreu · bin/forge-check:903
M55 · morreu · bin/forge-check:681
contagem (somada pelo QA a partir da saída; o forge-mutante não imprime linha de contagem): 58 mutantes · 57 morreu · 1 equivalente (M36) · 0 sobreviveu · 0 sem veredito
```

- Bugs abertos: nenhum. Veredito: aprovado.
