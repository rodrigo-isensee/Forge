---
tipo: revisao-seguranca
contrato: 1
pedido: impl-n-fechar-b2
branch: melhoria/impl-n-fechar-b2
commit: 7f3b9ba84da9896dcce81cb3acae9ae7da17072a
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-22
---
# Review de segurança: RET-FECHAR-B2

Escopo: os commits de `melhoria/impl-n-fechar-b2` desde `38c58247fdae5482ed441db4dd21bff4d55471d7` (cf4ff32 a 7f3b9ba): `bin/forge-fechar`, `docs/fechamento-integrador.md`, testes `tests/test_fechar*.py` e o fragmento `changelog.d/impl-n-fechar-b2.md`. A revisão é defensiva e estática. O merge da `develop` fica fora dela.

Histórico: a rodada 1 revisou o commit `2587662dd0a7aa4905be9a7e1beae1be36dcc034` e deu `reprovado` (A1 bloqueante, A2 recomendado; ver o commit `0fe6c1d`). A rodada 2 (volta 1) revisa o commit `7f3b9ba84da9896dcce81cb3acae9ae7da17072a` e dá `aprovado`.

## Gatilhos
- Controles do Forge (`bin/forge-fechar`, o script de integração): merge na `develop`, `--match-head-commit`, guarda de base (`R-MAIN`, `R-FLUXO`), espera do rótulo `afrouxa-regra` e da Catraca (`R-CONFORMIDADE`).

## Achados

## Revalidação (volta 1, commit 7f3b9ba)
Veredito: **aprovado**. Para ler o delta, rodei `forge-check delta --parecer` sobre o parecer anterior, no intervalo `2587662..7f3b9ba`. O delta toca:
- `bin/forge-fechar:666-669`
- `docs/fechamento-integrador.md:16`
- `tests/test_fechar.py:40`
- `tests/test_fechar_pr_numero.py:23` e `:117-135`
- `changelog.d/impl-n-fechar-b2.md:6`

O `changelog.d/impl-n-reg.md` vem do merge da `develop` e fica fora do escopo. Como o gatilho é controle do Forge, reli o passo 6 inteiro (`bin/forge-fechar:655-690`), não só as linhas do delta. Não usei critério novo.

- **A1 (bloqueante na rodada 1): resolvido.** Em `bin/forge-fechar:668-669`, antes do `pr ready` e do `pr merge`, o script relê o PR pelo nome da branch, que é a mesma resolução que esses dois comandos usam. A leitura passa por `ler`: são três tentativas, e se todas falham o script para (falha fechada). O número lido tem de ser o `#pr_n` cujas base, fork e head as guardas de `:657-662` conferiram; se não for, o script para. Assim, um 2.º PR aberto do mesmo head para `main` ou `homolog` para antes do ready e do merge. Provas:
  - `tests/test_fechar_pr_numero.py:117`: o nome da branch resolve para o `#99` e o PR guardado é o `#9`. O script para no passo 6, sem `pr ready` nem `pr merge`.
  - `:129`: quando os números coincidem, o merge segue.
  - Mutação: tirei a linha `[ "$por_nome" = "$pr_n" ]` e o teste de `:117` falhou (1 falha em 13). Com a linha de volta, passam os 13.

  O risco que sobra é a janela entre a releitura e o merge (milissegundos). Ela está registrada em `docs/fechamento-integrador.md:16` e no comentário de `bin/forge-fechar:667`, como a rodada 1 pedia.
- **A2 (recomendado na rodada 1): sem mudança.** O RET-FECHAR-B2-V1 deixou esse ponto fora da volta. Continua como recomendação, que não bloqueia (detalhe abaixo).
- **Frase do doc (A2 do review):** `docs/fechamento-integrador.md:16` já não diz que os PRs "não se confundem" no merge. Agora descreve a releitura e a janela que sobra, o que bate com o código.
- **Achados novos no delta: nenhum.** O dublê em `tests/test_fechar.py:40` só responde à leitura `--json number --jq`. Ele vem antes do padrão `*number,state*` e não captura as outras leituras: a suíte `tests/test_fechar*` passa inteira.

## Detalhe dos achados
**A1 da rodada 1: regressão da guarda de base do passo 6 (média, esforço P; resolvido em 7f3b9ba).**
Evidência: `bin/forge-fechar:657-662` lia o PR pelo número `#pr_n` e conferia base, fork e head. Já o `pr ready` e o `pr merge` agiam pelo nome da branch. O `gh` resolve o nome da branch para o PR aberto mais recente com aquele head, que pode não ser o `#pr_n`.
Caminho de ataque: na espera dos passos 4 e 5, outra sessão abre um 2.º PR do mesmo head para `main` ou `homolog`. Esse PR seria mesclado sem passar pela guarda, e o `--match-head-commit` não o barra, porque o head é o mesmo. Isso fere `R-MAIN` e `R-FLUXO`.
Correção: a que a rodada 1 indicou, aplicada em `:668-669`, com teste.

**A2 da rodada 1: Catraca reconhecida só pelo nome do check (baixa, esforço P a M; recomendação, segue aberta, não bloqueia).**
Evidência: `bin/forge-fechar:296` e `:309` tratam como Catraca toda linha cujo nome é `catraca`. Quando o rótulo já foi lido e há uma execução "nova" em `pass` ou pendente, a execução velha em `fail` passa a contar como `skipping` (`:312-314`).
Caminho de ataque: um workflow novo com um job chamado `catraca`, disparado em `labeled` e sempre verde, libera a espera antes da Catraca real concluir.
Realismo: baixo. Mexer em `.github/workflows/` dispara a própria Catraca e exige o rótulo do dono. Além disso, o token do bot não tem o escopo `workflow`.
Correção sugerida: amarrar a linha da Catraca ao workflow (`gh pr checks --json name,state,link,workflow`) ou exigir uma execução nova com `run_id` maior que os anteriores. Em qualquer caso, manter a Catraca como check obrigatório na proteção da `develop`.

Conferido sem achado (rodada 1, sem mudança no delta):
- B5, cadeia do sha: `sha_conferido` é lido antes do passo 1, passado ao `forge-check pr --ref <sha>` e relido nos passos 1 e 2. Ele é igualado ao head remoto e usado no `--match-head-commit`.
- B3, MERGED preso: `estado_do_pr` exige head, base e commit de merge de `#pr_n`. O `pr_n` só vem de número validado ou de uma única URL `/pull/<n>`. PR de fork para nos passos 3 e 6.
- B4, `dicas_de_log`: só imprime. Só dígitos do número da execução entram no comando, e o `TMPDIR` vai entre aspas simples escapadas.
- B1, `aviso_do_rotulo`: os nomes não passam caracteres de controle C0, DEL nem C1, o que barra sequência de escape de terminal.
- B2, `estados_da_espera`: o merge exige tudo `pass` ou `skipping` na última leitura.
- R2 do lote a: `tmp2b` e `dorme_pid` nascem vazios (`bin/forge-fechar:36`).

## Riscos aceitos e ferramentas
Nenhum risco aceito. O risco residual do A1 (a janela de milissegundos) está documentado. O A2 segue como recomendação aberta.

Ferramentas, rodada 2 (7f3b9ba):
- `shellcheck`: os mesmos 3 avisos da base (SC2034, SC2015, SC2086), nenhum novo.
- `python3 -m unittest` dos módulos `tests/test_fechar*`: 158 testes, OK.
- Mutação do A1, descrita acima.

Ferramentas, rodada 1 (2587662): `shellcheck` com os mesmos 3 avisos; 124 testes OK.

Lacuna: `gitleaks` e `semgrep` não estão no PATH e não foram instalados (`R-CUSTO`). Conferi o delta lendo, e ele não traz segredo nem credencial.
