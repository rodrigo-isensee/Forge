---
tipo: qa
contrato: 1
pedido: v047-pos-release
branch: melhoria/v047-pos-release
commit: fb7dccb4f31f290b147879709dafff67cebc7038
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 1
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-16
---
# QA: v047-pos-release

Item E2.223 (POS-RELEASE-SCRIPT-UNICO, Q5): `scripts/pos-release` no modelo de projeto. Sem especificação de UX nem contrato de API; os critérios vêm do cartão e do cabeçalho do script (CA-1 a CA-6 abaixo, derivados dele). A suíte inteira roda no CI do PR: ainda não há PR nem check-run `bateria` para este sha (consulta à API sem retorno), então não cito `run`.

## Achados
- A1 (bloqueante) templates/projeto/scripts/pos-release:31 · Linha recuada com # em qualquer ponto vira comentário: padrao recuado some e o alvo padrão passa; passo recuado é pulado e o resumo diz OK. Reproduzido (rc=0). Sem teste de linha recuada. Mesma causa do A1 do review.
- A2 (recomendado) tests/test_pos_release.py:1 · Sem teste para linha que não casa com chave: valor (script:32) nem para nome de passo vazio (script:45, o mutante PR10 só cobre comando vazio).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| CA-1 ensaio/real rodam os passos na ordem e resumem em 1 linha | test_ensaio_em_alvo_descartavel..., test_real_em_alvo_real_roda | modo ensaio e modo real | passou |
| CA-2 recusa antes do 1º comando (rc 2): vazio, ausente, padrão, modo inválido, regras ambíguas, alvo fora da regra do modo | test_recusa_* , test_ensaio_recusa..., test_real_recusa... | alvo vazio/ausente; igual ao padrão; real em descartável e vice-versa | passou |
| CA-3 para no 1º erro (rc 1) e diz qual e quantos não rodaram | test_para_no_primeiro_erro_e_diz_qual | passo do meio | passou |
| CA-4 arquivo de passos malformado ou incompleto recusa | test_recusa_chave_desconhecida..., test_recusa_arquivo_sem_passo..., test_recusa_arquivo_de_passos_ausente | arquivo ausente; sem passo; sem regra | passou, mas linha recuada com # fura (A1) |
| CA-5 credencial do alvo mascarada no resumo | test_mascara_a_credencial... | usuário:senha@ simples | passou (limite da máscara: A2 do review) |
| CA-6 modelo entregue recusa até o projeto preencher; passos recebem o alvo e rodam na raiz | test_modelo_entregue_recusa..., test_passos_recebem_o_alvo... | modelo vazio | passou |

## Cenários e resultado real
- `python3 -m unittest tests.test_pos_release`: 17 testes, OK.
- Vermelho antes do verde, `forge-testes --vermelho 9d10894f --modulos tests.test_pos_release`: contagem: prova (API ausente)=16; prova (asserção)=1; nenhum teste cai no HEAD.
- Mutantes, `bin/forge-mutante tests/mutantes/v047-pos-release.json tests/mutantes/v047-pos-release-2.json` (rev=fb7dccb4f31f): PR1 a PR15, PR17 e PR18 morreram (17 de 17; o id PR16 não existe, só lacuna de numeração). Cobertura da lista conferida à mão contra o diff (a ferramenta só diz `não coberto` para shell): as guardas das linhas 22, 26, 40-58, 68-86 têm mutante; as linhas 31 e 45 (parte do nome) não têm.
- `shellcheck` do script: ver Provas. Sondas manuais: linha sem `:` recusa (rc 2); passo `n :: echo x` roda; linha recuada com `#`: furo (A1).
- Acessibilidade e E2E de navegador: n/a (script de linha de comando).

## Bugs
- docs/qa/bugs/v047-pos-release-comentario-recuado.md (alta)
