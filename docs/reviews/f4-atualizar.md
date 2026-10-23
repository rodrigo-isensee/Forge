---
tipo: review
contrato: 1
pedido: F4-ATUALIZAR
branch: melhoria/f4-atualizar
commit: 4d86f26c7ff6266ff989476b75f2e2a1a3d691c3
parecer: reprovado
revisor: forge:tech-lead (outra instância)
data: 2026-10-23
---
# Review da F4: `forge atualizar` nasce da `develop` atual e oferece ao dono o conflito em `.forge/versao`

## Revalidação por delta (volta `1f2731b` testes, `4d86f26` correção)
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
- A6 (bloqueante) bin/forge-atualizar:117 · versao_de dá None para .forge/versao fora de X.Y.Z e `None > tuple` levanta TypeError: traceback no meio do merge, sem abort, deixa UU e MERGE_HEAD (S1). Comparar só com as duas válidas; teste com versão inválida
- A7 (recomendado) bin/forge-atualizar:63 · `develop` local à frente do remoto (commits não enviados) segue em silêncio e a branch do upgrade nasce com eles, que aparecem no PR; uma linha de aviso, como a da divergente.
- A8 (recomendado) changelog.d/f4-atualizar.md:2 · o fragmento não diz que há merge local de `origin/develop` só na branch do upgrade nem que a saída lista os arquivos trazidos; alinhar ao `README.md:77`.

## Parecer
Reprovado. A volta resolve o bloqueante da segurança (A1) e os recomendados dos dois pareceres, com testes que falham antes e passam depois. A comparação de versões nova, porém, abre um caminho que derruba o comando no meio da mesclagem e deixa o repositório do projeto em conflito, justo o que a F4 promete não fazer (A6). A correção é uma guarda de uma linha e um teste; A7 e A8 podem ir na mesma volta.
