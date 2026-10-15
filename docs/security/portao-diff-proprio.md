---
tipo: revisao-seguranca
contrato: 1
pedido: portao-diff-proprio
branch: melhoria/portao-diff-proprio
commit: b771f68254872435ff39e67fb156f6e4a279bf51
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-15
---
# Review de segurança: portao-diff-proprio (volta 2)

Escopo: `git diff 3a2f043..b771f68` em `bin/forge-check`, `tests/`, `docs/adr/` (commits 88341fc, 48d033f, b771f68). Estático; reproduções só em repositório temporário (git 2.55). Substitui o parecer reprovado da volta 1 (commit 3a2f043).

## Gatilhos
`R-SEGURANCA`: afrouxamento de portão do Forge (validade do parecer, ADR 0004 item 3) e efeito na catraca (`tests/catraca.py:484`, `mesmo_diff`).

## Achados anteriores
- S-1 (alta, `splitlines`): FECHADO. `bin/forge-check:244-257` (`trechos_do_arquivo`) lê bytes e separa só por `b"\n"`; o texto do diff não é mais normalizado por prefixo `index `. O comparador principal passou a ser o merge simulado (`bin/forge-check:263-306`), que compara árvores do git, sem análise de texto. Teste `test_separadores_de_linha_do_python_nao_escondem_conteudo` cobre `\r`, `\x0b`, `\x0c`, `\x1c-\x1e`, `\x85`, U+2028/2029.
- S-2 (média, linha movida): FECHADO. Em arquivo sem conflito, a árvore resultante do merge simulado é comparada com a do HEAD: linha movida ou cópia removida diverge (`test_linha_movida_da_branch_invalida`, `test_remover_copia_repetida_invalida`). Em conflito fora do `CHANGELOG.md`, falha fechada.

## Achados novos
Nenhum de severidade média ou maior.

- I-1 (informativa) Exceção do `CHANGELOG.md` em conflito: `bin/forge-check:293-301` compara as linhas `+`/`-` da branch (`-U0`, ordem, sem posição). Caminho de ataque: só reposicionar texto dentro do `CHANGELOG.md`; o arquivo não executa, linha nova ou removida diverge, binário, ausência ou erro do git divergem. Risco residual declarado na ADR. Sem ação.
- I-2 (informativa) `bin/forge-check:292` filtra conflitos com `startswith(tuple(ignorar))`, enquanto o `diff` usa pathspec exato. Na catraca `ignorar` são arquivos exatos de `PARECERES` (`tests/catraca.py:458-466`), então o prefixo só alcança nomes irmãos dentro de pastas já livres. Sem caminho de ataque; se quiser, trocar por igualdade ou prefixo de pasta.

## Caminhos verificados sem achado
- Reproduzido em repositório temporário, com `commit_vale(..., base="develop")`: merge limpo da base vale (None); mudança de modo, binário alterado, arquivo apagado, renomeação e symlink novo desatualizam e citam o arquivo.
- Resolução de merge com alteração só nela: entra na árvore do HEAD, diverge da árvore simulada (testes de conflito e `-X theirs`).
- Linhas movidas, reordenação, separadores: cobertos acima; conteúdo da base (mb_b) é confiável, pois já passou pelo portão da base.
- Falhas: git antigo sem `merge-tree --write-tree`, código fora de 0/1, `UnicodeError`, `OSError` retornam None, e `commit_vale` bloqueia citando `fora[0]`; `mesmo_diff` dá False. Falha fechada.
- Catraca: não mudou; `mesmo_diff` herda o critério novo, e o rótulo `afrouxa-regra` não cobre mais conteúdo novo nem movido. Arquivos de controle seguem exigindo o rótulo por caminho. Efeito colateral: `merge-tree` grava objetos soltos no repositório, sem risco.
- Mensagem do motivo: nomes vêm de saída `-z`, sem execução; sem injeção.
- Testes do pedido: `python3 -m unittest tests.test_portao_diff_proprio` roda 16 testes, OK.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: só `git` e `python3` locais; gitleaks, semgrep, zizmor e osv-scanner não usados (alvo é um script e sua ADR; sem segredo nem dependência nova). Sem lacuna relevante.

## Plano em cartões
Nenhum bloqueante. Opcional (tech-lead): I-2.
