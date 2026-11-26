---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-d2-no-brief
commit: 7cacc94c8fe74c3fba5cd9368d5c388d1007b910
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 1
bugs_baixos: 0
data: 2026-11-26
---
# QA: v0481 (E14.70, #903, D2-NO-BRIEF, 1ª rodada completa)

Clone `/root/.forge-contrib/wt/v0481-d2-no-brief-qa`, head `7cacc94c8fe7` (merge da develop com o #885, sem conflito). Diff lido contra o merge-base `34ab6714` (9 arquivos: `bin/forge-check`, `bin/forge_pronto.py`, 3 módulos de teste, 2 specs de mutante novas, 1 editada, fragmento do changelog). Obrigações (a ordem do dono D2-NO-BRIEF, E14.51, e as regras PR-TITULO-DO-BRIEF e PRONTO-BASE-VELHA citadas no código): (1) o brief de código do Forge cobra o D2; (2) a conferência da entrega roda o pronto e reprova fora do rc 0; (3) título de PR com o cabeçalho do brief reprova; (4) branch nascida antes da última marca da base recebe uma linha só.

- ci: 7cacc94c8fe74c3fba5cd9368d5c388d1007b910 verde

## Achados
- A1 (bloqueante) bin/forge-check:10452 · Sem worktree (`pasta` None) o D2 não roda e não reprova: a entrega cumpre com D2 vermelho se ninguém passa --worktree (a cópia do autor é clone); a ordem do dono diz que ela volta. Reprovar como o :10499 faz.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| (1) brief de código do Forge traz a PQ do D2; fora do Forge não | `test_pre_envio_brief.Gerar.test_codigo_do_forge_manda_rodar_o_d2_e_fora_do_forge_nao` (M8) | dentro x fora do Forge | passou |
| (2) pronto rc 0 prova; rc 1 e rc 2 reprovam com a última linha; prazo estourado reprova | `test_forge_pronto.ProvaDoPronto` (3 testes; M9 a M13) | rc 0, 1, 2, TimeoutExpired | passou |
| (2) conferência real na cópia do Forge: rc 1 não cumpre e nada é gravado | `test_selo_e_entrega.Entrega.test_d2_vermelho_na_copia_do_forge_nao_cumpre` (M12) | rc 1 de ponta a ponta, entrega não gravada | passou |
| (2) sem worktree: reprova | nenhum; o teste existente afirma o contrário (`ProvaDoPronto.test_so_leitura_sem_worktree_e_fora_do_forge_nao_rodam`, caso `pasta=None`, `reprova=False`) | pasta None | falhou (A1) |
| (2) `--so-leitura` e fora do Forge só informam | mesmo teste, casos `so_leitura` e pasta sem plugin.json | quem confere não roda código da branch | passou |
| (3) título com `E<n> (papel):` ou `[branch ` reprova; Conventional Commits, vazio e None passam | `TituloDoPr` (2 testes), `TituloNoCmdPronto` (M7, M6) | título vazio/None, `E3` citado no meio | passou |
| (4) marca nova na base depois do nascimento: uma linha, sem rodar os passos; base trazida não avisa; sem manifesto no nascimento não compara | `BaseVelha` (3 testes; M1 a M5) | versões iguais, manifesto ausente | passou |
| `pr_da_branch` pede `title` ao gh (spec editada) | M18 e M19 de `v0474-h1-ferramenta-3.json` | `corpo` falso não pede | passou |

## Cenários e resultado real
- **CI** (PARECER-LE-O-CI): check-runs do sha exato `7cacc94c`, lidos por `gh api repos/.../commits/7cacc94c.../check-runs`. Verdes: suíte 3.12 e 3.14 (partes 1 a 5), bateria (passos), bateria (verificações longas), bateria (python 3.14), instalação 3.14, teto de pulados 3.12 e 3.14, árvore já provada. Vermelhos: `bateria (pareceres)` (espera os pareceres), `bateria` (agregada, só por ele) e `catraca` (o parecer de segurança da mesma rodada diz que é R-CONFORMIDADE: `bin/forge-check` pede o rótulo afrouxa-regra do dono). Não li o log dos três: o download do log sai do sandbox (blob.core.windows.net negado) e as anotações só trazem "exit code 1"; a causa vem do parecer de segurança e da regra dos três, não de log lido por mim.
- **Módulos tocados, no head**: `python3 -m unittest tests.test_selo_e_entrega.Entrega.test_d2_vermelho_na_copia_do_forge_nao_cumpre` OK; `test_forge_pronto` e `test_pre_envio_brief` passam em H (coluna H=ok em todos os testes da rodada de vermelho). A suíte inteira não foi rodada à mão.
- **Vermelho antes do verde** (`bin/forge-testes --vermelho 34ab6714cbc13e41c35907b13cb3a6b2b71d9688 --modulos test_forge_pronto,test_pre_envio_brief`):
  ```
  vermelho: base=34ab6714cbc1 head=7cacc94c8fe7 módulos=test_forge_pronto,test_pre_envio_brief (restrito por --modulos)
  revertidos à base: bin/forge-check, bin/forge_pronto.py, changelog.d/v0481-d2-no-brief.md
  BaseVelha.test_marca_depois_do_nascimento_... · H=ok · B=falha · prova (asserção)
  ProvaDoPronto (4 testes) · H=ok · B=erro · prova (API ausente)
  TituloDoPr (2 testes) · H=ok · B=erro · sem veredito
  TituloNoCmdPronto.test_pr_aberto_com_o_titulo_do_brief_reprova · H=ok · B=falha · prova (asserção)
  Gerar.test_codigo_do_forge_manda_rodar_o_d2_e_fora_do_forge_nao · H=ok · B=falha · prova (asserção)
  contagem: não prova (passa na base)=49; prova (API ausente)=4; prova (asserção)=3; sem veredito=2
  ```
  O veredito geral saiu 2 pelos dois `TituloDoPr`: na base o erro é `TypeError` (o parâmetro `titulo` não existe), que a ferramenta não conta como prova; os outros 7 provam. O teste novo de `test_selo_e_entrega` ficou fora dessa rodada (o módulo é lento e a rodada com ele não terminou no meu prazo); recuo por cópia em `$TMPDIR` com `bin/` da base e `tests/` do head: `test_d2_vermelho_na_copia_do_forge_nao_cumpre` cai (`FAILED (failures=1)`); no head passa.
- **Mutantes** (`bin/forge-mutante tests/mutantes/v0481-d2-no-brief.json tests/mutantes/v0481-d2-no-brief-2.json --processos 4`, rc 0): M1 a M13 `morreu`, nenhum sobrevivente (forge_pronto.py:73, :47, :54, :61; forge-check:1236, :1250, :9600, :9943, :10452, :10459, :10460, :10622, :10462). `bin/forge-mutante tests/mutantes/v0474-h1-ferramenta-3.json`: M15, M16, M18, M19, M20, M22 `morreu`. `--cobertura --base 34ab6714`: `base=34ab6714… mb=34ab6714… rev=7cacc94c…`, 11 condições `coberta`, nenhuma sem mutante.
- **Fronteira que os mutantes não cobrem:** o ramo `pasta is None` está coberto por M11 só no sentido de "não roda"; o teste que o mata afirma o comportamento errado (A1).
- **Fora do alcance:** E2E e acessibilidade não se aplicam (ferramenta de linha de comando, sem UI). O D2 local do autor falhou em `test_oraculo_sempre_atual` e `ForgeCheck.test_raiz_depois_do_subcomando_e_git_isolado`, que o brief diz falhar igual na develop pura; não rodei esses dois.
- **A1, reprodução:** `prova_do_pronto(None, "develop", False)` devolve `[("pronto: não rodado aqui ...", False)]`; o ramo `elif pasta is None` do :10499 reprova as PQ `cmd` com "passe --worktree". O parecer de segurança da mesma rodada (E14.71) acha o mesmo ponto por sonda própria (S1 a S3). Correção: reprovar quando `pasta is None` e o head é do Forge, e inverter o caso `pasta=None` do teste.
