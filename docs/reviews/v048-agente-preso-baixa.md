---
tipo: review
contrato: 1
pedido: v048
branch: melhoria/v048-agente-preso-baixa
commit: af5dde244f771d0bf2f1b45e1ddc9c41128e685f
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-28
---
# Review: v048 (E12.9, PR #963, AGENTE-PRESO-SEM-BAIXA, E12.2)

## Rodada 2 (delta, head af5dde24; E12.13)
Delta lido (`forge-check parecer delta`): `2a310c7c..af5dde24`, só `tests/mutantes/trava-agente-morto.json` (M6) e um comentário em `tests/test_agente_preso_baixa.py`, fora os pareceres. Cópia própria `wt/v048-agente-preso-baixa-tech-lead-3` por `forge-copia clone ... --revisao`, no af5dde24.
- ci: af5dde244f771d0bf2f1b45e1ddc9c41128e685f verde
- CI lido no run 46162734439: suíte partes 1 a 5, teto de pulados, instalação, bateria passos, python 3.14 e verificações longas, catraca e catraca (conferência) verdes; `bateria (pareceres)` e `bateria` esperam os pareceres
- A1 resolvido: o `de` do M6 agora é `entrada.get("promptSource") == "system":`, que aparece uma vez só em `hooks/agentes.py` (linha 492); `para` `True:`. O M6 foi realinhado, não retirado.
- S2 refeita no af5dde24: `test_toda_spec_do_forge_confere_com_a_fonte_fora_as_pendentes` OK; `bin/forge-mutante --processos 1 --ids M6 tests/mutantes/trava-agente-morto.json`: `M6 · morreu · hooks/agentes.py:492`.
- Comentário da S9 no teste: só comentário, cita a sonda e o comando de reprodução; sem efeito no comportamento. O delta não toca código de `hooks/` nem shell; H1 sem mudança.

## Rodada 1 (completa, head 2a310c7c)
Diff lido: `d056c2ca..2a310c7c` (commits abbbbd37 e 2a310c7c): `hooks/agentes.py`, `hooks/vigia.py`, `tests/test_agente_preso_baixa.py`, `tests/mutantes/v048-agente-preso-baixa.json`, `-2.json` e `changelog.d/v048-agente-preso-baixa.md`. Cópia própria `wt/v048-agente-preso-baixa-tech-lead-2` por `forge-copia clone ... --revisao --origem <URL do GitHub>`, no 2a310c7c.
- ci: 2a310c7c3f20f9d34118eff8602c6829819eaf01 vermelho (run 46160762619: `suíte (python 3.12, parte 4/5)` e `bateria` em failure; instalação, bateria passos, python 3.14 e verificações longas, catraca e catraca (conferência) verdes)
- Causa da parte 4/5 reproduzida por mim: `tests.test_forge_mutante.ConferirTodas.test_toda_spec_do_forge_confere_com_a_fonte_fora_as_pendentes` falha com `['tests/mutantes/trava-agente-morto.json: M6'] != []` (A1, S1). Mesma causa achada pela segurança (A1 de `docs/security/v048-agente-preso-baixa.md`).
- Afetados (local): `python3 -m unittest tests.test_agente_preso_baixa tests.test_trava_agente_morto`, 68 testes OK.
- Mutantes refeitos por mim (R-PROVA): `bin/forge-mutante --processos 1` nas duas specs: M1 a M13 morreram (M6, M7 e M12 por erro do teste declarado sob o mutante). `--cobertura --base d056c2ca`: toda condição mudada do diff declarada, rc=0. Sem shell no diff.
- Tamanho (H1): cerca de 70 linhas de código em `hooks/`, contando docstrings; um comportamento (a baixa provada do agente parado), abaixo do teto.

## O que conferi
- **Baixa só com prova (TRAVA-AGENTE-MORTO, R-TETO):** a forma nova (`attachment` com `queued_command`, `commandMode` e `origin.kind` `task-notification`, fora de sidechain) só troca de onde vem o texto; o cabeçalho `NOTIFICACAO` do início, o carimbo depois do `desde`, o `toolUseId` do meta e a trava `pesado` para escrita seguem iguais. Conferi a forma contra os transcripts reais da máquina: 278 anexos `queued_command` de notificação, todos com `isSidechain` falso e `origin` `{"kind": "task-notification", "producer": "session-task"}`; a mensagem de subagente devolvida (`origin.kind` `peer`) e o texto do dono vêm com `commandMode` `prompt` e não passam. Campo ausente ou de outro tipo levanta e `notificacoes` pula.
- **`--limpar`:** monta um `Stop` sem `agent_id` por sessão do registro e chama o mesmo `atualizar_estado`; o ramo do `Stop` não tira nada sem `agent_id`, então só saem o vencido, a sessão morta e o que a `Liberacao` prova. Não há baixa por escolha. Sem sessão no registro, roda uma vez (prazo e sessão morta).
- **Dois transcripts da mesma sessão:** `transcript_path` vai `None` e a `Liberacao` não lê nada; o registro fica (teste e M8).
- **Registro ilegível:** `ler_estado` levanta `EstadoIlegivel` antes de qualquer gravação; sai 1, nada regravado (teste e M7). Outros erros (config ilegível, `fixar_estado_do_clone` que levanta, gravação negada) também param antes ou na gravação atômica, com traceback em vez da mensagem (A4).
- **Vigia:** a `Liberacao` só lê (os soltos ficam na memória, sem gravar nem logar); a trava `pesado` é a da pasta do `agentes.json` (`_run`), com teste. O `arquivo_de_estado` `None` segue levantando no `ler_estado` antes do `.parent`, e o chamador cala.
- **docs/hooks.md:** precisa citar o `--limpar` e a forma nova; é recomendação (A2).

## Achados
- A2 (recomendado) docs/hooks.md:101 · o texto diz "só o `transcript_path` da sessão atual" e "Não há liberação manual"; falta citar o `agentes.py --limpar` (as mesmas provas, sob demanda, transcript achado pela sessão do registro) e a forma `queued_command` do aviso.
- A3 (recomendado) hooks/agentes.py:468 · o C3 diz que o transcript sai "nunca de campo do registro", e o `--limpar` (linha 1518) o acha pela `sessao` do registro; registrar a exceção no docstring (o registro é protegido e o caminho é revalidado), para o C3 não parecer violado.
- A4 (recomendado) hooks/agentes.py:1510 · o ramo do clone (`fixar_estado_do_clone` falso) não tem teste próprio (M6 troca a condição inteira e o teste cobre só `raiz None`), e erro de gravação ou de config sai com traceback; teste do ramo e mensagem curta com onde rodar (terminal do dono).

## Sondas
- S1 · python3 -m unittest tests.test_forge_mutante.ConferirTodas.test_toda_spec_do_forge_confere_com_a_fonte_fora_as_pendentes (no 2a310c7c) · espera: OK · obtido: AssertionError ['tests/mutantes/trava-agente-morto.json: M6'] != [], igual ao CI run 46160762619 (o A1 da rodada 1, resolvido na rodada 2)
- S2 · python3 -m unittest tests.test_forge_mutante.ConferirTodas.test_toda_spec_do_forge_confere_com_a_fonte_fora_as_pendentes (no af5dde24) · espera: OK · obtido: OK; M6 · morreu · hooks/agentes.py:492

## Parecer
Rodada 2: aprovado. O único bloqueante (A1, spec do M6 fora da fonte) está corrigido: o M6 casa com a guarda nova, morre sob o teste declarado e o CI do af5dde24 está verde. A2 a A4 seguem recomendados e viram cartão depois do merge (R-REVIEW).

Rodada 1:
Reprovado por um só motivo: o CI do Revisar-sha está vermelho (A1), pela spec velha do M6 da TRAVA-AGENTE-MORTO, que o diff deixou sem casar com a fonte. É defeito provado (S1) e o brief só aprova com o CI verde; a correção fica em `tests/mutantes/` e não toca o código. O mérito está bom: a baixa nova exige os mesmos campos de prova da antiga e mais os da forma do anexo, conferida contra transcripts reais; o `--limpar` reaproveita o caminho do hook sem atalho; registro ilegível e transcript ambíguo mantêm o registro. Na volta leio só o delta (`forge-check parecer delta`) e o CI do head novo. A2 a A4 são recomendados e viram cartão depois do merge (R-REVIEW).
