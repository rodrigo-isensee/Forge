---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-pp1-aplicado-dono
commit: 4d60adf4f5d43fc8f55c8a7f27727e0823b18674
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-20
---
# QA: v0479-pp1-aplicado-dono (v0478 E52.4, volta no head 58da41ec)

Escopo lido: `0f6034ea..58da41ec` (`bin/forge-check`: `isencao_do_dono`, `emails_do_dono`, `patch_revisado_do_dono`, `parecer_cita_o_patch`; a classe `PatchRevisadoDoDono` em `tests/test_conf_escopo.py`; quatro specs de mutantes). Suíte inteira: no CI do PR (`R-QA`); aqui só o módulo tocado, com `TMPDIR` próprio. A volta fecha as A1, A2 e A3 do review e da segurança (4aadad19): patch conferido sobre pai, Base-sha e develop atual; e-mails lidos do Base-sha; sha256 do patch citado por parecer de segurança aprovado no head.

## Critério → teste → resultado
| Critério (DECISÃO DO DONO 18/11, 20/11; A1-A3) | Teste (`PatchRevisadoDoDono`) | Fronteira protegida | Resultado |
|---|---|---|---|
| (a) commit do dono igual ao `.patch` aplicado, árvore e modo | `test_patch_adulterado_ou_aplicado_diferente_recusa`, `test_indice_do_repositorio_intacto` | linha a mais, modo diferente, patch que não se aplica | passou |
| (a) + A1: pai, Base-sha e develop atual iguais no caminho | `test_s1_mudanca_anterior_da_branch_no_arquivo_recusa`, `test_develop_atual_diferente_ou_sem_resolver_recusa` | pai difere da base; develop mudou; develop sem resolver; `ls-tree` que falha | passou |
| (b) autor e committer do dono | `test_commit_que_nao_e_do_dono_recusa` | autor ou committer fora da lista; caixa do e-mail | passou |
| (b) + A2: lista da árvore do Base-sha | `test_emails_da_arvore_do_base_sha_e_nao_da_branch` | lista versionada só na branch (nada isenta); disco só sem versão na base | passou |
| (c) + A3: sha256 citado por parecer de segurança aprovado | `test_patch_sem_parecer_de_seguranca_aprovado_que_o_cite_recusa` | reprovado, tipo review, sem frontmatter, outro sha256, sha256 como parte de palavra | passou |
| (c) grava sha256 e sha40 | `test_quatro_condicoes_cumprem_e_a_conferencia_grava_os_shas` | caminho feliz | passou |
| ` patch <caminho>` válido na linha | `test_linha_sem_patch_ou_patch_fora_da_branch_recusa` | vazio, `..`, patch ausente da branch | passou |
| falha fechada (git, política) | `test_git_que_falha_ou_politica_ilegivel_recusa` (agora com `grep`) | `read-tree`, `log`, `grep` com rc 1; política vazia | passou |

Classe rodada: `python3 -I -m unittest discover -s tests -p test_conf_escopo.py -k PatchRevisadoDoDono` → `Ran 10 tests in 20.893s`, `OK`. Os testes das condições (a), (b) e (c) da 1ª rodada seguem verdes no novo `setUp` (parecer de segurança na base, `self.base` do ff da develop).

## Vermelho antes do verde
`bin/forge-testes --vermelho 0f6034ea5aaaab5f0aab8acb593523497cdc3b6f --modulos test_conf_escopo` → rc 0:
```
vermelho: base=0f6034ea5aaa head=58da41ec48c1 módulos=test_conf_escopo (restrito por --modulos)
revertidos à base: bin/forge-check, changelog.d/v0479-pp1-aplicado-dono.md, docs/reviews/v0479-pp1-aplicado-dono.md, docs/security/v0479-pp1-aplicado-dono.md
contagem: não prova (passa na base)=25; prova (API ausente)=2; prova (asserção)=7
```
Provam: `test_commit_que_nao_e_do_dono_recusa`, `test_develop_atual_diferente_ou_sem_resolver_recusa`, `test_linha_sem_patch_ou_patch_fora_da_branch_recusa`, `test_patch_adulterado_ou_aplicado_diferente_recusa`, `test_patch_sem_parecer_de_seguranca_aprovado_que_o_cite_recusa`, `test_quatro_condicoes_cumprem_e_a_conferencia_grava_os_shas`, `test_s1_mudanca_anterior_da_branch_no_arquivo_recusa` (asserção); `test_emails_da_arvore_do_base_sha_e_nao_da_branch`, `test_git_que_falha_ou_politica_ilegivel_recusa` (API ausente). Os 4 novos desta volta (S1, develop atual, e-mails do Base-sha, parecer de segurança) provam na base. `test_indice_do_repositorio_intacto` passa na base: é teste de propriedade preservada (índice temporário), não de regra nova.

## Mutação
`bin/forge-mutante` nas 4 specs (28 mutantes, `--processos 3`), rc 0:
```
forge-mutante: pedido=v0479-pp1-aplicado-dono rev=58da41ec48c1 spec=caa1fbb2… spec=d8158435… spec=8b15f539… spec=569f8906…
M1..M28 · morreu (todos; M4, M17 e M27 por erro do teste declarado sob o mutante, controle verde)
```
Delta da volta (`--base 4aadad19d27ec28ce467a05a61bd070e3497b003`, specs -3 e -4): `base=4aadad19… mb=4aadad19… rev=58da41ec…`; M17 a M28 · morreu.
Cobertura (`--cobertura --base 0f6034ea5aaaab5f0aab8acb593523497cdc3b6f`, rc 0): toda condição Python mudada em `bin/forge-check` tem mutante declarado (`coberta ... declarado, não provado`, provado pela rodada acima); nenhuma linha `não coberta`.

## Cenários e resultado real
- S1 do review e da segurança (agente muda o hook, patch só soma `# revisado`, dono aplica sobre o pai): recusa com `"<hook>" difere entre o pai do commit do dono, o Base-sha e a develop atual`; era rc 0 em 4aadad19.
- Lista de e-mails só na branch: nada isenta, nem pelo disco; lista no Base-sha vence a do disco.
- Parecer de segurança que só cita o sha256 sem frontmatter, reprovado, de review ou com sha256 colado a outro caractere: recusa.
- Limite aceito, não defeito: o e-mail é declarável (decisão do dono de 20/11, comentário e changelog registram); commit assinado fica para cartão.
- Observação: `parecer_cita_o_patch` aceita qualquer parecer de segurança aprovado em `docs/security/` do head que cite o sha256 (não amarra ao pedido ou à branch). O sha256 de 64 hex só aparece em parecer que leu aquele patch, e `docs/security/` é do portão; sem caminho de abuso provado, fica no recomendado.

## Revalidação no head 4d60adf4 (delta de `forge-check parecer delta`, base 58da41ec)
Delta no domínio: `bin/forge-check` (`parecer_cita_o_patch` e `patch_revisado_do_dono` passam a receber `(pedido, branch)`; só vale parecer `aprovado`, com `pedido:` e `branch:` iguais, fora de `docs/security/aceites/` e `ameacas/`), `tests/test_conf_escopo.py`, três specs de mutantes, changelog. Fecha o A1 recomendado da rodada anterior (mesmo achado, agora com teste).

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| A1/A4 (S3, S4): parecer só da própria branch e pedido, `aprovado`, fora de `aceites/` e `ameacas/` | `test_a4_so_o_parecer_aprovado_da_propria_branch_e_pedido_vale` | outra branch, outro pedido, `riscos-aceitos`, `aceites/`, `ameacas/`; o mesmo parecer em `docs/security/outro.md` isenta | passou |
| (c) A3 com a nova mensagem | `test_patch_sem_parecer_de_seguranca_aprovado_que_o_cite_recusa` | reprovado, review, sem frontmatter, outro sha256, sha256 colado | passou |
| assinatura nova de `isencao_do_dono` (branch) | `PatchDoDono` (8 testes), demais de `PatchRevisadoDoDono` | n/a | passou |

Provas (TMPDIR próprio, cópia `4d60adf4`):
- `python3 -I -m unittest discover -s tests -p test_conf_escopo.py -k PatchRevisadoDoDono` → `Ran 11 tests in 53.614s`, `OK`.
- `-k PatchDoDono` → `Ran 8 tests`, `OK`; `python3 -I -m unittest discover -s tests -p test_forge_mutante.py -k ConferirTodas` → `Ran 4 tests in 8.704s`, `OK`.
- Mutantes do delta: `bin/forge-mutante --processos 3 --base 58da41ec48c1d6fc8f05e9b41788d44a7ec6d4d0` nas 3 specs tocadas (rc 0): `base=58da41ec… mb=58da41ec… rev=4d60adf4…`; M1 a M8, M17 a M31 (M3, M23, M24 realinhados; M25, M29, M30, M31 novos) · morreu (M4, M17 e M27 por erro do teste declarado, controle verde).
- Cobertura `--cobertura --base 0f6034ea…` → rc 0, sem linha `não coberta`.
- Vermelho: `bin/forge-testes --vermelho 58da41ec48c1d6fc8f05e9b41788d44a7ec6d4d0 --modulos test_conf_escopo` → rc 2 (sem veredito). Linha que importa: `test_a4_so_o_parecer_aprovado_da_propria_branch_e_pedido_vale · H=ok · B=falha · prova (asserção)`. O rc 2 vem de 5 testes antigos (`PatchDoDono.test_c15`, `test_c8`, `PatchRevisadoDoDono.test_develop_atual…`, `test_git_que_falha…`, `test_indice…`) que dão erro na base por chamarem `isencao_do_dono` com o parâmetro `branch` que a base não tem; são testes realinhados, não de regra nova, e passam no head. O teste novo prova.
- Suíte inteira: CI do PR (`R-QA`), não rerrodada aqui.

Limite aceito, não defeito: o e-mail do dono é declarável (decisão de 20/11). Sem achado novo.
