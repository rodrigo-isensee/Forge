---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-conformidade-til-link
commit: 481d2855dbf0acc7c9fc9ec09d35ad8bf5d87e24
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-21
---
# Review: v0478 E80.2 (CONFORMIDADE-TIL-EM-SUBSTITUICAO e CONFORMIDADE-LINK-POR-COPIA)

Base `adc52def`, head `481d2855`, dois commits, um por cartão. Código em `hooks/conformidade.py`: 21 linhas (H1 dentro do teto).

## Achados
- A1 (recomendado) docs/hooks.md:56 · O link por cópia também recusa, para o papel que não é o jarvis na sessão do Forge, a linha que cita pasta de parecer ou `.git/forge` (`cp -r docs/reviews /tmp/r` do próprio tech-lead: base 0, head 2). O texto e o fragmento citam só o pedido e o brief da pasta de controle; registre esse alcance.

## Sondas

## Parecer
Aprovado. A mudança só aperta: as duas regras só acrescentam `barrar`. O alvo calculado é conferido em `decidir`, depois do parecer, e só quando não tem `SEM_VALOR`. A regex nova só acrescenta casos a `CAMINHO_TROCADO_NA_LINHA`, e o `sem_copia_de_wt` perde a exceção em mais linhas, o que também aperta (`R-CONFORMIDADE`).

Edições em testes que já existiam (pedido do autor):
- `tests/test_conformidade_verde.py:410-424`: as duas linhas `tar -x` saem da lista de liberação e passam a ser afirmadas como recusa em `test_tar_x_na_linha_que_cita_o_estado_recusa`. Elas citam `.git/forge`, e o `tar -x` entra na mesma classe do `ln` e do `mv`, que já recusavam ali. As linhas `tar -xf docs/a.tar -C docs`, `tar --checkpoint -xf …` e `tar --to-command=cat -xf …`, que não citam o estado, continuam na lista e liberam. O teste não afrouxa: a expectativa mudou de 0 para 2.
- `tests/mutantes/v0479-conformidade-trilha-13.json` W8: o `de` acompanha a linha nova (uma ocorrência no arquivo). O `para` continua tirando só a alternativa do ponto como programa. O mutante morre.

Sondas no head e na base, com o hook rodado sobre a entrada JSON e o papel tech-lead:
- `echo x >> "$(echo ~/.claude)/settings.json"`, o mesmo com `printf %s`, com `tee` e com `d=~/.claude; f=$d/settings.json`: base 0, head 2.
- `d=~/.claude; d=src; echo x >> "$d/settings.json"` dá 0, porque o valor do bash é `src`. `d=src; echo x >> "$d/app.js"` e `echo x > "$(echo src)/n.js"` também dão 0, sem regressão.
- Valor de 5000 caracteres no `$(printf …)` e caminho de 30 segmentos: 0, sem erro interno.
- Na sessão do Forge: `cp -r src /tmp/x` dá 0; `cp -r docs/reviews /tmp/x` e `tar -xf a.tar -C docs/reviews` passam de 0 a 2 (A1).

Testes rodados: `test_fixtures_do_til_em_substituicao`, `test_fixtures_do_link_por_copia`, `test_fixtures_do_controle_so_jarvis` e a classe `EstadoDoAgentesNoClone`, com 15 testes OK. Mutantes T1-T5 e L1-L6 (`bin/forge-mutante`, 1 processo) e W8: todos morreram. A `--cobertura --base adc52def` aponta as 4 linhas de guarda cobertas. A suíte inteira fica para o CI do PR (`R-REVIEW`); não há PR neste brief.
