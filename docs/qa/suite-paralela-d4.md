---
tipo: qa
contrato: 1
pedido: suite-paralela-d4
branch: melhoria/suite-paralela-d4
commit: 84de155340ab1991d6aa494d1de96e221ae8628c
parecer: aprovado
revisor: forge:qa-engineer
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-22
---
# QA: SUITE-PARALELA-D4, revalidação por delta 36e913d..84de155 (renome em `tests/test_pre_push_trava.py`)

Código testado: `84de155` (o HEAD `d0f217f` só soma pareceres de review e devops em `docs/`). O delta de código é só o renome de "senha" para "vez" em nomes, comentários e docstrings de `tests/test_pre_push_trava.py` (autorizado pelo dono, 2026-10-22 03:54). Conferido linha a linha com `git diff`: nenhuma asserção, valor esperado ou chamada ao hook mudou; `grep senha` no arquivo não acha mais nada. O resto da entrega foi visto em `36e913d` e segue na tabela. Sondas e cópias só em `$TMPDIR`; sem correção de código de produção.

## Achados

## Obrigação → teste → resultado
| Obrigação | Teste / comando | Fronteira protegida | Resultado |
|---|---|---|---|
| Suíte inteira passa | `python3 scripts/suite-paralela.py` em clone de `84de155` | N = min(4, nproc) | passou: 1372 testes, OK (skipped=1), 4 processos, 120 s, rc 0 (a serial passou em `36e913d`, 469 s; o delta não toca produção) |
| Renome sem mudar comportamento | `python3 -m unittest tests.test_pre_push_trava` e `tests.test_forge.NeutralidadeDoNucleo` | fila de vezes (viva, morta, ordem de chegada) | passou: 25 testes OK em 9,4 s; neutralidade 3 OK |
| Plugin válido (visto em `36e913d`; o delta não toca o plugin) | `scripts/validar-plugin.sh` | n/a | passou: "Validation passed" (só aviso ICON_MISSING, pré-existente) |
| Suíte em paralelo com carga (visto em `36e913d`; 12 laços de CPU) | mesmo comando, laços em `$TMPDIR` | redução de N sob carga | passou: 1372 testes, OK, 0 TRAVOU, 277 s; o script reduziu sozinho para 2 processos ("carga alta, load 14,1 de 16"), então a corrida não foi exercida com 4 processos sob carga |
| Terminal fechado antes do fim do processo não marca travou | `EsperaDoTerminal.test_saida_fechada_antes_do_fim_do_processo_nao_marca_travou` | processo que fecha 0, 1, 2 e termina 2 s depois | vermelho no antigo, verde no novo (abaixo) |
| Pergunta sem resposta continua marcada como travou | `EsperaDoTerminal.test_pergunta_sem_resposta_continua_marcada_como_travou` | `ocioso=2`, processo aguardando stdin | passou (classe `EsperaDoTerminal`, 3 testes OK, 12,7 s) |

## Vermelho antes do verde
Cópia `git archive 36e913d` em `$TMPDIR/antigo`, com `tests/test_atualizar.py` de `36e913d~1` mais o teste novo. Comando: `python3 -m unittest tests.test_atualizar.EsperaDoTerminal.test_saida_fechada_antes_do_fim_do_processo_nao_marca_travou`, duas vezes. Falha observada nas duas: `AssertionError: -9 != 0 : pronto [TRAVOU esperando resposta]`. No código novo (worktree) a classe passa. Mutação: sem ferramenta gratuita na stack do Forge para estes arquivos; o vermelho acima faz o papel (reverter o helper derruba o teste).

## Observações (não bloqueiam)
- Rede: o sandbox negou `api.anthropic.com:443` durante a suíte e a validação do plugin, e `datadoghq.com` na validação. A origem é a base (`scripts/preparar-estacao.sh` chama `claude plugin list`; já registrada na segurança, cartão SUITE-REDE-API); nada foi enviado e nenhum teste falhou por isso (R-CUSTO preservado).
- A corrida corrigida só aparece com 4 processos sob carga no runner; localmente a carga reduz N para 2, então a evidência forte é o teste de janela larga (2 s), não a repetição sob carga.
- `test_sugerir.py` recebeu a mesma correção; coberto pela suíte inteira (verde), sem teste dedicado de janela larga.

## Observações desta revalidação (não bloqueiam)
- Sonda errada minha, descartada: a primeira execução paralela foi numa cópia de `git archive` sem `.git` e teve 2 erros e 1 guarda (testes que exigem repositório); no clone real de `84de155` a mesma suíte passou limpa. Registro para não repetir a sonda em cópia sem `.git`.
- Uma execução ficou 1200 s na fila e o hook barrou ("a vez não chegou"), porque outros revisores usavam a mesma máquina; a fila funcionou como desenhado (R-TETO) e a repetição passou.
- Rede: o sandbox negou `api.anthropic.com:443` durante a suíte; origem na base (`scripts/preparar-estacao.sh`), nada enviado, nenhum teste falhou por isso (R-CUSTO preservado).
- Mantidas as observações do parecer anterior sobre a corrida do terminal fechado: a evidência forte é o teste de janela larga (2 s), com vermelho no antigo (`-9 != 0`) e verde no novo.
