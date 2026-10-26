---
tipo: review
contrato: 1
pedido: RET-LEITURA-HOOK
branch: melhoria/lote-leitura-hook
commit: 335ea5e2975658e3a04e4addfe50301a55f1fc29
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-26
---
# Review: o desenho do lote-leitura-hook conferido contra o código do head (RET-LEITURA-HOOK-PR, E1.0)

Esta revisão atualiza o parecer de desenho de 2026-10-22, que estava sobre `b9e15dc` e foi aprovado. Ela confere se o código de `335ea5e` segue o desenho em vigor. O desenho é a proposta `docs/propostas/lote-leitura-hook-volta-unica.md` com as emendas que o dono decidiu depois:
- rev12, opção A: o lançador passa só com as opções da lista positiva `LANCADORES`, e o teste instável (`ETXTBSY`) é corrigido no lote;
- rev13, opção A: sem o marcador, as regras leem todas as leituras possíveis, com teto K;
- rev14, opção B: com mais de uma leitura e um texto dividido sem aspa fechada, a linha recusa;
- a ADR 0011.

Quem revisou é uma instância que não escreveu o código do lote.

Delta lido: `git diff b9e15dc..335ea5e` em `hooks/` e `docs/hooks.md` (9 arquivos, 1448 linhas a mais e 232 a menos), lido nos pontos que o desenho e as três emendas nomeiam. De `d67f31f` a `335ea5e` só mudaram os três pareceres (`git diff --stat`: `docs/qa`, `docs/reviews` e `docs/security`). Então o código do head é o mesmo que os pareceres vigentes aprovaram, todos sobre `d67f31f`: review, segurança e QA da revalidação 16.

Ficou como "já lido", sem refazer: a correção do código caso a caso e as sondas dos pareceres de review, de segurança e de QA. Este parecer só responde se o código segue o desenho.

## Achados
- A1 (recomendado) docs/propostas/lote-leitura-hook-volta-unica.md:114 · R10 e F9 ainda dizem "o bash não grava" (linhas 114, 259, 300, 306 e 318). O corpus já corrigiu isso: R10 é caso R e o F9 saiu (`tests/fixtures/heredoc-volta-unica.json:21`). Corrigir o texto da proposta num PR de documento.
- A2 (recomendado) docs/adr/0011-analisador-de-comandos-gramatica-positiva.md:42 · O item 2 da ADR 0011 não tem as emendas das rev12 a rev14 (lista positiva dos lançadores, leituras possíveis, teto K); adiadas ao cartão ADR0011-EMENDA (decisão do Jarvis). Até lá, `docs/hooks.md` é a fonte da regra.

## Conferência do desenho contra o código
| Peça do desenho | Onde está em `335ea5e` | Segue? |
|---|---|---|
| M1 a M3 da volta única: leitor sequencial, `grava_arquivo` sobre o texto inteiro, `fora_do_texto`, `gravado_e_rodado` | `hooks/_comum.py:793`, `:890-916`, `:981`, `:1162`; M3 em `hooks/conformidade.py:737` e `hooks/parecer.py:398`, depois das regras específicas e só com `CRITICO` | sim. `GRAVA_REDIRECAO` saiu (`grep` vazio) |
| M5: `echo` e `true` na lista dos outros | `hooks/_comum.py:856` | sim |
| M6: frases próprias de M2 e M3, contorno "noutra chamada" | `hooks/conformidade.py:694` e `:738`, `hooks/parecer.py:374`, `:379` e `:398`; as leituras novas estão na ADR 0011, linhas 101 e 102 | sim |
| rev12 A: `LANCADORES` é a fonte única e positiva, e opção fora da tabela recusa com o marcador | `hooks/_comum.py:1747-1768` (env: `-i`, `-`, `--ignore-environment`, `-0`, `--null`, `-v`, `--debug`, `-u`/`--unset`, `-C`/`--chdir`); a recusa sai de `opcao_fora_da_tabela` (`:1789`) e de `reavaliacao_das_palavras` | sim. `env_divide_texto`, `ENV_COM_VALOR_CURTA`, `ENV_LONGAS_COM_VALOR`, `opcoes_do_lancador` e o regex `-[a-zA-Z]*[uC]` não existem em `hooks/` (`grep` vazio; o teste `tests/test_hooks.py:2880` exige essa ausência). `sudo -s` e `sudo -i` ficam fora da tabela e recusam |
| rev12, caminho 1 do teste instável | `tests/test_hooks.py:2440` (`montar_registradores_do_t9b`, separado da execução), `:2481` ("falha do arnês"), `:2426` (`envs_da_maquina`, GNU e uutils) | sim |
| rev13 A: leituras possíveis (sem valor, com valor e, no `env`, texto dividido); a primeira dá o estado; teto K = 3 | `_ler_lancadores` (`hooks/_comum.py:1862`), `TETO_FORA_DA_TABELA = 3` (`:1840`); os três chamadores: `segmento` (`hooks/conformidade.py:841-872`, com estado copiado e descartado), `rotulo_na_sessao_do_forge` (`:1394`, via `sem_lancadores`), `alvos_de_escrita` (`:1698`, união) | sim. O `parecer` não usa `separar_lancadores`, como a proposta diz |
| rev14 B: `TextoAbertoComLeituras` com `gasto > 0` recusa com `barrar`; com `gasto == 0` vai a `ilegivel`; `alvos_de_escrita` toma as palavras depois do `tee` | `_dividir` (`hooks/_comum.py:1916-1925`); `hooks/conformidade.py:852-861`; `:1712-1715` | sim. `rotulo_na_sessao_do_forge` não mudou, como a opção B manda |
| Textos de `docs/hooks.md`: rev12 4.1, rev13 3.1 e rev14 3.2 | `docs/hooks.md:95`; `grep -cF` deu 1 para cada frase-chave das três seções (REV12, REV13, REV14, "Com mais de três palavras fora da tabela", "salvo em dois casos em que o oráculo não vale", FD17 e FD18) e 0 para "Sem marcador, nada muda", que saiu | sim |

O código não se afastou do desenho. Não há mecanismo novo fora do que as três decisões pediram, e nenhuma regra ficou mais frouxa: todas as mudanças só recusam mais. As únicas exceções são L2, L3, L10 e L12, que a proposta já previa.

## Execução
- `python3 -m unittest tests.test_hooks.CorpusHeredocVoltaUnica` na worktree em `335ea5e`: `Ran 41 tests in 354.168s`, `OK`. Esse é o critério (i) da seção 4 da proposta, e passou.
- Não rodei a suíte completa, `scripts/validar-plugin.sh` nem as regras de ferramenta do `praticas.md`. Este parecer não muda código, e os pareceres vigentes já citam essas execuções sobre o mesmo código (`d67f31f`).

## Parecer
**Aprovado.** O código do head segue a proposta volta-unica com as emendas rev12 A, rev13 A e rev14 B e com a ADR 0011. Os dois recomendados são texto: a proposta tem trechos desatualizados sobre R10 e F9, e a emenda da ADR está num cartão. Nenhum deles muda o comportamento nem fere uma linha "Promete" da tabela 2.3.

Segurança: sem achado novo. O controle do lançador e do heredoc é do `security-engineer`, e o parecer dele (`docs/security/lote-leitura-hook.md`, aprovado sobre `d67f31f`) é o que vale.
