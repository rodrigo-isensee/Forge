---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-fechar-dryrun-branch
commit: 432ac20dda60577b3ff69c649deb5d44a89931fc
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-25
---
# QA: v0481 forge-fechar --dry-run sem a branch local (#898), volta por delta

Links: pedido v0481 (E14.45 correção, QA E14.54), `docs/fechamento-integrador.md`, `bin/forge-fechar`. Delta lido: `git diff 1bf95225..432ac20d`. Sem UX nem API. Offline, `gh` e `git` falsos (`R-CUSTO`). Clone no head do remoto (432ac20d).

- ci: 432ac20dda60577b3ff69c649deb5d44a89931fc verde
- suíte: 432ac20dda60577b3ff69c649deb5d44a89931fc rc=0 módulos=test_fechar

Sobre o ci acima (`gh pr checks 898` e check-runs do sha 432ac20d, concluídos): suíte 3.12 e 3.14 nas 5 partes, teto de pulados, passos, verificações longas, instalação e árvore provada verdes; fora `bateria (pareceres)`, `bateria` e `catraca`, que o parecer reprovado do head faz falhar; não li o log, o cache do gh é somente leitura)

## Achados
- A1 (parecer anterior, bloqueante) resolvido: as quatro specs (mp1311 M3 e M5, v0478-fechar-lote-2 FL-M11 e FL-M12) apontam linhas que existem; M3 e FL-M12 saíram junto com a guarda que o código não tem mais (o caso "sem branch local, sai 0"), M5 e FL-M11 foram reapontados.
- Nenhum achado novo.

## Critério → teste → resultado
| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| A ref criada pelo --dry-run sai no fim | `test_1c_no_dry_run_sem_a_branch_local_cria_da_origin_sem_rastreio_e_roda` (afirma ref ausente e `registro: apaguei`) | ref criada | passou; mutante M5 morre |
| O passo real seguinte lê o servidor, não a origin/<b> velha | `test_dry_run_sem_a_branch_local_nao_prende_o_passo_real_na_origin_velha` | origin/<b> atrás do servidor | passou; M5 morre |
| A recusa do 1c também apaga a ref | `test_1c_no_dry_run_sem_a_branch_local_que_recusa_para_com_1` | rc 1 do 1c | passou |
| Mutantes realinhados guardam o mesmo | mp1311 M5 (passo 1 com `refs/heads/`), FL-M11 (1c roda de verdade) | troca de linha | morreram |

## Conferências do brief
- Nada que barra deixa de barrar: o código novo só acrescenta `branch_criada="$sha_dry"` e texto; a limpeza reaproveita o `fim()` existente (`git update-ref -d refs/heads/<b> <sha criado>`, só apaga se a ref segue no sha criado; `branch_criada` nasce vazia). Nenhuma condição de recusa mudou; as recusas do dry-run (sem origin/<b>, ref não criada, 1c rc 1) seguem com 1, e a recusa agora também limpa.
- Mutantes realinhados: M3 e FL-M12 protegiam o marcador "sha não lido" e o "1c não roda sem branch local", que o código não tem mais; o que protegiam (1c que não roda nunca sai 0) segue em v0481 M3/M4 e nos testes de recusa. M5 (mp1311) e FL-M11 mudaram só `de`/`para`, mesma guarda.
- CI: vermelhos são catraca, bateria e bateria (pareceres); pela lista de checks, o item não tem falha própria (as 10 partes da suíte estão verdes). Não li os logs.
- D2: só rodei os módulos do item, sem falha; a suíte inteira verde no CI, logo nenhuma falha nova contra a develop.

## Provas
- `python3 -I -m unittest discover -s tests -p test_fechar.py`: 115 testes, OK (skipped=1, shellcheck ausente aqui); `test_fechar_ref_por_nome.py`: 5 testes, OK.
- `bin/forge-mutante` v0481 (rev=432ac20dda60): M1 :1660, M2 :1672, M3 :1674, M4 :1675, M5 :1676, todos `morreu`. mp1311: M1, M2, M4, M5 `morreu`. v0478-fechar-lote-2: FL-M9, FL-M10, FL-M11, FL-M13 `morreu`.
- `bin/forge-mutante --conferir --todas`: nenhuma linha de fechar, mp1311 ou v0478-fechar-lote (as demais são de outros pedidos, fora do delta).
- `forge-testes --vermelho 1bf95225 --modulos test_fechar`, rc=0: contagem: não prova (passa na base)=111; prova (asserção)=3; pulado=1 (guardei só o fim da saída; o cabeçalho `vermelho: base=… head=…` não foi copiado).

## Bugs
Nenhum.

## Veredito
Aprovado no delta 1bf95225..432ac20d: ref apagada no fim, também na recusa, passo real sem parar no passo 2, specs de mutante alinhadas e todos os mutantes mortos.
