---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-g4-f1-aviso
commit: d92b3a07d25f6ac354b128937b30684c85dffb16
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-25
---
# Review de segurança: v0481 (E7.10, #885, G4 F1: modo aviso por grupo, só infra)

Lido: `6959cec2..d92b3a07` inteiro (`hooks/conformidade.py`, `hooks/conformidade.json`, `tests/test_hooks.py` classe `ModoPorGrupo`, as 3 fixtures `grupo-*`, `tests/mutantes/v0481-g4-f1-aviso*.json`, `docs/hooks-fixtures.md`, `changelog.d/v0481-g4-f1-aviso.md`). Primeira rodada de segurança da branch; sem parecer anterior.

Gatilhos: controle do Forge (hook `conformidade`, caminho de recusa de todas as regras dele; estado em `.forge/run/`).

## Conferência
- **Nenhum grupo passa a aviso.** `hooks/conformidade.json:108-115`: os 6 IDs (`R-CONFORMIDADE`, `R-CONTRIB`, `R-FLUXO`, `R-MAIN`, `R-REVIEW`, `R-VERIFY`) em `barrar`; o teste `test_a_politica_entregue_tem_todo_grupo_em_barrar` trava o conjunto de valores em `{"barrar"}`, então passar um grupo a `avisar` exige mexer no teste, à vista do review. A política só vem de `PLUGIN/hooks/conformidade.json` (`hooks/conformidade.py:3927`): o projeto não a sobrepõe.
- **A recusa é a de hoje em todo caminho** (`hooks/conformidade.py:1570-1578`). Só `modos` dict e `modos.get(grupo) == "avisar"` (igualdade exata com o texto) deixa passar; mapa ausente, não dict (texto, lista, None), grupo fora do mapa (toda regra além das 6, como `R-PROVA`, `R-BRIEF`, `VV-*`), valor `Avisar`, `aviso`, `True` ou `barrar` caem no `bloquear` de antes, com o mesmo texto e o mesmo `simples`. Coberto por `test_grupo_fora_do_mapa_mapa_ilegivel_ou_valor_desconhecido_barra_e_registra` (8 casos). `modo_por_grupo` fora de `politica_valida` é falha fechada, não brecha: o desvio de forma só pode cair em barrar. `grupo` nenhum chamador passa hoje (só o teste); vale o `rid`.
- **`GuardaDaProva.barrar`** (`hooks/conformidade.py:4203-4213`) só repassa `alvo` e `grupo`; as quatro condições e o `ForaDaProva` seguem iguais.
- **Registro.** Linha montada com `json.dumps` (sem injeção de linha por `alvo` com quebra), `alvo` cortado em 300 caracteres, só na pasta `run` que já existe, `O_NOFOLLOW` no arquivo (link plantado não é seguido: teste `test_registro_nao_segue_link_e_erro_dele_nao_muda_a_decisao`), `except Exception` que não muda a decisão, e o `PrazoVencido` (`BaseException`) atravessa até `prazo_vencido`. Nada de comando nem segredo vai ao arquivo; `.forge/run/` é caminho protegido (`hooks/conformidade.json:38`) e ignorado pelo git. Única ressalva: A1.
- **Só aperta ou neutro, por escrito: neutro.** Toda recusa de antes segue recusa (S2, S3 e as 3 fixtures `grupo-*`); o que muda é só a linha a mais no `comandos.jsonl`. O caminho `avisar` não existe na política entregue.
- **Para a F2 (fora deste delta, condição a levar ao plano):** com um grupo em `avisar`, `barrar` passa a retornar, e todo chamador que hoje conta com a saída (código depois do `self.barrar(...)`, as chamadas em sequência da `GuardaDaProva`) passa a seguir; cada grupo que for a `avisar` pede a leitura dos chamadores dele e o rótulo `afrouxa-regra` (R-CONFORMIDADE, R-CONTRIB).
- **Observação para o `tech-lead` (requisito, não segurança):** na sessão do Forge (`hook.raiz` None, `hook._run` None) o `registrar_recusa` cai no `except` e não grava: a recusa do `R-CONTRIB` pelo rótulo não entra na medida (S1: o FIFO plantado nem é aberto).
- Testes: `python3 -m unittest tests.test_hooks.ModoPorGrupo` → 6 testes, OK. Suíte inteira: só no CI do PR #885, no mesmo head `d92b3a07` (em andamento ao escrever; `bateria (pareceres)` e `catraca` vermelhas aguardam os pareceres; o merge depende de tudo verde).

## Achados
- A1 (recomendado) hooks/conformidade.py:1521 · registrar_recusa abre comandos.jsonl sem O_NONBLOCK nem conferir arquivo regular: FIFO plantado prende o hook até o prazo de 3 s, e a recusa sai como prazo vencido (outra regra e outro Corrigir). Use O_NONBLOCK e S_ISREG no fstat, como anexar_ao_log em hooks/agentes.py:1112.

## Sondas
- S1 · sessão do Forge (clone descartável, gh falso de conta alheia), FIFO em .forge/run e .git/forge/run, `gh pr edit 1 --add-label afrouxa-regra` · espera: recusa R-CONTRIB · obtido: codigo=2 em 0 s, R-CONTRIB (igual à base)
- S2 · projeto temporário, sem FIFO, `git push origin feature/x:main` · espera: recusa R-MAIN · obtido: codigo=2 em 0 s, R-MAIN (igual à base)
- S3 · o mesmo projeto com FIFO em .forge/run/comandos.jsonl · espera: recusa R-MAIN imediata, como na base · obtido: codigo=2 em 4 s, R-CONFORMIDADE prazo de 3 s vencido (base: R-MAIN em 0 s)

## Detalhe dos achados
**A1.** Evidência: `hooks/conformidade.py:1521` (`os.O_WRONLY | os.O_APPEND | os.O_CREAT | os.O_NOFOLLOW`, sem `O_NONBLOCK`). Caminho: quem consegue pôr um FIFO em `.forge/run/comandos.jsonl` (caminho protegido; exige já ter escrita ali) faz toda recusa do `conformidade` esperar o vigia de prazo. Na sessão vigiada a recusa se mantém (falha fechada, S3), mas com a mensagem do prazo, que esconde a regra real e manda "dividir a chamada"; sem `SIGALRM` o prazo não existe e o hook ficaria até o `timeout` do `hooks.json`, que libera (no Windows nativo, porém, `os.O_NOFOLLOW` não existe e o registro cai no `except` antes do `open`). Não há liberação provada: severidade baixa. Correção mínima: `os.O_NONBLOCK` no `open` e gravar só se `stat.S_ISREG(os.fstat(fd).st_mode)`, fechando o fd nos dois casos; um teste com `os.mkfifo` no lugar do arquivo que confere recusa com a regra original em menos de 1 s. Esforço P. Dono: o autor da branch (E7.7).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática, o teste da classe nova e as três sondas acima (scripts em pasta temporária, só clones descartáveis e projeto temporário; nada externo). Varredor de segredos, SAST e auditor de dependências: o delta não traz dependência nem segredo.
