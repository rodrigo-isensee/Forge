---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0480-bench-versao
commit: 011c4c1e6d6eb550932e0d880b7a89244bb72190
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-24
---
# QA: bench de versões com agentes (#870, E175.3)

Escopo: `tests/bancada/versao.py`, `tests/test_bancada_versao.py`, `tests/mutantes/v0480-bench-versao.json`, `docs/bench-versao.md`, pedido e resposta fixos. Sem UI. A rodada real não foi executada (custo do dono, `R-CUSTO`): só os testes com `claude` e `gh` falsos e o roteiro sem `--executar`.

## Critério → teste → resultado
| Critério (docs/bench-versao.md) | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Só o dono roda: recusa com CI, GITHUB_ACTIONS, ANTHROPIC_API_KEY (`R-CUSTO`) | test_recusa_com_ci_github_actions_ou_chave_da_api; M1 | variável definida e vazia; com e sem `--executar` | passou |
| Padrão não chama o modelo, só valida e estima | test_sem_executar_so_valida_e_estima_sem_chamar | nenhuma chamada, nenhuma pasta criada | passou |
| Testes escondidos congelados pelo sha256 | test_teste_escondido_alterado_ou_ausente_recusa | alterado; ausente | passou |
| Marca em termos_proibidos_hash e na árvore da tag | test_marca_fora_do_config_ou_que_nao_bate_recusa, test_marca_na_arvore_da_tag_recusa; M5 | maiúsculas; hash que não bate | passou |
| Tag e `--repo` válidos | test_tag_inexistente_e_repo_malformado_recusam | tag ausente; repo sem barra | passou |
| Remoto vazio; uma rodada por vez | test_remoto_nao_vazio_recusa_antes_da_sessao, test_trava_de_outra_rodada_recusa; M4 | remoto com ref; trava existente | passou |
| Sessão `--permission-mode auto`, nunca bypass; retoma com a resposta fixa | test_rodada_retoma_com_a_resposta_fixa_avalia_o_pr_e_grava_a_linha | argv de cada chamada; `--resume` só na 2ª | passou |
| Forge instalado sai das configurações do projeto | mesmo teste; M8 | `enabledPlugins` removido | passou |
| Limites: 20 agentes, 3 voltas, tempo, tokens | test_mais_de_20_agentes_encerra_sem_retomar, test_20_agentes_ainda_cabem, test_sem_pr_para_nas_3_voltas_e_avalia_o_head, test_tokens_acima_do_limite_encerram, test_prazo_vencido_encerra_a_sessao_em_curso; M2, M3, M6 | 20 cabe, 21 estoura; 3 voltas; sessão em curso morre | passou |
| Tokens: usage por mensagem sem repetir; transcrições com subagentes | test_tokens_das_transcricoes_somam_subagentes_sem_repetir; M7 | id repetido, linha lixo, pasta ausente | passou |
| Linha do quadro, cabeçalho uma vez, marca no projeto | test_segunda_rodada_acrescenta_linha_sem_repetir_cabecalho, test_marca_no_projeto_aparece_na_linha | quadro existente | passou |

## Revalidação por delta (E3.7)
Intervalo `d2bdd9ab..011c4c1e` (`forge-check parecer delta`): versao.py, test_bancada_versao.py, 4 specs de mutante, pesos-d4.json, bench-versao.md, pedido fixo. Depois do 011c4c1e só entraram pareceres (7aca1f09, cb9c5a24), sem código.
- A1 (peso do módulo): resolvido. `tests/pesos-d4.json` ganhou `test_bancada_versao: 10.6`; `test_forge.py -k PesosDaSuite`: Ran 3, OK. O módulo mede 10,6 s localmente (Ran 26).
- A2 (SIGTERM sem prazo): resolvido por `encerrar()` (SIGTERM, 10 s, SIGKILL) e `leitor.join(ESPERA_KILL)`; coberto por M9 e M10.
- A3 (mutantes): resolvido para `--executar` e `claude` ausente; as condições novas do delta (recusa em sessão de agente, `api-paga`, `repo_descartavel`, cópia dos escondidos) têm M16 a M27.
- Cobertura do delta (`forge-mutante --cobertura --base d2bdd9ab`): sem mutante só em versao.py:131, 134, 135, 137 (normalização defensiva da saída do `gh`; o caso que decide, repo não público, vazio ou de outro dono, é o M21) e :229, :408. Mutei à mão o :229 (`ambiente_da_sessao` passa o ambiente inteiro) numa cópia: 1 teste cai. O :408 é a guarda do M1. Nada bloqueia.

## Provas
- Testes do módulo: `python3 -I -m unittest discover -s tests -p test_bancada_versao.py`: Ran 17 tests, OK (3,9 s); nenhum `skip`.
- Mutantes: `bin/forge-mutante tests/mutantes/v0480-bench-versao.json`: M1 a M8 `morreu` (rev=d2bdd9ab9e68), nenhum sobrevivente. Os 8 mutantes cobrem as guardas de decisão do diff; o que falta está em A3.
- Vermelho antes do verde: arquivo e testes novos, ausentes na base a27eab7e; sob cada mutante o teste cai (saída acima).
- Roteiro real sem `--executar` e sem a pasta do dono: `versao: teste escondido ausente: ~/.forge-bench/escondidos/romanos-v1/test_escondido.py` e `marca.txt`, rc 1; com `CI=1`: `recusado com CI definida(s)`, rc 2. Nada foi chamado e `~/.forge-bench` não foi criado.
- Vizinhos: test_bancada (19), test_comportamento (6), test_catraca (385) OK localmente.
- Falha reproduzida local (A1): `python3 -I -m unittest discover -s tests -p test_forge.py` no d2bdd9ab: `AssertionError: Lists differ: ['test_bancada_versao'] != []` em test_pr_nao_aumenta_os_modulos_sem_peso (test_forge.py:7313). Outra falha local, test_raiz_depois_do_subcomando_e_git_isolado, é do sandbox (gh sem rede). Severidade alta (bloqueia o CI); o relatório de bug fica neste achado, o brief pede só o parecer no commit.
- CI do mesmo sha (`gh pr checks 870`): `bateria` e as partes 3/5, 4/5, 5/5 (py 3.12) e 3/5, 5/5 (py 3.14) em `fail`; os logs não eram legíveis daqui, a ligação com A1 é provável, não confirmada.

## Limites
Não avaliei o comportamento do `claude` real (stream-json, `--resume`, caminho das transcrições): o roteiro depende do formato dele e só a primeira rodada do dono prova. O `docs/bench-versao.md` bate com o código (limites, cota, passos).

## Provas da revalidação (head 011c4c1e)
- Módulo: `python3 -I -m unittest discover -s tests -p test_bancada_versao.py`: Ran 26 tests, OK; nenhum `skip`.
- Mutantes: `bin/forge-mutante --processos 4` com as 4 specs `tests/mutantes/v0480-bench-versao*.json` (rev=011c4c1e6d6e): M1 a M27 `morreu`, rc 0, nenhum sobrevivente nem equivalente.
- Vermelho antes do verde: sob cada mutante o teste cai (saída acima); os testes novos do delta (17 para 26) não existiam no d2bdd9ab.
- Roteiro real: nunca rodei o `--executar`; `~/.forge-bench` não existe.
- CI do #870 (`gh pr checks`): `passos`, `verificações longas`, `catraca`, `instalação 3.14` e suítes 3.12 partes 1, 2, 4, 5 passam; `bateria (pareceres)` falha (esperado enquanto os pareceres do head não fecham) e as partes 3.14 estavam pendentes na leitura. Não cito o `bateria` como verde: o merge depende dele, este parecer não.
