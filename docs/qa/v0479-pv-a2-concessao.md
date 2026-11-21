---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-pv-a2-concessao
commit: 4c325c557ee7cf5544a28488eb06346ae9bfbc1f
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 2
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-20
---
# QA: v0479-pv-a2-concessao (E57.63)

Alvo `item:<CARTAO>` da concessão presa ao `Commit` revisado (PR-VERDE E1, PV-A2, ADR 0018). Passada única no head 4c325c55; suíte inteira fica no CI do PR (check-run `bateria` do mesmo sha, não rodado aqui).

## Achados
- A1 (bloqueante) bin/forge_autorizacao.py:29 · RESSALVA é lista negativa (AR-3): "depois do CI", "antes da release", "sem a segurança", "só com o QA" saem `ativa` (reproduzido, sonda do QA); o item 5 da ADR 0018 pede ressalva barrada.
- A2 (bloqueante) bin/forge_autorizacao.py:176 · `git diff --name-only` sem `--no-renames`: `git mv codigo.txt docs/qa/codigo.txt` depois do Commit deixa a concessão `ativa` com o código removido do Ramo (reproduzido, sonda do QA).

## Critério → teste → resultado
Critérios: a especificação é a E1 da ADR 0018 e o A2 do desenho (`docs/propostas/v0479-pr-verde-de-primeira.md`).
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Commit é o head do Ramo com pareceres aprovados; sha curto do parecer aceito | test_head_com_os_pareceres_aprovados_fica_ativa_e_o_parecer_pode_citar_o_sha_curto | prefixo de 7 caracteres | passou |
| Commit fora do Ramo, ramo sem ref, Ramo muda depois, parecer reprovado, de outro commit ou curto demais | test_commit_que_nao_e_o_head_com_os_pareceres_aprovados_fica_inativa | head exato, sha de 6 caracteres, sem commit | passou |
| Commit sha40, Ramo sem `-` inicial nem `..`, ato único | test_commit_abreviado_ausente_ramo_fora_da_forma_ou_ato_errado_e_adulterada | 12 caracteres, maiúsculo, ausente, `-x`, `a..b` | passou |
| `item <CARTAO>` na frase do ato; sem ressalva (negação, condição) | test_alvo_sem_marcador_fora_da_frase_ou_com_ressalva_nao_nasce_ativa | cartão vizinho `PV-A2X`/`PV-A2.1`, frase vizinha | passou (cobre só "não" e "se"; ressalva positiva não coberta, A1) |
| Parecer só do Ramo exato, ref `origin` vale antes da local | test_ramo_sem_parecer_dele_fica_inativo_e_a_ref_do_origin_vale_antes_da_local | `branch: <ramo>-x`, sem frontmatter | passou |
| `GIT_*` herdado não desvia | test_git_herdado_do_ambiente_nao_desvia_a_leitura | GIT_DIR inválido | passou |
| Depois do Commit só pareceres (sem renomeação) | nenhum | rename para docs/ | não coberto (A2, bug alto) |

## Cenários e resultado real
Vermelho (`R-QA`), módulo do diff, saída 0:
```
vermelho: base=d4f0b10aead7 head=4c325c557ee7 módulos=test_autorizacao (restrito por --modulos)
revertidos à base: bin/forge_autorizacao.py, changelog.d/v0479-pv-a2-concessao.md
tests.test_autorizacao.ItemPresoAoCommit.* (6 testes) · H=ok · B=falha · prova (asserção)
tests.test_autorizacao.Ler.* (8 testes) · H=ok · B=ok · não prova (passa na base)
contagem: não prova (passa na base)=8; prova (asserção)=6
```
A primeira tentativa, sem `--modulos`, rodou os 6 módulos e estourou o `timeout 900` (rc=124, sem veredito); não vale como prova.

Mutantes (`bin/forge-mutante` das 4 specs, `--processos 2`): rc=0, M1 a M28 todos `morreu` (M3, M4, M27, M28 por erro do teste sob o mutante com controle verde). Sem sobrevivente.
Cobertura (`--cobertura --base d4f0b10a`): rc=0; toda condição Python mudada tem mutante declarado, sem `não coberto`, sem `isenta velha`.
Os mutantes são declarados para as linhas que existem; as duas lacunas dos achados são de linhas que a spec não atinge (a RESSALVA sem vocabulário positivo e o `diff` com renomeação), então o rc=0 não as prova.

Sondas do QA (`ItemPresoAoCommit`, estado da concessão `ativa` obtido onde se espera `adulterada`/`inativa`):
- corpo `pode aplicar o rótulo afrouxa-regra no item PV-A2` + "depois do CI verde" / "antes da release" / "sem a segurança" / "só com o QA": `('ativa', '')` nos quatro.
- `git mv codigo.txt docs/qa/codigo.txt` e commit depois do parecer: `('ativa', '')`.

Os pareceres de review (A1) e segurança (A1, A2) no mesmo head, já na branch, trazem os mesmos dois defeitos; A3/A4 da segurança e A2/A3 do review ficam com seus pareceres.

Bugs: A1 e A2 são os dois bugs altos (rótulo que afrouxa regra liberado fora da fronteira que a ADR 0018 fixa). Responsável: autor da branch (dev do Forge). Retestar por `forge-check parecer delta docs/qa/v0479-pv-a2-concessao.md`.
