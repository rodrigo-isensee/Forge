---
tipo: qa
contrato: 1
pedido: suite-paralela-d4
branch: melhoria/suite-paralela-d4
commit: 36e913dc903714d77335271a70804bb7dd7a191d
parecer: aprovado
revisor: forge:qa-engineer
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-21
---
# QA: SUITE-PARALELA-D4, delta 8201795..36e913d (corrida do terminal fechado)

Código testado: `36e913d` (o HEAD `5099850` só soma pareceres em `docs/`). Substitui o parecer anterior (`1bdd3e8`); o delta é a correção em `tests/test_atualizar.py` e `tests/test_sugerir.py` depois do merge da develop `c092f1b`. Sondas e cópias só em `$TMPDIR`; sem correção de código de produção. Os pareceres de review, segurança e devops do pedido estão sem achados bloqueantes.

## Achados

## Obrigação → teste → resultado
| Obrigação | Teste / comando | Fronteira protegida | Resultado |
|---|---|---|---|
| Suíte inteira passa, serial | `python3 -m unittest discover -s tests -q` | n/a | passou: 1372 testes, OK, 469 s |
| Plugin válido | `scripts/validar-plugin.sh` | n/a | passou: "Validation passed" (só aviso ICON_MISSING, pré-existente) |
| Suíte em paralelo, máquina limpa (load 5,9) | `python3 scripts/suite-paralela.py` | N = min(4, nproc) | passou: 1372 testes, 4 processos, 168 s, 0 falha, 0 TRAVOU, árvore intacta |
| Suíte em paralelo com carga (12 laços de CPU) | mesmo comando, laços em `$TMPDIR` | redução de N sob carga | passou: 1372 testes, OK, 0 TRAVOU, 277 s; o script reduziu sozinho para 2 processos ("carga alta, load 14,1 de 16"), então a corrida não foi exercida com 4 processos sob carga |
| Terminal fechado antes do fim do processo não marca travou | `EsperaDoTerminal.test_saida_fechada_antes_do_fim_do_processo_nao_marca_travou` | processo que fecha 0, 1, 2 e termina 2 s depois | vermelho no antigo, verde no novo (abaixo) |
| Pergunta sem resposta continua marcada como travou | `EsperaDoTerminal.test_pergunta_sem_resposta_continua_marcada_como_travou` | `ocioso=2`, processo aguardando stdin | passou (classe `EsperaDoTerminal`, 3 testes OK, 12,7 s) |

## Vermelho antes do verde
Cópia `git archive 36e913d` em `$TMPDIR/antigo`, com `tests/test_atualizar.py` de `36e913d~1` mais o teste novo. Comando: `python3 -m unittest tests.test_atualizar.EsperaDoTerminal.test_saida_fechada_antes_do_fim_do_processo_nao_marca_travou`, duas vezes. Falha observada nas duas: `AssertionError: -9 != 0 : pronto [TRAVOU esperando resposta]`. No código novo (worktree) a classe passa. Mutação: sem ferramenta gratuita na stack do Forge para estes arquivos; o vermelho acima faz o papel (reverter o helper derruba o teste).

## Observações (não bloqueiam)
- Rede: o sandbox negou `api.anthropic.com:443` durante a suíte e a validação do plugin, e `datadoghq.com` na validação. A origem é a base (`scripts/preparar-estacao.sh` chama `claude plugin list`; já registrada na segurança, cartão SUITE-REDE-API); nada foi enviado e nenhum teste falhou por isso (R-CUSTO preservado).
- A corrida corrigida só aparece com 4 processos sob carga no runner; localmente a carga reduz N para 2, então a evidência forte é o teste de janela larga (2 s), não a repetição sob carga.
- `test_sugerir.py` recebeu a mesma correção; coberto pela suíte inteira (verde), sem teste dedicado de janela larga.
