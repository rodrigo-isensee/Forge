---
tipo: review
contrato: 1
pedido: conf-base-dono
branch: melhoria/conf-base-dono
commit: 8c243582ee0eadd602956a67e210337560f33912
parecer: reprovado
revisor: forge:tech-lead (CONF-BASE-DONO-REV E1.1)
data: 2026-10-23
---
# Review: CONF-BASE-DONO (E1.1 do CONF-BASE-DONO-REV)

Code review (R-REVIEW) da branch inteira, `daf2ffa5f64230f698b58547d03c53d801f4a4e7...8c243582ee0eadd602956a67e210337560f33912`: 6 commits, 7 arquivos, +232 -13 (`bin/forge-check`, `bin/forge-testes`, `agents/conferente.md`, `agents/jarvis.md`, `changelog.d/conf-base-dono.md`, `tests/test_conferencia_base_dono.py`, `tests/test_testes_tocados.py`). Li o diff inteiro e conferi contra o escopo E1 a E4 e as decisões do dono do pedido `CONF-BASE-DONO`. A segurança é da E2.1 (`docs/security/`) e o QA da E3.1; não os refaço.

Ferramenta: o Forge não tem `docs/engineering/praticas.md`; a regra de ferramenta é a suíte, que fica com o QA e o pre-push. Rodei só `tests.test_conferencia_base_dono` (HOME isolado em $TMPDIR): 14 testes OK.

## Casos reais (forge-check entrega novo, HOME isolado, git de ~/Forge)
- **REVAL-288, branch lote, head `ad6a9bd`, Base-sha `7423c44`:** a linha real de 15:56 (`base do delta para a conferência: agt-a ..., lote 0b8a307...`) não está na forma nova e segue recusada (`escopo: --desde sem conferência anterior`, rc 1). Com uma cópia do pedido mais a linha `- ...: base do delta fixada pelo dono 0b8a307bea766815b567409ff33fec4688fff9a1`, e `--raiz-pedidos` para a cópia, etapas `review` e `qa`: rc 0, `intervalo: 0b8a307..ad6a9bd`, `base: fixada pelo dono (linha do Histórico)` e os três arquivos `docs/qa/`, `docs/reviews/`, `docs/security/lote-forge-check-0.28.0.md`. É o que a conferência manual deu ("só pareceres"), igual a `git diff --name-only 0b8a307 ad6a9bd`.
- **INTEG-LOTE-FC, merge `8649439` (pais `ad6a9bd` e `daf2ffa`), Base-sha `daf2ffa`, etapa `review`:** com a linha do dono para `ad6a9bd` na forma nova: rc 0, `base: fixada pelo dono`, `escopo: integração da base (o que difere dos dois pais)` e `bin/forge-check`, `bin/forge-testes`, `docs/hooks.md`, `tests/test_testes_tocados.py`, igual a `git show --cc --name-only 8649439` e à conferência manual de 19:12/19:16. Os números (`bin/forge-check +386 -10`) são contra o `--desde`, não contra os dois pais (A4).
- **Pedidos em `~/.forge-contrib/forge` com `--raiz-pedidos`:** o pedido é achado, a linha `origem:` sai com o caminho real; sem a opção, o pedido só pelo id não é achado (o padrão é `~/.forge-contrib/docs/pedidos/`).
- **Sem a linha do dono e sem merge de integração, a saída é a de antes:** comparei a `bin/forge-check` da `origin/develop` com a da branch (descontada a linha `versão não conferida` da cópia antiga fora de clone) em 17 combinações: REVAL-288 original e com `conferida 0b8a307` no lugar da linha do dono, etapas `codigo`, `review`, `qa`, `pr`, com e sem `--desde`; INTEG-LOTE-FC original sem `--desde` em `review` e `merge-integracao` (o merge não é isolado sem base fixada, comportamento de antes); e CONF-BASE-DONO etapa `codigo`. Saídas e rc idênticos em todas.

## Testes
`tests/test_conferencia_base_dono.py` cobre: E1 em 6 testes (aceita e diz a origem; sem a linha, o de hoje; fora do Histórico, sha abreviado, sha fora da branch, sem "dono"; a mais recente entre conferida e dono; gravada na própria entrega; etapa de branch inteira); E2 em 3 (integração limpa, conflito resolvido, commit próprio depois da integração); E3 em 5 (sem a opção, com a opção, antes do subcomando, `brief gerar`, brief de união). Faltam: duas integrações seguidas no intervalo (A2, o caso que hoje escapa) e `brief gerar --volta` com `--raiz-pedidos`, que o E3 cita (A5).

## Achados
- A1 (bloqueante) hooks/conformidade.json:49 · segurança/controle: o hook protege ~/.forge-contrib/docs/pedidos/, mas os pedidos reais e o alvo do --raiz-pedidos estão em ~/.forge-contrib/forge/docs/pedidos/; sonda do hook com forge:tech-lead gravando a linha da base do dono ali: rc 0 (no caminho protegido, rc 2). Proteja o caminho real
- A2 (bloqueante) bin/forge-check:844 · correção: o E2 só exige que não haja commit próprio sem merge; com duas integrações seguidas no intervalo, conteúdo novo posto no primeiro merge some (sonda: s.txt no merge 1, merge 2 limpo: "sem commit"; a develop lista s.txt). Limite ao head ser o único commit do intervalo, mais teste
- A3 (recomendado) bin/forge-check:1259 · consistência: brief gerar --volta propõe --desde só da última conferida; com a linha do dono mais recente, a PQ gerada reprova (--desde sem conferência anterior). Use bases_do_pedido aqui
- A4 (recomendado) bin/forge-check:896 · clareza: no escopo de integração, os números +/- são contra o --desde e não contra os dois pais (bin/forge-check +386 -10 no 8649439 é o que a develop trouxe); pode enganar a regra de anexo com remoção. Conte contra o pai da branch ou diga na linha
- A5 (recomendado) tests/test_conferencia_base_dono.py:123 · testes: o E3 cita brief gerar --volta com --raiz-pedidos e não há teste dele; acrescente um caso
- A6 (recomendado) bin/forge-check:888 · clareza: na etapa codigo, integração limpa sem commit próprio sai "pendente: intervalo vazio ... nenhum commit novo", mas há um commit (o merge); a linha engana quem confere uma entrega que é só a integração

## Parecer
**Reprovado**, por A1 e A2. O resto do E1 e do E3 está correto e confere com os casos reais; o E4 (agentes, changelog, mapa do `forge-testes`) está coerente e o `ESCOPO+` do mapa é técnico e justificado.

- **A1** (bloqueia, segurança/controle). A linha nova afrouxa o `--desde` da mesma forma que a `conferida`, e o pedido põe fora do escopo "aceitar base sem decisão do dono registrada": essa garantia depende de só o Jarvis gravar no pedido. O hook casa `~/.forge-contrib/docs/pedidos/` e, no projeto, `docs/pedidos/` relativo à raiz da sessão; a pasta real `~/.forge-contrib/forge/docs/pedidos/` (sem git, fora das duas) fica livre para qualquer papel. A lacuna já existia para a `conferida`, mas esta entrega documenta o `--raiz-pedidos` apontando para lá e acrescenta uma segunda linha que abre o delta. O autor levantou o ponto no Histórico. Sugestão: proteger a raiz real (ou toda raiz `*/docs/pedidos/` sob `~/.forge-contrib/`) com fixture de hook. Vira cartão também para o `security-engineer` (E2.1).
- **A2** (bloqueia, correção). `diferem_dos_dois_pais` olha só os pais do head. Com o intervalo `c1 -> M1 (merge da develop + s.txt novo) -> M2 (merge limpo da develop)`, o `log --no-merges` sai vazio, a interseção em M2 não tem s.txt (igual em M1) e a saída é `escopo: sem commit (nada a conferir)`, rc 0; a `bin/forge-check` da develop, no mesmo repositório, lista `confira "s.txt"`. É regressão e caminho para conteúdo sem conferência. O escopo diz "entrega cujo único commit é um merge de integração": exija `git rev-list de..head --not <base>` igual a só o head (ou some o `--cc` de cada merge do intervalo) e cubra com teste.
- A3 a A6 (recomendados), na lista acima.
