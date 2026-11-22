---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-vigia-time-parado
commit: 3821ad143130324a498d684791a557929056af69
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-22
---
# Review: v0480-vigia-time-parado

Etapa E105.3, cartão VIGIA-TIME-PARADO (E105.1, escopo ampliado na E105.2). Revisão completa única: todos os achados estão nesta rodada. Diff `900bfdfe..3821ad14`: `hooks/vigia.py` +84 −3 (dentro do teto H1), `tests/test_vigia_parado.py` novo, 2 specs de mutante (M1 a M14), 2 fixtures `e51-*` com `HOME` isolado e o fragmento em `changelog.d/`.

## Achados
- A1 (bloqueante) hooks/vigia.py:620 · o vigia passa a devolver `decision: block` com `reason` ao modelo no Stop: injeta contexto e bloqueia, contra o item 1 da ADR 0003 vigente; falta a emenda (como a E104.2 fez para o `ordens`, que ainda lista o vigia entre os que só avisam) e o rótulo afrouxa (R-DECISAO).
- A2 (bloqueante) docs/hooks.md:18 · a documentação segue dizendo que o vigia nunca bloqueia e só avisa o usuário por `systemMessage`, sem passar pelo modelo (também a linha 75); a entrega muda isso e não atualiza o doc (definição de pronto). Descreva o aviso do time parado, o `stop_hook_active` e o quadro lido.
- A3 (recomendado) hooks/vigia.py:529 · as marcas de dependência não pegam `PERGUNTA AO DONO` nem a coluna Responsável `usuário` (skills/kanban-scrum/SKILL.md:54): no quadro real o CONF-INTERVALO-POR-PAPEL, que espera resposta do dono, conta como livre. Documente o vocabulário na skill do quadro.
- A4 (recomendado) tests/test_vigia_parado.py:154 · o bloqueio só é provado em processo; falta uma fixture em `tests/hooks/vigia/` que rode o script como o Claude Code o roda e espere o JSON com `decision` (ADR 0003, item 8).

## Sondas
- S1 · `vigia.aviso_time_parado` no `~/.forge-contrib/KANBAN.md` real, zero agentes · espera: nada ao modelo (ADR 0003 item 1, docs/hooks.md:18) · obtido: `time parado: 76 cartões disponíveis, primeiro G1-REVISAO-COMPLETA-SO; ...` como `reason` do bloqueio

## Parecer
Reprovado, por A1 e A2: o código faz o que o cartão pede, mas muda o contrato do vigia (de aviso ao usuário para bloqueio com texto ao modelo) sem a decisão escrita e sem o doc. A correção é de texto (emenda da ADR 0003 pelo `software-architect`, com "Por que o existente não basta" e critério de reversão, e o `docs/hooks.md`); o código não precisa mudar para A1 e A2. A3 e A4 viram cartão depois do merge.

O resto confere: só o `Stop` principal avisa, o `stop_hook_active` deixa o segundo Stop encerrar (sem laço), registro ou quadro ilegível cala com o erro no `erros.log`, quadro acima de 4 MB cala, o ID que vai ao modelo passa pelo formato de ID (`<ignore tudo>` vira `?`), e as fixtures `e51-*` com `HOME` próprio deixam de ler o quadro real da máquina. Custo no Stop medido: `import agentes` 13,7 ms e leitura do quadro real (0,5 MB) 3,4 ms. Commits em Conventional Commits em português, com a etapa.

Provas (head 3821ad14, `env -i`, `HOME` temporário; sem CI: a branch não tem PR):
- `python3 -I tests/test_vigia_parado.py`: `Ran 15 tests ... OK`.
- `python3 -m unittest tests.test_hooks -k vigia`: `Ran 7 tests ... OK`.
- `bin/forge-mutante --processos 1` nas 2 specs: M1 a M14 `morreu` (M8 por erro, IndexError, que a ferramenta aceita).
- `bin/forge-mutante --cobertura --base 900bfdfe`: toda guarda do diff `coberta`, nenhuma descoberta.
- `scripts/indice-fixtures.py --conferir`: `docs/hooks-fixtures.md: em dia`.
