---
tipo: review
contrato: 1
pedido: lote-fechar2
branch: melhoria/lote-fechar2
commit: 03155612d2d56a54686248d5131557075289e4b8
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-26
---
# Review: lote-fechar2

Base `b6eb84fed86e3b5289f3950b33d43a86f34343c2`, head `03155612d2d56a54686248d5131557075289e4b8` (2 commits, um por cartão: `69f7f01` LSREMOTE-EXATO, `0315561` SHELLCHECK-FECHAR; 5 arquivos: `bin/forge-fechar`, `.github/workflows/ci.yml`, `tests/test_fechar.py`, `tests/mutantes/lote-fechar2.json`, `changelog.d/lote-fechar2.md`).

## Achados
- A1 (recomendado) bin/forge-fechar:599 · a mensagem nova do passo 2 para a leitura do ls-remote que falha não tem teste; antes, com pipefail, o script saía calado; um caso com o git falso devolvendo erro no ls-remote fixaria a mensagem
- A2 (recomendado) tests/test_fechar.py:594 · o filtro `"printf" not in l` não exclui nenhuma linha hoje (a 482 já sai por começar com echo) e deixaria passar uma chamada crua futura que use printf %q no nome; tirar o filtro
- A3 (recomendado) bin/forge-fechar:522 · `mapfile` é o primeiro uso de recurso do bash 4 no repositório; o script já depende de `sort -z` e `comm -z` do GNU, então não é regressão prática, mas vale uma linha no comentário do cabeçalho

## O que li
- Ajudante `remoto_exato` (linhas 134 a 141): `"$@"` vazio não deixa palavra sobrando; a falha do `git ls-remote` vira `return 1` antes do filtro, e a resposta vazia vira sha vazio (o `awk` não imprime nada). O filtro `$2 == r` compara a coluna 2 com `refs/heads/<branch>` inteiro e para na primeira linha. O `printf | awk ... exit` sob `pipefail` só daria SIGPIPE com saída acima do buffer do pipe, o que não acontece com o padrão exato de uma branch.
- Os quatro pontos de uso: passo 2 (linha 599, agora com `die` próprio para a leitura que falha e o mesmo `die` de antes para branch ausente), passo 2b (linha 513, com as mesmas duas mensagens de antes), limpeza (linha 461, mesmo `rem_st=pendente` na falha) e conferência depois do delete (linha 474, com `com_teto 10` como prefixo, igual ao comportamento anterior). Nenhuma outra chamada a `ls-remote` sobra fora de comentário, `echo` e `passo`.
- `conferir_base`: SC2034 (`comuns` saiu do `local`), SC2015 (o `a && b && c || die` virou `if ! { ...; }`, com a mesma semântica) e SC2086 (`$mbs` sem aspas virou `lista_mb`, lida com `mapfile -t` de `<<<`; como `mbs` vem de `$(...)` e não é vazio, a lista não ganha elemento vazio). O `for` e o `rev-list --not` usam `"${lista_mb[@]}"`.
- Testes de isca: a isca `refs/heads/a/refs/heads/<nome>` aparece antes da ref verdadeira na listagem (a asserção de duas linhas prova que ela é vista), então o código antigo (`awk '{print $1}'` e `${srv%%[[:space:]]*}`) pegaria o sha errado. O caso do passo 2b põe na isca o sha da branch, que difere da base. O caso da conferência depois do delete usa `delete_apaga_e_falha`, que apaga de verdade e sai com erro, e a asserção de "já não existe" só passa se a isca for ignorada. O `head_do_pr` do gh falso agora filtra pela coluna 2; sem isso, a isca daria duas linhas ao falso `pr view`.
- Mutantes: refiz o M1 numa cópia em `$TMPDIR/tech-lead-lote-fechar2/mut`, e os três testes de isca falharam (`FAILED (failures=3)`). O M2 e o M3 ficam com a prova do autor (pedido, 14:11).
- Teto M14: 85 linhas de código e teste (`ci.yml` 2, `bin/forge-fechar` 31, `tests/test_fechar.py` 52); o JSON de mutantes e o changelog ficam fora. Dentro do teto, sem `hooks/` e sem caminho protegido.
- Changelog: `### Corrigido` descreve os dois cartões como o código faz. Regras: nada de `--force` nem `--no-verify`; `R-NEUTRO` e `R-CUSTO` sem impacto.

## Ferramentas (citadas, não refeitas à mão)
- `shellcheck bin/forge-fechar` (ShellCheck 0.11.0): rc=0, sem aviso; fecha a pendência do review fechar-master (SC2034 da base).
- `python3 -m unittest tests.test_fechar tests.test_fechar_orfao`: `Ran 102 tests in 80.162s` / `OK`.
- Devops (o lote toca `.github/workflows/ci.yml`), segurança e QA: pareceres próprios (E4.1, E2.1, E3.1), que não refaço aqui.

## Parecer
Aprovado. O ajudante único resolve o casamento pelo fim do nome nos quatro pontos, a leitura que falha não se confunde mais com branch ausente, as correções de shellcheck mantêm a semântica, e os testes de isca falham com o filtro antigo. A1 a A3 são recomendações e não devolvem a entrega.
