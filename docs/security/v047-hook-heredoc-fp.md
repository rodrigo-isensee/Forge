---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-hook-heredoc-fp
commit: aaaa429572b119c5d5dd557601ca09da9b02b61d
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-16
---
# Review de segurança: v047, E2.543 (revalidação por delta depois da atualização com a develop; heredoc no hook `parecer`)

Head revisado: `aaaa4295` (intervalo do delta `0eee1453..aaaa4295`, escopo sem o que veio da base `86ac0fcb`). Parecer anterior (E4.13, head `0eee1453`): aprovado, com A5 recomendado. Desde então a branch recebeu a develop (merge `dd71ea87`) e os pareceres de review e QA; nenhum deles toca o domínio de segurança.

**Veredito: aprovado.** O patch do hook não mudou: o diff de `hooks/parecer.py` contra a develop `86ac0fcb` (107 linhas `+`/`-`, 99 inserções e 6 remoções) tem a mesma soma de verificação (md5 `53cd3a03…`) do diff contra a base `9b2c6474` no head revisado antes (`0eee1453`), e `git diff dd71ea87 HEAD -- hooks` é vazio. O resto do delta do domínio (`docs/hooks.md`, `tests/hooks/parecer/texto-barra-python-stdin-com-gh-pr.json`, fixtures e mutantes) é o mesmo conjunto já revisado; o que veio da develop está fora do escopo do delta e foi revisado nos pedidos que o trouxeram. Nenhum `bin/`, `scripts/`, `.githooks/` ou `.github/` mudou no patch.

## Gatilhos
`R-SEGURANCA`: mudança em controle do Forge (hook PreToolUse que guarda `gh pr`, merge e pull), com afrouxamento de regra de ADR (emenda v047 na ADR 0011, rótulo `afrouxa-regra`). Sem mudança de gatilho desde o parecer anterior.

## Achados
- A5 (recomendado) hooks/parecer.py:176 · lançador que acha a função pelo nome em texto fora da lista passa no head (a base barrava): operator.methodcaller e operator.attrgetter com 'sys'+'tem', inspect.getmembers; equivale ao python3 -c que a base libera e a doc declara a lista como não fronteira

## Sondas

## Detalhe dos achados
Os achados A1 a A4 do parecer E4.9 seguem resolvidos (código idêntico ao já sondado no head `0eee1453`: `LANCA_PROCESSO` com fronteira à esquerda, comando de PR nas constantes de texto pelo `ast` com falha fechada, `chamada_muda_o_corpo` para `PATH=` solto e `git` fora dos corpos, emenda v047 na ADR 0011). Na revalidação rodei o teste afetado e os mutantes no head `aaaa4295`; as sondas da tabela do parecer anterior valem porque o código sob sonda é byte a byte o mesmo.

**A5, caminho de ataque:** o agente da sessão, deliberadamente, quer mesclar sem parecer e esconde o nome do lançador atrás de `operator` ou `inspect` (`operator.methodcaller("sys"+"tem","gh pr merge feat/x")(os)`, `operator.attrgetter("sys"+"tem")(os)(…)`, `inspect.getmembers(os)` filtrado pelo nome montado). **Por que recomendado:** a mesma entrada com `python3 -c` passa na base, fora da regra pela ADR 0011 (N-HOOK1); o critério de reversão da emenda não é atingido; `docs/hooks.md:103` declara a barreira como lista de nomes, não fronteira. O uso por engano não forma esse texto. Severidade: baixa.
**A5, correção mínima** (P, `tech-lead`): acrescentar a `LANCA_PROCESSO` os nomes `attrgetter`, `methodcaller` e `getmembers`, com uma fixture `heredoc-interpretador-python-methodcaller-bloqueia`; ou, sem mudar o código, citar `operator` e `inspect` entre os exemplos do que a lista não cobre em `docs/hooks.md:103`. Não bloqueia a entrada na develop.

## Riscos aceitos e ferramentas
Nenhum risco aceito por este parecer. Suíte: sem PR aberto (brief: não abrir), sem CI a citar; por ordem do dono de 16/11, só os testes dos arquivos tocados. Rodado: `python3 -m unittest tests.test_hooks_parecer_pasta.PastaDoGit.test_corpus_heredoc_interpretador_libera_e_bloqueia` (OK, 1 teste) e `bin/forge-mutante tests/mutantes/v047-hook-heredoc-fp*.json`. A suíte inteira fica para o CI do PR. Ferramentas: só leitura do código, `git diff` e o próprio hook; nenhuma varredura externa.
