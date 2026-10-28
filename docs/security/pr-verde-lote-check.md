---
tipo: revisao-seguranca
contrato: 1
pedido: pr-verde-lote-check
branch: melhoria/pr-verde-lote-check
commit: 26d2260eecbc01712927cfdaa67003df6b0ec107
parecer: reprovado
revisor: forge:security-engineer
data: 2026-10-27
---
# Review de segurança: pr-verde-lote-check

Pedido PR-VERDE-LOTE-CHECK (G1, G2, G6 e D4 do ESTUDO-PR-VERDE), revisado no pedido PR-VERDE-LOTE-CHECK-REV (E2.1). Diff `1f7bd7fd08cf04651d07fec674eaa5233c03215c...26d2260eecbc01712927cfdaa67003df6b0ec107`, 14 arquivos. Veredito: **reprovado**, com 2 bloqueantes nesta passada única: G2 deixa uma mudança do autor sumir atrás do merge da base (A1), e D4 tira do hash mais do que o fragmento (A2).

## Gatilhos
- `controles do Forge`: `bin/forge-check`, um arquivo protegido (portões `entrega`, `pr` e `brief`).

## Achados
- A1 (bloqueante) bin/forge-check:987 · controle do Forge afrouxado (defeito provado): no G2, o merge da base que descarta mudança da develop (resolução ours) some do escopo; com o Base-sha após o merge, antes listava src/app.txt +1 -1 e d.txt +0 -1, agora não
- A2 (bloqueante) bin/forge-check:702 · requisito da especificação (D4, só o fragmento): o startswith também tira do hash changelog.d/<slug>.md.md, changelog.d/<slug>.mdx/codigo.py e changelog.d/<slug>.md~; numa sonda, nenhum deles desatualiza o parecer
- A3 (recomendado) bin/forge-check:125 · já existia: KANBAN.md em LIVRES também casa por prefixo (KANBAN.md.x); usar a mesma correção do A2
- A4 (recomendado) bin/forge-check:503 · já existia, antes e depois: com --desde, o merge ours não aparece (o arquivo é igual na conferida e no head); comparar o head com a base atual, como o E4 faz nas etapas de merge
- A5 (recomendado) bin/forge-check:702 · o fragmento vem do argumento do pr, não da branch; usar branch_da_convencao quando houver, para que seja o fragmento da própria branch

## Detalhe dos achados
**A1 (G2, `escopo_pelo_primeiro_pai`, `bin/forge-check:972-989`; uso em `:1033-1036`).** No merge cujo segundo pai é ancestral da base, o código conta só `diff(p1,M) ∩ diff(p2,M)`, que é o `--cc`. Um arquivo que a develop mudou e que a resolução manteve igual ao lado da branch (`git merge -s ours`, ou "aceitar o meu lado" num conflito) fica igual ao primeiro pai. Por isso ele sai da interseção e deixa de ser contado, embora o merge desfaça a mudança da base. É uma mudança feita pelo autor, escondida atrás do merge.
- Prova: a sonda `sonda_g2.py` em `$TMPDIR/security-engineer-pr-verde-lote-check/` roda o binário de `1f7bd7f` e o de `26d2260` no mesmo repositório temporário. O cenário: trabalho em `a.txt`, a develop corrige `src/app.txt` e cria `d.txt`, a branch faz `merge -s ours`, e depois entra um commit de parecer.
- Com `--base-sha` no merge-base depois do merge, que é o que o `brief gerar` grava quando a branch já existe, e etapas `codigo`, `review` e `pr`, sem `--desde`:
  - o binário de antes lista `confira "d.txt" +0 -1` e `confira "src/app.txt" +1 -1`;
  - o de agora só lista `escopo: integração da base (o que difere dos dois pais)`, `a.txt` e o parecer, com rc 0 nos dois.
- O merge limpo continua correto: nele, o que a base trouxe sai do escopo, como pede o G2.
- Caminho: um agente autor (por erro de resolução de conflito ou de propósito) descarta, no merge da develop, uma correção que já está na base, por exemplo um controle do Forge. O conferente, que lê o `forge-check entrega`, não vê a reversão. Ela só aparece se o review ler o diff contra a develop.
- Severidade: média (o controle de escopo afrouxou, e outro portão ainda pode pegar a reversão). Esforço: P. Dono: `tech-lead`.
- Correção mínima: no merge da base, contar também o que a base mudou e o merge não manteve. Ou seja, somar `diff(merge-base(p1,p2), p2) ∩ diff(p2, M)` à interseção, o que dá `proprios = (diff(p1,M) ∩ diff(p2,M)) ∪ (diff(mb,p2) ∩ diff(p2,M))`. Junto vêm:
  - um teste com `merge -s ours` e uma resolução "meu lado", que hoje passa e deve listar o arquivo;
  - um mutante que tire o termo novo.
- O corpus das 4 asserções invertidas (`tests/test_conferencia_base_dono.py:125,151`, `tests/test_forge.py:4519`, `tests/test_volta_por_delta.py:288`) só tem merges limpos, em que o arquivo é igual ao lado da base. Nesses casos a inversão está certa e não abre caminho por si. Falta a dimensão "merge que descarta a base" na matriz.

**A2 (D4, `bin/forge-check:452`, `:702`; também `:419`).** O `commit_vale` filtra com `f.startswith(livres)`. Com o fragmento como entrada, `changelog.d/<slug>.md` serve de prefixo, e qualquer caminho que comece por ele fica fora do hash.
- Prova: a sonda `sonda_d4.py` pega um parecer aprovado e, depois dele, faz um commit com cada um destes caminhos: `changelog.d/ramo.md.md` (que a release também lê, porque o `forge-changelog` faz `glob("*.md")`), `changelog.d/ramo.mdx/codigo.py` e `changelog.d/ramo.md~`. O `cmd_pr` não devolve nenhum `desatualizado`.
- A decisão D4 do dono e o brief pedem que só o fragmento `changelog.d/<slug>.md` saia do hash.
- Impacto: um texto de changelog não revisado entra por um segundo fragmento, e um arquivo qualquer pode entrar sob a pasta `<slug>.mdx/` sem pedir parecer novo. Hoje nada executa `changelog.d/`, então a severidade é baixa, mas o requisito declarado não se cumpre. Esforço: P. Dono: `tech-lead`.
- Correção mínima: casar a entrada sem `/` final por igualdade, e só a com `/` por prefixo (`f == x or (x.endswith("/") and f.startswith(x))`). Isso vale no `:452` e no laço de conflitos do `:419`. Junto vêm um teste com os três caminhos acima e um mutante.

**A3.** `LIVRES` (`:125`) tem `KANBAN.md` e `docs/kanban/`. `KANBAN.md.x` também fica fora do hash. Já existia antes desta entrega, e a correção do A2 o resolve junto.

**A4.** Com `--desde` (`arquivos_da_entrega`, `:503`), o resultado é `nomes ∩ desde..head`. O arquivo que o merge ours mantém igual ao da conferida não entra em `novos`. A sonda deu o mesmo resultado antes e depois desta entrega, então não foi introduzido aqui. Fica como dimensão para um próximo cartão: comparar o conteúdo do head com a base atual (o E4 já faz isso nas etapas de merge).

**A5.** O `cmd_pr` monta o fragmento livre como `changelog.d/{pedido}.md` a partir do argumento. Na convenção `melhoria/<slug>`, o argumento coincide com o slug. Fora dela, ou com um argumento diferente do slug, o fragmento livre deixa de ser o da branch. O `branch_da_convencao(raiz, ref)` dá o slug certo.

**Conferido sem achado:**
- **G2, merge de outra branch:** quando o segundo pai não é ancestral da base, o merge conta inteiro, o que está certo (falha fechada). Merge octopus e commit raiz também caem em falha fechada. O teste `test_merge_de_outra_branch_conta_tudo` e o mutante M5 cobrem esse caso.
- **G2, `pedido_do_pr`:** o slug só é trocado quando existe um único slug. O `uso_do_pr` roda de novo sobre o resultado, e o slug é impresso com `nome_seguro`.
- **G6, `reescrito_por_portao`:** só é chamado depois de `autoria_do_parecer`, que já prova que aquele papel gravou aquele conteúdo. A única coisa que muda é a linha informativa "anexo com remoção", que passa a "ok". O parecer reescrito pelo autor não tem registro de autoria, cai em `escopo: confira` como antes e continua reprovando. O casamento é pelo `commit:` e pelo papel do `Agente destino`, nunca pelo caminho.
- **G6, `--brief` do `-REV`:** a união com um brief do `-REV` continua exigindo a mesma Branch, Base e Base-sha, e o conferente confere o sha256.
- **G1:** só acrescenta reprovações (o corte do `Cobre`, o caminho do PQ e as decisões do pedido de origem). Nada afrouxa. A regex `CAMINHO_NO_PQ` é linear, e o argumento do `cat-file` começa sempre pelo ref, então não vira opção.
- **Testes do item:** passam (176 testes, nos 5 módulos tocados e nas classes `EntregasParalelas` e `PrAposMergeDaBase` de `test_forge`).
- **PA-7** (`docs/engineering/achados-recorrentes.md`): a lista está vazia, então não há item a conferir.

## Riscos aceitos e ferramentas
- Nenhum risco aceito.
- Ferramentas: só revisão estática por leitura, mais sondas locais em repositórios temporários (`$TMPDIR/security-engineer-pr-verde-lote-check/`).
- Lacuna: `gitleaks`, `semgrep`, `zizmor`, `actionlint` e `osv-scanner` não estão no PATH. A entrega não toca workflow nem dependência.
