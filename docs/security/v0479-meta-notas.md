---
tipo: revisao-seguranca
contrato: 1
pedido: v0479-meta-notas
branch: melhoria/v0479-meta-notas
commit: 870159838c177a81663725861816f6c14914b512
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-18
---
# Review de segurança: v0479-meta-notas (v0478 E25.3)

Escopo: diff `0c47762a..87015983`, foco em `hooks/meta.py` (`notas_da_rodada`, `notas_em_outro_idioma`, `medir_mensagem`), que passa a ler o transcrito da sessão (entrada grande e não confiável) para medir o idioma das notas entre chamadas de ferramenta.

## Gatilhos
Gatilhos: hook (leitura de entrada não confiável, registro em `mensagens.jsonl`)

## Achados

## Sondas

## Detalhe dos achados
Sem achado bloqueante nem recomendado. O que foi conferido:

- **Teto de leitura:** a leitura passa por `linhas_do_fim` (`hooks/meta.py:129-137`), presa a `LEITURA_MAXIMA` (4 MiB do fim, `hooks/meta.py:37`); o texto juntado das notas para em `TETO_DA_MEDIDA` (20000 caracteres, `hooks/meta.py:284-288`). Linhas com `"tool_result"` ou sem `"user"`/`"assistant"` nem se decodificam (`hooks/meta.py:271-272`). Sonda local (pior caso de cada forma, arquivo de 3 a 5,6 MB): 90 mil linhas curtas de assistente 0,99 s; 3000 notas longas em outro idioma 0,03 s com 20000 caracteres; uma nota de 4 MB 0,13 s com 20000 caracteres; JSON aninhado 1,5 milhão de níveis 0,08 s (RecursionError tratado); lixo com a palavra-chave 0,03 s. O custo é limitado e cabe no tempo do hook.
- **Falha:** é medida, não controle. Erro de forma (`message` ou bloco não dict, texto não string) é pulado sem exceção (`hooks/meta.py:279-283`; o dict vazio de `:281` só vale com `message` dict); qualquer exceção restante cai no `except Exception` de `principal` (`hooks/meta.py:333-336`), que só registra no erros.log e não muda a decisão do Stop, já tomada em `avaliar_meta`. Falha aberta aqui é o correto: a medida não guarda nada.
- **Vazamento do transcrito para o registro:** a linha gravada leva só `notas_em_outro_idioma` (inteiro, soma de booleanos, `hooks/meta.py:297`) e o booleano `outro_idioma` (`hooks/meta.py:318`); nenhum texto de nota, nem o idioma por nota, chega a `mensagens.jsonl`. As exceções possíveis no caminho novo (decodificação já tratada) não carregam o texto ao erros.log.
- **Origem do caminho:** `transcript_path` vem do evento do próprio cliente (fronteira confiável); caminho apontado para arquivo arbitrário só seria lido até 4 MiB e reduzido a uma contagem, sem caminho de ataque realista.
- **Subagente e rodada:** `isSidechain` fora e parada na última fala do dono (`texto_do_dono`, `hooks/vigia.py:299-314`) limitam a rodada; os testes `test_nota_de_subagente_nao_conta`, `test_nota_de_rodada_anterior_nao_conta`, `test_resultado_de_ferramenta_nem_se_decodifica`, `test_registro_fora_da_forma_e_pulado_sem_erro` e `test_notas_param_no_teto_da_medida` (`tests/test_meta.py`) cobrem os casos de abuso.

Observação de custo, não de segurança: o Stop agora lê o fim do transcrito até três vezes (`hooks/meta.py:142`, `:156`, `:270`); somado, continua limitado (até 12 MiB, cerca de 1 s no pior caso medido).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Testes rodados: `python3 -m unittest tests.test_meta` (43 testes, OK) e a sonda de tempo descrita acima; a suíte inteira fica com o CI. Ferramentas de segredo, SAST e workflow ausentes do PATH neste ambiente (lacuna registrada); o diff não toca workflow nem dependência.
