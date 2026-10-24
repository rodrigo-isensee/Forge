---
tipo: revisao-seguranca
contrato: 1
pedido: fechar-master
branch: melhoria/fechar-master
commit: 14a6b0cd8595be38b05927a5083a11b4a9b76776
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-23
---
# Review de segurança: fechar-master

Escopo: `git diff 139a3b451a1c367ed7764257486c0a0f39c73e8b...14a6b0cd8595be38b05927a5083a11b4a9b76776` (`bin/forge-fechar`, `tests/test_fechar_longas.py`, `changelog.d/fechar-master.md`), com releitura do passo 7 (`limpar_entrega`, `bin/forge-fechar:343-442`) e do `--limpar` (`bin/forge-fechar:519-527`), que são quem apaga branch.

## Gatilhos
Controles do Forge (`R-SEGURANCA`): o `bin/forge-fechar` apaga branch local e remota no passo 7 e no `--limpar`.

## Achados

## Detalhe dos achados
Veredito: a recusa fecha o A1 do QA da LIMPEZA-REGRA. `--ref` igual a `main`, `master`, `develop` ou `homolog` morre em `bin/forge-fechar:56`, antes de qualquer `gh`, `forge-check` ou git que escreve, com e sem `--limpar`. Como o passo 7 apaga a local (`git branch -D "$ref"`, só se `refs/heads/$ref` existe, `:348` e `:392`) e a remota (`git push origin --delete "refs/heads/$ref"`, `:429`) a partir do mesmo `$ref`, a recusa vale para as duas.

Sonda (repositório e `HOME` em `$TMPDIR/security-engineer-fecharmaster/`, o harness do `tests/test_fechar.py` com `gh` falso respondendo PR MERGED na develop com o sha da `master`, e `master`, `main`, `homolog` e `trunk` criadas local e remotamente). Com e sem `--limpar`, as variantes `MASTER`, `Master`, `Main`, `DEVELOP`, `refs/heads/master`, `refs/heads/develop`, `heads/master`, `origin/master`, `" master"`, `"master "`, `./master`, `master/`, `master.`, `master@{0}`, `-` e `@{-1}` (com a `master` como branch anterior) deixaram intactas todas as refs locais (`for-each-ref refs/heads`) e remotas (`ls-remote`). As inválidas param no `check-ref-format` (`:64`). As válidas viram outra ref (`refs/heads/refs/heads/master`, `refs/heads/origin/master`, `refs/heads/@{-1}`), que não existe, e a limpeza não acha nada para apagar. Os 4 testes de `tests.test_fechar_longas` passam.

Ficam duas recomendações, nenhuma com caminho de ataque realista hoje.

R1 (baixa; correção P; dono tech-lead) · `bin/forge-fechar:61`. A leitura da branch de integração do `CLAUDE.md` falha calada em três casos, e então só vale a lista fixa:
- (a) Locale `C`/POSIX, comum em CI e em shell sem `LANG`: `integra[cç][aã]o` compara byte a byte e não casa `integração` em UTF-8. Na sonda, `LC_ALL=C` com `- Branch de integração: \`trunk\`` aceitou `--ref trunk`.
- (b) Se uma linha anterior cita "integração" com crase (`- Testes de integração com \`pytest\``), ou se a mesma linha tem outra crase antes do nome, o primeiro trecho entre crases do arquivo inteiro vence e a branch real fica sem proteção.
- (c) Um `CLAUDE.md` que o grep vê como binário não é lido.

Impacto hoje: nenhum. O script só roda no repositório do Forge (`:139`), que não tem `CLAUDE.md` na raiz, e a integração dele (`develop`) está na lista fixa. Por isso fica como recomendação.

Correção mínima: casar só o prefixo ASCII (`grep -ai 'integra'`) ou forçar `LC_ALL=C.UTF-8` nesse grep, e ler só a linha com uma chave fixa (por exemplo `Branch de integração:`), que o modelo `templates/projeto/CLAUDE.md` passaria a trazer. Junto, um teste com `LC_ALL=C` e outro com uma linha de "testes de integração" antes. O formato da linha está como suposição no histórico do pedido FECHAR-MASTER (cartão), e esta recomendação cabe nesse cartão.

Sobre um `CLAUDE.md` hostil ou malformado:
- Não consegue fazer aceitar uma protegida, porque a lista fixa (`:56`) vem antes e não depende dele.
- Não consegue fazer recusar tudo, porque a comparação é por igualdade exata com um único valor. Na sonda, `*` e crases vazias não barraram nada, e só a ref igual ao valor foi recusada.
- Um symlink para `/dev/zero` não passa no `-f` e não trava o script.

O pior caso é negar uma branch de trabalho específica, e quem escreve o `CLAUDE.md` já tem escrita no repositório.

R2 (informativa; correção P; dono tech-lead) · `bin/forge-fechar:56`. A comparação diferencia maiúsculas. Em sistema de arquivos que não diferencia (macOS padrão, `/mnt/c` no WSL), `refs/heads/MASTER` solta pode resolver para o arquivo da `master`, e `--ref MASTER --limpar` apagaria a local. Isso exige que o `gh` mostre um PR MERGED na develop com head `MASTER` e que o sha da `master` já esteja na base. Não foi sondado: o ambiente só tem ext4 gravável. Correção mínima: comparar em minúsculas (`case "${ref,,}" in main|master|develop|homolog)`) e o mesmo para a integração.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas usadas:
- Sonda local pelo harness do `tests/test_fechar.py` (log em `$TMPDIR/security-engineer-fecharmaster/sonda-1.log`).
- `python3 -m unittest tests.test_fechar_longas`: 4 OK.
- `shellcheck bin/forge-fechar`: 3 avisos, os mesmos da base `139a3b4` (`:457`, `:474`, `:481`, fora do diff; o script não está na lista do job `shellcheck` do CI).

`gitleaks` não está no PATH (lacuna). O diff não traz segredo nem credencial.
