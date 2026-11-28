---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-s1-status
commit: 154a36f1283ebb81be649cf08e1235f4636ba6a6
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-26
---
# QA: v0481 S1a, `forge-check status` (PR #910, E20.4, 1.ª rodada)

## Critério → teste → resultado
Escopo E20.1/E20.2 sem `CA-n` numerado: cada obrigação do brief vira um teste.

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| seis linhas `status:` | Executar.test_sem_rede_... | n/a | passou |
| último merge, idade | Itens.test_ultimo_merge_* | resposta fora da forma, data ilegível | passou |
| PRs por estado | Itens.test_prs_* | lista vazia, número não inteiro | passou |
| contador | Contador.* | falha, silêncio, prazo estourado | passou |
| decisões abertas e idade | Itens.test_decisoes_* | zero, sem data, leitura recusada | passou; data inexistente agora não verificável, rc 0 (Itens.test_decisoes_com_data_fora_do_calendario_nao_verificavel, PeloForgeCheck.test_pergunta_com_data_inexistente_nao_verificavel_e_rc_0 e a variante de mês 13) |
| versão publicada e plugin | Itens.test_ultima_versao, test_plugin_da_sessao | tag vazia, plugin ilegível | passou |
| sem rede: não verificável, rc 0 | Executar, PeloForgeCheck | sem gh, `--agora` sem fuso (rc 2) | passou |
| só leitura, sem rede além de leitura | leitura do código | n/a | passou: só gh api GET, gh pr list, gh release view, git de leitura via forge-contador e cmd_abertas; nada grava, sem fetch; testes com gh falso (pasta_com_gh, gh_json injetado) |
| índice do Forge em dia (CI) | test_indice_forge | arquivo novo em bin/ | passou: docs/indice-forge.md regerado, linha de forge_estado.py |

## Revalidação do delta 0b412b4a..154a36f1
- A1 (data fora do calendário): corrigido em bin/forge_estado.py:100 (instante()); testes do ramo (2 datas, forge-check pela raiz e por --raiz-pedidos) e M33. Bug v0481-s1-status-data-invalida fechado.
- A2 (índice): corrigido, linha no índice; suíte 3/5 verde. A3 (fuso, recomendado) segue como cartão em Melhoria vista.
- Testes novos da limpeza ctx seguro (gh falso com ESC e U+2028) e M34.
- bin/forge-mutante tests/mutantes/v0481-s1-status-5.json: rev=154a36f1283e, M33 morreu (bin/forge_estado.py:100), M34 morreu (bin/forge_estado.py:134); sem sobrevivente.
- Resto da árvore: só o que veio da develop, não relido (ordem do dono de 26/11).
- ci: 154a36f1283ebb81be649cf08e1235f4636ba6a6 verde (suítes 3.12 e 3.14 partes 1 a 5, bateria (passos), bateria (python 3.14), bateria (verificações longas), instalação, teto de pulados, árvore provada na develop; bateria, bateria (pareceres) e catraca esperam parecer e rótulo)
