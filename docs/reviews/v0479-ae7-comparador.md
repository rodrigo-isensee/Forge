---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-ae7-comparador
commit: caae27c42db773f7984803f27b62ae3da7b4053e
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-21
---
# Review: v0478 (E58.58, AE7.1 `forge-check comparar`, revalidação no head caae27c4)

Revalidação (H3, R-REVIEW) do parecer aprovado em e2e87c6b (E58.54, head 2d1fa4fa). Delta lido por
`forge-check parecer delta docs/reviews/v0479-ae7-comparador.md`: intervalo `2d1fa4fa..caae27c4`, no domínio
`bin/forge-check` (ajuda), `bin/forge_comparar.py`, `changelog.d/v0479-ae7-comparador.md`,
`docs/propostas/v0479-melhorias-anti-erro.md` (F3 e F6 da emenda), `tests/mutantes/v0478-ae7-comparar-{12,13,17}.json` e
`tests/test_comparar.py`. Fora do delta nada foi relido.

## Conferido
- F6 (A17): `cabecalho` parte o texto com `splitlines() or [""]` e fecha na linha exatamente `---`; `cabecalho_simples` só
  junta e reparte por `\n`. As quebras do `splitlines` contêm as do YAML (`\r`, `\r\n`, `\n`, `\x85`, U+2028, U+2029), então
  todo começo de linha do YAML é começo de linha aqui: só acrescenta rc 2. O `.md` vazio não derruba (`or [""]`).
- F6, fecho mais cedo: conferi no binário do Claude Code 2.1.224 que o `Np` corta o cabeçalho com
  `/^---\s*\n([\s\S]*?)---\s*\n?/`, que fecha no primeiro `---` em qualquer posição. Sonda local: `name: a\v---\nhooks: x`
  e `name: a\r---\nhooks: x` dão cabeçalho `name: a` aqui e `name: a\v` (ou `\r`) lá; U+2028 e CRLF com `hooks` dão False.
  O cabeçalho medido nunca é menor que o do Claude Code; a quebra extra no `\v` não abre fecho antecipado.
- F3 (A18): `RAIZ_FORA` ganhou `monitors` e `workflows`, comparados com o 1º nome do caminho, sem caixa, então pasta ou
  arquivo da raiz saem e `docs/monitors/...` mede (teste). Conferi no binário a lista de convenção citada no docstring
  (`.claude-plugin`, `commands`, `skills`, `agents`, `hooks`, `themes`, `output-styles`, `monitors`, `workflows`,
  `SKILL.md`, `.mcp.json`, `.lsp.json`): bate. O manifesto por cabeçalho de `SKILL.md` (`monitors:`, `mcpServers:` no
  cabeçalho) só vale para a origem `skills-dir` (`~/.claude/skills`), não para plugin instalado: fora da medida, sem achado.
- Ajuda do subcomando, changelog e emenda dizem o mesmo que o docstring.
- Teste do item: `python3 -I -m unittest discover -s tests -p test_comparar.py`, ambiente limpo: 65 OK.
- Neutralidade (R-NEUTRO): `python3 -I -m unittest discover -s tests -p test_forge.py -k Neutralidade`, ambiente limpo: 6 OK.
- Mutantes (V2): `bin/forge-mutante --cobertura --base 2d1fa4fa`: linhas 145, 148 e 178 cobertas, rc 0;
  `bin/forge-mutante --processos 1` nas specs 12, 13 e 17: 21 morreram, nenhum sobreviveu, rc 0 (CMP108 a CMP112 novos).
- `praticas.md` sem regra "decidida por: leitura"; suíte inteira fica com o CI (R-CUSTO), não rerrodada aqui.

## Achados
- A4 (recomendado) bin/forge_comparar.py:285 · segue das rodadas anteriores: só a raiz do projeto é normalizada nas reescritas; `HOME` e `transcript_path` diferem em cada lado e dão `entrada-reescrita` falso. Erro do lado seguro; normalizar o HOME como `{home}`.
- A15 (recomendado) docs/propostas/v0479-melhorias-anti-erro.md:170 · o C0 da emenda pede `forge-check comparar X X` em `origin/develop` e `origin/main`, que dão rc 2 por falta do corpus; reescrever o oráculo como `fora_da_medida` None em cada ref.

## Parecer
Aprovado no head caae27c4. A F6 só ficou mais estrita (o cabeçalho medido contém o do Claude Code) e a F3 cobre as duas
entradas da raiz que faltavam, com a lista conferida no binário da versão sondada. A4 e A15 seguem recomendados (R-REVIEW)
e viram cartão depois do merge. Os bloqueantes da segurança são decisão do `security-engineer` (R-SEGURANCA).
