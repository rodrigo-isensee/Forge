---
tipo: qa
contrato: 1
pedido: conformidade-leitura
branch: melhoria/conformidade-leitura
commit: 2e1e7129d7494912f5de2dba382dae15a5d64c4b
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-21
---
# QA - conformidade-leitura (M1: a F6 deixa passar linha só de leitura que cita forge e sugerir)

Links: pedido `conformidade-leitura` (decisão M1 do dono), `docs/reviews/conformidade-leitura.md` e `docs/security/conformidade-leitura.md` (ambos aprovados sobre este commit). Sem UX nem API. Offline (`R-CUSTO`); sondas em `$TMPDIR`. O HEAD da branch (`b11d286`) só soma os dois pareceres sobre o código testado.

## Resultados
| ID | Obrigação / cenário | Fronteira protegida | Resultado |
|---|---|---|---|
| CT-01 | Suíte completa `python3 -m unittest discover -s tests -q` | n/a | Passou: 1194 testes, OK (420 s) |
| CT-02 | `scripts/validar-plugin.sh` | n/a | Passou: `Validation passed` (a validação tenta api.anthropic.com e o sandbox nega; não afeta o resultado) |
| CT-03 | Fixtures `tests/hooks/conformidade/leitura-*.json` (16), dentro da suíte | leitura x execução | Passaram (3 libera, 13 bloqueia) |
| CT-04 | Leitura que cita `forge sugerir` passa: `grep -n`, `cat x \| grep`, `git log \| grep`, `tail && grep` (hook real, cópia em `$TMPDIR`) | pipe e `&&` só de leitores | Passou, saída 0 |
| CT-05 | `#` colado ou solto, variável antes do programa, `eval`, `bash -c`, `xargs`, `> arquivo`, `\| tee`, `; forge sugerir`, `&& forge sugerir`, `--pre=` | ofuscação e execução | Recusou todos, saída 2 (`R-CONFORMIDADE`) |
| CT-06 | `sed -n '/forge sugerir/p' README.md` | `sed` fora do recorte | Recusou (saída 2): `sed` não está em `LEITORES_SEM_EXEC` (o recorte do pedido é cat, head, tail, nl, tac, grep, egrep, rg, od, strings, base64 e `git log/show/diff`). Conservador e coerente com a M1; ver recomendação R1 |
| CT-07 | Funções `so_leitura` direto: 7 positivos, 26 negativos (crase, `$()`, heredoc, várias linhas, caminho no programa, `sed -i`, `find -exec`) | borda de parser | Todos como esperado, exceto `sed -n` (CT-06) |

## Vermelho antes do verde
As 3 fixtures `*-libera` rodadas contra o hook de `origin/develop` (cópia em `$TMPDIR/velha`): as três falham com saída 2, `R-CONFORMIDADE: forge sugerir fora da forma ...`; com o hook da branch saem 0. As fixtures de bloqueio passam nos dois (a regra anterior já recusava; elas travam o afrouxamento). Mutação: sem ferramenta gratuita na stack do Forge; não executada.

## Observações sem bloqueio
- `grep $S x` (sem a palavra `sugerir` na linha) passa; é comportamento anterior, fora da F6, e a linha só lê.
- `grep -f x y` e `grep x y 2>&1` passam: leem, não executam nem gravam.

## Condição de merge
Esta mudança afrouxa um bloqueio da F6. O PR para a `develop` leva destaque no título e o rótulo `afrouxa-regra` posto pelo dono na E1.5; sem isso, não mescla.

## Recomendações (não bloqueiam)
- R1: se o dono quiser `sed -n` como leitura, incluir `sed` com lista própria de opções (`e`, `w`, `-i` executam ou gravam); hoje recusa, sem risco.

## Volta 2 (código 2e1e712: `so_leitura` lê a linha por `leituras()` da #269)
Revalidação sobre `2e1e7129d7494912f5de2dba382dae15a5d64c4b` (HEAD da branch `445e769` só soma pareceres). Offline (`R-CUSTO`); sondas em `$TMPDIR`.

| ID | Obrigação / cenário | Fronteira protegida | Resultado |
|---|---|---|---|
| CT-08 | Suíte completa `python3 -m unittest discover -s tests -q` | n/a | Passou: 1298 testes, OK (395 s) |
| CT-09 | `scripts/validar-plugin.sh` | n/a | Passou: `Validation passed` (rede negada pelo sandbox, sem efeito no resultado) |
| CT-10 | Liberações da M1 no hook real (cópia de 2e1e712 em `$TMPDIR`): `grep -n 'forge sugerir' README.md`, `git log --oneline \| grep 'forge sugerir'`, `cat x \| grep forge sugerir` | leitura pura | Saída 0 |
| CT-11 | Contornos: `; forge sugerir`, variável (`forge $S`), crase, `eval`, `xargs`, `\| forge sugerir`, `&&`, `>`, aspa sem par, `--pre=sh`, `f#;forge`, `bash -c`, `sug""erir`, `forge sugerir --fila` | ofuscação e execução | Todos saída 2 (`R-CONFORMIDADE`) |
| CT-12 | Merge 95a7321 não liberou nada da #269: `git diff fa75b67 2e1e712` só toca `hooks/conformidade.py` (+58/-3, só `so_leitura` e seu uso); `hooks/_comum.py` sem diferença; as fixtures da #269 passam na suíte | regressão da #269 | Confere |

Vermelho antes do verde: sem teste novo neste delta (a volta 2 só troca `comandos()` por `leituras()`); as 3 fixtures `*-libera` seguem vermelhas contra o hook da `develop` (verificado na volta 0). Mutação: sem ferramenta gratuita na stack; não executada.

Observação sem bloqueio: `git log --grep='forge sugerir' --oneline` sai 2 (`--grep` fora da lista branca de opções); fora do recorte da M1, conservador, sem risco.

## Achados
