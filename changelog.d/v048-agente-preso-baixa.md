### Corrigido
- Registro de agentes volta a dar baixa sozinho no agente que terminou: o hook agentes reconhece a notificação de tarefa que o Claude Code grava no meio do turno (anexo queued_command), o vigia deixa de avisar esse agente como preso e python3 hooks/agentes.py --limpar aplica as mesmas provas sob demanda (AGENTE-PRESO-SEM-BAIXA, v048 E12.2).
