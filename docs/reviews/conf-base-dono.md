---
tipo: review
contrato: 1
pedido: conf-base-dono
branch: melhoria/conf-base-dono
commit: d47d1b4728cae7d6811a21649eb333025b264d7b
parecer: aprovado
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

## Achados da rodada 1 (8c24358)
- A1 (bloqueante) hooks/conformidade.json:49 · segurança/controle: o hook protege ~/.forge-contrib/docs/pedidos/, mas os pedidos reais e o alvo do --raiz-pedidos estão em ~/.forge-contrib/forge/docs/pedidos/; sonda do hook com forge:tech-lead gravando a linha da base do dono ali: rc 0 (no caminho protegido, rc 2). Proteja o caminho real
- A2 (bloqueante) bin/forge-check:844 · correção: o E2 só exige que não haja commit próprio sem merge; com duas integrações seguidas no intervalo, conteúdo novo posto no primeiro merge some (sonda: s.txt no merge 1, merge 2 limpo: "sem commit"; a develop lista s.txt). Limite ao head ser o único commit do intervalo, mais teste
- A3 (recomendado) bin/forge-check:1259 · consistência: brief gerar --volta propõe --desde só da última conferida; com a linha do dono mais recente, a PQ gerada reprova (--desde sem conferência anterior). Use bases_do_pedido aqui
- A4 (recomendado) bin/forge-check:896 · clareza: no escopo de integração, os números +/- são contra o --desde e não contra os dois pais (bin/forge-check +386 -10 no 8649439 é o que a develop trouxe); pode enganar a regra de anexo com remoção. Conte contra o pai da branch ou diga na linha
- A5 (recomendado) tests/test_conferencia_base_dono.py:123 · testes: o E3 cita brief gerar --volta com --raiz-pedidos e não há teste dele; acrescente um caso
- A6 (recomendado) bin/forge-check:888 · clareza: na etapa codigo, integração limpa sem commit próprio sai "pendente: intervalo vazio ... nenhum commit novo", mas há um commit (o merge); a linha engana quem confere uma entrega que é só a integração

## Parecer da rodada 1
**Reprovado**, por A1 e A2. O resto do E1 e do E3 está correto e confere com os casos reais; o E4 (agentes, changelog, mapa do `forge-testes`) está coerente e o `ESCOPO+` do mapa é técnico e justificado.

- **A1** (bloqueia, segurança/controle). A linha nova afrouxa o `--desde` da mesma forma que a `conferida`, e o pedido põe fora do escopo "aceitar base sem decisão do dono registrada": essa garantia depende de só o Jarvis gravar no pedido. O hook casa `~/.forge-contrib/docs/pedidos/` e, no projeto, `docs/pedidos/` relativo à raiz da sessão; a pasta real `~/.forge-contrib/forge/docs/pedidos/` (sem git, fora das duas) fica livre para qualquer papel. A lacuna já existia para a `conferida`, mas esta entrega documenta o `--raiz-pedidos` apontando para lá e acrescenta uma segunda linha que abre o delta. O autor levantou o ponto no Histórico. Sugestão: proteger a raiz real (ou toda raiz `*/docs/pedidos/` sob `~/.forge-contrib/`) com fixture de hook. Vira cartão também para o `security-engineer` (E2.1).
- **A2** (bloqueia, correção). `diferem_dos_dois_pais` olha só os pais do head. Com o intervalo `c1 -> M1 (merge da develop + s.txt novo) -> M2 (merge limpo da develop)`, o `log --no-merges` sai vazio, a interseção em M2 não tem s.txt (igual em M1) e a saída é `escopo: sem commit (nada a conferir)`, rc 0; a `bin/forge-check` da develop, no mesmo repositório, lista `confira "s.txt"`. É regressão e caminho para conteúdo sem conferência. O escopo diz "entrega cujo único commit é um merge de integração": exija `git rev-list de..head --not <base>` igual a só o head (ou some o `--cc` de cada merge do intervalo) e cubra com teste.
- A3 a A6 (recomendados), na lista acima.

## Revalidação (d47d1b4)

Volta `557c602..d47d1b4`: `05bab4a`, `1a8e223`, `6eeecad`, `f7f2fdc` (correção, `git diff 557c602 f7f2fdc`: `agents/conferente.md`, `bin/forge-check`, `tests/test_conferencia_base_dono.py`, +144 -32) e `d47d1b4`, merge da `develop` (`139a3b4`) sem resolução própria (`git show --cc` vazio). Delta lido: `forge-check delta --parecer docs/reviews/conf-base-dono.md` (desde `8c24358`) lista, além da correção, `.github/workflows/ci.yml`, `changelog.d/ci-py314.md`, `changelog.d/impl-n-agt-a.md` e `bin/forge-check` 1503-1517, que vieram da `develop` (#294, #295) e têm pareceres próprios: ficaram como "já lido" (fora desta entrega). Li a correção inteira.

Ferramenta: `tests.test_conferencia_base_dono` (HOME isolado em $TMPDIR): 21 testes OK (eram 14). A suíte completa é do QA e do pre-push (o autor registra 1744 OK).

Achados da rodada 1:
- **A1** fora desta volta por decisão técnica do Jarvis (cartão HOOK-RAIZ-CONTRIB; o PR desta branch só abre depois dele). A volta reduz a superfície: `--raiz-pedidos` agora só aceita pasta sob `~/.forge-contrib` ou sob a raiz do repositório (rc 2 fora, com teste), e a linha do dono exige a forma exata.
- **A2 resolvido.** `diferem_dos_dois_pais` exige que o head seja o único commit próprio de `de..head` (`rev-list ... --not <base>` igual a `[head]`), que um pai seja o `--desde` e o outro ancestral da base; com dois merges seguidos volta ao escopo de sempre. O teste `test_dois_merges_seguidos_nao_escondem_arquivo_do_autor` reproduz a minha sonda (s.txt no primeiro merge) e afirma `confira "s.txt"`.
- **A3 resolvido.** `gerar_volta` usa `bases_do_pedido` (a linha mais recente, `conferida` ou do dono); `conferidas_do_pedido` saiu sem outro uso. Testes `test_a_pq_da_volta_traz_a_base_do_dono_como_desde` e `test_a_pq_gerada_passa_no_entrega`.
- **A4 resolvido.** No escopo de integração os números são, por arquivo, o maior `+`/`-` contra os dois pais (o `-` do binário prevalece), e a regra do anexo com remoção não é enganada. Teste `test_os_numeros_da_integracao_sao_contra_os_dois_pais` (`+1 -4`).
- **A5 resolvido.** Classe nova de `brief gerar --volta` com `--raiz-pedidos` (os dois testes do A3).
- **A6 resolvido.** Na etapa `codigo`, entrega só de integração sai `pendente: a entrega é só a integração da base (o merge não traz trabalho próprio)`, com teste.

Contrato novo da linha do dono: `BASE_DO_DONO` casa só `- <data>[ <hora>]: base do delta fixada pelo dono <sha40>` abrindo a linha do `## Histórico`, e só vale com uma `DECISÃO DO DONO` no pedido; base do dono igual ao head é recusada (delta vazio sem aviso), com teste. Documentado em `agents/conferente.md:81` (forma exata, exigência da decisão, regra dos dois merges e limite do `--raiz-pedidos`) e na ajuda do `bin/forge-check` (linha 73 e `AJUDA_RAIZ_PEDIDOS`).

Commits: Conventional Commits em português, um por achado, mensagens claras.

## Parecer da revalidação
**Aprovado.** A2 a A6 resolvidos e testados; A1 segue no cartão HOOK-RAIZ-CONTRIB, fora desta entrega. Um recomendado novo (A7), que não bloqueia; vale também como cartão para o `security-engineer` (E2.1) avaliar.

## Achados
- A7 (recomendado) bin/forge-check:731 · controle: a linha do dono vale com qualquer DECISÃO DO DONO do pedido, não com a que fixou a base; quase todo pedido tem uma (este tem três), e a amarra é fraca. Exija que a decisão cite o sha da base (sha7 ou sha40)
