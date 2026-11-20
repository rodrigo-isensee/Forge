# META85 na trilha do `bin/forge-check` (pedido v0478, E34.1)

Desenho curto dos três cartões, antes do código (ordem do dono 18/11 17:00 e 19/11 14:52: meta de 42 min do 1.º commit ao
merge). Tudo neutro (`R-NEUTRO`): vale para todo projeto que usa o Forge; os comandos vêm do `stacks/<nome>/pronto.md` da
stack do projeto, nunca de um projeto específico. Nenhum dos três afrouxa controle: os dois primeiros apertam ou informam, o
terceiro recusa o que hoje passa.

## 1. META85-ENTREGA-COM-MUTANTES
**Regra:** na etapa `codigo`, a entrega cujo escopo tem código (`e_codigo`, a mesma regra do T1) só passa no
`forge-check entrega` com as duas provas do autor, cada uma um log do comando da stack:
- `--mutantes <log>`: o comando de mutação da stack (no Forge, `bin/forge-mutante` só no diff, com a spec e `--cobertura`);
- `--pronto <log>`: o comando de pronto do projeto (`CLAUDE.md`, sugerido pelo `pronto.md` da stack).

**Forma do log** (a mesma do envio longo, `esperar-estado`): 1.ª linha `head=<sha40>` igual ao head entregue, a saída do
comando e, na última linha não vazia, `rc=0`:
`{ echo head=$(git rev-parse HEAD); <comando>; } > <log> 2>&1 && echo rc=0 >> <log> || echo rc=1 >> <log>`

Sem a prova, com o head de outro commit ou com `rc=` diferente de 0, a linha sai `pendente:` e o `entrega` sai com rc 1.
O `forge-check` não roda o comando (só lê o log, como sempre: não executa nada dos documentos); o log é do autor e o CI
segue sendo o portão que roda tudo. Limite conhecido: o log é um arquivo que o autor grava; a regra pega o esquecimento e o
head errado, não a fraude, que o CI e a mutação do revisor pegam. Só a forma antiga (`entrega <pedido> --branch ...`, o PQ
do autor) cobra as provas; a conferência do Jarvis (`entrega --pedido`) já roda os PQ do brief.

- **Autor:** entrega com os dois logs no PQ do `forge-check entrega`; mutante vivo ou pronto vermelho não chega ao parecer.
- **Revisor:** não refaz mutação nem pronto do autor; cita os logs da entrega e roda só o mutante ou teste novo.
- **Jarvis:** o `brief gerar` de código já escreve o PQ do autor com `--mutantes ${TMPDIR:-/tmp}/forge-mutantes.log
  --pronto ${TMPDIR:-/tmp}/forge-pronto.log` (fora da raiz: `.forge/run/` é estado dos hooks e ninguém o grava); a entrega recusada volta ao autor sem abrir rodada.

## 2. META85-REVALIDA-SO-QUEM-BARROU
**Regra:** depois da volta, revalida o parecer que barrou e, dos outros, só aquele cujo domínio a correção mexeu. O
`forge-check parecer delta <parecer>` termina com uma linha `revalida:`:
- `revalida: sim (este parecer barrou)` quando o parecer não é `aprovado`;
- `revalida: sim (<motivo>)` quando o domínio dele mudou, pela mesma função do `forge-check pr` (`commit_vale`, com a base, os
  livres e os testes do QA dispensados), para as duas respostas nunca divergirem;
- `revalida: não (não barrou e o domínio não mudou; o parecer segue valendo)` nos outros casos.

Não afrouxa: o `forge-check pr` continua recusando o parecer cujo domínio mudou; a linha só diz quem precisa voltar.

- **Autor:** nada muda.
- **Revisor:** na volta, roda o `parecer delta` do próprio parecer; com `revalida: não`, não emite parecer novo.
- **Jarvis:** dispara na volta só os portões com `revalida: sim`.

## 3. META85-ITEM-ATE-10-ARQUIVOS
**Regra:** o `forge-check classe` conta os arquivos do item (diff `base...head`) e, com mais de 10, imprime
`item: <n> arquivos, teto 10: corte o item antes de começar` e sai com rc 1 (o `--json` ganha `arquivos_do_item` e
`teto_de_arquivos`). Contam todos os arquivos do diff, menos:
- testes (`e_teste`, a mesma regra do T1, com `tests/mutantes/`); os módulos do portão em `tests/` contam;
- fragmentos de `changelog.d/`;
- pareceres e quadro (`LIVRES`).

Motivo: teste, spec de mutante e fragmento acompanham todo item por regra; contá-los puniria quem testa. Código,
documentação, texto de agente e skill contam. O desenho (o corte do tech-lead, `tamanho-por-item.md`) recusa o item
maior antes do primeiro commit, junto do teto de 150 linhas.

- **Autor:** recebe item de até 10 arquivos; acima disso, o corte vem antes.
- **Revisor:** item maior que chegou ao review é achado `bloqueante` pelo `forge-check classe`.
- **Jarvis:** corta no desenho e roda `forge-check classe --head <branch>` antes de delegar.
