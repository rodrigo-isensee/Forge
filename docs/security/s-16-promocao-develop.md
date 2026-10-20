---
tipo: revisao-seguranca
contrato: 1
pedido: s-16-promocao-develop
branch: melhoria/s-16-promocao-develop
commit: 571bba08cc1c030c3b19d18551c7e25dae5b3775
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-20
---
# Review de segurança: s-16-promocao-develop

Escopo: `git diff 0f480c884f8a3f5af1ea8eba861fb937d61f9619 571bba08cc1c030c3b19d18551c7e25dae5b3775` (tests/catraca.py, tests/test_catraca.py, changelog.d/s-16-promocao-develop.md) contra o modelo de ameaças da E0.1 (mitigações M1 a M7, casos de abuso B1 a B17) e a isenção do catraca.py em tests/test_ambiente_git.py:29-32. Revisor não é o autor (D-ETAPAS-INST).

## Gatilhos
`R-SEGURANCA`: tests/catraca.py é controle do Forge (está em PROTEGIDOS e SENSIVEIS). Nenhum outro gatilho: o diff não toca `.github/workflows/`, segredos, dependências nem regras.

## Achados

## Detalhe dos achados
Nenhum bloqueante. Nenhum caminho libera conteúdo sem o rótulo do dono; o caminho novo só é avaliado depois que o caminho atual falhou e exige mais provas, não menos (`R-CONFORMIDADE` preservada).

Conferência das mitigações no código:
- M1 (fetch só com a refspec explícita): tests/catraca.py:732-740. Refspec única `refs/pull/<n>/head:refs/catraca/pull/<n>`, `n` passado por `int()`, sem `+` (não sobrescreve ref existente fora de avanço rápido), `--no-tags`, `--no-recurse-submodules`, `--no-write-fetch-head`, remoto fixo `origin`, sem checkout dos objetos (só `rev-parse`, `cat-file`, `merge-base`, `ls-tree`). Manutenção desligada no próprio fetch (`maintenance.auto=false`, `gc.auto=0`).
- M2 (S igual ao do servidor, ref trazido igual ao `head.sha`): S continua vindo só de `commit_do_rotulo` (tests/catraca.py:790); `head.sha` da API validado como SHA completo (tests/catraca.py:754); depois do fetch, o ref resolvido tem de ser igual a `head.sha` e S tem de existir (tests/catraca.py:760); S ancestral de `head.sha` (tests/catraca.py:762).
- M3 (substituto do squash só quando a ancestralidade falha): o caminho atual roda primeiro e fica intacto (tests/catraca.py:795); o substituto exige M com um pai só (tests/catraca.py:751) e, por arquivo, `mesmo_arquivo(M, S)` somado ao `mesmo_arquivo(head, S)` existente (tests/catraca.py:825). Merge commit com S fora da ancestralidade é recusado.
- M4 (M na cadeia de primeiro pai de base..head): tests/catraca.py:751.
- M5 (falha fechada): código de saída do fetch diferente de zero vira aviso e None (tests/catraca.py:738-740); `TimeoutExpired` e `OSError` do git viram aviso e None no invólucro (tests/catraca.py:834-841); `http.client.HTTPException` passa a valer como None na API (tests/catraca.py:629). O fetch só ocorre depois que a API confirmou o candidato (mesclado, base, próprio repositório, rótulo do dono sem app, S conhecido) e só se S ou `head.sha` não estiverem locais.
- M6 (nada novo no workflow): o diff não toca `.github/workflows/`; `persist-credentials: false` e as permissões só de leitura seguem como estão; o token não é passado ao git (nenhum `http.extraheader` no diff).
- M7 (filtros da S-16 intactos): os filtros de `sha_rotulado_do_mesclado` antes de S não mudaram; `R-CUSTO` e violações sem arquivo seguem fora (cobertos por B15).

Prova por mutação (cópia própria em $TMPDIR a partir de `git archive 571bba0`, classe `RotuloDePrSquash`, 21 testes; sem mutação: OK). Cada mutação removeu uma única guarda:
- B3, sem `mesmo_arquivo(M, S)` em tests/catraca.py:825: falha `test_b3_merge_com_conteudo_diferente_do_rotulado_pede_mesmo_se_o_head_volta_ao_rotulado`.
- B4, sem `trazido != final` em tests/catraca.py:760: falha `test_b4_ref_do_remoto_diferente_do_head_da_api_pede`.
- B7, sem a ancestralidade S → `head.sha` em tests/catraca.py:762: falha `test_b7_head_rotulado_que_nao_e_ancestral_do_head_final_pede`.
- B8, sem a cadeia de primeiro pai em tests/catraca.py:751: falha `test_b8_merge_fora_da_cadeia_de_primeiro_pai_pede`.
- B9, aceitando M com dois pais em tests/catraca.py:751: falha `test_b9_merge_com_dois_pais_e_s_fora_da_ancestralidade_pede`.
- Extra M1, destino do fetch em `refs/remotes/origin/develop`: falham `test_b14_o_fetch_nao_escreve_em_refs_existentes`, `test_m1_fetch_so_com_a_refspec_explicita_do_pr` (e o B1 erra).
- Extra B6, invólucro sem `TimeoutExpired`: erra `test_b6_fetch_que_estoura_o_prazo_pede_sem_traceback`.

Custo (`R-CUSTO`): só `git fetch` anônimo do `origin` público e as GETs que já existiam com o token do run; nenhum serviço pago nem URL de API paga no diff.

Recomendações (não bloqueantes):
- R1 (informativa) tests/test_ambiente_git.py:29-32: a isenção do catraca.py diz que ele só lê o repositório; agora ele grava objetos e `refs/catraca/pull/<n>` num fetch. Não há risco de manutenção automática, porque o fetch a desliga por `-c` (tests/catraca.py:735), mas o motivo escrito ficou desatualizado. Caminho de ataque: nenhum; é precisão do controle. Correção mínima: atualizar o texto da isenção citando o fetch com manutenção desligada. Esforço P. Dono: tech-lead (pedido próprio; o catraca.py e a isenção são controles, fora do escopo deste).
- R2 (baixa) tests/catraca.py:790-795: S (o `head_sha` da execução) entra em argv do git sem a checagem de SHA completo que `head.sha` ganhou (tests/catraca.py:754). Caminho de ataque: só o servidor do GitHub escreve esse campo, então não há atacante realista; é defesa em profundidade contra um valor iniciado por `-` virar opção. Correção mínima: `SHA_COMPLETO.fullmatch(s)` antes de usar S. Esforço P. Dono: tech-lead.
- R3 (informativa): o caminho de merge commit (tests/catraca.py:795) segue sem a exigência de primeiro pai que o squash ganhou; é o comportamento da S-16 (M7 manda não mudar) e a recomendação A1 do parecer s-16 continua aberta.

## Riscos aceitos e ferramentas
Nenhum risco aceito novo. Residuais do modelo de ameaças (sem mudança): disponibilidade de `refs/pull/N/head` (falha fechada) e pior caso de tempo acima dos 10 min do job até o cartão CATRACA-PRAZO-API (job morto fica vermelho).
Ferramentas: leitura estática do diff e mutação local dos testes. `gitleaks`, `zizmor`, `actionlint`, `semgrep` e `osv-scanner` não estão no PATH (lacuna; as varreduras são do CI). Nenhuma rede usada nesta revisão.
