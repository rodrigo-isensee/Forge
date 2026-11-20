---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-meta85-placar
commit: 6f6aab30715d2ae7cd6136c37cc35ed10bb59f81
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-19
---
# Review: v0478 E36.6 (melhoria/v0479-meta85-placar, head 97ef4fd1; revalida E36.2)

Escopo: só o que a branch acrescenta à `melhoria/v0479-placar-fases` (42c2a906, aprovada nos três portões), `git diff origin/melhoria/v0479-placar-fases...HEAD`: `bin/forge-placar`, `tests/evals/test_placar.py`, `tests/mutantes/v0479-meta85-placar{,-2,-3,-4}.json`, os três `v0479-placar-fases-{2,3,4}.json` reescritos, `changelog.d/v0479-meta85-placar.md` e `docs/melhoria-continua.md`.

## Achados
- A2 (recomendado) bin/forge-placar:658 · Nada no time escreve as linhas `PARADA sessão|promoção ... até ...` (grep em agents/, skills/, templates/: zero); sem o Jarvis registrá-las ao retomar, a medida nunca sai. Cartão para o texto de registro do histórico.
- A3 (recomendado) bin/forge-placar:676 · `gh run list --branch develop` mistura workflows e o PR develop→homolog (headBranch develop): um verde de outro workflow fecha a vermelha; timed_out e startup_failure não contam. Cartão: documentar `--workflow ci.yml --event push` e tratar essas conclusões como falha.
- A4 (recomendado) tests/evals/test_placar.py:580 · O teste compara com o relógio real (tolerância 60/61 min); passa de 90 s de carga e cai. É da classe da varredura de testes de prazo pedida pelo dono (19/11 08:54): injete o "agora" (variável de ambiente ou parâmetro) em vez de ler a hora.

## Revalidação (E36.6)
Delta lido: `forge-check parecer delta docs/reviews/v0479-meta85-placar.md`, intervalo 87aff761..97ef4fd1, domínio `bin/forge-placar`, `tests/evals/test_placar.py`, `tests/mutantes/v0479-meta85-placar-{2,4}.json`. O A1 de 87aff761 (sem linha `PARADA <tipo>` a parada saía 0) está resolvido: `paradas_do_historico` devolve None sem intervalo do tipo (bin/forge-placar:673) e segue 0 quando há linha do tipo noutro dia; a data impossível vira aviso com o pedido em vez de rc 2, mesma semântica de `momento` (fromisoformat, hora local). Testes do ramo: `test_sem_historico_ou_sem_linha_do_tipo_as_paradas_saem_tracinho` e `test_parada_com_data_impossivel_cita_o_arquivo_e_segue`; mutantes M12, M13 reescritos e M29 a M31 novos. A2 a A4 seguem recomendados e viram cartão depois do merge.

Provas no head 97ef4fd1: `python3 -m unittest tests.evals.test_placar` (ambiente limpo): 48 testes OK. `bin/forge-mutante --processos 1 tests/mutantes/v0479-meta85-placar-2.json tests/mutantes/v0479-meta85-placar-4.json`: todos morreram, M29 (:673), M30 (:671), M31 (:666) inclusive. `bin/forge-mutante --cobertura --base 87aff761`: linhas de guarda do delta cobertas (M13, M29). Sonda S1 repetida: `horas paradas, sessão: -`.

## Revalidação (E36.10, junção com a develop)
Delta lido: `forge-check parecer delta docs/reviews/v0479-meta85-placar.md`, intervalo 97ef4fd1..f74d6dd7, escopo sem o que veio da base. Aviso do delta: o merge 5d6d87a não está na origin/develop; o que ele trouxe conta inteiro, e o delta mostrou só a varredura linear, o teto de 64 e o `--prs`, sem ruído. A junção (12 conflitos) tem a develop como base e a META85 por cima: `origin/develop` (5ae868eb) é ancestral do head e `git diff origin/develop...HEAD -- bin/forge-placar tests/evals/test_placar.py` só remove as linhas da meta de 85 e a função `itens_do_dia` que a META85 substitui; `fundo_demais`, `TETO_ANINHAMENTO` e `--prs` seguem no código e nos dois testes de aninhamento. Nada da develop se perdeu.

Specs: M13, M19 e M24 da placar-fases voltaram ao trecho adaptado (M34, em placar-fases-6, aponta a guarda `fundo_demais`). A guarda `if not itens` do trecho antigo (bin/forge-placar:641 na base) foi para `estatisticas()` como `if not totais` (bin/forge-placar:671), que o M19 muta e o teste `test_dia_sem_item` mata. Por isso o `--cobertura --base origin/develop` sai com rc 1 só por `apagada · bin/forge-placar:641(base) · itens`: aceito, a guarda não sumiu, mudou de lugar e tem mutante que morre. As três isentas (test_placar.py:515, :573, :607) são linhas de asserção e auxiliar do teste, não guarda, com motivo escrito. Os achados A2 a A4 seguem recomendados.

Provas no head f74d6dd7: `python3 -I tests/evals/test_placar.py`: 50 testes OK. `bin/forge-mutante --processos 1 tests/mutantes/v0479-meta85-placar*.json`: 31 mutantes mortos, rc 0. `bin/forge-mutante --processos 1 tests/mutantes/v0479-placar-fases*.json`: 49 mortos, rc 0. Parecer segue aprovado.

## Revalidação (E36.13, guarda de aninhamento no --ci)
Delta lido: `forge-check parecer delta docs/reviews/v0479-meta85-placar.md`, intervalo f74d6dd7..d340b213, domínio `bin/forge-placar`, `tests/evals/test_placar.py`, `tests/mutantes/v0479-meta85-placar-4.json`. `paradas_do_ci` chama `fundo_demais(texto)` antes do `json.loads` e sai com rc 2 e mensagem fixa (bin/forge-placar:712), sem eco da entrada; o teste com `[` repetido 100000 vezes confere rc 2, a mensagem "aninhado acima de", ausência de Traceback e de `[[[[` no erro; mutante M32 (`if False:`) declarado em `v0479-meta85-placar-4.json`.

Provas no head d340b213: `python3 -I tests/evals/test_placar.py`: 50 testes OK. `bin/forge-mutante --processos 1 tests/mutantes/v0479-meta85-placar-4.json`: M32 morreu (:712), demais mortos. `bin/forge-mutante --cobertura --base f74d6dd7`: guarda :712 coberta por M32. Sem achado novo; parecer segue aprovado.

## Revalidação (E36.19, junção com a develop e corte para 150)
Delta lido: `forge-check parecer delta docs/reviews/v0479-meta85-placar.md`, intervalo 57a66ff4..89936fa3 (d340b213 na saída do delta), domínio `bin/forge-placar` e `tests/mutantes/v0479-placar-fases-3.json`; `tests/evals/` sem mudança no intervalo. Comportamento igual: a guarda do dia sem item voltou ao texto `if itens` em `cmd_fases` (bin/forge-placar:744), com as três chaves em None, e `estatisticas()` passou a exigir ao menos um item (único chamador, :744); `FONTES_DE_PARADA` ganhou `DO_HISTORICO` com os mesmos três textos; o resto são docstrings e reflow da ajuda (6 linhas de corte). O M19 aponta agora `for i in itens]) if itens else dict.fromkeys(` e morre.

Provas no head 89936fa3: `python3 -I tests/evals/test_placar.py`: 50 testes OK. `bin/forge-mutante --processos 1 tests/mutantes/v0479-placar-fases-3.json`: M19 morreu (:744), demais mortos, rc 0. `python3 tests/catraca.py --base origin/develop --head HEAD`: rc 0. Sem achado novo; parecer segue aprovado.

## Revalidação (E36.23, M34 com trecho único)
Delta lido: `forge-check parecer delta docs/reviews/v0479-meta85-placar.md`, intervalo 89936fa3..7e20ac8b, domínio `tests/mutantes/v0479-placar-fases-6.json` (único arquivo no domínio). O `de` e o `para` do M34 passaram a incluir a linha do `raise` (`--prs {arq} não é JSON`), e o trecho `if fundo_demais(texto):` aparece uma vez em `bin/forge-placar` (ocorrências: 1), com a guarda em :237. Sem mudança de código nem de teste: o mutante não é mais ambíguo e o parecer segue aprovado.

Provas no head 7e20ac8b: `bin/forge-mutante --processos 1 tests/mutantes/v0479-placar-fases-6.json`: rc 0, M34 morreu (bin/forge-placar:237), demais mortos. Sem achado novo.

## Revalidação (E36.26, hora do merge sempre com +00:00)
Delta lido: `forge-check parecer delta docs/reviews/v0479-meta85-placar.md`, intervalo 7e20ac8b..6f6aab30, domínio `bin/forge-placar`, `tests/evals/test_placar.py`, `tests/mutantes/v0479-meta85-placar-5.json`. `hora_numerica` (bin/forge-placar:623) troca o `Z` final do `%cI` por `+00:00` e é aplicada só ao campo `merge` do item (:647); `total` e fases seguem pelo epoch. O teste usa um `git` falso no PATH que reescreve `+00:00` em `Z` só no fim do campo ou antes de espaço, o que imita o git novo e confere a mesma forma que o código corrige; o esperado é a hora com `+00:00`. Mutante M50 (`endswith("X")`) declarado em `v0479-meta85-placar-5.json`.

Provas no head 6f6aab30: `python3 -I tests/evals/test_placar.py`: 51 testes OK. `bin/forge-mutante --processos 1 tests/mutantes/v0479-meta85-placar-5.json`: M50 morreu (bin/forge-placar:625), rc 0. `bin/forge-mutante --cobertura --base 7e20ac8b`: `coberta · bin/forge-placar:625 · M50`. Sem achado novo; parecer segue aprovado.

## Sondas
- S1 · `bin/forge-placar fases --git . --ref origin/develop --dia 2026-11-19 --raiz-pedidos /root/.forge-contrib` (histórico sem PARADA) · espera: `horas paradas, sessão: -` · obtido: 87aff761 `0 h 00 min`; 97ef4fd1 `-`

## Parecer
Aprovado no head 97ef4fd1: o A1 está corrigido e coberto (ver Revalidação). Histórico do parecer em 87aff761, reprovado por um bloqueante (A1), de correção pequena e local: em `paradas_do_historico`, sem nenhuma linha `PARADA <tipo>` em todos os pedidos, devolver `None`; com ao menos uma linha do tipo (em qualquer dia), a janela sem parada segue 0. Teste do ramo: raiz com `docs/pedidos` e histórico sem `PARADA` dá `min` None e o texto `-`; mutante declarado na guarda nova. Sem a raiz (`docs/pedidos` ausente) já sai `-` (S1 sem `--raiz-pedidos`).

O resto está correto e coberto: média, mediana e p75 inclusivo (`statistics.quantiles`, um item só vale o próprio total), corte `[desde, ate)` pela hora do merge com fuso opcional e erro com rc 2, PR do merge de dois pais pelo assunto e do squash pelo `(#N)`, `merge` no `--json`, união de intervalos recortada na janela, develop vermelha do fim do reprovado ao fim do verde seguinte, cada parada com a fonte por escrito, meta 42 min (ordem do dono 19/11 14:52). Ajuda, `docs/melhoria-continua.md` e fragmento de changelog acompanham. A2 a A4 não devolvem (META85: recomendado vira cartão depois do merge).

Tamanho (H1): `bin/forge-placar` +124 −21 sobre a placar-fases, dentro de 150; a placar-fases entra antes na develop (mesmo arquivo, `forge-check sobreposicao`), e esta branch traz a develop só no merge.

Ferramentas e provas: `python3 -m unittest tests.evals.test_placar` no head 87aff761: 47 testes OK. `bin/forge-mutante --processos 1 tests/mutantes/v0479-meta85-placar*.json`: M1 a M28 morreram; `v0479-placar-fases-{2,3,4}.json` (M13, M19 e M24 reescritos): todos morreram. `bin/forge-mutante --cobertura --base origin/melhoria/v0479-placar-fases`: toda guarda de `bin/` coberta (o "sem mutante" só aparece em linhas auxiliares do teste). Suíte inteira: fica no CI do PR (sem suíte local, pelo brief).
