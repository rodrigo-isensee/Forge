---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-vigia-time-parado
commit: b13b7016c1fd7dd1796ea1f84a0cab672fc44c71
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-22
---
# Review: v0480-vigia-time-parado

Etapa E105.7, revalidação da volta única (H3, R-REVIEW) do parecer da E105.3 (head 3821ad14, reprovado por A1 e A2). Delta lido: `forge-check parecer delta docs/reviews/v0480-vigia-time-parado.md`, intervalo `3821ad14..b13b7016`, no domínio: `changelog.d/v0480-vigia-time-parado.md`, `docs/hooks.md`, `hooks/vigia.py`, `tests/mutantes/v0480-vigia-time-parado{,-2,-3,-4}.json`, `tests/pesos-d4.json`, `tests/test_vigia_parado.py`. Fora do delta nada foi relido. `hooks/vigia.py` soma +120 −4 contra a base 900bfdfe (dentro do teto H1).

## Achados
- A1 (recomendado) tests/test_vigia_parado.py:8 · `import subprocess` entra no delta sem uso (o teste de subprocesso do A4 anterior não entrou); tire-o junto do cartão do A4.

## Parecer
Aprovado no head b13b7016.

Achados anteriores:
- A1 (bloqueante, ADR 0003 item 1): resolvido pelo item 7 da emenda da ADR 0003, na branch `melhoria/v0480-ordens-adr` (e7a94603). Condição de integração (R-FLUXO, dependência): aquela branch entra na `develop` antes desta; o código e o doc daqui citam o item 7 e ficam sem âncora se a ordem se inverter.
- A2 (bloqueante): resolvido. `docs/hooks.md:18` e a seção do `vigia` descrevem a exceção única (o `reason` fixo do time parado só no `Stop` da sessão do Jarvis), o `stop_hook_active`, o quadro lido, as marcas e o formato do ID.
- A3 (recomendado): resolvido no código. Marcas ampliadas, comparadas sem caixa nem espaço repetido (`_normal`), e o Responsável `usuário` achado pelo cabeçalho da tabela; linha curta e tabela sem a coluna valem só pela Obs. (testes próprios).
- A4 (recomendado): segue para cartão, como o brief registra (o laço de `tests/test_hooks.py:830-837` recusa `decision`/`reason`; muda com o item 7 da emenda).

O resto do delta confere: `sessao_do_jarvis` lê o papel `jarvis` de `hooks/conformidade.json` (`forge:jarvis`) e cala sem `agent_type`, com outro agente ou com o nome sem prefixo; `ler_quadro` abre com `O_NOFOLLOW|O_NONBLOCK` e recusa o não regular, e o chamador cala e registra no `erros.log`; o ID que vai ao modelo passa pela lista positiva `[A-Za-z0-9.-]{1,16}` e, fora dela, a linha sai sem o ID; o `reason` perde o prefixo `Forge:` e fica texto fixo. Guardas novas com mutante declarado (M15 a M23) e teste do ramo de falha. Commits em Conventional Commits em português, com a etapa.

Provas (head b13b7016, `env -i`, `HOME` temporário; a suíte inteira fica no CI do PR):
- `python3 -I tests/test_vigia_parado.py`: `Ran 22 tests ... OK`.
- `bin/forge-mutante --processos 1` nas specs `-3` e `-4`: M15 a M23 `morreu` (M16, M18 e M21 por erro, que a ferramenta aceita).
- `bin/forge-mutante --cobertura --base 3821ad14`: toda guarda do delta `coberta`; único não coberto, `tests/pesos-d4.json` (dado, sem guarda).
