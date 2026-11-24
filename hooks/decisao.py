#!/usr/bin/env python3
"""Forge: decisao (ANTI-ALUC-F4-HOOK-DECISAO, fatia L28a; v0478 E172.6) - avisa a mensagem ao dono com mais de uma decisão.

Stop da sessão do Jarvis (`agent_type` do papel `jarvis` em `conformidade.json`, pelo `sessao_do_jarvis` do `vigia`; a sessão
que não se identifica cala): lê a mensagem final ao dono (o campo last_assistant_message do evento; sem ele, a última do
transcrito, pelo `mensagem_ao_dono` do `meta`) e aplica a regra do `forge-check transcricao decisoes` (`medir_decisoes` de
bin/forge_transcricao.py, fonte única): mais de um grupo de opções A/B/C, ou um grupo sem "Recomendo", viola `R-DECISAO`.
Com violação, uma linha ao USUÁRIO (`systemMessage`; nunca `additionalContext` nem `decision`: ADR 0003, item 1) e saída 0.
Nesta fatia NUNCA bloqueia: o bloqueio (L28b, com `stop_hook_active`) só depois da medida e da decisão do dono.
Lê só TETO_DA_LEITURA caracteres do início da mensagem: o tempo não cresce com ela. Nada grava. Fora de projeto do Forge e
do clone do Forge: silêncio. Erro interno: silêncio e uma linha no erros.log (o `executar`). Só biblioteca padrão."""
import json
import sys

from _comum import PLUGIN, executar
from meta import mensagem_ao_dono
from vigia import sessao_do_jarvis

TETO_DA_LEITURA = 20000  # caracteres do início da mensagem, como o TETO_DA_MEDIDA do `meta`
AVISO = ("Forge decisao: a última mensagem traz mais de um grupo de opções ou um grupo sem \"Recomendo\"; "
         "uma decisão por vez, com a recomendação (R-DECISAO). Só aviso.")


def viola(texto):
    """A mensagem fere a regra de `forge-check transcricao decisoes`: `medir_decisoes` conta a violação (fonte única)."""
    sys.path.insert(0, str(PLUGIN / "bin"))
    from forge_transcricao import medir_decisoes
    return medir_decisoes({"stop": [texto[:TETO_DA_LEITURA]]})["stop"][2] > 0


def principal(hook):
    if hook.campo("hook_event_name") != "Stop":
        return
    if hook.projeto(hook.cwd(), clone_do_forge=True) is None:
        return
    if not sessao_do_jarvis(hook):
        return
    texto = mensagem_ao_dono(hook)
    if texto and viola(texto):
        print(json.dumps({"systemMessage": AVISO}, ensure_ascii=False))


if __name__ == "__main__":
    executar("decisao", principal)
