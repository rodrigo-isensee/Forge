---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-fechar-busca-pareceres
commit: be7d10f412d3814a7a4d60f3ee447f3d752da164
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-23
---
# QA · busca dos pareceres citados no forge-fechar (E132.4, PR #817)

Head be7d10f4, base 0e59c446. Sem suíte local: a bateria inteira é o check-run `bateria` do CI do mesmo sha; aqui, só o módulo tocado, o vermelho e os mutantes.

| Obrigação (FECHAR-BUSCA-PARECERES-CITADOS) | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Busca da origin pelo sha40 e da `--principal`; diz o que não existe em lugar nenhum; sem ref nova nem FETCH_HEAD; passo 1 segue primeiro | `test_busca_da_origin_e_da_principal_e_diz_o_que_nao_existe` | sha inexistente, sha só na principal, `## Notas` fora do histórico | passou |
| Sem `--principal`, só a origin | `test_sem_principal_busca_so_da_origin` | fonte única | passou |
| Pedido da cópia principal do repositório (fora de `~/.forge-contrib`) | `test_pedido_da_copia_principal_do_repositorio` | pasta alternativa | passou |
| Tudo legível: nenhum fetch (sem a refspec padrão) | `test_tudo_legivel_nao_busca_nada` | lista vazia | passou |
| O veredito do passo 1 não muda | `test_o_veredito_do_passo_1_nao_muda` | rc 1 do forge-check | passou |
| `--principal` que não é repositório para antes do passo 1 | `test_principal_que_nao_e_repositorio_para_antes_do_passo_1` | pasta inexistente, zero chamadas | passou |
| `--principal` sem valor | `test_principal_sem_pasta_e_erro_de_uso` | argumento ausente | passou |
| `--lote` recusa `--principal` | `test_lote_recusa_principal` | combinação proibida | passou |

## Cenários e resultado real
- `python3 -m unittest tests.test_fechar_busca_pareceres` (da raiz, sem `-I`): 8 testes, OK. A saída traz `fatal: Not a valid object name` do `git cat-file` de teste, que é o esperado para o sha inexistente.
- Vermelho antes do verde:
```
vermelho: base=0e59c44642a8 head=be7d10f412d3 módulos=test_fechar_busca_pareceres (restrito por --modulos)
revertidos à base: bin/forge-fechar, bin/forge-testes, changelog.d/v0480-fechar-busca-pareceres.md, tests/pesos-d4.json
contagem: não prova (passa na base)=1; prova (asserção)=7
```
  Saída 0. O único que passa na base é `test_tudo_legivel_nao_busca_nada`, guarda negativa (não buscar), morta pelo mutante que remove o `return 0` do fetch sem sha.
- `bin/forge-mutante --base 0e59c446` nas duas specs: base=0e59c44642a8f388649cb794072fd347ebebd8aa, 11 de 11 mortos (M1..M11, em `bin/forge-fechar` nas linhas 123, 139, 1422, 1425 a 1427, 1431 a 1433, 1437 e 1446). A lista cobre as guardas do diff: `--principal` no lote, o argumento, `faltam`, a guarda de lista vazia, o fetch e o fetch por sha, a `--principal`, o `die`, o `cd`, o `[ -f` do pedido e o aviso final. Mutante extra por mim, à mão (`h = 1` no awk do `## Histórico`): morreu em 2 testes; árvore restaurada.
- Falhas locais citadas no brief, na base 0e59c446 (cópia por `git archive`, sem o diff): `test_oraculo_sempre_atual` falha igual (39 falhas e 1 erro em 59 testes, as mesmas 40 do head) e `test_fechar_longas` falha igual (1 de 4, `test_branch_de_integracao_do_claude_md_e_recusada`). Não vêm deste PR.
- Mapa: `bin/forge-testes` põe o módulo novo no plano de `bin/forge-fechar`; `tests/pesos-d4.json` traz o peso.
