---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-bp3-s3-registro
commit: 1f31729169cd2163c883a4891ba761d0da9c1830
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 E39.7 (BP3 S3, registro de interrompidos no hook agentes)

## Revalidação no head 1f317291
Delta lido por `forge-check parecer delta` (intervalo `b3cd1ee4..1f317291`, sem o que veio da `develop` pelo merge `4f5028df` do `forge-fechar`): no domínio só `tests/mutantes/v047-h2-autor-fica-3.json`, o M23 com `de`/`para` trocando `a.get` por `registro.get`, o nome atual em `hooks/agentes.py:363`.

- O trecho `de` existe uma vez só em `hooks/agentes.py` (linha 363); o `para` tira a condição do tipo da retomada, a mesma guarda de antes.
- `bin/forge-mutante --processos 1 --ids M23 tests/mutantes/v047-h2-autor-fica-3.json`: `M23 · morreu · hooks/agentes.py:363`.
- `bin/forge-mutante --conferir --base b3cd1ee4`: `conferidas: o trecho de cada spec do diff está no lugar`.
- Nada de código muda no delta; o parecer abaixo e a A1 seguem.

## Revalidação no head b3cd1ee4
Delta lido por `forge-check parecer delta` (intervalo `d03cc57f..1a86b815`; `1a86b815` só traz o parecer da segurança, fora do domínio): `hooks/agentes.py` +20 −4 (A1 da segurança), `tests/test_agentes_interrompidos.py` +28, specs de mutante (M15 e M29 com o trecho no lugar novo, `-3.json` com M30 a M32) e o fragmento do changelog.

- `caiu_em_finito` aceita int ou float finito; o `OverflowError` do inteiro enorme conta como não finito. Em `interrompidos_vigentes`, o `caiu_em` numérico e não finito lança `EstadoIlegivel`, que o `principal` já converte em recusa (linha 1292) ou, com recusa do R-BRIEF, registra e recusa pelo R-BRIEF; o item não numérico segue sumindo. Coerente com HOOK-ESTADO-ILEGIVEL-LIBERA; nenhuma trava afrouxa.
- O teste de disparo prova a recusa com o arquivo intacto (sem regravação), e o de função cobre 10**400, ±inf e nan.
- Verificadores no head `b3cd1ee4`: `python3 -m unittest test_agentes_interrompidos`: `Ran 26 tests … OK`; `bin/forge-mutante` em `-3.json`: M30, M31, M32 `morreu`; M15 e M29 `morreu`; `--cobertura --base d03cc57f`: linhas 633, 645 e 647 `coberta`, nenhuma descoberta.
- A1 abaixo segue como estava (recomendado, fora do delta).

## Review original (head d03cc57f)

Base `004ce869`, head revisado `d03cc57f`, um commit (`feat(agentes)`, E39.3). Diff de código: `hooks/agentes.py` (+116 −9, abaixo do teto H1), um comportamento: a reserva guarda `briefs` (caminho e sha256) e o registro de sessão provadamente morta vai para `interrompidos` em vez de sumir.

## Achados
- A1 (recomendado) hooks/agentes.py:1299 · `caidos_da_sessao` refaz `sessao_morta` (novo `os.kill`) sobre a lista crua, depois do `vigentes` da linha 1295: o pid que morre entre as duas leituras fica nos agentes e no interrompidos, e volta duplicado no evento seguinte. Derivar os caídos da mesma avaliação do `vigentes`.

## Sondas

## Parecer
Aprovado. Lido o diff inteiro contra o escopo do E39.3:

- Faz o pedido e só ele: nenhuma recusa do R-TETO ou do R-BRIEF muda; a única guarda nova de recusa é `interrompidos` não-lista em `ler_estado` (linha 430), que segue a regra já existente do estado ilegível (HOOK-ESTADO-ILEGIVEL-LIBERA) e o docstring do topo foi atualizado.
- `briefs_da_reserva` grava só o trecho `docs/briefs/<nome>.md` de caracteres seguros e o hash dos bytes lidos; nada do prompt entra (teste `test_nenhum_byte_do_prompt_entra_no_registro`). `interrompido` copia só campos de forma conhecida, sem PID.
- Ordem de gravação coerente: com liberação, o estado com `interrompidos` sai antes da recusa e os vencidos vão ao `liberacoes.log` uma vez só (`vencidos = []`); sem gravação, nada é logado e o evento seguinte recalcula. `fechar_por_relancamento(…, agentes[-1])` só roda depois do `lancar`, que sempre reserva ou sai.
- `dentro_do_prazo` extraído do `vigentes` sem mudar a condição (M25, M26 mortos).
- A1 é corrida de microssegundos com efeito só cosmético (item duplicado, fechado pela mesma regra); não bloqueia (`R-REVIEW`).

Verificadores (rodados no head `d03cc57f`, só o módulo tocado; suíte inteira fica no CI do PR):
- `python3 -m unittest test_agentes_interrompidos` (em `tests/`): `Ran 23 tests … OK`.
- `bin/forge-mutante --cobertura --base 004ce869…`: todas as guardas do diff `coberta`, nenhuma descoberta.
- `bin/forge-mutante tests/mutantes/v0479-bp3-s3-registro.json` e `-2.json`: M1 a M29 `morreu` (M15, M25 a M29 por erro do teste declarado com controle verde, que conta como morto pela ferramenta).
