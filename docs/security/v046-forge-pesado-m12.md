---
tipo: revisao-seguranca
contrato: 1
pedido: v046
branch: melhoria/forge-pesado-m12
commit: cdfafd25f1f6dcbeb7d22caabdb58b68f53f6773
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-11
---
# Review de segurança: v046 (E14.2, `bin/forge-pesado`, M12)

Escopo: `git show cdfafd25` (1 commit, 5 arquivos): `bin/forge-pesado` (113 linhas), `tests/test_forge_pesado.py` (15 testes), 2 arquivos de mutantes, fragmento de changelog. Só leitura da branch (Z10); código extraído com `git archive` para pasta descartável.

## Gatilhos
Comando novo que lê o estado de um controle (hook `pesado`, trava e fila) e imprime texto vindo de arquivo gravado por outro processo. `R-SEGURANCA`.

## Achados
- A1 (recomendado) bin/forge-pesado:62 · `desde` não finito ou enorme em `pesado.json` dá `OverflowError` fora do `except (OSError, ValueError)` da linha 106: traceback e rc 1 (no `esperar`, o código de `fim=teto`; no `status`, não o 2 de estado ilegível); texto inteiro no detalhe.
- A2 (recomendado) bin/forge-pesado:98 · o cabeçalho promete leitura sem escrever, mas `Hook.run()` (hooks/_comum.py:2592) cria `.forge/run/` e o `.gitignore` dele quando faltam; efeito pequeno e idempotente, só documentar ou ler o caminho sem `run()`.

## Sondas
- S1 · `pesado.json` com `{"desde": Infinity, "agente":"x","comando":"y","pid":1}` em `.forge/run/` da cópia extraída, `python3 bin/forge-pesado status` · espera: rc 2 com mensagem de estado ilegível · obtido: `OverflowError: timestamp out of range for platform time_t`, rc 1

## Detalhe dos achados
**A1** (baixa, dono tech-lead, esforço P). Texto inteiro do achado: `desde` não finito ou enorme em `pesado.json` (JSON aceita `Infinity` e inteiro gigante) dá `OverflowError` em `fromtimestamp` (e em `estado`, linha 56, com inteiro gigante), fora do `except (OSError, ValueError)` da linha 106: traceback e rc 1, que no `esperar` é o código de `fim=teto`, e no `status` não é o 2 documentado de estado ilegível. Caminho de ataque: só quem já escreve em `.forge/run/` do próprio usuário (mesmo UID, pasta ignorada pelo git), ou o hook com bug; não ganha execução nem escalada, ganha um falso `fim=teto` ou queda do comando. Correção mínima: incluir `OverflowError` no `except` da linha 106 e exigir em `estado` que `desde` seja finito (`math.isfinite`) e `desde <= time.time()` mais folga; teste com `Infinity` e `10**400`. `pid_vivo` (hooks/pesado.py:133) tem o mesmo defeito para pid gigante (`os.kill` com `OverflowError`); o `forge-pesado` só o chama com `pid` do JSON, então a mesma correção cobre.

**A2** (informativa, dono tech-lead, esforço P). Não há escrita do estado da trava nem limpeza da fila; a única escrita é a criação da pasta de estado.

**Conferido sem achado.**
- Saída escapada: `agente`, `comando` (cortado em 80 caracteres antes) e `pid` passam por `json.dumps` (`:64-67`); ESC, CR e quebra de linha viram `\u001b`, `\r`, `\n`; `desde` só entra como `isoformat` de número; teste `test_comando_com_caractere_de_controle_sai_escapado` cobre. Sem `shell=True`, sem `eval`, sem subprocesso.
- Fila (`esperando`, `:38-50`): ignora link simbólico, abre só leitura e tenta `flock` compartilhado sem bloqueio; não apaga nem grava. Resíduo: a checagem de link e o `open` não são atômicos, e uma senha numérica que seja FIFO bloquearia o `open`; exige escrita local na pasta de estado do mesmo usuário, sem ganho, tratado como aceitável.
- `--teto` limitado a (0, 540] e `--passo` > 0 (`:90-91`); NaN falha na comparação e é recusado; o `esperar` não ocupa a vez (só lê), logo não há negação de serviço da fila.
- Não decide pela vida do pid (só mostra), como pede a skill `esperar-estado`; sem segredo, sem caminho pessoal, sem rede, sem dependência nova.
- `tests.test_forge_pesado` no head: 15 testes OK (9 s). Mutantes (16) lidos como dados, não reexecutados.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do diff, testes dos arquivos tocados, sonda S1. Ausentes no PATH (lacuna, não instaladas): varredor de segredos dedicado, SAST, auditoria de dependências e linters de workflow; o CI do PR cobre a varredura. O parecer está em `/workspaces/.forge-contrib/docs/security/` e não foi commitado na branch (Z10, brief: gravar no caminho da raiz de pedidos).
