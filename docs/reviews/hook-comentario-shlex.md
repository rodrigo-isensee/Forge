---
tipo: review
contrato: 1
pedido: hook-comentario-shlex
branch: melhoria/hook-comentario-shlex
commit: 74dc3f62f205dc63bc95c13aeeacf7dc72f884a0
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-21
---
# Code review: HOOK-COMENTARIO-SHLEX

Rodada 1 (E1.2), entrega inteira `10c838f..74dc3f6`: 2 commits, 12 arquivos, 251+/8-. Revisor diferente do autor da E1.1 (D-ETAPAS-INST). Segurança (E1.3): parecer próprio do `security-engineer`, não refeito aqui.

Ferramentas rodadas em 74dc3f6: `python3 -m unittest tests.test_hooks.Hooks.test_fixtures tests.test_hooks.Hooks.test_cerquilha_so_abre_comentario_no_inicio_de_palavra` → `Ran 2 tests in 31.040s OK`. Suíte inteira e `scripts/validar-plugin.sh` não refeitos aqui (R-TETO): o pre-push do envio deste parecer roda a suíte, e o QA os refaz no head. O Forge não tem `docs/engineering/praticas.md`; o checklist da skill foi lido sobre o diff.

## O que foi conferido
1. **Escopo (E1, E2).** `fichas()` desliga o comentário do `shlex` (`lex.commenters = ""`) e passa a tratar o `#` só no início de palavra (`ANTES_DE_COMENTARIO = " \t\n;&|("`), pulando até a quebra de linha, que segue separando comandos. As três linhas do pedido (`echo a#; git push --force origin main`, `cat a#&&git push origin main`, `grep x f#; forge sugerir --fila`) têm fixture de recusa, o comentário real (`ls # nota: git push --force origin main`) tem fixture que libera, e o fragmento `changelog.d/hook-comentario-shlex.md` existe. Nada além do pedido.
2. **Reprodução do furo na base.** `_comum.comandos` de 10c838f devolve `[['echo', 'a']]`, `[['cat', 'a']]` e `[['grep', 'x', 'f']]` para as três linhas (o push e o `forge sugerir` somem), e junta `ls # nota\ngit push --force ...` num comando só (`['ls', 'git', 'push', ...]`). Em 74dc3f6 os quatro saem separados e lidos.
3. **Paridade com o bash (sonda própria em $TMPDIR, 19 linhas).** Para cada linha comparei as palavras do hook com o que o `bash -c` executa (com `git` trocado por uma função). Em todos os casos em que o bash executa o `git`, o hook enxerga o `git push`: `a|#x\n`, `(#x\n`, `a&#b\n`, `{#x`, `${#x}`, `x=#y`, `'a'#b`, `"a"#b`, `a#b#c`, `<(#x\n)`, `$(#x\ngit push)`, comentário só com espaços antes e linha começando por `\n#`. Onde o hook diverge do bash (`)#b`, `2>#x`, `a \\\n#b`), ele lê mais que o bash, nunca menos: a dúvida cai para o lado de ler a linha inteira, como diz o comentário de `hooks/_comum.py:220`.
4. **`#` depois de `(`.** Abre comentário, igual ao bash (o `(` é metacaractere; `(#x\ngit push)` executa o push no bash, e o hook o lê). Correto manter no conjunto.
5. **`instream.seek`.** O `shlex` recebe a linha como `str`, então `instream` é um `StringIO` e o `seek` é seguro. O salto só ocorre entre fichas (logo depois de um `get_token`, com `token` vazio e estado `' '`), e o `_pushback_chars.clear()` descarta só o caractere já coberto pelo salto (caso `ls;#nota`, que o teste cobre). O uso de atributo privado do `shlex` já existia (`_pushback_chars` em `posicao`), não é dependência nova.
6. **Duas fixtures existentes trocaram o motivo da recusa** (`nao-modelado-cerquilha-no-meio-push-main-dev-bloqueia`, `nao-modelado-comentario-push-main-dev-bloqueia`: de "não modela" para R-MAIN, código 2 nos dois). Aceito: o resultado (recusa, código 2) não mudou, o motivo novo é mais forte e decorre justamente da correção (o push na main, antes escondido, agora é lido), e a cobertura do ADR 0011, item 2 foi preservada pelas duas gêmeas novas com push para `feature/x` (`nao-modelado-*-push-dev-bloqueia`), que seguem recusando por "não modela". `construcao_nao_modelada` não foi tocada. As descrições das fixtures alteradas explicam a troca e apontam a gêmea.
7. **Testes.** O teste novo `test_cerquilha_so_abre_comentario_no_inicio_de_palavra` cobre 15 casos (colado, início de palavra depois de espaço, `;`, `&&`, `|`, linha só de comentário, quebra de linha, apóstrofo dentro do comentário, `\ #`, `"#"`, `$#`, `$(…)#`, `>#`, `\r#`). Falha na base (item 2) e passa na entrega.
8. **Regras.** Nada afrouxa controle (endurece um existente); sem custo (R-CUSTO); nada específico de projeto (R-NEUTRO); `invariantes` não tocados.
9. **Commits.** Dois commits, Conventional Commits em português, um para o código e os testes e outro para o changelog.

## Achados

## Recomendações (não bloqueiam)
- `hooks/_comum.py:222` e `hooks/_comum.py:388`: `ANTES_DE_COMENTARIO` (`" \t\n;&|("`) e `INICIO_DE_PALAVRA` (`" \t\n;&|()"`, usado por `construcao_nao_modelada`) são quase o mesmo conjunto e diferem só no `)`. A diferença é segura (o `fichas` lê mais), mas uma referência cruzada num dos comentários evitaria que alguém os "unifique" no sentido errado no futuro.
- `hooks/_comum.py:248`: um comentário curto dizendo que o `seek` vale porque o `instream` é `StringIO` (linha passada como `str`) deixaria explícita a premissa de que o salto depende.
