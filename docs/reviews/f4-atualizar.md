---
tipo: review
contrato: 1
pedido: F4-ATUALIZAR
branch: melhoria/f4-atualizar
commit: 6634cd800fd9366b1e8fcaf75e01e948e758880c
parecer: aprovado
revisor: forge:tech-lead (outra instância)
data: 2026-10-23
---
# Review da F4: `forge atualizar` nasce da `develop` atual e oferece ao dono o conflito em `.forge/versao`

## Revalidação 2 por delta (volta `106cb84` testes, `6634cd8` correção)
Delta lido: `forge-check delta --parecer docs/reviews/f4-atualizar.md` (intervalo `4d86f26..6634cd8`) listou só `bin/forge-atualizar` (62-68, 115-126, 134-139), `changelog.d/f4-atualizar.md:2` e `tests/test_atualizar.py:495-525`. Li esses trechos e o que eles chamam (`resolver_conflito` inteiro, `trazidos`, `fv.versao_de` em `bin/forge_versoes.py:30`, o tratamento de `EOFError`/`KeyboardInterrupt` na linha 300). Já lido, sem mudança: o resto de `bin/forge-atualizar`, o `README.md` e os testes até a linha 494.

Evidência de execução (`HOME=$TMPDIR/tech-lead-f4`):
- `python3 -m unittest tests.test_atualizar` em `6634cd8`: `Ran 73 tests in 48.277s OK`.
- A mesma suíte na árvore de `106cb84` (só os testes novos): `FAILED (failures=3)`, os subtestes `0.4` e `lixo` da versão fora de X.Y.Z e o da develop local à frente. Vermelho antes, verde depois: confere.
- Commits: `test(...)` e `fix(...)` em Conventional Commits em português, um por mudança coerente, corpo citando cada achado. Sem `--force` nem `--no-verify` (`R-VERIFY`), sem custo (`R-CUSTO`), sem termo de projeto (`R-NEUTRO`).

### Achados da revalidação anterior
- A6 (= A4 da segurança, bloqueante): **resolvido**. `bin/forge-atualizar:134-139` só compara quando as duas versões são X.Y.Z; se não, avisa que não dá para comparar e pergunta (padrão N). `integrar_develop` (linhas 115-123) desfaz a mesclagem em qualquer erro inesperado e em `EOFError`/`KeyboardInterrupt` antes de sair. O teste da linha 495 (`0.4` e `lixo`) confere: sem traceback, status limpo, sem `MERGE_HEAD`, branch do upgrade intacta. A revalidação formal do A4 é do `security-engineer`.
- A7 (recomendado): **resolvido**. Linhas 62-68 avisam quantos commits a develop local tem à frente e que eles entram no PR, sem mexer nela; teste da linha 512.
- A8 (recomendado): **resolvido**. `changelog.d/f4-atualizar.md:2` cita o merge local de `origin/develop` só na branch do upgrade, a lista dos arquivos trazidos com o destaque, o padrão N e o aviso da develop à frente, alinhado ao `README.md:77`.

### A correção abriu outro problema?
Nenhum bloqueante. Um recomendado (A9): o `except Exception` envolve também o caminho em que o commit da resolução já deu certo (`trazidos` roda depois dele); se algo levantasse ali, o `merge --abort` falharia em silêncio e a mensagem diria "Desfiz a mesclagem" com o merge já feito. `trazidos` só chama `git` e formata texto, então a chance é baixa.

## Revalidação 1 por delta (volta `1f2731b` testes, `4d86f26` correção)
Delta lido: `forge-check delta --parecer docs/reviews/f4-atualizar.md` (intervalo `671c625..4d86f26`) listou só `README.md:77`, `bin/forge-atualizar` (8-9, 54-124, 208, 231-232, 241, 251, 266-272) e `tests/test_atualizar.py:422-502`. Li esses trechos e as funções que eles chamam (`git`, `fv.versao_de` em `bin/forge_versoes.py:30`, `bin/forge-upgrade:56-64`). Já lido, sem mudança: o resto de `bin/forge-atualizar`, `changelog.d/f4-atualizar.md` e os testes até a linha 421.

Evidência de execução (`HOME=$TMPDIR/tech-lead-f4`):
- `python3 -m unittest tests.test_atualizar` em `4d86f26`: `Ran 71 tests in 61.155s OK`.
- A classe `AtualizarComDevelopQueAvancou` rodada na árvore de `1f2731b` (só os testes): `FAILED (failures=6)`; o novo que passa antes é o da `develop` atrasada com a pessoa nela (linha 452), que cobre caminho que já existia (A4). Vermelho antes, verde depois: confere.
- Sonda S1 (teste extra fora do repositório, no scratchpad): conflito em `.forge/versao` com a `develop` trazendo `lixo`, respostas `s n n`: `TypeError: '>' not supported between instances of 'NoneType' and 'tuple'` em `bin/forge-atualizar:117`; o repositório fica com `STATUS 'UU .forge/versao'` e `MERGE_HEAD True` (A6).
- Commits: `test(...)` e `fix(...)` em Conventional Commits em português, um por mudança coerente, corpo citando cada achado. Sem `--force` nem `--no-verify` (`R-VERIFY`), sem custo (`R-CUSTO`), sem termo de projeto (`R-NEUTRO`).

### Achados da revisão anterior
- A1 ("avancei" sem checar o retorno): **resolvido**. `bin/forge-atualizar:69-74` guarda o código de saída do `merge --ff-only` e do `update-ref` e só anuncia e devolve True quando deu.
- A2 (pergunta sem a versão da develop): **resolvido**. `versoes_do_conflito` (linha 90) lê `:3:` (develop) e `:2:` (upgrade), corretos para `merge origin/develop` na branch do upgrade; mostra as duas e avisa quando a da develop é maior (testes das linhas 478 e 487). A comparação, porém, abriu o A6.
- A3 (develop divergente em silêncio): **resolvido em parte**. A divergente agora avisa (linhas 64-67, teste da linha 463). A `develop` local só à frente do remoto continua em silêncio (linha 63): vira A7, recomendado.
- A4 (testes da develop atrasada com a pessoa nela e da divergente intacta): **resolvido**. Linhas 452 e 463.
- A5 ("Não mudei nada" com a develop já adiantada): **resolvido**. Linhas 231-232 e 241 usam `avancou`.

### Achados da segurança (`docs/security/f4-atualizar.md`, parecer de `671c625`)
- A1 (mescla fora da branch do upgrade, bloqueante): **resolvido**. `integrar_develop` sai sem mesclar se a branch atual não é `forge/upgrade-<nova>` (linha 101), o mesmo nome que `bin/forge-upgrade:64` cria; a mensagem final distingue "nada a fazer" (linhas 251, 266-270). Testes da `main` e de branch qualquer (linhas 422 e 438) falham antes e passam depois. A revalidação formal é do `security-engineer`.
- A2 (versão da develop na pergunta): **resolvido**, como o A2 acima, com a ressalva do A6.
- A3 (texto e lista dos arquivos trazidos): **resolvido** no código, na docstring (linhas 8-9) e no `README.md:77`; `trazidos` (linha 77) lista e destaca `.forge/`, `.claude/` e hooks (teste da linha 495). O fragmento do changelog não acompanhou: A8, recomendado.

## O que conferi antes (671c625, continua valendo)
Branch do upgrade nascendo da `develop` atual por avanço simples; recusa sem terminal e dentro do Claude antes de qualquer passo; `.forge/versao` só pelo dono no terminal (`R-CONFORMIDADE`); outro conflito desfeito por inteiro; sem remoto o fluxo segue como antes; nada é enviado. Regras "ferramenta": o Forge não tem `docs/engineering/praticas.md`; a bateria completa (suíte, shellcheck, validação do plugin) roda no pre-push e no CI.

## Achados
- A9 (recomendado) bin/forge-atualizar:120 · o `except Exception` cobre também o pós-commit da resolução (`trazidos`); erro ali diria "Desfiz a mesclagem" com o merge feito. Sugestão: chamar `trazidos` fora do try ou abortar só se houver `MERGE_HEAD`.
## Parecer
Aprovado. A6, A7 e A8 resolvidos (detalhe em "Revalidação 2"). A volta 2 fecha o bloqueante A6 (A4 da segurança) com a guarda na comparação e uma rede que desfaz a mesclagem em qualquer erro, e resolve A7 e A8, com testes que falham antes e passam depois. O A9 é recomendado e não impede o QA.
