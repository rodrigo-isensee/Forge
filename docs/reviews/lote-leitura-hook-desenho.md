---
tipo: review
contrato: 1
pedido: RET-LEITURA-HOOK
branch: melhoria/lote-leitura-hook
commit: b9e15dc986bb74095fbf735cec9c0941db82767c
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-22
---
# Review: desenho da volta única do lote-leitura-hook (RET-LEITURA-HOOK, E2.2)

Revalidação 1 do desenho. Escopo: `docs/propostas/lote-leitura-hook-volta-unica.md` em `b9e15dc` (a volta 1 do arquiteto), contra os achados A1 a A8 do parecer anterior (reprovado sobre `d557a37`, commit do parecer `68bd13c`). Delta lido: o diff `d557a37..b9e15dc` do desenho inteiro (226 linhas a mais, 127 a menos), já que o documento todo mudou. Já lido e sem mudança: a ADR 0011, a revalidação 5 (`docs/reviews/lote-leitura-hook.md`) e as seções 3 a 5 da retrospectiva. Critério desta passada: o mesmo da anterior. Achado novo só entra se ferir uma linha "Promete" da tabela 2.3. Nenhum entrou.

Sondas: os casos [INF] pedidos rodaram de dois modos, ambos em `$TMPDIR`. Primeiro, nos dois hooks do código atual (`1b0fb6b`, sem mudança até `b9e15dc`), montados pelo `Fixture` dos modelos da seção 3. Depois, no bash 5.3.9 (`bash --noprofile --norc -c`, ambiente limpo), com o corpo `echo RODOU > prova`.

## Achados

## Revalidação dos achados anteriores
- A1 (bloqueante) · **resolvido**. M2, "Enumerador positivo" (linhas 63 a 67): a palavra é programa salvo redireção completa com alvo, atribuição ou `ANTES_DO_PROGRAMA`. Os casos S17 e S18 estão nas linhas 164 e 165, e o T7 na 260. Sonda S17a (`…⏎EOF⏎chmod +x x.sh⏎2>&1 ./x.sh`): no bash criou `prova` com `RODOU`.
- A2 (bloqueante) · **resolvido**. Leitor sequencial com um estado para as aspas (linhas 47 a 53), sem `re.sub` de aspas no lote. Os casos R19a a R19e estão nas linhas 123 a 127, e o T6 tem os prefixos P1 a P4 (linha 259). Sondas R19b e R19c: 0 / 0 nos hooks e `.husky/pre-push` gravado no bash. Isso confirma o [INF] e a marca `M2`.
- A3 (bloqueante) · **resolvido**. A marca `fecha` cobre os dois lados (linhas 252 a 255). A ordem tem um commit por regra, suíte e validação verdes em cada commit, fixtures invertidos no commit da regra e "depende de" declarado (linhas 263 a 271).
- A4 (bloqueante) · **resolvido**. A tabela 2.3 (linhas 83 a 93) e o critério (i)/(ii) (linhas 273 a 276) decidem por pertença a uma linha "Promete". O texto é o proposto no parecer anterior.
- A5 (bloqueante) · **resolvido**. F7a, F7b, F8a e F8b estão nas linhas 290 a 293, com contorno, e a seção 6 lista todos os F novos. A frase "são os únicos novos" saiu (`grep` vazio).
- A6 (recomendado) · **resolvido**. O T6 pula quando `BASH_VERSINFO[0] < 4` e dá o motivo (linha 259).
- A7 (recomendado) · **resolvido**. Os `corpos` trazem a linha literal do modelo do `parecer` (linha 237), igual ao `command` de `forge-clone-pr-merge-no-corpo-de-heredoc-gravado-e-make-bloqueia.json`.
- A8 (recomendado) · **resolvido**. M2 e M3 têm frase própria (linhas 71 e 78), as leituras da ADR 0011 ganham linhas próprias (linha 80) e a seção 5 conta cada F pela regra que o gera (linha 279).

## Sondas dos casos [INF]
| Caso | Hooks em `1b0fb6b` (conf / par) | Bash 5.3.9 | Leitura |
|---|---|---|---|
| S18a, S18b, S18c | 0 / 0 | `prova` = `RODOU` nos três | furo real hoje. M2 promete "dono sem programa não só lê", e a marca `M2` confere |
| R20a, R20c | 2 / 2 | `.husky/pre-push` gravado | já passam. A marca `M2` sobra e o passo (1) a tira, como diz a linha 255 |
| R20b | 2 / 2 | `>&2 git apply` aplicou o patch | idem |
| R19b, R19c | 0 / 0 | `.husky/pre-push` gravado | confirma a marca `M2` |
| R19d | 2 / 2 (item 2, `$'`) | não rodado (o item 2 já recusa) | confere com "—" |
| R19e | 2 / 2 | não rodado | confere com "—" |
| L10 | 2 / 0 (par fora do `PREFILTRO`, "—") | nada gravado | confere com `fecha: M5`: o `echo` segura até o passo (6) |
| F10 | 0 / 0 | nada roda | falso positivo esperado, marca `M2` confere |
| R10 / F9 (sonda extra) | não rodado | `cat 1>&x` **gravou** o arquivo `x` | o [INF] "o bash não grava" está errado (nota abaixo) |

## Parecer
**Aprovado.** A volta 1 fecha os oito achados sem mudar o caminho aprovado (B). Corpus, marcas e critério de parada servem como contrato comum da implementação (E3.1) e dos pareceres (E3.2 a E3.4). As sondas [INF] confirmam as marcas previstas, menos R20a a R20c, que já passam. O próprio desenho prevê a correção dessas marcas no passo (1), então nada bloqueia.

### Notas para o passo (1) do E3.1 (não são achados: nenhuma fere uma linha "Promete")
- **R10 e F9.** No bash 5.3.9, `cat 1>&x <<'EOF'…` grava o arquivo `x`. O M1 já conta `[n]>&arquivo` como gravação (linha 60), e o T6 só exige a implicação, então o código e os testes ficam certos. O texto fica errado em três lugares. A linha 114 diz "o bash não grava". A linha 259 diz "R10 confirma o [INF]: o bash não grava". A linha 294 trata o F9 como falso positivo. No passo (1), o R10 vira caso R comum e o F9 sai da classe F e da lista da seção 6. Assim a contagem do A8 não soma um acerto como falso positivo.
- **R20a a R20c.** Os três já dão 2 / 2 em `1b0fb6b`. A marca `M2` sobra e o passo (1) a tira. Eles ficam como guarda do enumerador.

### Fora do bloco
- O diff é só documento. Os testes, `scripts/validar-plugin.sh` e as regras de ferramenta do `praticas.md` não se aplicam e não foram rodados.
- Segurança: S18 é furo real em `1b0fb6b` (o corpo roda no bash e os dois hooks saem 0). Ele já está no corpus com a marca `M2`, e o `security-engineer` o recebe por ali no E3.3, sem cartão à parte.
