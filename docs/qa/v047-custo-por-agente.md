---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-custo-por-agente
commit: b2a1470ae35196c6df3be1fb8c8c00046c42a6c7
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-16
---
# QA: v047 custo por agente (E2.354)

Item E2.312 (CUSTO-MEDIA-POR-AGENTE): `forge-check transcricao custo --media-por-agente`, no head b2a1470a. Sem especificação de UX nem contrato de API; as obrigações são o texto do item e a ajuda do parser (CA-1 a CA-6, abaixo). Suíte inteira: no CI do PR (check-run `bateria` do mesmo sha); aqui só os cenários do item.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| CA-1 faixa, média e máximo por agente, tabelas nas duas formas de cabeçalho | test_faixa_e_media_por_agente_nas_duas_formas_de_tabela | `—` no tokens ignorado; média inteira | passou |
| CA-2 só linha de tabela com colunas agente e tokens; fora de tabela fecha a tabela | test_linha_de_tabela_sem_cabecalho_de_agente_e_tokens_nao_conta, test_linha_curta_conta_como_ignorada | linha curta (3 células), tabela sem as colunas | passou |
| CA-3 agente vazio vira `-`; controle no nome não sai na linha | test_agente_vazio_sai_como_traco, test_controle_no_nome_do_agente_nao_sai_na_linha | vazio; ESC | passou |
| CA-4 lê da `--raiz-pedidos` se dada | test_le_da_raiz_pedidos_quando_dada | n/a | passou |
| CA-5 rc 1: arquivo ausente, link simbólico, acima de 2 MB, sem linha com tokens inteiros | test_sem_arquivo_sai_1_sem_medida, test_link_simbolico_sai_1, test_maior_que_o_teto_sai_1_e_no_teto_le, test_sem_linha_com_tokens_inteiros_sai_1 | teto 2 MiB: no limite lê, 1 byte acima recusa | passou |
| CA-6 rc 2 combinado com alvo, `--entregas`, `--pedido`, `--desde`, `--ate` | test_nao_se_combina_com_outra_entrada_do_custo | cinco combinações | passou |

## Cenários e resultado real
- Testes do item: `python3 -m unittest tests.test_medidas_m14b.CustoMediaPorAgente` na raiz do clone: `Ran 11 tests ... OK`.
- Vermelho antes do verde (R-QA): `forge-testes --vermelho 1b88640e` estourou meu prazo de 175 s (rc 124, plano com ~90 módulos); só imprimiu `vermelho: base=1b88640e8734 head=b2a1470ae351` e `revertidos à base: bin/forge-check, bin/forge_transcricao.py, changelog.d/v047-custo-por-agente.md`. Fiz à mão numa cópia em `$TMPDIR`, com os dois arquivos de `bin/` da base e os testes do HEAD: `Ran 11 tests ... FAILED (failures=10, errors=5)`; os 11 testes da classe caem (o de combinação, nos 5 subcasos). Prova manual; o veredito do `forge-testes` fica ao CI.
- Mutação (R-QA), 3 specs, 19 mutantes: `forge-mutante --processos 3 <3 specs>` rc 0, `pedido=v047 rev=b2a1470ae351`, M1 a M19 todos `morreu`.
- Cobertura: `forge-mutante --cobertura --base 1b88640e8734`: toda condição mudada em `bin/forge-check:9758` e `bin/forge_transcricao.py` (382, 392, 397, 400, 402, 405, 413, 416, 418, 423, 434) tem mutante declarado; nenhuma linha sem mutante, nenhuma isenta.
- Dado real: `transcricao custo --media-por-agente --raiz-pedidos /root/.forge-contrib` rc 0, uma linha por agente com faixa e média; aviso de leitura local em stderr.
- Permissões e abuso: link simbólico, arquivo grande e caractere de controle cobertos (CA-3, CA-5); sem rede.
- Acessibilidade e E2E: n/a (comando de terminal).
- Remoto: avançou só com os pareceres de review e segurança (8b67af3c, 712f9e90); trazido por merge, sem rebase. O código testado segue b2a1470a.
- PA-7 (`docs/engineering/achados-recorrentes.md`): AR-1 (lista de mutantes completa) e AR-2 (ramo de falha com teste) conferidos; AR-5: os testes rodam o `forge-check` com `-I`.
