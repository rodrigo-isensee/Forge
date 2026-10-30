---
tipo: qa
contrato: 1
pedido: worktree-orfas
branch: melhoria/worktree-orfas
commit: 398791ade119ef41e35c5b7d5b279190122a656e
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-30
---
# QA - forge-fechar, passo 7: a lista do prune vai só ao log (F1)

Links: `docs/fechamento-integrador.md` (Limpeza: registro órfão), pedido WORKTREE-ORFAS (E1, E2). Sem UX nem API; as obrigações são as do pedido: lista do `git worktree prune -v` só no log (marca `[prune]`), tela com a contagem, `limpeza:` como última linha antes de `Entrega … fechada`, aviso quando o prune falha. Offline, só disco local (`R-CUSTO`). Carga de 1 minuto abaixo de 7 em cada disparo (teto do dono). Commit testado: 398791a.

## Resultados
| ID | Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|---|
| CT-01 | E1: lista fora da tela, contagem na tela, `limpeza:` fecha o passo 7 | `test_prune_com_centenas_de_orfas_conta_na_tela_e_a_lista_fica_so_no_log` (300 órfãs + 1) | muitos registros; tradução do git (`pt_BR`) | Passou (vermelho na base) |
| CT-02 | E1: prune negado avisa com código e log, sem vazar o erro cru | `test_c3_prune_negado_com_diretorio_ausente_imprime_prune_e_nao_remove` | prune com erro | Passou (vermelho na base) |
| CT-03 | Lista do prune gravada no log | `test_c3_prune_automatico_lista_no_log_o_que_removeu` | log | Passou |
| CT-04 | Limpeza não muda (ordem, códigos, comandos pendentes) | demais 14 testes de `test_fechar_orfao` e 184 das outras suítes `test_fechar*` | n/a | Passou: 201 testes, OK |
| CT-05 | Prune só roda com o diretório da worktree ausente (guarda `[ ! -d "$arvore" ]`, linha mudada no diff) | nenhum | diretório presente (suja ou ocupada) | SEM TESTE: ver A1 |

## Provas
- `python3 -m unittest tests.test_fechar_orfao`: 17 testes, OK. As 14 suítes `test_fechar*` juntas: 201 testes, OK (130 s).
- `shellcheck bin/forge-fechar`: rc=0.
- `scripts/verificar-contribuicao.sh origin/develop`: rc=0 (`ok: nenhum segredo nem caminho pessoal no diff`).
- Vermelho: `bin/forge-testes --vermelho 31257c14c8d245d66e7806edb7cd65e22b3aeb04 --modulos test_fechar_orfao`, rc=0. Abertura: `vermelho: base=31257c14c8d2 head=398791ade119 módulos=test_fechar_orfao (restrito por --modulos)`; revertidos à base `bin/forge-fechar`, `changelog.d/worktree-orfas.md`, `docs/fechamento-integrador.md`. Provam: `test_c3_prune_negado_com_diretorio_ausente_imprime_prune_e_nao_remove` (B=falha, asserção) e `test_prune_com_centenas_de_orfas_conta_na_tela_e_a_lista_fica_so_no_log` (B=falha, asserção); os outros 15 passam na base (guardas de não-regressão).
- Mutantes do autor: `bin/forge-mutante tests/mutantes/worktree-orfas.json`, rc=0: M1 a M5 `morreu` (linhas 414 a 417).
- Conferência da lista contra o diff (`forge-mutante --cobertura` sai `não coberto: bin/forge-fechar`, shell): as linhas de guarda mudadas são `if [ ! -d "$arvore" ]` (412), `|| prune_rc=$?` (414), o laço `gravar_linha` (415), `grep -c '^Removing '` (416) e `[ "$prune_rc" = 0 ] ||` (417). A 412 (a guarda que decide se o prune roda) não tem mutante na spec.
- Mutantes do QA (spec descartável em `$TMPDIR`, rodada com `bin/forge-mutante`): Q1 `if [ ! -d "$arvore" ]` para `if true` · SOBREVIVEU (bin/forge-fechar:412); Q2 `|| prune_rc=$?` para `|| true` · morreu; Q3 `[ "$prune_rc" = 0 ]` para `= 1` · morreu; Q4 aviso sem `>&2` · morreu.

## Achados
- A1 (bloqueante) bin/forge-fechar:412 · mutante Q1 sobrevive: com o diretório da worktree presente (remove falhou por suja ou ocupada), o prune passa a rodar e podar registros de outras worktrees sem teste que caia; a guarda foi reescrita no diff (`[ -d ] || prune` virou `if [ ! -d ]`) e não tem mutante na spec nem teste de "diretório presente não chama prune". Classe: AR-1 (lista de mutantes incompleta) e AR-2 (ramo de guarda sem teste de comportamento). Correção: teste com `wt_busy` sem apagar o diretório que afirma ausência de `git worktree prune` no registro do git falso, mais o mutante Q1 na spec.

## Bugs
Nenhum bug de produto aberto; o achado A1 é lacuna de prova de uma guarda mudada (`R-QA`).

## Veredito
Reprovado em 398791a por A1, único bloqueante. Comportamento do diff verificado e correto: suíte verde, vermelho provado, M1 a M5 mortos, shellcheck e verificar-contribuicao limpos. Revalidação por delta: o teste novo e o mutante Q1 mortos.
