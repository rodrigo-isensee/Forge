---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-hook-texto-merge
commit: 9d9a069d997fffe261c4563b8e1c6137b8382773
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-16
---
# QA: v047 hook-texto-merge (E2.271, HOOK-TEXTO-COM-MERGE)

Head 9d9a069d, base 5e74c70e. Diff lido contra o pedido: `hooks/parecer.py` (regex `ALVO_DO_CAT` e uma chamada em `conferir_linha`), 11 fixtures `texto-*`, spec de mutantes, índice e fragmento de changelog. Sem especificação de UX: as obrigações são o pedido E2.271 e `R-REVIEW`.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E2.271: texto com merge, gh pr ou pull gravado por `cat > alvo` com alvo entre aspas ou `$VAR` deixa de ser recusado | `texto-passa-gravado-em-variavel-com-merge`, `...-com-chaves-e-pull`, `...-caminho-entre-aspas-com-apostrofo` | alvo `"$X/…"`, `${X}` sem aspas, `'…'` com espaço; texto com apóstrofo | passou |
| E2.271: sem afrouxar (R-REVIEW): `$( )`, `${X:-…}`, crase no alvo | `texto-barra-gravado-em-substituicao`, `...-variavel-com-operador` | operador e substituição no alvo | passou (rc 2) |
| E2.271: sem afrouxar: arquivo gravado e rodado na mesma chamada, ação crítica fora do corpo | `...-variavel-e-sh-roda`, `...-e-git-add`, `...-e-wc`, `...-para-processo` | comando fora da lista curta, redirecionamento de processo | passou (rc 2) |
| E2.271: sem afrouxar: `python3 -` com texto que cita ou roda a ação crítica | `texto-barra-python-stdin-com-gh-pr`, `...-roda-merge` | interpretador lê o corpo | passou (rc 2) |

## Cenários e resultado real
- `python3 -m unittest tests.test_hooks_parecer_pasta` na raiz do clone: 3 testes, OK (49 s). Suíte inteira: no CI do PR (`bateria`), fora desta passada (R-QA).
- Vermelho antes do verde: `forge-testes --vermelho 5e74c70e…` passa dos 180 s do sandbox e o processo é morto ("fatal library error, lookup self"), sem veredito. Equivalente feito à mão: cópia limpa do head com `hooks/parecer.py` da base, `test_corpus_texto_passa_e_barra`: `FAILED (failures=4)`, ex.: `AssertionError: 2 != 0 : R-REVIEW: `>` na chamada com heredoc e gh pr, gh api, merge ou pull: o hook não modela`. Os 4 casos `texto-passa-*` novos caem na base e passam no head; os 7 `texto-barra-*` guardam o que continua recusado.
- Mutação (`bin/forge-mutante tests/mutantes/v047-hook-texto-merge.json`, rc 0):
  - `forge-mutante: pedido=v047 rev=9d9a069d997f spec=1cfbbb0e018e…`
  - `HTM1 · morreu · hooks/parecer.py:960`
  - `HTM2 · morreu · hooks/parecer.py:72`
  - `HTM3 · morreu · hooks/parecer.py:73`
- Cobertura: `forge-mutante --cobertura --base 5e74c70e…` sem condição mudada fora da spec (só a linha `base=… rev=9d9a069d…`).
- Abuso, sondado direto no hook (script próprio, fora do repositório), todos rc 2 salvo o primeiro: alvo `"$TMPDIR/x.md"` com texto de merge (rc 0, o caso novo); crase no alvo; `bash $X` ou `$X` depois; `. arq` e `source arq` depois; heredoc sem aspas com `$( )` no corpo; a ação crítica fora do corpo; aspa interna com `$(id)`; `| sh` após o heredoc; `> >(sh)`; `xargs -a arq sh -c`; `cat > "$A" "$B"` (dois alvos). Nenhum atravessou.
- Fronteira fora do plano e inofensiva: `$VAR` sem aspas que se divide em palavras vira redirecionamento ambíguo do bash (erro, sem execução); só grava arquivo.

## Itens do PA-7
Conferidos contra `docs/engineering/achados-recorrentes.md`: teste novo nasce de obrigação nomeada, sem `skip`, o corpus `texto-*` mantém a guarda de mínimo (30), um mutante por linha de guarda mudada (a cobertura confirma). Sem classe repetida: nenhuma linha `AR-` nova.
