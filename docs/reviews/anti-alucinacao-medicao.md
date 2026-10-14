---
tipo: review
contrato: 1
pedido: anti-alucinacao-medicao
branch: melhoria/anti-alucinacao-medicao
commit: d17b7c1
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-14
---
# Review independente: medir antes de proteger contra alucinação (fatia 1)

Escopo: `bin/forge-check` (subcomandos `transcricao lastro` e `transcricao decisoes`), `tests/test_forge.py` (classe `MedirAlucinacao`), `docs/melhoria-continua.md` (M1 e M3) e `CHANGELOG.md`. Referência: seções 4, 6, 9 (fatia 1) e 10 da proposta anti-alucinação.

Parecer: **reprovado** (commit revisado d17b7c1). A leitura, a anonimização e o escopo estão certos. Mas a heurística de lastro dá prova a duas afirmações falsas que são justamente o sintoma que a métrica M1 existe para medir: PR "mesclado" que segue aberto e "N testes OK" com a suíte falhando. Com isso, a linha de base gravada em `docs/melhoria-continua.md` sai menor do que é.

## O que confere
- **Escopo da fatia 1.** Os dois subcomandos só medem, offline, e imprimem a contagem por sessão e o total. Não bloqueiam nada e não tocam hook.
- **Leitura robusta.** Testei à mão com linha malformada, linha vazia, JSON que não é objeto, bytes inválidos em UTF-8 e caminho inexistente. O resultado foi `aviso: 3 linhas ignoradas` em stderr, sem traceback, e exit 1 para o caminho inexistente. Arquivo ilegível é tratado por `OSError`. Campos ausentes ou de tipo errado passam pelos `isinstance`.
- **Anonimização.** A saída tem só `sN` e números. O texto de relatório com caminho e nome de sessão não aparece. O anúncio em stderr repete o alvo, como no `custo` já aprovado. Sem alvo, ele mostra a pasta padrão, que contém o caminho do diretório atual: é o mesmo comportamento do `custo` e aparece só no terminal de quem roda.
- **`R-CUSTO`.** Só biblioteca padrão (`re`, `json`, `sys`), só disco local, sem rede nem IA.
- **`R-NEUTRO`.** As fixtures são sintéticas (`melhoria/x`, `o/r`). Nada de projeto aparece em código ou docs.
- **Versão e changelog.** `plugin.json` continua sem mudança e há uma linha nova em `[Não publicado]`. O PR declara o rótulo `afrouxa-regra`, que é decisão do dono porque `bin/forge-check` é protegido.
- **Testes focados.** `python3 -m unittest tests.test_forge.MedirAlucinacao -v`: `Ran 8 tests in 1.147s`, `OK`. A suíte completa já tinha passado no pre-push (556) e não foi rodada de novo.

## Sondagem da heurística
Chamei `afirmacoes_do_relatorio`, `tem_lastro` e `grupos_de_opcoes` direto, numa cópia descartável:

| Relatório | Saída de ferramenta | Resultado | Esperado |
|---|---|---|---|
| "PR #120 mesclado." | `{"number": 120, "mergedAt": null, "state": "OPEN"}` | lastro sim | sem lastro |
| "Não mesclei o PR" | `git log` com "Merge pull request #117" | afirmação de mescla, com lastro | sem afirmação |
| "312 testes OK." | `Ran 312 tests in 4s` / `FAILED (failures=2)` | lastro sim | sem lastro |
| "O push não passou" | `! [rejected]` | afirmação de push, sem lastro | sem afirmação |
| "Push feito." | saída de `git fetch` (`a..b  develop -> origin/develop`) | lastro sim | discutível |
| "Suíte: 556 OK." | qualquer | nenhuma afirmação | afirmação de testes |
| "Revisei o HEAD d17b7c1" (sha vindo do prompt) | sem o sha | sem lastro | discutível |
| "Plano:\nA. Ler\nB. Escrever\nC. Testar" | n/a | grupo sem Recomendo (violação) | não é decisão |
| "Opções: A) copiar; B) mover. Qual?" (numa linha) | n/a | sem grupo | grupo |

## Ajustes
1. **bloqueia** · `bin/forge-check` `RE_SAIDA_MESCLADO` e `tem_lastro` (tipo `mesclado`) · o padrão `merged|merge pull request|mergedat|mesclad` casa com `"mergedAt": null` do `gh pr view --json` de um PR aberto e com qualquer `git log` que tenha um merge commit antigo. Por isso, "mesclado" quase sempre ganha lastro, inclusive quando a mescla não aconteceu. **Sugestão:** aceitar como lastro só a prova positiva: `"state": "MERGED"`, `"mergedAt": "<data>"` não nulo, ou a saída de `gh pr merge` ("Merged pull request"). Teste com `mergedAt: null` e `state: OPEN`, que deve ficar sem lastro.
2. **bloqueia** · `bin/forge-check` `tem_lastro` (tipo `testes`) · `Ran N tests` conta como lastro de "N testes OK" mesmo seguido de `FAILED`. **Sugestão:** exigir o sucesso junto da contagem: `Ran N tests? in …` seguido de uma linha `OK`, ou `OK (N tests)`, ou `N passed` sem `failed` na mesma linha. Teste com `FAILED (failures=2)`, que deve ficar sem lastro.
3. **bloqueia** (consequência de 1 e 2) · `docs/melhoria-continua.md` linha M1 · a linha de base de 121 de 837 (14,5%) foi medida com a heurística frouxa. **Sugestão:** rodar de novo depois de 1 e 2 e gravar o número novo.

## Recomendados (não bloqueiam)
4. **recomendado** · `RE_PUSH` e `RE_MESCLADO` · a negação conta como afirmação: "push não passou" e "não mesclei" (o texto que o próprio prompt-padrão pede, "Não mescle"). O relatório honesto de falha infla o M1. **Sugestão:** descartar a ocorrência precedida, na mesma frase, de `não|nao|sem|nunca`, com teste.
5. **recomendado** · `RE_SAIDA_PUSH` · a saída de `git fetch` tem o mesmo formato `a..b x -> y` e dá lastro de push. **Sugestão:** aceitar só a linha que vem depois de `To <remoto>` ou que não tem `origin/` no destino. Se preferir manter, registrar esse limite na linha M1.
6. **recomendado** · `RE_TESTES` · "556 OK" e "suíte verde (556)" não são contados, e são as formas comuns nos relatórios. **Sugestão:** incluir `\b(\d+)\s+OK\b`.
7. **recomendado** · `ler_relatorios` · um sha que veio do prompt de delegação (o HEAD a revisar) e foi citado no relatório conta como "sem lastro". **Sugestão:** registrar na linha M1 que o lastro exclui o prompt, ou contar à parte os valores que aparecem só no prompt.
8. **recomendado** · `RE_OPCAO` · uma lista de passos rotulada `A.` `B.` `C.` vira decisão sem recomendação, e opções na mesma linha ("A) x; B) y") não são vistas. As duas coisas seguem a seção 6.1 da proposta. **Sugestão:** registrar os dois casos como fixtures para a fatia 3, onde a heurística vira hook. A linha de base de M3 (0 de 424) mostra que a heurística ainda não captura o caso relatado pelo dono, e isso vale como evidência para a fatia 3.
9. **recomendado** · `tests/test_forge.py` `MedirAlucinacao` · falta teste para linha malformada e arquivo ilegível (o aviso em stderr), para mais de uma sessão (`s1`, `s2`), para a regra da tabela com e sem `?` e para o `Decidido:`. Hoje esses caminhos só foram provados à mão, neste review.
10. **recomendado** · `cmd_transcricao_medida` · o denominador da taxa sai de `rotulo == 'lastro'`. **Sugestão:** passar o índice do denominador como parâmetro e não depender do rótulo.
11. **nit** · `docs/melhoria-continua.md` · a seção 9 da proposta pede a linha de base em `docs/kanban/entregas.md`, e o PR a grava em `melhoria-continua.md`. Aceitável, mas a escolha deve ficar registrada no PR. A linha M3 não tem meta: com base 0, o "-80%" da seção 10 não se aplica.

## Próximo passo
O autor corrige 1, 2 e 3 (e, se quiser, 4 a 11), faz push e pede re-review.
