---
tipo: qa
contrato: 1
pedido: impl-pre-push
branch: melhoria/impl-pre-push-c5
commit: 01ae5742b90c69cd0f674b1d0951d05e0d75aae3
parecer: aprovado
revisor: forge:qa-engineer
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-31
---
# QA: impl-pre-push (c5, E4: namespace no texto da trava)

## Achados
- A1 (recomendado) .githooks/pre-push:244 · o ramo "?" (leitura de /proc/self/ns/pid que falha) não tem teste próprio: o mutante Q4 só morre porque o sandbox também devolve vazio; vale um teste com a leitura forçada a falhar, em pedido futuro.

## Escopo
Só a c5: E4 do pedido (C5 do desenho; C-16 e C-17 do modelo). Diff `234dbe0..01ae574`: `.githooks/pre-push` +4 -1, `tests/test_pre_push_trava.py` +11, fragmento de changelog e parecer de review. O C-14 saiu por revert (7404c26) e está na c6; não é testado aqui. O 8bbda6d (parecer de segurança, só `docs/security/`) veio depois do commit testado e não muda código.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E4a: o texto da trava traz o namespace | `test_texto_da_trava_traz_o_namespace_depois_do_pid` (`ns ` no `--status`) | trava recém-gravada, lida pelo status | passou |
| E4b / C-17: "pid N" segue nos dois primeiros campos | mesmo teste (regex `^pid [0-9]+ ns [0-9?]+ desde `) | ordem dos campos que `scripts/suite-paralela.py:510` confere | passou |
| E4c: o campo só tem dígitos ou "?" | mesmo teste (regex) | caractere fora de dígito, leitura que falha | passou |
| Regressão da trava (fila, status, orfã, links, modo) | os 33 testes de `test_pre_push_trava`, rodados no vermelho (coluna H) | n/a | todos ok no HEAD |

## Cenários e resultado real
**Vermelho antes do verde** (`bin/forge-testes --vermelho 234dbe0fb90b005450d7c2eb59e6241ea9779155`, rc=0, 62 min por causa da carga):
```
vermelho: base=234dbe0fb90b head=01ae5742b90c
revertidos à base: .githooks/pre-push, changelog.d/impl-pre-push-c5.md, docs/reviews/impl-pre-push.md
mantidos no HEAD: tests/test_pre_push_trava.py
tests.test_pre_push_trava.PrePushTrava.test_texto_da_trava_traz_o_namespace_depois_do_pid · H=ok · B=falha · prova (asserção)
contagem: não prova (passa na base)=2305; prova (asserção)=1; pulado=28
```
Nenhum teste cai no HEAD. Os 28 pulados são os mesmos H=pulado e B=pulado (shellcheck e lançadores sem a ferramenta neste ambiente, nada novo da c5).

**Mutação** (`bin/forge-mutante` sobre spec do QA, 4 mutantes, uma linha de guarda por mutante; o diff muda 2 linhas de shell: 243 e 244; rc=0):
```
forge-mutante: pedido=impl-pre-push rev=01ae5742b90c spec=181347877e286384659a680f7ba1ac8ca638c3bf3708a0c4e52e08c34ef40d3e
Q1 · morreu · .githooks/pre-push:244   (tira o campo ns)
Q2 · morreu · .githooks/pre-push:243   (tira o filtro de dígitos)
Q3 · morreu · .githooks/pre-push:244   (ns antes do pid)
Q4 · morreu · .githooks/pre-push:244   (tira o fallback "?")
```
Nenhum sobrevivente. Q4 morreu porque `readlink` falha dentro do sandbox e o campo fica vazio; fora dele a leitura funciona e o ramo "?" fica sem prova (A1, recomendado).

**M14 (agents/tech-lead.md:19):** cumpre. Linhas de código e teste: `.githooks/pre-push` 5 (4+1) e `tests/test_pre_push_trava.py` 11, total 16, abaixo de 150; fragmento e pareceres ficam fora. Um comportamento só (o texto gravado na trava); o C-14 saiu da branch.

**Limites do que rodei:** `shellcheck` não existe neste ambiente (o teste `test_shellcheck_no_hook` fica pulado aqui; o CI do PR o roda). A suíte completa fica no CI do PR (decisão do dono M8); rodei o filtro do `--vermelho`, que cobre todos os módulos afetados, sem falha no HEAD. Sem gatilho de segurança novo para o QA além do parecer de segurança já gravado; sem bugs abertos, sem acessibilidade (sem interface).
