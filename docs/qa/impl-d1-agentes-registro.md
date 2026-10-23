---
tipo: qa
contrato: 1
pedido: impl-d1-agentes-registro
branch: melhoria/impl-d1-agentes-registro
commit: 195e36ca91db52bb6ce9fd25d8e7a603c130537c
parecer: aprovado
revisor: forge:qa-engineer
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-22
---
# QA: impl-d1-agentes-registro

Escopo: `git diff c092f1b..195e36c` (F1 AGENTE-REGISTRO-PRESO, C1; o C2 não entrou, como o desenho manda sem a reprodução). Fontes: desenho em `docs/propostas/aq/melhorias-f1-f10.md` §1 e modelo de ameaças `docs/security/ameacas/melhorias-f1-f10.md` §2.1 (L1). O pedido não tem especificação de UX nem `CA-n`: as obrigações são o desenho (F1) e os controles C1-1 a C1-8. Depois do commit testado entraram só os pareceres de review e de segurança (aprovados).

## Achados

## Critério → teste → resultado
| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| F1: sessão morta libera a vaga na hora, sem esperar o prazo | fixtures `sessao-morta-libera`, `duplicado-de-sessao-morta-libera`; sonda de ponta a ponta (abaixo) | PID de processo real encerrado, no teto 1 | passou |
| F1: nunca solta sessão viva, teto e duplicado intactos (C1-8, R-TETO) | `sessao-viva-mantem`, `duplicado-de-sessao-viva-barra`, `fim-de-um-nao-solta-o-de-sessao-viva`; sonda: B barrada com A viva | PID vivo; teto 1 | passou |
| C1-1: PID de tipo ou faixa inválidos mantém o registro | `pid-texto`, `pid-booleano`, `pid-fracionario`, `pid-zero`, `pid-negativo`, `pid-acima-do-limite`, `pid-gigante-nao-derruba-o-hook` e o teste unitário `test_registro_de_agente_solta_so_com_prova_de_sessao_morta` | 0, -1, 1.5, True, texto, `pid_max`+1, 2**63 | passou |
| C1-2: erro em um registro não derruba `vigentes` | teste unitário (registros `None`, texto, número, `desde` inválido; `PermissionError` e `RuntimeError` simulados) | lista com registro malformado | passou |
| C1-3: outro namespace, namespace ilegível ou ausente mantém | `outro-namespace-mantem`, `namespace-ilegivel-mantem`, `sem-namespace-gravado-mantem` | namespace diferente ou vazio | passou |
| Registro antigo sem PID segue o prazo | `registro-sem-pid-segue-prazo` | sem campo `pid` | passou |
| C1-4: só grava PID vivo, válido, fora de casca e com `session_id` | `reserva-grava-pid-e-sessao`, `reserva-sem-session-id-nao-grava-pid`, `inicio-sem-par-grava-pid-da-sessao`, unitário de `da_sessao` (PID morto, casca, sem sessão) | sem `session_id`; casca; PID morto | passou |
| C1-5: `SubagentStart` só casa a reserva da mesma sessão e não herda PID | `inicio-so-casa-reserva-da-mesma-sessao`, `inicio-casa-reserva-da-sessao-e-mantem-pid`, `inicio-sem-session-id-nao-leva-pid` | sessões diferentes; sem sessão | passou |
| C1-6: nenhum escape novo por ambiente | leitura do diff: sem variável nova; testes usam PID e namespace reais | n/a | passou |

## Cenários e resultado real
- **Suíte do arquivo alterado** (`python3 -m unittest tests.test_hooks`, cópia limpa do commit 195e36c em `$TMPDIR`): `Ran 42 tests`, `OK`. A suíte completa roda no pre-push; este parecer não repete o resultado dela.
- **Vermelho antes do verde.** Cópia com o commit testado e só `hooks/agentes.py` da base c092f1b (mesmo comando): `FAILED (failures=6, errors=1)`. Falham o teste unitário (erro: `namespace_de_pid` não existe) e as fixtures `sessao-morta-libera`, `duplicado-de-sessao-morta-libera`, `reserva-grava-pid-e-sessao`, `inicio-sem-par-grava-pid-da-sessao`, `inicio-sem-session-id-nao-leva-pid` e `inicio-so-casa-reserva-da-mesma-sessao`. As fixtures de "mantém" passam na base de propósito: guardam que o F1 não afrouxa o teto.
- **Reprodução do caso real (ponta a ponta, sem fixture).** Um processo faz de sessão A e roda o hook `agentes.py` de verdade (PreToolUse, teto 1, projeto git marcado); depois a sessão B tenta lançar com A viva; depois A é encerrada com `kill` e a sessão C tenta lançar. Base: A reserva, B barrada, C barrada com `R-TETO: 1 agentes ativos, teto 1` (registro preso depois da sessão morta). Entrega: A reserva e o registro traz `pid`, `pidns` e `sessao`; B barrada (código 2); C passa (código 0). Reproduz o defeito e a correção; sessão viva nunca é solta.
- **Mutação no diff** (`hooks/agentes.py`, 4 mutantes, rodados com o teste unitário e as fixtures): sem a checagem de namespace, `PermissionError` tratado como morte, sem o limite superior de `pid_max` e sem a exclusão de casca. Os 4 morreram (falha em pelo menos um teste). Nenhum sobrevivente.
- **Recomendações do review (10eb7b1), conferidas:** casar também a reserva sem `sessao` no `SubagentStart` é seguro (o confirmado perde o `pid`, cai no prazo, a vaga fica ocupada); `pid_max()` relido por registro é custo desprezível. Nenhuma bloqueia.
- **Recomendações da segurança (4f7f48d), conferidas:** R1 (gravar também o `boot_id` para hospedeiros que dividem a cópia por rede) e R2 (`pid == pid_max` aceito) não bloqueiam; ambas erram para o lado de contar a mais ou de efeito nulo, e R1 só vale num arranjo raro. Sugestão minha: abrir pedido próprio para R1 se o dono quiser.
- **Acessibilidade e E2E de interface:** não se aplicam (mudança só em hook de linha de comando, sem tela).
- **Limite honesto:** a prova de PID usa o namespace e o `/proc` do Linux; no Windows o desenho mantém o registro no prazo, e isso não foi exercitado aqui (sem ambiente).
