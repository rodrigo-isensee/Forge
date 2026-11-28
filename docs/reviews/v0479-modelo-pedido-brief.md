---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-modelo-pedido-brief
commit: 83246fbf4c5ec96f5e9caeb114084f6089289423
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-21
---
# Review: v0478 (E86.2, MODELO-PEDIDO-E-BRIEF, texto e modelo)

Diff `ad3b3b6f..83246fbf`: `templates/projeto/docs/pedidos/_modelo.md`, `skills/checagem-do-brief/SKILL.md`, `skills/checagem-do-brief/por-tema.md` (novo), `skills/fluxo-do-pedido/SKILL.md`, classe `ModeloPedidoEBrief` em `tests/test_modelos_projeto.py`, 2 specs de mutante e o fragmento `changelog.d/v0479-modelo-pedido-brief.md`. Só texto e modelo: zero linha de código (H1 dentro do teto).

## Escopo
- Faz o que a E86.1 pede: retrospectiva como etapa no modelo (K-159), uma etapa numerada por delegação, pedido com dois repositórios com a marca `(outro repositório)` que o `forge-check` lê, e o `por-tema.md` (cópia nova com `status -sb`, `.githooks/` como proposta de diff, PQ `forge-check pr` rc=0 em brief de parecer, número de testes só de comando com data e commit). O resto para o `bin/forge-check` fica para depois do E83, como o histórico registra.
- Diretriz 25: a skill traz o resumo de uma linha e aponta `por-tema.md`; o detalhe fica no arquivo da skill.

## Cortes de texto (regras protegidas e neutralidade)
- Cortes: o caminho `docs/engineering/brief-checklist.md` na `description` e o caminho do modelo vazio em `checagem-do-brief/SKILL.md`; em `fluxo-do-pedido/SKILL.md`, o parêntese "selado pelo passo 3 dela...; selo no genérico, uma escrita por branch".
- Conferido por script: nenhuma string de `tests/config.json` presente nos três arquivos na base sumiu no head (as duas ocorrências acusadas eram a pasta `templates` como substring, falso positivo). As invariantes de `skills/fluxo-do-pedido/SKILL.md` seguem no texto.
- O conteúdo cortado do fluxo continua na fonte que a linha aponta: `skills/briefs-e-conferencia/SKILL.md:13-14` (selar no passo 3; uma delegação de escrita por branch, Z10). A frase "Se existir `docs/engineering/brief-checklist.md` no projeto..." que o teste `ChecagemDoBrief` cobra ficou intacta.
- Neutralidade (`R-NEUTRO`): `por-tema.md` sem termo de `SO_DO_FORGE` (o teste novo confere) e sem nome de projeto; `forge-copia`, `.githooks/` e o hook `conformidade` valem em todo projeto (`hooks/conformidade.py:63` protege `.githooks`).

## Testes e mutantes
- `python3 -m unittest tests.test_modelos_projeto tests.test_jarvis_nucleo tests.test_comando_pronto`: 71 testes, OK; `tests.test_forge -k TMPDIR -k checagem`: 3 OK (as formas do `${TMPDIR:-/tmp}` na checagem seguem). Suíte inteira: fica no CI do PR.
- `bin/forge-mutante --processos 1` nas duas specs, rev 83246fbf4c5e: M1 a M7, M9 e M10 morreram (9 de 9). Cada mutante muda o comportamento lido (trecho do modelo ou da skill), não a fonte do teste.

## Parecer
Aprovado. Faz o que a E86.1 pede, sem corte de regra protegida nem quebra de neutralidade (`R-REVIEW`, `R-NEUTRO`); commits limpos em Conventional Commits.
