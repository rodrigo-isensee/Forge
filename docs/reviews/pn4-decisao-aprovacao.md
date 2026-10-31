---
tipo: review
contrato: 1
pedido: pn4-decisao-aprovacao
branch: melhoria/pn4-decisao-aprovacao
commit: e2f3390adad9be87cca02a42d37bde2411812ff4
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-30
---
# Review: pn4-decisao-aprovacao

Pedido PN4-DECISAO-APROVACAO (P-N4), revisão E1.1 do PN4-DECISAO-APROVACAO-REV. Diff lido: `add00ab...8ebaa95` (4 commits: f21e77f, 0a88e66, fda3d88, 8ebaa95). Rodada 2 (volta 1, e2f3390), por delta sobre o parecer d0a907a (head 8ebaa95).

## Achados
- A1 (recomendado) bin/forge-check:4341 · hora_da_aprovacao lê o conferencias.md só da --raiz; com os pedidos por --raiz-pedidos a aprovação não é vista e tudo segue cobrado (falha fechada). Mantido da rodada 1; em cartão PN4-CONF-RAIZ-PEDIDOS.
- A2 (recomendado) bin/forge-check:4342 · a guarda `len(c) >= 6` segue sem teste nem mutante (classe AR-2). Mantido da rodada 1; em cartão PN4-GUARDA-LINHA-CURTA.
- A3 (recomendado) agents/conferente.md:49 · o texto e docs/regras/R-BRIEF.md:12 não citam o aviso `decisão posterior à aprovação` (classe AR-9). Mantido da rodada 1; em cartão PN4-DOC-CONFERENTE.
- A4 (recomendado) bin/forge-check:4343 · a comparação é no minuto: o brief reescrito no mesmo minuto depois da aprovação ainda vale como aprovado. Limite da hora `HH:MM` do registrar; janela de menos de 60 s, sem gatilho provado. Fica para o parecer de segurança.

## Revalidação por delta (rodada 2)
- **Delta lido** (`forge-check delta --parecer` e `git diff ddcf322..e2f3390`): `bin/forge-check` 4338-4340, 4343 e 4626; `tests/test_decisao_aprovacao.py` 2, 8, 61, 98 e 100; `tests/mutantes/pn4-decisao-aprovacao.json` (M1 a M4, M10, M14 e M15). **Já lido** na rodada 1 e sem mudança: o resto do diff `add00ab...8ebaa95`, incluindo `decisao_posterior`, `decisoes_cobradas`, `bin/forge-testes` e `tests/test_testes_tocados.py`.
- **`c[0] >= escrita`** (`bin/forge-check:4340` e `:4343`): o mtime do brief vai para `AAAA-MM-DD HH:MM` no fuso local (`fromtimestamp(...).astimezone()`), o mesmo formato e o mesmo fuso do `conferencia registrar` (`datetime.now().astimezone()`, `:2065`). As duas strings passam pelo `HORA_DO_REGISTRO.fullmatch` antes de comparar, então a ordem de texto é a ordem do tempo. Aprovação anterior ao minuto da escrita não vale e o brief volta a ser cobrado contra tudo (falha fechada). Isso corrige o A1 da segurança (ddcf322). O `chmod 0444` do `proteger_brief_aprovado` (`:2079`) não mexe no mtime, então o brief protegido continua aprovado. Brief copiado ou reescrito depois perde a aprovação, o que é o lado seguro.
- **Caminho do brief em vez de `brief.name`** (`:4626`, `:4339`): os dois chamadores de `avaliar_brief` (`:4664` e `:4824`) passam um `Path` que já foi lido (`read_bytes`), então o `stat()` não acha arquivo ausente. O `Path(brief).name` mantém o nome conferido como antes. `decisoes_cobradas` só chama `hora_da_aprovacao` com brief verdadeiro (`:4419`), e o mutante M10 (`None`) morre.
- **Testes**: o brief do teste ganha mtime fixo de 10:00:30 (`os.utime` com `time.mktime`, hora local, o mesmo fuso do código). O caso `09:59` prova o A1, e o caso `10:00` (mesmo minuto) continua aprovando no teste do aviso. A hora torta `2026` virou `10:5` para que o M4 continue morrendo com a comparação nova. `python3 -m unittest tests.test_decisao_aprovacao`: 7 testes, OK.
- **Ferramenta citada**: `bin/forge-mutante tests/mutantes/pn4-decisao-aprovacao.json` em e2f3390 dá M1 a M15 `morreu`, rc 0. M14 (sem a comparação) e M15 (`>` no lugar de `>=`) cobrem as duas bordas novas.
- **Teto M14**: `git diff --numstat --no-renames add00ab...e2f3390` dá `bin/forge-check` 39, `bin/forge-testes` 2, `tests/test_decisao_aprovacao.py` 106 e `tests/test_testes_tocados.py` 2, ou seja, **149 de 150**, sem exceção. A spec de mutantes, o fragmento e os pareceres ficam fora da conta. É um comportamento só e nada em `hooks/`.
- **Commit** e2f3390: Conventional Commits em português, com o pedido e o A1 da segurança no título.
- **Achados recorrentes** (PA-7): A2 é da classe AR-2 e A3, da AR-9. O delta não traz classe nova. Sem linha AR nova nesta rodada (DECISÃO TÉCNICA 2026-10-29 15:28 do pedido T1-CONF-ESCOPO-REV).

## Parecer
**Aprovado** sobre e2f3390. A volta corrige só o A1 da segurança, como manda a DECISÃO TÉCNICA 2026-10-30 00:46. Os recomendados A1 a A3 seguem em cartão, e o A4 é recomendação nova que não devolve.

### Rodada 1 (8ebaa95), mantida como já lida
A entrega faz o que o E1 e o E2 pedem, nem mais nem menos.

- **hora_da_aprovacao** (`bin/forge-check:4336`): lê a última linha da tabela com o nome do brief (sem `.md`, sem caixa), modo `brief`, resultado aprovado (`_aprovou`, o mesmo critério dos outros leitores) e hora no formato do registrar (`HORA_DO_REGISTRO.fullmatch`); hora torta, outro brief, outro modo ou reprovação não valem como aprovação. O arquivo é só acrescentado pelo `conferencia registrar`, então a última linha na ordem do arquivo é a mais recente.
- **decisao_posterior** (`bin/forge-check:4346`): comparação estrita de texto `AAAA-MM-DD HH:MM` (ordenável por ter zeros à esquerda); só data e hora maiores viram aviso; a mesma hora da aprovação segue cobrada; decisão sem hora (`DECISÃO DO DONO (2026-10-24)`) não casa com `HORA_DA_DECISAO` e segue cobrada; sem aprovação, `False`. Conferi também por execução numa cópia em `$TMPDIR` do pedido REV com duas decisões novas: a de 01:10 saiu como aviso e a de 00:39 (hora igual à aprovação) saiu como `decisões: falta`, rc 1.
- **Brief sem aprovação registrada**: `aprovacao` é `None`, `decisao_posterior` devolve `False` e tudo é cobrado como antes. Os dois chamadores de `decisoes_cobradas` no `brief gerar` (`:1527`, `:5048`) não passam o brief e ficam iguais; `avaliar_brief` (`:4625`) passa o nome e cobre o `forge-check brief` e o `brief mensagem`.
- **Mapa FORGE_CHECK** (`bin/forge-testes:71`) com `test_decisao_aprovacao` e a conta fixa de `tests/test_testes_tocados.py:61` de 31 para 32: consequência direta do módulo novo, no mesmo commit (DECISÃO TÉCNICA 2026-10-30 00:23).
- **Teto M14**: `git diff --numstat --no-renames` dá 38 em `bin/forge-check`, 2 em `bin/forge-testes`, 104 em `tests/test_decisao_aprovacao.py` e 2 em `tests/test_testes_tocados.py`: 146 linhas, dentro de 150, sem exceção (a spec de mutantes e o fragmento ficam fora). Um comportamento só; nenhum arquivo de `hooks/`. `bin/forge-check` está em `PROTEGIDOS`, o que só impede a exceção do teto, que não é usada.
- **Testes** (`tests/test_decisao_aprovacao.py`): os três casos do E2 (posterior avisa com rc 0, anterior faltando reprova, sem aprovação cobra tudo) e as bordas (última aprovação, hora igual, decisão sem hora, aprovação falsa por reprovação, outro brief, outro modo e hora torta). O teste limpa `GIT_*` e `FORGE_*` e isola o `HOME` (classe AR-4 conferida). `python3 -m unittest tests.test_decisao_aprovacao tests.test_testes_tocados`: 88 testes, OK.
- **Ferramentas citadas, não refeitas à mão**: `bin/forge-mutante tests/mutantes/pn4-decisao-aprovacao.json` em 8ebaa95: M1 a M13 `morreu`, rc 0; `bin/forge-mutante --cobertura --base add00ab`: as linhas novas de guarda aparecem `coberta`, rc 0. Sem shell tocado (shellcheck não se aplica).
- **Commits**: Conventional Commits em português, um por item (E1, spec, fragmento, mapa), corpo com o pedido. Fragmento `changelog.d/pn4-decisao-aprovacao.md` presente; o `CHANGELOG.md` não foi editado.
- **Achados recorrentes conferidos** (PA-7): AR-1 (lista de mutantes) e AR-2 (ramo de guarda sem teste) aparecem só no A2, como recomendação; AR-4 conferido acima; AR-5 não se aplica (o teste não decide caminho com python); AR-9 aparece no A3 (texto antigo em outro arquivo, fora do escopo). Sem linha AR nova nesta rodada, pela DECISÃO TÉCNICA 2026-10-29 15:28 do pedido T1-CONF-ESCOPO-REV: a classe do A2 é a do AR-2 e a do A3, a do AR-9.
- **Para a segurança** (cartão, não refeito aqui): a aprovação vem de uma linha do `docs/kanban/conferencias.md`; uma linha acrescentada fora do `conferencia registrar` transformaria decisões posteriores em aviso. O brief aprovado fica `0444`, o que limita a troca do texto depois da aprovação. Parecer próprio do `security-engineer` (E2.1).
