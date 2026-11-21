---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-ae7-comparador
commit: 2d1fa4faf827fbe077af623b60c21ca05882dec4
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-21
---
# Review: v0478 (E58.54, AE7.1 `forge-check comparar`, revalidação no head 2d1fa4fa)

Revalidação (H3, R-REVIEW) do parecer aprovado em 2a7f9ec2 (E58.49, head 757355b4). Delta lido por
`forge-check parecer delta docs/reviews/v0479-ae7-comparador.md`: intervalo `757355b4..2d1fa4fa`, no domínio
`bin/forge-check`, `bin/forge_comparar.py`, `changelog.d/v0479-ae7-comparador.md`,
`docs/propostas/v0479-melhorias-anti-erro.md` (emenda AE7.1, E58.52), `tests/mutantes/v0478-ae7-comparar-{5,7,8,10..16}.json`
e `tests/test_comparar.py`. Fora do delta nada foi relido.

## Conferido (emenda AE7.1 item por item contra `bin/forge_comparar.py`)
- F1: `MODOS` = 100644 e 100755; `fora_da_medida` recusa o primeiro modo fora (link 120000, gitlink 160000) com
  `F1 modo <m> na árvore`; `extrair` também recusa modo fora da F1. O teste do submódulo passou de "não derruba" a rc 2 nos
  dois lados.
- F2: basename `.gitattributes` ou `.gitmodules` em qualquer pasta, sem caixa. Bate com o texto.
- F3: `.mcp.json`, `.lsp.json`, `settings.json` só na raiz (compara o caminho inteiro, sem caixa); a fonte está citada no
  docstring (plugins-reference, Claude Code 2.1.224), como a emenda pede. O teste confirma que `docs/settings.json` e
  `a/.mcp.json` medem.
- F4: `CHAVES_PLUGIN` é a lista exata da emenda; objeto que não é dict sai. O autor foi mais estrito: `hooks` em qualquer
  nível (`author.hooks`) também sai. Só acrescenta rc 2, não afrouxa; aceito.
- F5: raiz em `$schema`, `name`, `owner`, `metadata`, `plugins`; `metadata` dict só com `description`/`version`; uma entrada
  dict com chaves de `CHAVES_ENTRADA` (F4 menos `agents`, `skills`, `commands`, mais `source`; precedência `-` antes de `|`
  conferida) e `source` `.` ou `./`. Sem `plugins` sai (KeyError). Bate com o texto.
- F6: `cabecalho_simples` segue a forma do texto (1ª linha na coluna 0, chave `[A-Za-z0-9_-]` seguida de `:`, linha recuada é
  valor, `hooks`/`allowed-tools` saem, sem caixa). Mais estrito que o texto ao exigir espaço ou fim depois do `:` (`x:y: z`,
  `hooks:{}`). Sonda local: o caso do antigo A14 (`? |-` com comentários) dá False, assim como `"hooks": x`, `hooks : x` e
  o fluxo `name: {` com `hooks: x}` na coluna 0. O A14 recomendado desta revisão fica fechado.
- F7: inalterada; só a mensagem ganhou o prefixo.
- Limites declarados e ajuda: docstring, `help` do subcomando e changelog dizem o mesmo que a emenda.
- Oráculo C0: `origin/develop` e `origin/main` não têm o corpus, então `comparar X X` dá rc 2 pelo corpus, não pela forma.
  A medida do autor responde à pergunta do C0 (a árvore cumpre F1 a F7?). Conferi por sonda: `fora_da_medida` dá None em
  `origin/develop` (821db42e), `origin/main` (1d5aeb03) e `HEAD` (2d1fa4fa). Oráculo aceito; o texto literal da emenda pede
  um comando que não roda nessas refs (A15).
- Teste do item: `python3 -I -m unittest discover -s tests -p test_comparar.py`, ambiente limpo: 63 OK.
- Neutralidade (R-NEUTRO): `python3 -I -m unittest discover -s tests -p test_forge.py -k Neutralidade`, ambiente limpo: 6 OK.
- Mutantes (V2): `bin/forge-mutante --cobertura --base 757355b4`: toda linha de guarda do delta coberta, rc 0;
  `bin/forge-mutante --processos 1` nas specs 13 a 16 (CMP83 a CMP107): os 24 morreram,
  rc 0 (CMP106 morreu por erro do teste declarado, que a ferramenta conta como morte).
- Tamanho (H1): `bin/forge_comparar.py` foi de 295 a 326 linhas (88 adições, 57 remoções; o docstring cresceu junto), dentro
  das 30 linhas de código que a emenda admite. O PR atualiza a linha `teto: excedido` com a contagem nova.
- `praticas.md` sem regra "decidida por: leitura"; suíte inteira fica com o CI (R-CUSTO), não rerrodada aqui.

## Achados
- A4 (recomendado) bin/forge_comparar.py:279 · segue da rodada anterior: só a raiz do projeto é normalizada nas reescritas; `HOME` e `transcript_path` diferem em cada lado e dão `entrada-reescrita` falso. Erro do lado seguro; normalizar o HOME como `{home}`.
- A15 (recomendado) docs/propostas/v0479-melhorias-anti-erro.md:168 · o C0 da emenda pede `forge-check comparar X X` em `origin/develop` e `origin/main`, que dão rc 2 por falta do corpus; reescrever o oráculo como `fora_da_medida` None em cada ref (o que foi medido).

## Parecer
Aprovado no head 2d1fa4fa. O código implementa F1 a F7 como a emenda escreve, mais estrito na F4 (`hooks` em qualquer nível)
e na F6 (espaço depois do `:`), o que só acrescenta rc 2. As árvores reais do Forge cumprem a lista. A4 e A15 são
recomendados (R-REVIEW) e viram cartão depois do merge. Os bloqueantes da segurança, pelo critério de parada da emenda, são
decisão do `security-engineer` (R-SEGURANCA).
