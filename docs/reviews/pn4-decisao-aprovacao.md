---
tipo: review
contrato: 1
pedido: pn4-decisao-aprovacao
branch: melhoria/pn4-decisao-aprovacao
commit: 8ebaa9540c4019591558de816c0bda8775250cee
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-30
---
# Review: pn4-decisao-aprovacao

Pedido PN4-DECISAO-APROVACAO (P-N4), revisão E1.1 do PN4-DECISAO-APROVACAO-REV. Diff lido: `add00ab...8ebaa95` (4 commits: f21e77f, 0a88e66, fda3d88, 8ebaa95). Primeira rodada: sem parecer anterior, sem delta.

## Achados
- A1 (recomendado) bin/forge-check:4340 · hora_da_aprovacao lê o conferencias.md só da --raiz; com a raiz no clone e os pedidos por --raiz-pedidos, a aprovação não é vista e tudo segue cobrado (falha fechada, como o registrar). Sugestão: ler também das RAIZES_DE_BRIEF, como o ler_registro.
- A2 (recomendado) bin/forge-check:4341 · a guarda `len(c) >= 6` (linha de tabela curta) não tem teste nem mutante na spec; sem ela, uma linha curta derruba o comando com IndexError. Sugestão: um caso com linha de 3 células e o mutante dela na spec.
- A3 (recomendado) agents/conferente.md:49 · o texto ainda diz que o comando cobra todas as linhas do dono e não cita o aviso `decisão posterior à aprovação`; o mesmo vale para docs/regras/R-BRIEF.md:12. Fora do escopo deste pedido (cadeia K e regra com ID): cartão próprio.

## Parecer
**Aprovado.** A entrega faz o que o E1 e o E2 pedem, nem mais nem menos.

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
