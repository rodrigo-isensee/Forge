---
tipo: revisao-seguranca
contrato: 1
pedido: v0474
branch: melhoria/v0476-conformidade-formas
commit: b4bd700e8eebe148c68b67f6e4465c49ecb7d0bf
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-17
---
# Review de segurança: v0476-conformidade-formas (v0474 E3.50, parecer E3.146)

Revalidação por delta: `eb18768b..b4bd700e` (`forge-check parecer delta`). A rodada anterior (aprovado no `eb18768b`, E3.96) fica no git.

## Gatilhos
Gatilhos: hook de controle (`hooks/conformidade.py`, `hooks/_comum.py`), texto do brief que cita a forma aceita (`bin/forge-check`), receita de comando de skill (`skills/esperar-estado/SKILL.md`).

## Achados

## Sondas

## Detalhe dos achados
Nenhum achado; a rodada anterior não tinha achado aberto. Delta lido:

- **`bin/forge-check`:** listado pelo delta, mas o diff `eb18768b..b4bd700e` é idêntico, linha a linha, ao do `7c463a42` (#646, E3.49, já mesclado na `develop` com o próprio review) e chegou pelo merge `0d61a5e0` da `develop`; a branch não tem commit próprio em `bin/forge-check` nesse intervalo (`git log --first-parent` só mostra o merge). Fora do escopo desta branch.
- **`skills/esperar-estado/SKILL.md` e `skills/esperar-estado/envio-longo.md` (`b4bd700e`, E3.139):** só texto. A receita do laço do log (bloco `bash`) não muda; o detalhe (caminho literal nas três vezes; `bin/forge-fechar` com `--espera` longa) vai para o arquivo de apoio, sem perder conteúdo nem afrouxar a orientação. A fixture `e350-laco-do-log-com-variavel-bloqueia` segue passando.
- Nada de hook, workflow, segredo nem dependência mudou no delta próprio da branch.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. A catraca (rc 1) acusa só `R-CONFORMIDADE` em `bin/forge-check`, `hooks/_comum.py` e `hooks/conformidade.py` (controles tocados pela branch): o merge depende do rótulo `afrouxa-regra` do dono, já sabido na rodada anterior; não é achado de segurança. Suíte inteira: o CI do PR #652 é o portão. Rodados localmente no head: `tests.test_esperar_estado`, `tests.test_metricas_texto` (17 OK) e `tests.test_hooks.Hooks.test_fixtures_do_e350` (OK). Ferramentas de varredura: não aplicáveis a delta só de texto; nada instalado.
