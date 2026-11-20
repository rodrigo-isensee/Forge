---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-meta85-placar
commit: 6f6aab30715d2ae7cd6136c37cc35ed10bb59f81
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-19
---
# Review de segurança: v0479-meta85-placar, revalidação pós-junção (v0478 E36.11)

Volta por delta (R-REVIEW): `forge-check parecer delta docs/security/v0479-meta85-placar.md`, intervalo 97ef4fd1..f74d6dd7. No domínio, só `bin/forge-placar` (junção com a develop: `fundo_demais`, teto 64, :208-231 e :240-245); fora, `changelog.d`, `tests/evals/test_placar.py` e dois mutantes. Rodadas anteriores (87aff761, 97ef4fd1) ficam no git: A1 (PARADA com data impossível) segue resolvido.

Gatilhos: nenhum (ferramenta local de leitura; sem autenticação, segredo, dependência, CI, rede nem controle do Forge).

## Achados
- A2 (recomendado) bin/forge-placar:712 · RESOLVIDO em d340b213: `paradas_do_ci` (META85, `fases --ci`) lê JSON agora chama `fundo_demais` antes do `json.loads` (:712-713); antes só captava `RecursionError`

## Revalidação (head 6f6aab30, v0478 E36.27)
Delta (`forge-check parecer delta`, 89936fa3..6f6aab30): no domínio, só `bin/forge-placar`, nova `hora_numerica` (:623-625) aplicada ao campo `merge` de `itens_do_dia` (:647); fora, `tests/evals/test_placar.py` (teste com `git` falso) e dois mutantes. A função só troca um `Z` final por `+00:00` em string vinda do `%cI` do git local: sem execução, sem arquivo, sem rede, sem regex. Sem achado aberto; A1 e A2 seguem resolvidos; parecer segue aprovado.
- S16 · `hora_numerica` executada (`python3 -I`) com `...12:00:00Z`, `...12:00:00+00:00`, `...09:00:00-03:00` e `""` · espera: só o `Z` muda, vazio não quebra · obtido: `+00:00`, `+00:00`, `-03:00` intacto, `''`.
- S17 · `python3 tests/evals/test_placar.py -k test_merge_em_utc` (teste novo, com `git` falso em `$TMPDIR` que reescreve `+00:00` em `Z` via `sed`) · espera: passa · obtido: `Ran 1 test ... OK`. O `git` falso fica no PATH só do subprocesso do teste; não toca o repositório nem o PATH real.

## Revalidação (head d340b213)
Delta (`forge-check parecer delta`): só `bin/forge-placar` no domínio, +2 linhas em `paradas_do_ci` (:712-713, `fundo_demais` antes do `json.loads`, mensagem fixa); fora, `tests/evals/test_placar.py` e um mutante. A2 resolvido, sem achado aberto; parecer segue aprovado. S8 repetida abaixo (S11).

## Revalidação (head 89936fa3, v0478 E36.20)
Delta (`forge-check parecer delta`, 57a66ff4..89936fa3, sem o que veio da base): no domínio, só `bin/forge-placar` (guarda do dia sem item, docstrings, `FONTES_DE_PARADA` montado de um `DO_HISTORICO`); fora, um mutante. Lido: nenhuma mudança em `fundo_demais`, `paradas_do_ci`, `--prs` nem `paradas_do_historico`. Sem achado aberto; A1 e A2 seguem resolvidos; parecer segue aprovado.
- Fontes de parada: o dicionário `FONTES_DE_PARADA` de 57a66ff4 e o de 89936fa3, executados, são iguais (S12).
- Aninhamento: `--prs` (:237-238) e `--ci` (:706-707) seguem chamando `fundo_demais` antes do `json.loads` (S13, S14).
- Data impossível: o `try/except ValueError` por linha de `paradas_do_historico` (:693-696) segue, aviso fixo, demais linhas valem (S15).

## Sondas
- S12 · `FONTES_DE_PARADA` executado em 57a66ff4 e em 89936fa3 (`python3 -I`, `git show`) · espera: iguais · obtido: `True`, 3 chaves
- S13 · `forge-placar --prs ARQ`, ARQ com 100000 `[` · espera: rc 2 pela guarda · obtido: rc 2, `não é JSON legível (aninhado acima de 64 níveis)`
- S14 · `forge-placar fases --ci ARQ`, ARQ com 100000 `[` e 100000 `]` · espera: rc 2 · obtido: rc 2, `não é uma lista de runs legível (aninhado acima de 64 níveis)`, sem traceback
- S15 · `fases --raiz R` com `- 2026-11-19 09:00: PARADA sessão 2026-13-45 09:00 até 2026-13-46 10:00` e uma linha válida de 1 h · espera: aviso, linha pulada, 1 h contada · obtido: `PARADA com data impossível em docs/pedidos/v0001.md; linha ignorada` e `1 h 00 min`
- S11 · fases --raiz R --ci ARQ, ARQ com 100000 colchetes abertos (também fechados; também em objeto) · espera: rc 2, mensagem fixa, sem eco nem traceback · obtido: py 3.12.3, rc 2 nos três, stderr uma linha com o caminho do argumento e teto 64, sem traceback
- S8 · `fases --raiz R --ci ARQ` com `[`x100000 e `]`x100000, e com `[{"conclusion":"x","a":[`...`]}]` aninhado igual · espera: sai 2 com mensagem · obtido: (py 3.12.3) rc 2, `--ci ... não é uma lista de runs legível`, nos dois
- S9 · `--prs ARQ` com os 100000 `[` · espera: sai 2 pela guarda · obtido: `não é JSON legível (aninhado acima de 64 níveis)`
- S10 · `--ci ARQ` (caminho da develop, `ci_vermelha` :199) com os 100000 `[` · espera: sai 2 · obtido: traceback `RecursionError`, rc 1; idêntico na develop (fora do delta)

## Detalhe
- Ponto 1 (mesma guarda de aninhamento): **parcial**. `--prs` passa por `fundo_demais` (teto 64, passe linear, sem regex; sai 2 em qualquer versão). A leitura de JSON da META85 (`paradas_do_ci`, :712-715) não a chama; segue o mecanismo antigo (captar `RecursionError`), que funciona no 3.12 (S8) mas, pelo comentário da própria develop, não dispara no 3.14. Sem Python 3.14 no PATH, não sondei. Caminho de ataque: quem controla o arquivo `--ci` (saída de `gh run list`, gerada localmente pelo operador) é o próprio operador; no pior caso o JSON fundo é aceito no 3.14, analisado em tempo linear, sem travar nem vazar (elemento aninhado sem `.get` cai em `AttributeError`, captado). Sem ganho para atacante: inconsistência de comportamento, daí `recomendado`. Correção mínima: chamar `fundo_demais(texto)` antes do `json.loads` em :712, com a mensagem de `--prs` (dono: o autor de `bin/forge-placar`). O `ci_vermelha` (:199, S10) já era assim na develop e fica fora deste delta.
- Ponto 2 (PARADA com data impossível): **continua tratado**. `paradas_do_historico` (:688-703) tem o `try/except ValueError` por linha, aviso fixo só com o nome do pedido, demais linhas seguem, sem intervalo legível devolve None (`-`); a junção não tocou esse trecho (S5 e S7 da rodada anterior valem).
- `fundo_demais` e o teto 64 vindos da develop, lidos no delta: contagem de nível fora de strings, escape tratado, retorno cedo ao passar do teto; sem backtracking.

## Riscos aceitos e ferramentas
Sem risco aceito. Ferramentas: leitura do delta e sondas locais em `$TMPDIR` com `python3 -I`. Suíte: não rodada localmente (brief: sem suíte local); a suíte inteira fica com o CI do PR. Varredor de segredos e SAST não estão no PATH: lacuna registrada; o delta não traz credencial.
