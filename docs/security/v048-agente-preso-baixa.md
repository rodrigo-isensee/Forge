---
tipo: revisao-seguranca
contrato: 1
pedido: v048
branch: melhoria/v048-agente-preso-baixa
commit: 2a310c7c3f20f9d34118eff8602c6829819eaf01
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-28
---
# Review de segurança: v048 (AGENTE-PRESO-SEM-BAIXA, E12.2), 1ª rodada

Escopo: `hooks/agentes.py` (forma `queued_command` aceita, comando `--limpar`), `hooks/vigia.py` (`agentes_rodando` com a mesma prova), `tests/test_agente_preso_baixa.py` e os 13 mutantes, de `d056c2ca..2a310c7c`. Base das provas: a da TRAVA-AGENTE-MORTO (`docs/security/trava-agente-morto.md`, C1 a C11), que esta entrega estende e não afrouxa.

## Gatilhos
Gatilhos: trava de controle do R-TETO (hook `agentes`), leitura de arquivo fora do repositório (transcript da sessão), comando novo que regrava o registro do teto.

## Ataques tentados (ordem do dono de 10:08)
Todos rodados como sondas locais sobre a `Base` de `tests/test_trava_agente_morto.py`, no head 2a310c7c; nenhum soltou o registro. O mérito de segurança do código está aprovado; o parecer só reprova pelo A1 (CI do Revisar-sha vermelho por uma spec de mutante velha).
- **Anexo forjado no transcript.** O transcript só é escrito pelo próprio Claude Code (o sandbox nega escrita em `~/.claude/projects`); o texto de agente, de ferramenta ou de par entra como string escapada, e `json.loads` da linha não cria chave de topo. Sonda: o anexo inteiro dentro de um `tool_result` fica (S4). Notificação real de outro agente cujo `<result>` traz o cabeçalho deste: fica, porque `NOTIFICACAO.match` só lê o início do `prompt` (`hooks/agentes.py:498`) (S3). E a C2 segue exigindo o `toolUseId` do `agent-<id>.meta.json` igual ao `<tool-use-id>` da nota.
- **Texto digitado pelo dono no meio do turno.** Exige os três campos juntos, `type queued_command`, `commandMode task-notification` e `origin.kind task-notification` (`hooks/agentes.py:477-480`); cada um é preso por teste (`test_anexo_com_um_campo_fora_da_forma_nao_libera`) e por mutante. Sondas: `origin.kind human` com o modo de notificação fica (S2); mensagem de par (`commandMode prompt`, `origin.kind peer`) com o cabeçalho fica (S1). Conferência passiva das formas reais nos transcripts locais (só estrutura, sem conteúdo): 559 anexos `human` e 3600 `peer`, todos `commandMode prompt`, nenhum começando pelo cabeçalho; as notificações vêm com `origin.kind task-notification`. Premissa residual: o Claude Code escolhe o modo pela origem e não pelo texto, o que não se prova sem o código dele.
- **Sidechain.** `isSidechain is not False` sai antes de qualquer forma (`hooks/agentes.py:490`); `True` e `None` têm teste, e as sondas com `"false"` e `0` ficam (S5). O transcript de subagente (`<sessão>/subagents/agent-*.jsonl`) nem é lido: `transcript_da_sessao` exige `projects/<projeto>/<uuid>.jsonl` pelo caminho real.
- **Glob ou caminho no `--limpar`.** A sessão do registro só procura transcript com `SESSAO_UUID.fullmatch` (`hooks/agentes.py:1501`); sondas `*`, `**`, `../x`, `<uuid>/../x`, 36 `?`, UUID maiúsculo e UUID com quebra de linha voltam lista vazia (S8). O caminho achado ainda passa por `transcript_da_sessao` (caminho real, pasta-avó igual a `~/.claude/projects`, nome `<sessão>.jsonl`), então pasta de projeto que é link para fora cai.
- **Dois transcripts da mesma sessão.** Com mais de um, `transcript_path` vai `None` (`hooks/agentes.py:1520`) e só valem prazo e sessão morta; teste `test_dois_transcripts_da_mesma_sessao_nenhum_vale`.

Outros pontos conferidos: no `--limpar` a C3 (registro da mesma sessão do evento) vira "o transcript da sessão gravada no registro"; quem forja a `sessao` do registro já escreve o `agentes.json` e poderia apagá-lo, e a nota ainda precisa do `agent-<id>.meta.json` da mesma sessão (C2), então não há ganho. O `--limpar` passa pela mesma trava (`hook.trava()` em `atualizar_estado`), recusa o registro ilegível sem regravar (`EstadoIlegivel`) e respeita o `hooks_desligados` pelo `Hook.projeto`. No vigia, o `Liberacao` só conta (os `soltos` não são gravados), lê a trava `pesado` da pasta do `agentes.json` (C9, teste `test_trava_pesado_e_a_da_pasta_do_registro`) e qualquer exceção cala o aviso, que é só informativo. Nota que chega antes do `desde` não solta (S7).

Fora do escopo desta entrega, já existente na TRAVA-AGENTE-MORTO: o carimbo usado é o da entrega da nota no transcript, não o do fim do agente; uma retomada registrada entre o fim e a entrega poderia ser solta pela nota velha. A forma do meio do turno entrega mais cedo que a do início de turno, então não amplia essa janela.

Sondas de ataque executadas (nenhuma prova bloqueante, por isso fora do bloco `## Sondas`): S1 par com cabeçalho; S2 `origin.kind human` com modo de notificação; S3 cabeçalho forjado no `<result>` de outra nota; S4 anexo aninhado em `tool_result`; S5 `isSidechain` `"false"` e `0`; S6 `prompt` que não é texto; S7 nota antes do `desde`; S8 sessões com glob e caminho. Todas: espera o registro mantido, obtido o registro mantido.

## Achados
- A1 (bloqueante) tests/mutantes/trava-agente-morto.json:46 · M6 (guarda C1 do promptSource system) não casa mais com a fonte: o de termina em "and " e a linha nova em ":"; a suíte do Revisar-sha fica vermelha (parte 4/5) e a spec da trava perde o mutante. Corrigir o de de M6 para a linha nova ou retirá-lo (v048-2 M3 cobre).

## Sondas
- S9 · python3 -m unittest tests.test_forge_mutante.ConferirTodas.test_toda_spec_do_forge_confere_com_a_fonte_fora_as_pendentes (no 2a310c7c) · espera: OK · obtido: AssertionError ['tests/mutantes/trava-agente-morto.json: M6'] != [], igual ao CI run 46160762619

## Detalhe dos achados
A1. Evidência: `tests/mutantes/trava-agente-morto.json:46` (M6, `de` `entrada.get("promptSource") == "system" and `) contra `hooks/agentes.py:492`, que agora termina em `== "system":`. Caminho: não é ataque; é a guarda de mutação de um controle de segurança (C1, texto do dono não solta o registro) que deixou de ser exercida pela spec dela, e o CI do Revisar-sha falha por isso (run 46160762619, jobs `suíte (python 3.12, parte 4/5)` e `bateria`). O controle em si segue coberto por `tests/mutantes/v048-agente-preso-baixa-2.json` M3 e pelo teste `test_mensagem_do_usuario_nao_libera`. Severidade: baixa no mérito; bloqueia porque é defeito provado e o brief só aprova com o CI do Revisar-sha verde. Correção mínima: trocar o `de` de M6 por `entrada.get("promptSource") == "system":` com `para` `True:`, ou remover M6 e deixar só o M3 novo. Esforço P. Dono: autor da E12.2. Na volta, mudança só em `tests/mutantes/` não reabre o mérito do código: confiro o delta e o CI.

Testes rodados localmente no head: `tests.test_agente_preso_baixa` e `tests.test_trava_agente_morto`, 68 testes, OK. A suíte inteira é do CI do PR #963.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Revisão estática e sondas locais com a biblioteca padrão; nenhuma ferramenta externa necessária para este diff (sem dependência, workflow nem segredo tocado).
