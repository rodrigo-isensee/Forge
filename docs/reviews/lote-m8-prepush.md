---
tipo: review
contrato: 1
pedido: lote-m8-prepush
branch: melhoria/lote-m8-prepush
commit: e025ed8a210a7c97796adc5075854066bc0e0b9a
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-24
---
# Review: lote-m8-prepush (EST-M8, REVERSAO-MAPA, FORGE-TESTES-CAMINHOS)

Escopo: revalidação por delta (pedido LOTE-M8-PREPUSH-REV, E1.1) do parecer anterior (`7169849`, sobre `a15a569`, aprovado) para o head `e025ed8a210a7c97796adc5075854066bc0e0b9a` (volta 1: `64a05b3`, `cdec018`, `e025ed8`). O teto M14 foi conferido sobre a branch inteira (`3c66b88...e025ed8`).

## Delta lido
`bin/forge-check delta --parecer docs/reviews/lote-m8-prepush.md` (intervalo `a15a569..e025ed8`), lido inteiro:
- `.githooks/pre-push`: 241-244, 246, 248, 256-264, 274, 301-303
- `bin/forge-testes`: 69-73, 75, 81, 93-96, 117, 471
- `changelog.d/lote-m8-prepush.md`: 2
- `tests/mutantes/lote-m8-prepush.json`: 1-86
- `tests/test_pre_push_afetados.py`: 112-165
- `tests/test_testes_tocados.py`: 2, 49, 129, 131-137, 143-170, 172-201, 215-237

Já lido (parecer anterior, sem mudança no delta): o laço de bloqueios de conteúdo do hook (main, homolog, develop, não fast-forward antes de qualquer teste), as condições de recuo que não mudaram, `caminhos_pedidos` e as regras REVERSAO-MAPA e `(dev/)?\.claude-plugin/`, a mudança de `NaoEPortao`.

## O que conferi
- **A2 anterior (base resolvida duas vezes): resolvido.** `.githooks/pre-push:257` resolve `refs/remotes/origin/develop^{commit}` uma vez em `base_dev`; o plano (`:264`) e a execução (`:274`) usam o mesmo sha. A ref completa também tira a ambiguidade com uma branch local `origin/develop` (teste `test_base_e_a_ref_remota_mesmo_com_branch_local_de_mesmo_nome`).
- **A3 anterior (comentário da prova): resolvido.** `:241-244` e `:301-303` dizem que o `so_parecer` repete a anotação por herança da árvore remota verde, não como prova nova.
- **A4 anterior (descrição do argparse): resolvido.** `bin/forge-testes:471`.
- **Guarda do diff vigiado** (`.githooks/pre-push:261-263`): `merge-base` com a base remota e `git diff --name-only` sobre `bin/forge-testes`, `tests/config.json` e `.githooks/`; qualquer arquivo listado, ou falha do `merge-base`, devolve 1 e cai na suíte inteira (falha fechada). O teste `test_diff_que_toca_o_filtro_o_mapa_ou_o_hook_roda_a_suite_inteira` monta um filtro permissivo já na base (controle: só `test_a` roda) e prova que tocar cada um dos três caminhos roda a suíte inteira. Observação, sem achado: a guarda vive no próprio hook da branch, então um diff do hook pode removê-la; o controle de fundo continua sendo a bateria completa do CI do PR, como decidiu o dono (M8). A leitura de segurança disso é do `security-engineer`.
- **Mapa ampliado** (`bin/forge-testes:69-75`, `:81`, `:93-96`, `:117`): `LEITORES_DE_TEXTO` entra em `CONTEUDO`, logo alcança `agents/`, `skills/`, `docs/`, `stacks/`, `templates/` e o manifesto; `bin/forge-changelog` ganha `test_conferir_release`; `hooks/.*` ganha `test_agentes_hash_brief`, `test_agentes_clone` e `test_textos_dono_f10`; `IMPORTADO_POR` ganha `test_portao_diff_proprio -> test_ambiente_git`. Só alarga o conjunto rodado (nunca estreita), então não abre recuo novo. O comentário de `:93-94` cita `agentes.py`, `_comum.py` e `vigia.py`, mas a regex é `hooks/.*` inteira: correto, só mais largo que o comentário.
- **Conferência `MapaCobreOQueOsTestesLeem` por `ast`** (`tests/test_testes_tocados.py:128-237`): reconhece `RAIZ / "a" / "b"`, `joinpath`, variável de módulo que guarda caminho, `Path(__file__).resolve().parent[.parent]` e `ler("...")`; parte dada por variável marca o módulo como dinâmico e, aí, todo literal do módulo que é arquivo do Forge conta (falha fechada). `test_a_conferencia_enxerga_as_formas_de_citar_um_caminho` prova as formas com um fonte sintético; `test_a_familia_dos_testes_que_executam_hooks_e_bin_roda_no_envio_dirigido` fixa os casos do A1 da segurança. A exceção `SO_CITA = {"test_testes_tocados"}` é justificada (o módulo só passa caminhos como texto a `planejar`). O mínimo de 40 itens da varredura segue (checklist, item 11).
- **Testes das guardas do hook** (`tests/test_pre_push_afetados.py:112-165`): árvore suja com arquivo mapeado (afirma o caminho tomado pela mensagem, não só as marcas, o que mata o mutante que sobrevivia), ferramenta que é link, filtro/mapa/hook tocados, ref ambígua. Spec `tests/mutantes/lote-m8-prepush.json` com os mutantes de cada guarda e o teste que os mata; a execução dos mutantes é do QA.
- **Rodado aqui:** `python3 -m unittest tests.test_pre_push_afetados tests.test_testes_tocados -q` → `OK` (19,6 s); `shellcheck .githooks/pre-push` → sem saída; `bin/forge-testes --listar --base 3c66b88` → `suíte completa (.githooks/pre-push sem mapa)`. A suíte inteira passou no pre-push da volta (1964 OK, histórico do pedido); não a refiz.
- R-CUSTO, R-NEUTRO: nada pago, nenhum termo de projeto. Fragmento `changelog.d/lote-m8-prepush.md` atualizado. Commits em Conventional Commits, cada um citando o achado que corrige.
- PA-7 (`docs/engineering/achados-recorrentes.md`): lista vazia, nada a conferir.

## Teto M14 (exceção pedida: não aceita)
`git diff --numstat --no-renames 3c66b88...e025ed8`, só os contáveis: `.githooks/pre-push` 40+3, `bin/forge-testes` 49+13, `tests/test_pre_push_afetados.py` 209+0, `tests/test_testes_tocados.py` 168+18 = **500 linhas**, acima de 400. Fora da conta: pareceres, `changelog.d/` e `tests/mutantes/`.

A exceção não pode ser aceita: o pedido diz que o PR não toca `hooks/` nem `PROTEGIDOS`, mas `.githooks/` está em `PROTEGIDOS` (`tests/catraca.py:43`, já registrado no parecer anterior), e a M14 diz que a exceção não vale em PR que mexe em caminho de `PROTEGIDOS` (`agents/tech-lead.md`, item 3; skill `engineering-practices`). Isso é o A5, bloqueante por requisito. Saída sugerida (do autor): dividir em dois PRs, cada um abaixo do teto e com o seu teste: (1) o mapa e a conferência, `bin/forge-testes` + `tests/test_testes_tocados.py` (62 + 186 = 248 linhas: REVERSAO-MAPA, FORGE-TESTES-CAMINHOS e o A1 da segurança), entrando primeiro; (2) o hook, `.githooks/pre-push` + `tests/test_pre_push_afetados.py` + a spec de mutantes (43 + 209 = 252 linhas: EST-M8 e as guardas). Tirar a exceção da regra é decisão do dono (`R-DECISAO`), não deste review.

## Achados
- A1 (recomendado) README.md:68 · continua aberto: o README, docs/economia-de-tokens.md:10 e agents/tech-lead.md:22 ainda dizem que o pre-push roda a suíte inteira; segue para o cartão DOCS-REGRA5-PREPUSH (ampliado), não devolve
- A5 (bloqueante) .githooks/pre-push:247 · requisito (decisão M14): a branch soma 500 linhas contáveis (teto 400) e toca `.githooks/`, caminho de `PROTEGIDOS` (`tests/catraca.py:43`), onde a exceção `teto: excedido` não vale; dividir em dois PRs abaixo do teto (mapa e conferência; hook e as suas guardas)

## Parecer
Reprovado, só pelo A5. Na substância, a volta resolve o que o review anterior recomendou (A2 a A4) e o que a segurança e o QA pediram dentro do que este review lê: base única pela ref remota, guarda do diff vigiado com falha fechada, mapa mais largo provado pela conferência por `ast`, e as guardas do hook com teste e spec de mutantes. Nenhum defeito de comportamento achado no delta. O bloqueio é de forma (tamanho do PR num caminho protegido) e se resolve dividindo a branch, sem mudar o código. Ao dividir, cada PR passa por revalidação por delta (o código é o mesmo; o que muda é a base do segundo). Segurança e QA têm parecer próprio (E2.1, E3.1).
