---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-mutante-diagnostico
commit: bb8aac06413679d6db6564019c95cfe14c20dfe9
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-16
---
# QA: v047 · E1.297 (forge-mutante: isenta pelo texto, recusa cedo, por quê, pedidos diferentes)

Classe C (controle em `bin/`). Intervalo `origin/develop..ef1fb25b` (develop em c5c3a449, 2 commits de código, 12 arquivos). A branch avançou com 2 commits só de parecer (review e segurança), mesclados aqui sem tocar código. Sem UX nem API: as obrigações vêm do item E1.283 do pedido v047. Quem testa não fez a entrega. Sem PR nem check-run `bateria` para o sha (a API de check-runs de ef1fb25b responde total 0); a suíte inteira fica para o CI do PR. Local rodei os cenários: `python3 -m unittest tests.test_forge_mutante` = `Ran 115 tests ... OK`.

## Achados
- A1 (recomendado) tests/mutantes/guarda-sem-mutante-4.json:25 · RESOLVIDO em bb8aac06: M25, M31 e M32 realinhados à fonte; os 8 mutantes da spec morrem (rc=0).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| ISENTA-POR-TEXTO: apagada uma vez casa pelo texto do nó, sobrevive à base deslocada, `linha_base` ignorada | `Cobertura.test_isenta_pelo_texto_libera_a_apagada_repetida_e_sobrevive_a_base_deslocada` | base com 0, 1 (não ASCII) e 9 linhas novas antes; `linha_base` 99 | passou; vermelho na base; MD2, MD4, IL3, IL12 mortos |
| Isenta que não casa o nó, outro arquivo, repetida ou da condição que ficou é rc 2; não solta a outra apagada | `test_isenta_pelo_texto_que_nao_casa_o_no_fica_solta` | trecho fora do nó, ausente, isenta usada 2 vezes | passou; MD1, MD3, IL4 mortos |
| Uma isenta cobre uma condição só; apagada 2+ vezes não casa pelo texto | `test_isenta_por_linha_cobre_uma_condicao_so`, `test_isenta_por_linha_nao_casa_texto_apagado_duas_vezes` | duas condições na mesma linha; texto apagado 2 vezes | passou; MD3, MD6, IL2, IL15 mortos |
| Árvore suja com spec diferente ou ausente no commit recusa rc 2 antes de rodar; igual ou limpa roda | `Execucao.test_arvore_suja_com_spec_diferente_da_do_commit_recusa_antes_de_rodar` | spec editada, spec nova, spec igual, árvore limpa com `--rev` antigo | passou; vermelho na base; MD15, MD16, MD18, MD20 mortos |
| Spec fora do repositório não se confere | `Execucao.test_mutante_que_o_teste_derruba_morre_e_sai_0` (spec em `$TMPDIR`) | spec fora da raiz | passou; MD17 morto |
| `--cobertura` diz `por quê` para o mutante que toca o nó e não cobre (`de` repetido, curto, troca fora do nó); nada se não toca o nó | `Cobertura.test_sem_mutante_diz_por_que_o_mutante_que_toca_o_no_nao_cobre` | `de` 2x, `de` com menos de 8 não brancos, troca fora do nó, outro arquivo | passou; vermelho na base; MD7 a MD12, MD19 mortos |
| Specs de pedidos diferentes saem 2 com uma chamada por pedido, caminho com espaço citado | `ValidacaoDaSpec.test_varias_specs_com_pedido_diferente_ou_id_repetido_sao_invalidas`, `Execucao.test_specs_de_pedidos_diferentes_saem_2_com_uma_chamada_por_pedido` | 2 pedidos, 3 specs, nome com espaço | passou; vermelho na base; MD13, MD14 mortos |
| 17 mutantes realinhados não afrouxaram | rodada das 6 specs editadas | M28 a M30, M60, M1, M4, C1 a C3, C5, IL1 a IL5, IL11, IL12, IL15 | todos `morreu` (M25, M31, M32 são antigos: A1) |

## Vermelho antes do verde
`bin/forge-testes --vermelho c5c3a449d7c34667f60a355c398a621fd967b122 --modulos test_forge_mutante` (rc=0), colado:
```
vermelho: base=c5c3a449d7c3 head=a50e3af31a43 módulos=test_forge_mutante (restrito por --modulos)
revertidos à base: bin/forge-mutante, changelog.d/v047-mutante-diagnostico.md, docs/reviews/..., docs/security/...
contagem: não prova (passa na base)=110; prova (asserção)=5
```
Provam (asserção): `test_isenta_pelo_texto_libera_a_apagada_repetida_e_sobrevive_a_base_deslocada`, `test_sem_mutante_diz_por_que_o_mutante_que_toca_o_no_nao_cobre`, `test_arvore_suja_com_spec_diferente_da_do_commit_recusa_antes_de_rodar`, `test_specs_de_pedidos_diferentes_saem_2_com_uma_chamada_por_pedido`, `test_varias_specs_com_pedido_diferente_ou_id_repetido_sao_invalidas`. Os 110 restantes já existiam e passam nos dois lados. O head do vermelho é a50e3af3 (mesmo código de ef1fb25b mais os dois pareceres).

## Mutação (pedido de controle)
- `bin/forge-mutante --cobertura --base c5c3a449` (rc=0): todas as condições mudadas de `bin/forge-mutante` saem `coberta` (linhas 386, 388, 513 a 556, 564, 612, 825 a 832, 943); a guarda dividida sai `isenta · bin/forge-mutante:527(base)` com motivo verificável (MD1 e MD5). As seis specs antigas só saem `spec editada`.
- `bin/forge-mutante --processos 4` nas 3 specs v047-mutante-diagnostico (rc=0): MD1 a MD20 `morreu`, nenhum sobrevivente, nenhum inválido.
- Specs realinhadas: guarda-sem-mutante-9, lote-mutante, mutante-casa-espaco, mutante-isenta-linha e mutante-isenta-linha-2 saem rc=0, todas `morreu`. guarda-sem-mutante-4: M26 a M30 `morreu`; M25, M31, M32 `inválido` (A1, pré-existente), rc=2.
- Afrouxamento: IL1 virou mutante mais grosso (`True or id(i)`), mas IL2 e IL3 seguram o que ele deixou de provar; IL4 troca a guarda por `is None` (remove a guarda, mesma força). Nenhum realinhamento enfraqueceu o teste alvo.

## Bordas conferidas
Isenta repetida e isenta de outro arquivo (rc 2); spec fora do repositório ignorada; `--rev` antigo com árvore limpa roda. O walrus `motivo :=` apontado no review não muda o resultado.

## Bugs
Nenhum aberto. A classe do A1 já é AR-12 (`docs/engineering/achados-recorrentes.md`); a contagem sobe para 3 no PR do autor, porque o brief restringe este commit ao parecer.

## Revalidação por delta (head dc405b6b, base aprovada ef1fb25b)
`forge-check parecer delta` lista no domínio: `bin/forge-mutante`, `tests/mutantes/guarda-sem-mutante-4.json`, `tests/test_forge_mutante.py`. O delta próprio do item é M25, M31 e M32 da spec (alinhados à fonte, mesma mutação); o resto veio da develop (E1.140, E2.215 e afins, fora deste pedido). Sem PR nem `bateria` para o sha; a suíte inteira fica para o CI.
- `python3 -m unittest tests.test_forge_mutante` (sem -I): `Ran 127 tests ... OK`.
- `bin/forge-mutante tests/mutantes/guarda-sem-mutante-4.json --processos 4` (rc=0): M25 a M32 `morreu`, nenhum sobrevivente nem inválido (M31 em bin/forge-mutante:533, M32 em :534).
- `bin/forge-mutante --conferir --base 86ac0fcb` (rc=0): `conferidas: o trecho de cada spec do diff está no lugar`.
- `forge-check docs` rc=0.
Veredito: aprovado. A contagem de AR-12 segue para o PR do autor (o brief restringe o commit ao parecer).
