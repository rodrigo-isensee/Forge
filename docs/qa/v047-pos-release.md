---
tipo: qa
contrato: 1
pedido: v047-pos-release
branch: melhoria/v047-pos-release
commit: 76e00f859a469a2067bc8106f7ba89224b67cc90
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-16
---
# QA: v047-pos-release

Item E2.223 (POS-RELEASE-SCRIPT-UNICO, Q5): `scripts/pos-release` no modelo de projeto. Sem especificação de UX nem contrato de API; os critérios vêm do cartão e do cabeçalho do script (CA-1 a CA-6 abaixo, derivados dele). A suíte inteira roda no CI do PR: ainda não há PR nem check-run `bateria` para este sha (consulta à API sem retorno), então não cito `run`.

## Achados
- A1 (bloqueante) templates/projeto/scripts/pos-release:31 · Resolvido em 76e00f85. Só linha vazia ou que começa por # é ignorada; recuada com comentário, sem chave ou com padrao recuado agora é recusada (rc 2). Coberto por test_linha_recuada_ou_com_comentario_no_fim_nao_e_pulada.
- A2 (recomendado) tests/test_pos_release.py:110 · Resolvido em 76e00f85. Testes novos para linha que não casa com chave e para nome de passo vazio; mutantes PR20 e PR21 mortos.

## Revalidação (volta 1, delta fb7dccb4..76e00f85)
`forge-check parecer delta` listou script, passos, doc, testes, mutantes e changelog. Conferi o diff: o único código de guarda novo é a linha 31 (regex), a máscara (linha 56) e o doc/modelo. Sondas e testes cobrem as três; a máscara sobre-mascara de propósito (vai até o último @), sem vazar segredo.
- `python3 -m unittest tests.test_pos_release`: 20 testes, OK. `shellcheck templates/projeto/scripts/pos-release`: rc 0.
- Vermelho contra fb7dccb4 (`forge-testes --vermelho fb7dccb4 --modulos tests.test_pos_release`): prova (asserção)=2 (linha recuada; máscara com @, / e consulta); nenhum cai no HEAD. test_passo_com_nome_vazio passa na base (guarda já existia, sem teste); prova por mutante PR21.
- Mutantes (`bin/forge-mutante` nas 3 specs, rev=76e00f859a46): PR1 a PR15, PR17 a PR23 morreram (22 de 22; PR16 inexistente, lacuna de numeração). A saída não trouxe linha `base=` (rodou o conjunto inteiro). Cobertura conferida à mão: cada linha de guarda mudada (31, 32, 40, 56) tem mutante.
- A suíte inteira roda no CI do PR; ainda não há PR para este sha, então não cito `run`.
- Bug docs/qa/bugs/v047-pos-release-comentario-recuado.md: corrigido no head; sem bug aberto.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| CA-1 ensaio/real rodam os passos na ordem e resumem em 1 linha | test_ensaio_em_alvo_descartavel..., test_real_em_alvo_real_roda | modo ensaio e modo real | passou |
| CA-2 recusa antes do 1º comando (rc 2): vazio, ausente, padrão, modo inválido, regras ambíguas, alvo fora da regra do modo | test_recusa_* , test_ensaio_recusa..., test_real_recusa... | alvo vazio/ausente; igual ao padrão; real em descartável e vice-versa | passou |
| CA-3 para no 1º erro (rc 1) e diz qual e quantos não rodaram | test_para_no_primeiro_erro_e_diz_qual | passo do meio | passou |
| CA-4 arquivo de passos malformado ou incompleto recusa | test_recusa_chave_desconhecida..., test_recusa_arquivo_sem_passo..., test_recusa_arquivo_de_passos_ausente | arquivo ausente; sem passo; sem regra | passou (A1 corrigido: linha recuada recusa) |
| CA-5 credencial do alvo mascarada no resumo | test_mascara_a_credencial... | usuário:senha@ simples | passou (senha com @ ou /, password=, senha=, token= também) |
| CA-6 modelo entregue recusa até o projeto preencher; passos recebem o alvo e rodam na raiz | test_modelo_entregue_recusa..., test_passos_recebem_o_alvo... | modelo vazio | passou |

## Cenários e resultado real
- `python3 -m unittest tests.test_pos_release`: 17 testes, OK.
- Vermelho antes do verde, `forge-testes --vermelho 9d10894f --modulos tests.test_pos_release`: contagem: prova (API ausente)=16; prova (asserção)=1; nenhum teste cai no HEAD.
- Mutantes, `bin/forge-mutante tests/mutantes/v047-pos-release.json tests/mutantes/v047-pos-release-2.json` (rev=fb7dccb4f31f): PR1 a PR15, PR17 e PR18 morreram (17 de 17; o id PR16 não existe, só lacuna de numeração). Cobertura da lista conferida à mão contra o diff (a ferramenta só diz `não coberto` para shell): as guardas das linhas 22, 26, 40-58, 68-86 têm mutante; as linhas 31 e 45 (parte do nome) não têm.
- `shellcheck` do script: ver Provas. Sondas manuais: linha sem `:` recusa (rc 2); passo `n :: echo x` roda; linha recuada com `#`: furo (A1).
- Acessibilidade e E2E de navegador: n/a (script de linha de comando).

## Bugs
- docs/qa/bugs/v047-pos-release-comentario-recuado.md (alta, corrigido em 76e00f85)
