---
tipo: review
contrato: 1
pedido: versao-033
branch: melhoria/forge-testes-aviso-mapa
commit: 7d20b39b7f9cc08666be45f5a34e1809cc748c1e
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-04
---
# Review: versao-033 (forge-testes-034)

## Achados

- A1 (bloqueante) bin/forge-testes:1 · Três comportamentos num PR (módulo sem mapa, aviso de MAPA, -k): M14. Divida em três PRs, um por commit (a1537d1, 4c5e197, 1d7a02f); 118 linhas, teto de linhas ok. Resolvido: pilha sem-mapa (aec5092), aviso-mapa (7d20b39), filtro-k (704a606)
- A2 (recomendado) bin/forge-testes:570 · modulos_sem_mapa é chamado duas vezes no mesmo elif; guarde o resultado numa variável. Resolvido em aec5092 (`:=`)

## Parecer

Aprovado na revalidação sobre 7d20b39, branch melhoria/forge-testes-aviso-mapa (seção abaixo). Texto da rodada anterior (1d7a02f, branch única):

Código correto; só A1 bloqueia, por M14, e a divisão é mecânica (cherry-pick dos commits).

- Pre-push: o hook chama `--listar --base` sem CAMINHO nem -k e cai na suíte inteira se bin/forge-testes mudar. Os avisos vão a stderr (descartado no hook) e o plano do diff não mudou: um push não roda menos testes.
- Cartão 15: só vale se todos os pedidos casam tests/test_x.py e existem; inexistente ou misturado vai a planejar (mapa, falha fechada). Teste cobre os dois casos.
- Cartão 19: regex sem AST, com falsos positivos conhecidos; é só aviso em stderr, não muda plano nem rc, então é aceitável. A suíte completa segue como autoridade.
- Cartão 20: -k anexado ao comando, recusado com --vermelho (teste cobre).
- Testes rodados: test_testes_tocados (93) e test_pre_push_afetados (20), rc=0. Sem shell no diff.

## Revalidação (7d20b39, volta por delta)

- `bin/forge-check delta --parecer docs/reviews/forge-testes-034.md` sai com rc 2 ("1d7a02f não é ancestral de 7d20b39"): a pilha foi reempilhada. Por isso o delta veio do `git range-diff b45e40a..1d7a02f b45e40a..704a606`. Mudaram só o `:=` do A2 (aec5092) e o fragmento separado por branch; 4c5e197 e b928474 têm o mesmo código. O delta novo é `git diff b928474 7d20b39`: `bin/forge-testes:191-221` (regex `LEITURA_DE_BIN` trocada por `bin_lidos`, que lê o AST) e `:233`, mais um teste (`tests/test_testes_tocados.py:1028-1031`). Li só isso; o resto da pilha é o "já lido".
- O AST resolve o falso positivo do cartão 19. Conferi `bin_lidos` caso a caso. Acham o arquivo: `RAIZ / "bin/x"`, `RAIZ / "bin" / "x"`, `RAIZ.joinpath("bin", "x")` e `ler("bin/x")`. Não acham nada: a chamada `f("bin/x")` (o bug), a tupla `("bin/x", 1)`, `self.d / "bin" / "x"`, `Path("bin/x")`, f-string, bytes e `bin/a/b`. Os falsos negativos (`Path(...)`, `os.path.join`, variável) cabem num aviso: o plano e o rc não mudam, e a autoridade continua sendo a suíte completa (`MapaCobreOQueOsTestesLeem`).
- Exceções. Erro de sintaxe e byte nulo (Python 3.12.3) dão `SyntaxError`, que é capturado e devolve um conjunto vazio. Uma cadeia de 20 mil `/` dá `RecursionError` em `ast.parse`, sem captura em `bin_lidos`. Ela é subclasse de `RuntimeError`, que a chamada em `main` (`bin/forge-testes:594-598`) captura. Os avisos daquela chamada se perdem, mas o plano segue. Não derruba o comando.
- Prova de vermelho: com o `bin/forge-testes` de b928474 e o teste de 7d20b39, `test_sem_aviso_quando_o_teste_passa_bin_x_como_argumento_ou_dado` falha; em 7d20b39, passa. O QA confirmou o bug fechado (e7e40cd).
- `python3 -I -m unittest discover -s tests -p test_testes_tocados.py` em 7d20b39: 92 testes, OK, rc 0.
- M14: `git diff --numstat --no-renames aec5092 7d20b39` dá `bin/forge-testes` 57 e `tests/test_testes_tocados.py` 20, 77 linhas, um comportamento (aviso do MAPA). A branch está empilhada sobre melhoria/forge-testes-sem-mapa. Para o PR contra a develop levar um comportamento só, a sem-mapa entra antes; do contrário, o diff contra a develop soma 131 linhas e dois comportamentos.
- Pendência fora deste parecer: a sem-mapa (aec5092) e a filtro-k (704a606) precisam de parecer de review próprio, com `branch:` de cada uma.
