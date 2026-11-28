---
tipo: qa
contrato: 1
pedido: v0477
branch: melhoria/v0477-forge-check-defeitos
commit: 4603cde822b5484bbd5965327f10060e5c51abc9
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-18
---
# QA: v0477 (forge-check, defeitos pequenos)

Escopo: `veredito_trocado` em `bin/forge-check` (VEREDITO-TROCADO-LENTO), os dois testes novos em `tests/test_selo_e_entrega.py`, os 2 mutantes e as provas do fragmento sobre ENTREGA-PUSH-RAIZ-PEDIDOS e BRIEF-SELAR-LINHA-DA-ETAPA.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| `git grep` que falha conta como veredito trocado (falha fechada) | `test_grep_que_falha_conta_como_veredito_trocado` | falha do git (rc > 1) | vermelho na base, verde no head |
| Só a versão que cita o sha revisado é lida (um `git show`, não um por arquivo) | `test_so_le_a_versao_que_cita_o_sha_revisado` | arquivo da pasta sem o sha, não lido | vermelho na base, verde no head |
| Veredito trocado segue detectado (regressão) | testes `*_segue_fora` e vizinhos de `ParecerDoPortao` | outro arquivo, mesmo commit, apagado | verde (H=ok, 115 inalterados) |
| ENTREGA-PUSH-RAIZ-PEDIDOS já não acontece | `tests.test_git_rede_config` (6 testes) | ambiente do proxy no `ls-remote` | 6 OK; a2dfb22b é ancestral de 038249c5 |

## Vermelho antes do verde
Os dois testes aparecem em duas classes (`ParecerDoPortao` e `MatrizDaBuscaDoVeredito`, por herança), 4 linhas.

```
vermelho: base=038249c510aa head=4603cde822b5 módulos=test_selo_e_entrega (restrito por --modulos)
revertidos à base: bin/forge-check, changelog.d/v0477-forge-check-defeitos.md
mantidos no HEAD: tests/mutantes/v0477-forge-check-defeitos.json, tests/test_selo_e_entrega.py
tests.test_selo_e_entrega.MatrizDaBuscaDoVeredito.test_grep_que_falha_conta_como_veredito_trocado · H=ok · B=falha · prova (asserção)
tests.test_selo_e_entrega.MatrizDaBuscaDoVeredito.test_so_le_a_versao_que_cita_o_sha_revisado · H=ok · B=falha · prova (asserção)
tests.test_selo_e_entrega.ParecerDoPortao.test_grep_que_falha_conta_como_veredito_trocado · H=ok · B=falha · prova (asserção)
tests.test_selo_e_entrega.ParecerDoPortao.test_so_le_a_versao_que_cita_o_sha_revisado · H=ok · B=falha · prova (asserção)
contagem: não prova (passa na base)=115; prova (asserção)=4
rc=0
```

## Mutantes (`bin/forge-mutante tests/mutantes/v0477-forge-check-defeitos.json`)
Um mutante por guarda mudada no diff (as duas: `cod > 1` e o `continue` do filtro).
```
forge-mutante: pedido=v0477-forge-check-defeitos rev=4603cde822b5 spec=d599b069646af07b2553c137048b4f5306a5e850a0df5f34c34e9deee1bd98d2
M1 · morreu · bin/forge-check:2808
M2 · morreu · bin/forge-check:2816
rc=0
```

## Leitura do diff
- `git grep -l -F -e <sha> <versões> -- <pasta>`: rc 1 (sem acerto) segue; rc > 1 retorna True (falha fechada). A chave `"<sha>:<arquivo>"` bate com o prefixo que o `git grep` imprime para a mesma árvore passada; o frontmatter com `commit: <sha>` sempre contém o sha, então nenhum parecer que decidiria o veredito é filtrado.
- ENTREGA-PUSH-RAIZ-PEDIDOS: o fragmento afirma sem mudança de código; confirmado que a2dfb22b (correção do ambiente do proxy) está na base e `tests/test_git_rede_config.py` passa. BRIEF-SELAR-LINHA-DA-ETAPA: sem código, conforme a decisão do pedido; fora do que o QA testa.

## Observações (sem bloqueio de QA)
- `python3 -I tests/catraca.py --base origin/develop` responde `R-CONFORMIDADE` para `bin/forge-check`: precisa do rótulo `afrouxa-regra` do dono no PR (decisão do dono, `R-DECISAO`); a guarda tem mutantes declarados, então não é "guarda sem mutante".
- Suíte inteira: só no CI do PR (check-run `bateria` do mesmo sha); não rodada local, por brief.
