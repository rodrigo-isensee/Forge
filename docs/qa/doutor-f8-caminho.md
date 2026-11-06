---
tipo: qa
contrato: 1
pedido: versao-033
branch: melhoria/doutor-f8-caminho
commit: c5eb2465b09751cc80ea316d131844960cd95f36
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-04
---
# QA: doutor-f8-caminho (N-DOUTOR-F8-CAMINHO)

Testado: 85c5b80 (head do autor) mais o commit de teste do QA c5eb2465b09751cc80ea316d131844960cd95f36 (só `tests/test_qa_doutor_f8.py`; produção intocada). Review e segurança aprovados em 85c5b80, não repetidos. Escopo: o módulo da branch (D-5).

## Achados

## Critério → teste → resultado
| Critério (cartão) | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Cita `docs/engineering/protecao-de-branch.md` se existe | `test_so_o_de_docs_engineering` (QA, `bin/forge-doutor` real, `gh` falso) | arquivo presente | passou |
| Cita `docs/protecao-de-branch.md` se existe | `test_so_o_de_docs` (QA); `test_o_aviso_cita_o_passo_a_passo_so_se_o_arquivo_existe_na_raiz` (autor) | arquivo presente | passou |
| Os dois existem: um só, o de engineering | `test_os_dois_existem_cita_so_o_de_engineering` (QA) | precedência | passou |
| Nenhum existe: cita a skill `ci-cd` | `test_nenhum_arquivo_cita_so_a_skill` (QA); `test_main_sem_protecao_vira_problema_que_cita_a_branch_e_a_skill_ci_cd` (autor) | nenhum candidato | passou |
| Só se o arquivo existir (não basta o nome) | `test_diretorio_ou_link_quebrado_com_o_nome_do_arquivo_nao_conta` (QA: diretório e symlink pendente) | existe o nome, não é arquivo | passou |
| Vale para develop, homolog e main | `test_o_caminho_vale_para_cada_branch_sem_protecao` (QA, 3 avisos) | três branches | passou |
| Sem problema, o caminho não aparece | `test_protegidas_continuam_em_silencio_mesmo_com_o_arquivo` (QA) | branches protegidas, rc 0 | passou |

## Cenários e resultado real
- Os testes do QA rodam o `bin/forge-doutor` completo como subprocesso, com HOME, `gh` falso e raiz de projeto descartáveis (a `Base` do módulo do autor).
- Vermelho antes do verde: com `bin/forge-doutor` da base b45e40a e os testes do QA, caem 4 (`so_o_de_docs_engineering`, `so_o_de_docs`, `os_dois_existem`, `o_caminho_vale_para_cada_branch`); no head, 7 de 7 passam. Os outros 3 são guardas contra citar caminho inexistente e passam também na base, como devem.
- `python3 -I -m unittest discover -s tests -p test_doutor_protecao_gh.py` em 85c5b80: 15 testes, OK. Módulo novo `test_qa_doutor_f8.py`: 7 testes, OK.
- Mutação: o cartão não declarou spec e não é pedido de guarda de controle de decisão (só troca de texto); sem `tests/mutantes/doutor-f8-caminho.json`. As provas de vermelho acima matam as mutações óbvias (caminho fixo, caminho ausente, uma das duas entradas, ordem).
- Bugs abertos: nenhum.
