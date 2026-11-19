---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-sandbox-controle
commit: 1aaea973c977ffa0111ca0482ac3e4b353863649
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-19
---
# Review: v0478 (E29.8, revalidação de A1 a A3 de SANDBOX-TRAVA-CONTROLE, head 1aaea973)

Revalidação (H3, R-REVIEW): li só `forge-check parecer delta docs/reviews/v0479-sandbox-controle.md`, intervalo `03448b3d..1aaea973`, 22 arquivos no domínio. A4 a A6 (recomendados) não foram relidos. Suíte inteira não rodada (fica no CI do PR); rodei o teste novo: `python3 -m unittest tests.test_sandbox_controle tests.test_apoio_sandbox` deu `Ran 37 tests ... OK (skipped=2)`, os dois do bubblewrap pulados com "Creating new namespace failed: Operation not permitted". Os 11 mutantes estão em `tests/mutantes/v0479-sandbox-controle.json` (M1 e M2 na falta_bwrap, M3 a M11 nas guardas novas); a catraca os confere.

Delta lido dos achados anteriores:
- A1 resolvido: `tests/test_apoio_sandbox.py` move `ambiente_sem_ci` para depois da classe `Sondas`; o teste de falta_bwrap passa a ser coletado (roda e passa) e M1 e M2 cobrem os dois ramos.
- A2 resolvido: `bin/forge-init` e `hooks/doutor.py:252` (`preparar_controle`, no SessionStart, fora do sandbox) criam `agentes.json` e `pesado.json` antes do primeiro Bash, só o que falta; o hook `pesado` grava `null` ao soltar em vez de apagar; a fila do projeto saiu do denyWrite.
- A3 resolvido: `skills/novo-projeto/SKILL.md:27` e `skills/fluxo-do-pedido/SKILL.md:44` passam o `forge ritmo` ao dono, com o comando exato.

## Achados
- A7 (recomendado) hooks/agentes.py:392 · 0 byte valer registro vazio muda HOOK-ESTADO-ILEGIVEL-LIBERA sem precisar: forge-init e preparar_controle já criam o arquivo que o hook lê (S4). Reverta a linha e a fixture; se mantida, título afrouxa-regra e OK do dono antes do merge.

## Sondas
- S4 · agentes.ler_estado, arquivo ausente e de 0 byte, no head 1aaea973 · espera: 0 byte só se o preparar_controle falhar · obtido: os dois dão {'agentes': []}; preparar_controle (doutor.py:252) cria o arquivo antes do Bash; gravar_json usa os.replace, nunca deixa 0 byte

## Parecer
Aprovado. Os três bloqueantes foram resolvidos como pedido, e a soltura com `null` fecha o buraco que o apagar abriria.

Sobre o afrouxamento (A7), a pergunta do brief: ele não é necessário. A criação antes do primeiro Bash já tira o gatilho do A2. O hook lê `hook.run()`, que é a pasta da cópia principal (`hooks/_comum.py`, `Hook.run`). Nesse caminho o arquivo passa a existir sempre: o forge-init cria-o no projeto novo, o SessionStart no antigo, e a soltura do `pesado` não apaga mais. Na worktree, o vazio que o runtime monta no caminho relativo fica numa pasta que o hook não lê. O 0 byte só chega ao hook se o `preparar_controle` falhar com OSError, e essa falha já vai ao erros.log. Nesse caso, recusar com R-TETO é o lado seguro da regra: o dono apaga o arquivo no terminal e reabre a sessão. O time fica travado só nessa falha registrada.

Em poder, a mudança quase não afrouxa: arquivo ausente já valia `{"agentes": []}`, e quem consegue truncar o arquivo numa `.forge/run` gravável consegue também apagá-lo. Mesmo assim, ela muda o texto e a fixture de uma regra com ID. Para manter a regra como estava, basta tirar `hooks/agentes.py:392` e a fixture renomeada. O `ler_trava` do `pesado.json` pode ficar: o 0 byte equivale à ausência, que já liberava, e a trava não tem regra de ilegível. Se o autor mantiver o A7, a mudança é afrouxamento listado (o changelog já o declara) e o merge espera o OK do dono.
