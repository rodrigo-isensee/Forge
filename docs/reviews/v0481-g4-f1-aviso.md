---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-g4-f1-aviso
commit: d92b3a07d25f6ac354b128937b30684c85dffb16
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-25
---
# Review: v0481 (E7.8, #885, G4 F1: modo aviso por grupo, só infra; classe C)

Lido: `6959cec2..d92b3a07` (`hooks/conformidade.py`, `hooks/conformidade.json`, `tests/test_hooks.py` classe `ModoPorGrupo`, as 3 fixtures `grupo-*`, `tests/mutantes/v0481-g4-f1-aviso*.json`, `docs/hooks-fixtures.md`, `changelog.d/v0481-g4-f1-aviso.md`) e o parecer de segurança da branch (`docs/security/v0481-g4-f1-aviso.md`, aprovado, mesmo sha). Primeira rodada de code review; sem parecer anterior.

## Conferência
- **Nenhum grupo passa a aviso.** `hooks/conformidade.json:107-115`: os 6 IDs em `barrar`; `test_a_politica_entregue_tem_todo_grupo_em_barrar` trava o conjunto de valores (mutante M10 morre).
- **Decisão do modo:** só `isinstance(modos, dict) and modos.get(grupo) == "avisar"` deixa passar (`hooks/conformidade.py:1569-1571`). Mapa ausente, não objeto, grupo fora do mapa e valor `Avisar`, `aviso`, `True` barram (8 casos no teste). Correto e com falha fechada na lógica.
- **Registro:** `json.dumps` (sem injeção de linha), `alvo` cortado em 300, só em pasta `run` existente, `O_NOFOLLOW`. Mas a gravação fica **antes** do `bloquear` e dentro do vigia de prazo, e o `open` bloqueia: A1.
- **Mutantes (V2):** `bin/forge-mutante --processos 1` nas duas specs, em `d92b3a07`: M1 a M10 morreram. `python3 -m unittest tests.test_hooks.ModoPorGrupo`: 6 testes, OK. Suíte inteira: só no CI do #885 (em andamento no head `1a5625bf` ao escrever), sem rerrodar.
- **Tamanho (H1):** cerca de 66 linhas de código (py + json), um comportamento; dentro do teto.
- **Guardas do diff:** as 10 linhas de guarda mudadas têm mutante declarado e teste de ramo de falha; nenhum teste lê o texto da fonte.

## Achados
- A1 (bloqueante) hooks/conformidade.py:1521 · open de comandos.jsonl sem O_NONBLOCK nem S_ISREG, antes do bloquear e sob o vigia: FIFO em .forge/run faz a sessão do Forge (raiz e cwd no clone, não vigiada) liberar push na main, --force e --no-verify (S1 a S3, código 0; base: 2).
- A2 (recomendado) hooks/conformidade.py:1515 · com hook._run None, o registro chama git (copia_principal) no caminho da recusa, sob o prazo de 3 s que na sessão do Forge não vigiada vira liberação; resolva a pasta sem subprocesso ou só use a pasta já resolvida.
- A3 (recomendado) hooks/conformidade.py:1574 · o aviso vai ao stderr com saída 0, que o Claude Code não mostra ao agente: a forma certa não chega a ninguém. Resolver antes da F4, que é quando um grupo vai a avisar.
- A4 (recomendado) docs/propostas/g4-fatias.md:36 · as linhas do vigia no mesmo comandos.jsonl não têm fonte nem alvo: pela definição escrita, toda recusa do vigia conta como falsa e cada recusa conta duas vezes. A medida filtra fonte=conformidade; docs/hooks.md (previsto na F1) não foi tocado.

## Sondas
- S1 · sessão do Forge (CLAUDE_PROJECT_DIR e cwd no clone com .claude-plugin), FIFO em .forge/run/comandos.jsonl, `git push origin feature/x:main` · espera: código 2, R-MAIN, como na base 6959cec2 · obtido: código 0 em 3,1 s, stderr vazio (liberado)
- S2 · a mesma sessão e FIFO, `git push --force origin feature/x` · espera: código 2, R-VERIFY (base: 2) · obtido: código 0 em 3,1 s, stderr vazio
- S3 · a mesma sessão e FIFO, `git commit --no-verify -m x` · espera: código 2, R-VERIFY (base: 2) · obtido: código 0 em 3,1 s, stderr vazio
- S4 · a mesma sessão, sem FIFO, os três comandos · espera: código 2 com a regra · obtido: código 2 em 0,2 s, R-MAIN, R-VERIFY, R-VERIFY, e a linha com fonte, grupo e alvo no comandos.jsonl

## Parecer
**Reprovado** por A1, defeito provado com gatilho. O item promete "o hook recusa igual a hoje em todo caminho" e "o registro não abre brecha"; as sondas mostram o contrário. A gravação da medida roda antes do `bloquear`, dentro do vigia de prazo de 3 s (`hooks/_comum.py:2820`). Com um FIFO no lugar do `comandos.jsonl`, o `os.open(O_WRONLY)` espera um leitor, o alarme dispara e o `prazo_vencido` decide. Na sessão vigiada a decisão continua recusa, só que com a regra trocada (é a S3 da segurança). Na sessão do Forge com o cwd no clone, que não é vigiada (`sessao_vigiada` com `clone_do_forge=False`, `hooks/_comum.py:254`), o `prazo_vencido` libera. As travas de push na main, `--force` e `--no-verify` passam (S1 a S3). Na base `6959cec2`, com o mesmo FIFO, as três recusam em 0,1 s. A segurança descartou a liberação com base no caminho do rótulo (`hook.raiz` None), mas o caminho das travas é outro: `prova_fora_de_projeto` atribui `hook.raiz` (`hooks/conformidade.py:4452`) e o registro chega ao `open`. O gatilho exige escrever em `.forge/run/`. É caminho protegido no projeto, mas na sessão do Forge só as travas valem. E a regressão vem só deste diff: antes, nenhum arquivo era aberto no caminho da recusa.

Correção mínima (do autor, E7.7):
1. Em `hooks/conformidade.py:1521`, adicione `os.O_NONBLOCK` ao `open` e grave só se `stat.S_ISREG(os.fstat(fd).st_mode)`, fechando o fd nos dois casos (como `anexar_ao_log`, `hooks/agentes.py:1112`).
2. Crie um teste de comportamento que troca o `comandos.jsonl` por `os.mkfifo` e confere a recusa com a regra original, em menos de 1 s, nas duas sessões: o projeto e a sessão do Forge com o cwd no clone.
3. Declare o mutante que tira o `O_NONBLOCK`.

A2 fecha o mesmo tipo de risco pelo tempo (git lento sob o prazo). Fica recomendado porque não tem sonda.

Na volta, leio só o delta (`forge-check parecer delta docs/reviews/v0481-g4-f1-aviso.md`).
