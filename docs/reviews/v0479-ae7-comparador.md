---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-ae7-comparador
commit: 757355b43bd7f4bb2b3b5dd109270cdb1d426f80
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-21
---
# Review: v0478 (E58.49, AE7.1 `forge-check comparar`, revalidação no head 757355b4)

Revalidação (H3, R-REVIEW) do parecer aprovado em f133eb07 (E58.45, head f50171d2). Delta lido por
`forge-check parecer delta docs/reviews/v0479-ae7-comparador.md`: intervalo `f50171d2..757355b4`, no domínio
`bin/forge-check`, `bin/forge_comparar.py`, `changelog.d/v0479-ae7-comparador.md`,
`tests/mutantes/v0478-ae7-comparar-{5,7,8,10,11,12}.json` e `tests/test_comparar.py`. Fora do delta nada foi relido.

## Conferido
- A11 (link simbólico): `fora_da_medida` lê o `ls-tree -r -z -l`; modo 120000 em qualquer pasta dá `nao-verificavel`
  (link simbólico na árvore), lista que falha ou não casa dá "árvore ilegível"; `extrair` deixa de gravar link (devolve
  False). Testes `LinksESource` (S15 a S17) nos dois lados. Na árvore real (`HEAD`, `origin/develop`, `origin/main`): 0 links.
- A12 (source do marketplace): `plugin_fora_da_raiz` exige uma entrada só com `source` `.` ou `./`; JSON ilegível, objeto,
  repositório de fora e dois plugins dão rc 2. O marketplace real tem `['.']`, então a medida segue útil.
- A13 (cabeçalho YAML): só o bloco entre os `---` iniciais (BOM e linhas em branco antes; sem fecho, o texto todo), lido em
  lote com `blobs_do_lote`, que recusa resposta truncada; `CABECALHO_SUSPEITO` pega `hooks` + `:` em qualquer recuo e em
  fluxo, `? hooks`, barra invertida, âncora, alias e tag. Sonda na árvore real: 0 dos `.md` do head casam, sem falso
  `nao-verificavel`. Isso também fecha o A6 da rodada anterior (o corpo do `.md` não conta mais).
- Lista do que mede: o docstring do módulo e o `help`/`description` do subcomando dizem o que dá rc 2 e o limite (hook
  declarado por outro caminho não é visto). O changelog acompanha.
- Testes trocados: o teste do `git grep` saiu junto com a busca; os falsos de `ls-tree` separam a lista com `-l`
  (`fora_da_medida`) da sem `-l` (extração) pelo argumento exato, a mesma regra do código (checklist, item 12). O CMP34 saiu
  com o código que ele guardava.
- Neutralidade (R-NEUTRO): `python3 -I tests/test_forge.py Neutralidade NeutralidadeDoNucleo`, ambiente limpo: 6 testes OK.
- Teste do item: `python3 -I tests/test_comparar.py LinksESource CabecalhoDoMd HooksForaDoHooksJson`, ambiente limpo: 12 OK.
- Mutantes (V2): `bin/forge-mutante --processos 1` nas specs 10, 11 e 12: CMP61 a CMP82 (22) morreram.
- Tamanho (H1): `git diff --numstat --no-renames origin/develop...HEAD` em `bin/`, `hooks/`, `scripts/`, `.github/` e
  `.githooks/` dá 303 linhas (`bin/forge_comparar.py` 295, `bin/forge-check` 6, `bin/forge-testes` 1+1); o delta somou 119
  em `bin/forge_comparar.py` (88 adições, 31 remoções) e 3 em `bin/forge-check`. **Excesso justificado:** segue um
  comportamento só (a medida "só aperta"); as linhas novas fecham A11, A12 e A13 da segurança, sem os quais o comparador
  diria `so-aperta: medido` sem rodar o hook que o Claude Code roda, pior que não ter a medida; cada guarda tem teste de
  comportamento e mutante morto. O PR deve dizer `teto: excedido, 303 linhas, guardas A9 a A13 da segurança, sem elas a
  medida afirma o falso`.
- `praticas.md` sem regra "decidida por: leitura"; suíte inteira fica com o CI (R-CUSTO), não rerrodada aqui.

## Achados
- A4 (recomendado) bin/forge_comparar.py:191 · só a raiz do projeto é normalizada nas reescritas; `HOME` e `transcript_path` diferem em cada lado, então um hook que os cite no `updatedInput` dá `entrada-reescrita` falso. Erro do lado seguro; normalizar o HOME como `{home}`.
- A14 (recomendado) bin/forge_comparar.py:42 · chave explícita por bloco literal com dois comentários antes do `:` (`? |-`, `  hooks`, `# a`, `# b`, `: {}`) escapa do `CABECALHO_SUSPEITO` (sonda local); o parse como chave `hooks` não foi provado (sem YAML aqui). Tratar `?` no começo de linha e `|`/`>` como suspeitos.

## Parecer
Aprovado no head 757355b4. O delta fecha A11, A12 e A13 da segurança e o A6 desta revisão, com teste de comportamento e
mutante morto em cada guarda nova; o excesso do teto (303 linhas) é justificado pelo critério do H1. A4 e A14 são
recomendados (R-REVIEW): viram cartão depois do merge. A decisão sobre os bloqueantes da segurança é do
`security-engineer` (R-SEGURANCA), na revalidação dele.
