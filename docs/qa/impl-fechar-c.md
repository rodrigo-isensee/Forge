---
tipo: qa
contrato: 1
pedido: impl-fechar-c
branch: melhoria/impl-fechar-c-c3
commit: d5afb7864265dc0b11cb3d624fbeac9fe3109e5c
parecer: aprovado
revisor: forge:qa-engineer
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-31
---
# QA: impl-fechar-c (branch c3)

Etapa E1.4, `R-QA`. Diff lido: `234dbe0..d5afb78` (`bin/forge-fechar` 5+3, `tests/test_fechar.py` +19, `docs/fechamento-integrador.md`, fragmento; mais os pareceres).

## Item entregue e M14
Item E3 do pedido (FECHAR-B-REC-REVIEW 2): o `--dry-run` descreve o sha (lido só localmente, com marcador se a branch local não existe) e o número do PR (marcador, só existe depois do passo 3) que os passos usam. M14 (agents/tech-lead.md:19): um comportamento, 27 linhas de código e teste, abaixo do teto; fora de `hooks/` e `PROTEGIDOS`. Cumpre.

## Achados
- A1 (recomendado) bin/forge-fechar:557 · Mutante sobrevivente: ler o sha com `git ls-remote` no lugar do rev-parse local passa os testes; nada prende o C3-1 (--dry-run sem servidor), porque o git falso não registra ls-remote. Não bloqueia: só texto, saída igual.
- A2 (recomendado) bin/forge-fechar:559 · A1 da segurança (C3-3): linhas do --dry-run com cara de comando ainda imprimem a ref sem printf '%q'; ref com $ sai sem escape. Não bloqueia (recomendado no modelo de ameaças); o dono é o tech-lead.

## Critério → teste → resultado
O pedido não traz `CA-n`; os critérios são C3-1 e C3-2 do modelo de ameaças (SEC-FECHARC-3) e os casos AB-C3-1 e AB-C3-2.
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| C3-1/AB-C3-1 sha local e marcador do PR; zero chamadas | `test_dry_run_descreve_o_sha_e_o_numero_do_pr_que_os_passos_usam` | passo 6 segue por nome; `chamadas() == []` | passou (vermelho na base) |
| C3-2/AB-C3-2 sem branch local: marcador, rc 0 | `test_dry_run_sem_branch_local_marca_o_sha_como_nao_lido` | branch ausente | passou (vermelho na base) |
| C3-1 regressão: dry-run não chama gh nem check | `test_dry_run_nao_altera_nada_nem_chama_gh_ou_check` (existente) | sem rede | passou (verde antes e depois) |

## Cenários e resultado real
Vermelho antes do verde, `forge-testes --vermelho 234dbe0fb90b005450d7c2eb59e6241ea9779155 --modulos test_fechar`:
```
vermelho: base=234dbe0fb90b head=d5afb7864265 módulos=test_fechar (restrito por --modulos)
revertidos à base: bin/forge-fechar, changelog.d/impl-fechar-c-c3.md, docs/fechamento-integrador.md, docs/reviews/impl-fechar-c.md, docs/security/impl-fechar-c.md
mantidos no HEAD: tests/test_fechar.py
tests.test_fechar.Fechar.test_dry_run_descreve_o_sha_e_o_numero_do_pr_que_os_passos_usam · H=ok · B=falha · prova (asserção)
tests.test_fechar.Fechar.test_dry_run_sem_branch_local_marca_o_sha_como_nao_lido · H=ok · B=falha · prova (asserção)
contagem: não prova (passa na base)=86; prova (asserção)=2; pulado=1
rc=0
```
Os 86 são testes que já existiam e passam na base, como esperado. Mutação (`bin/forge-mutante`, spec do QA fora do repositório, 5 mutantes, rev d5afb7864265; o autor não declarou spec, o QA a escreveu, um mutante por linha de guarda mudada):
```
M1 · morreu · bin/forge-fechar:558
M2 · morreu · bin/forge-fechar:557
M3 · morreu · bin/forge-fechar:562
M4 · morreu · bin/forge-fechar:563
M5 · sobreviveu · bin/forge-fechar:557
rc=1
```
M5 é o A1 (recomendado, justificado acima).

Suíte: módulos `tests/test_fechar*.py` no head, sem bytecode: `Ran 204 tests` / `OK (skipped=1)` (o skip é `test_shellcheck_fechar_passa_limpo`, que pula sem `shellcheck` no PATH; o CI o roda). A bateria completa e o `scripts/validar-plugin.sh` ficam com o pre-push e o CI do envio.
