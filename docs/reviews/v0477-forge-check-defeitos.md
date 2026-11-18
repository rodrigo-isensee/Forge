---
tipo: review
contrato: 1
pedido: v0477
branch: melhoria/v0477-forge-check-defeitos
commit: 4603cde822b5484bbd5965327f10060e5c51abc9
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-18
---
# Review: v0477 (E1.2, primeira rodada)

Diff `038249c5...4603cde8`: `bin/forge-check` (+8 -1), `tests/test_selo_e_entrega.py` (+20), `tests/mutantes/v0477-forge-check-defeitos.json`, `changelog.d/v0477-forge-check-defeitos.md`. Código e teste: 29 linhas, abaixo do teto M14; um comportamento só (VEREDITO-TROCADO-LENTO).

## Achados
- A1 (recomendado) bin/forge-check:2814 · anterior ao diff: `ls-tree` sem `-z` cita entre aspas o nome não ASCII e o `git show` dessa versão falha calado (lida como sem frontmatter, falha aberta); o `git grep` cita igual e não piora. Sugestão: `-z` no `ls-tree` e no `grep`, com `nomes_z`.

## Sondas

## Parecer
Aprovado. A troca é correta e não afrouxa a conferência: o `parecer:` só conta quando o frontmatter tem `commit:` literalmente igual ao `revisado` (`ler_frontmatter` não decodifica valor), então toda versão que importa contém o sha e passa no `git grep -l -F -e`; o `-e` protege sha começado por `-`. O código de saída 1 do `grep` (nenhuma versão cita) segue como "nada trocado"; 2 ou mais falha fechada (`R-CONFORMIDADE`). A chave `<sha>:<caminho>` casa a saída do `grep` com a do `ls-tree` também em nome com espaço ou não ASCII (sonda própria: as duas saídas citam igual).

Ferramentas, sem refazer:
- `bin/forge-mutante --processos 1 tests/mutantes/v0477-forge-check-defeitos.json`: M1 morreu (bin/forge-check:2808), M2 morreu (bin/forge-check:2816).
- `bin/forge-mutante --cobertura --base 038249c5`: as duas guardas mudadas cobertas por M1 e M2.
- `python3 -m unittest tests.test_selo_e_entrega.ParecerDoPortao`: 23 testes, OK. Suíte inteira: fica para o CI do PR.
- `python3 -I tests/catraca.py --base origin/develop`: rc=1, só `R-CONFORMIDADE` (mudança em `bin/forge-check` pede o rótulo `afrouxa-regra` do dono depois do último push). Pendência do Jarvis, não do código: pela decisão do dono de 18/11 08:46 no pedido, o rótulo é pedido antes, com o motivo em uma linha (perf de controle, sem afrouxar).

Testes: o de falha fechada reusa `trocado_com_git_que_falha`, como os do `ls-tree` e do `rev-list`; o de leitura conta os `git show` reais e afirma não vazio antes de comparar o conjunto (checklist 11). ENTREGA-PUSH-RAIZ-PEDIDOS e BRIEF-SELAR-LINHA-DA-ETAPA ficaram sem código, com a prova no fragmento; nada a revisar neles. Commits limpos, em português, Conventional Commits.
