---
tipo: review
contrato: 1
pedido: hook-ansi-c
branch: melhoria/hook-ansi-c
commit: f3d1fd092979c2bb8eb0af09db16e33909f94154
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-27
---
# Review: hook-ansi-c

Escopo revisado: a volta 1, por delta `3707e280ce4e3ff11bc28b79b6ab75820d920b27..f3d1fd092979c2bb8eb0af09db16e33909f94154`. Só o commit f3d1fd0 traz código; bfc0701, 471824c e 2fe8e1c são pareceres. A rodada anterior (head 3707e28, parecer 471824c) revisou `770c19a3c3f64d0f132eb358232e126e69e33b2e...3707e28`.

## Achados

## Parecer
**Aprovado.** A1 e A2 do review anterior estão resolvidos sem drible. A função nova `_ansi_com_aspa_escapada` cumpre a opção (b) do A1 da segurança (DECISÃO TÉCNICA 2026-10-27 17:55) e falha fechado.

### Revalidação por delta
`bin/forge-check delta --parecer docs/reviews/hook-ansi-c.md` listou: `bin/forge-testes`:101; `changelog.d/hook-ansi-c.md`:2; `hooks/_comum.py`:963-965, 983-997, 1092-1093; `tests/mutantes/hook-ansi-c.json`:58-90; `tests/test_hook_ansi_c.py`:6, 16, 19, 27-32, 51, 54, 107-129, 138-141; `tests/test_testes_tocados.py`:61. Li só essas faixas. O resto do diff ficou como já lido na rodada de 3707e28: a marca `aspa_escapada` no nível `ansi`, o portão de `leituras`, `LeituraDoTexto` e os 6 testes originais.

- **A1 (anterior), resolvido.** `tests/test_hook_ansi_c.py:19` voltou a usar `HOOK = RAIZ / "hooks" / "conformidade.py"`, e o parâmetro `nome` saiu (`:51`, `:54`). `bin/forge-testes:101` ganhou `test_hook_ansi_c` na regra `hooks/.*`, e essa foi a única linha mexida no mapa. Prova: `bin/forge-testes --listar hooks/_comum.py` responde `dirigido (… test_forge, test_hook_ansi_c, test_hooks, …)`. `python3 -m unittest tests.test_testes_tocados` passou com 81 testes OK, sem drible.
- **A2 (anterior), resolvido.** `ambiente_limpo` agora é importado de `test_forge` (`:16`), e a cópia saiu. O módulo entrou no `FORGE_CHECK` (`bin/forge-testes:71`), e a contagem de `tests/test_testes_tocados.py:61` passou a 26, o que bate com a tupla.
- **`_ansi_com_aspa_escapada` (`hooks/_comum.py:983-997`, chamada em `:1092-1093`).** A chamada fica só no ramo "fora de aspas", quando a barra é seguida de `$'`. A leitura do conteúdo segue a do bash para ANSI-C: `\` consome o caractere seguinte, `\'` marca e o primeiro `'` sem barra fecha. O índice `texto[i + 1:i + 2]` não estoura no fim do texto. Conferi com sondas em `palavras_do_texto` e `leituras` (`$TMPDIR/tech-lead-hook-ansi-c/sonda.py`):
  - marcam e ficam ilegíveis: `\$'it\'s'; cat .env \'`, `\$'a\'`, o segundo `\$'…'` da linha, e `\\$'it\'s'`, que é ANSI-C de verdade e já era marcado pelo nível `ansi`;
  - não marcam: `\$'a\\'`, `\$'a\nb'`, `it\'s \$'a'`, `\$` sozinho, e `"\$'it\'s'"` (dentro de aspas duplas o bash de dentro também lê literal, então não marcar está certo);
  - `\$'abc` sem fecho não marca, mas a linha fica ilegível pelo `shlex`, então falha fechado do mesmo jeito.
- **Hook real** (`$TMPDIR/tech-lead-hook-ansi-c/sonda2.py` e `sonda3.py`, numa pasta com `.forge/`). Fora da matriz do autor, saem 2 com "aspas sem par": aninhamento duplo `bash -c "bash -c \"echo \\\$'it\\\\'s'; cat .env \\\\'\""`, `bash -lc "…"` e `sudo bash -c "…"`. O bash real lê o `.env` falso nos dois primeiros. O controle `bash -c "echo \$'ok'"` sai 0.
- **Custo conhecido, aceito pela decisão.** No nível 0, `printf '%s' \$'x\'y'` também fica ilegível, embora o bash de fora leia `\$` literal ali. É recusa a mais, rara, na direção conservadora que a opção (b) escolheu. Não é achado. A correção exata (a) está registrada como cartão depois do HOOK-CD.
- **Testes e mutantes.** `python3 -m unittest tests.test_hook_ansi_c` passou com 9 testes OK em 2,2 s. A nova dimensão (argumento de `bash -c`, `sh -c` e `eval` entre aspas duplas) prova o furo com o bash real e cobre recusa e controles. `bin/forge-mutante tests/mutantes/hook-ansi-c.json` (rev f3d1fd092979) matou A1 a A8, e A6 a A8 cobrem a função nova: chamada removida, qualquer barra marca, barra sem pular.
- **Teto M14.** Pelo `git diff --numstat --no-renames 770c19a...f3d1fd0`, contam `bin/forge-testes` 4, `hooks/_comum.py` 27, `tests/test_hook_ansi_c.py` 145 e `tests/test_testes_tocados.py` 2, total de 178 linhas, abaixo de 400. Em `hooks/` há uma classe de comportamento só (citação ANSI-C no leitor), e `hooks/conformidade.py` não foi tocado. `tests/config.json` também não. O fragmento `changelog.d/hook-ansi-c.md` foi atualizado com a variante aninhada. Sem termo de projeto (`R-NEUTRO`) e sem custo (`R-CUSTO`).
- **PA-7.** `docs/engineering/achados-recorrentes.md` está com a lista vazia. Não há recorrência a registrar, porque A1 e A2 foram achados únicos.

## Revisões
- Portões de outros: a segurança (`docs/security/hook-ansi-c.md`, E2.1) e o QA (`docs/qa/hook-ansi-c.md`, E3.1) revalidam este head em outra delegação.
- O A2 da segurança (`hooks/pesado.py:90`) virou o cartão PESADO-ANSI-C (DECISÃO TÉCNICA 2026-10-27 17:56) e fica fora desta revisão.
