---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-ae2-c1-contagem
commit: aa8e521a99a2708e2ed14c872d3b50989e4aefbd
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 1
data: 2026-11-20
---
# QA: v0478 (AE2 C1 e C3)

Pedido v0478 (branch melhoria/v0479-ae2-c1-contagem), etapa E56.3. Cobre `bin/forge_contador.py` (AE2 C1, contagem; AE2 C3, teto). Sem especificação de UX nem contrato de API: as obrigações são as da descrição do módulo e do desenho `v0479-ae2-contador` (seção 4.1), citadas nos nomes dos testes do autor.

## Achados
- A1 (recomendado) bin/forge_contador.py:25 · `\d` sem `re.ASCII` em TAG_DE_VERSAO, MERGE_DE_PR e SQUASH_DE_PR: a tag `v٩.٩.٩` vira marca e a versão sai `9.9.10`. Reproduzido; bug em docs/qa/bugs/v0479-ae2-c1-tag-com-digito-unicode.md.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Contagem desde a marca, dois merges e três cartões, repetido uma vez | Contagem.test_gatilho_dois_merges_tres_cartoes_depois_da_tag | repetido entre PRs, caixa | passou |
| Squash `(#N)` conta pela mensagem; commit direto não | Contagem.test_squash_conta_pela_mensagem | commit sem PR | passou |
| Sem tag, conta do primeiro commit; tag no topo, zero PR | Contagem.test_sem_tag_conta_desde_o_primeiro_commit, test_tag_no_topo_sem_prs | vazio | passou |
| Só tag na forma; vale a maior | Contagem.test_tag_fora_da_forma_e_ignorada_e_vale_a_maior, test_so_tag_na_forma_sem_nenhuma_valida | tag torta, 0.9 contra 0.10 | passou (ressalva A1: dígito não ASCII) |
| Assunto forjado dentro do PR não é PR | Contagem.test_assunto_de_merge_forjado_fora_da_primeira_linha_nao_e_pr, test_merge_sem_assunto_de_pr_nao_conta | forja de merge | passou |
| Byte inválido não derruba | Contagem.test_mensagem_com_byte_invalido_nao_derruba | UTF-8 inválido | passou |
| Forma do ID, 80 caracteres, vazio, caracteres especiais | Citacoes.test_ids_recusados, test_id_vazio_e_recusado, test_id_no_limite_de_80_passa | 80 e 81, controle, Cf | passou |
| Chave sem caixa, NFD, CRLF, separador | Citacoes.test_chave_sem_caixa_nfd_e_fim_de_linha_crlf, test_linha_que_nao_comeca_pela_chave_nao_conta, test_separador_unicode_nao_abre_linha | recuo, U+2028 (sondado) | passou |
| Repetido uma vez; teto de 10 por PR | Citacoes.test_repetido_conta_uma_vez, test_teto_de_dez_por_pr, test_dez_exatos_sem_aviso | 10 e 11 | passou |
| Não verificável: ref com hífen, ausente, git lento, ausente, falha no meio, GIT_* herdado | NaoVerificavel (6 testes) | falha fechada | passou |
| Teto C3: padrão 20, 1 a 200, valor que não vale com aviso | Teto.test_sem_arquivo_e_sem_chave_vale_o_padrao_calado, test_valor_que_vale, test_valor_que_nao_vale_usa_o_padrao_com_aviso | 0, 1, 200, 201, booleano | passou |
| Config ilegível: não objeto, grande, link, pasta, fifo | Teto.test_config_que_nao_e_objeto_json, test_config_por_link_nao_e_seguida, test_config_que_nao_e_arquivo_regular | recursão, 65536 bytes | passou |

## Cenários e resultado real
Execução local só do módulo tocado, com TMPDIR (sem suíte local; a suíte inteira é do CI do PR, I5).

- `python3 -I -m unittest discover -s tests -p test_contador.py`: `Ran 30 tests ... OK`.
- Vermelho antes do verde: `forge-testes --vermelho 5ccac0bf616cea83f070d6a2408285c0f5a02933 --modulos test_contador` saiu 0: `vermelho: base=5ccac0bf616c head=aa8e521a99a2 módulos=test_contador (restrito por --modulos)` e `contagem: prova (API ausente)=30` (os 30 testes `H=ok · B=erro`). Sem `--modulos` a ferramenta sai 2 (`módulo sem arquivo em tests/: test_placar`), sem veredito; ver Melhoria vista no relatório.
- Mutação (pedido de controle declara 24 mutantes em 3 specs): `bin/forge-mutante` das três specs, `--processos 3`, saiu 0: M1 a M24 todos `morreu` (14 deles `(erro)`, teste declarado com erro sob o mutante e verde sem ele). Nenhum sobrevivente, nenhum equivalente.
- Cobertura: `forge-mutante --cobertura --base 5ccac0bf...` lista 19 linhas de guarda de `bin/forge_contador.py` todas `coberta` por mutante declarado; a única `não coberto` é `tests/pesos-d4.json`, dado sem guarda.
- Sonda própria (fora da suíte): U+2028 e letra de largura total no ID são recusados; dígito Unicode na tag é aceito (A1).
- Sem acessibilidade nem E2E: módulo de biblioteca, sem interface.

Bugs: 1 baixo (`docs/qa/bugs/v0479-ae2-c1-tag-com-digito-unicode.md`), vira cartão.
