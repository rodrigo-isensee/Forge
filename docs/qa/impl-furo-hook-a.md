---
tipo: qa
contrato: 1
pedido: impl-furo-hook-a
branch: melhoria/impl-furo-hook-a-a4
commit: 820043b91cfe0d1df1afaf3dcceafa92eaf999c3
parecer: reprovado
revisor: forge:qa-engineer
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-31
---
# QA: impl-furo-hook-a, branch a4 (A4 FC-SUBCOMANDO-HOOK)

Diff lido: 234dbe0..820043b. Item do pedido: E4/A4, o `conformidade` lê o subcomando do `forge-check` em todo papel (`anotar`, `brief --gravar`, `transcricao anonimizar`) e o destino passa pela política de caminhos. Código: `hooks/conformidade.py` +42 (`args_do_forge_check`, `forge_check_grava`, tabelas), `tests/test_hooks.py` +19, 22 fixtures novas, spec `tests/mutantes/impl-furo-hook-a-a4.json`, `docs/hooks.md`. M14 (`agents/tech-lead.md:19`): 61 linhas de código e teste, uma classe em `hooks/`. Cumpre. O comportamento está provado (testes e vermelho abaixo); o que reprova é a prova de mutação do pedido que toca `hooks/`.

## Achados
- A1 (bloqueante) tests/mutantes/impl-furo-hook-a-a4.json:1 · a spec ficou velha depois da volta do review: A4-m2, A4-m6 e A4-m7 saem "inválido" (trecho aparece 0 vezes), rc=2, sem veredito; as linhas 74, 76 e 77 de hooks/conformidade.py (guarda do interpretador) não têm mutante declarado
- A2 (bloqueante) hooks/conformidade.py:77 · mutante sobrevivente: trocar `if achados else None` por `if achados else args` passa em todos os testes do lote; interpretador sem forge-check na linha passaria a ser lido como forge-check. Falta teste (ex.: `python3 -X utf8 x.py anotar --tipo ...` libera) ou justificativa aceita

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| A4: `forge-check anotar` fora do papel só de leitura não forja a decisão do dono nem a linha conferida | fixtures `fc-anotar-*-dev-bloqueia` (direto, caminho, interpretador, `-X`, `-W`, env, `=`, abreviada, raiz antes do subcomando, opaco) | todas as formas de chamar; jarvis libera (`fc-anotar-jarvis-libera`) | passou |
| A4: `brief --gravar` (também abreviado) e saída do `transcricao anonimizar` seguem a política de caminhos | fixtures `fc-brief-gravar-*`, `fc-anonimizar-saida-*`; `fc-brief-sem-gravar-dev-libera`, `fc-pr-dev-libera`, `fc-sem-subcomando-dev-libera` | só grava com `--gravar`; destino livre libera | passou |
| A4: todo subcomando que grava está classificado | `test_a4_todo_subcomando_do_forge_check_que_grava_esta_classificado` | piso de 4 subcomandos; prefixo recusado | passou (OK) |
| A4: spec de mutantes declarada cobre cada linha de guarda | `bin/forge-mutante tests/mutantes/impl-furo-hook-a-a4.json` | cobertura "declarado, não provado" | falhou (rc=2, 3 inválidos; A1) |

## Cenários e resultado real
- Vermelho antes do verde (manual, cópia em `$TMPDIR` com `hooks/conformidade.py` da base e os testes do head): `test_fixtures_do_lote_furo_hook_a` falha em várias fixtures (`fc-anonimizar-saida-protegida`, `fc-anotar-atras-de-env`, `fc-anotar-com-igual`, `fc-anotar-dev`, `fc-anotar-opaco`, `fc-anotar-por-caminho`...), FAILED. Verde no head: OK. O `forge-testes --vermelho` sobre a suíte inteira estourou o prazo aqui, sem veredito.
- Mutação da spec do autor: `A4-m1 morreu :72`, `m3 :78`, `m4 :1012`, `m5 :1015`, `m8 :80`, `m9 :938`, `m10 :1005`, `m11 :1007`, `m12 :1008`, `m13 :1009` morreram; `A4-m2`, `A4-m6` e `A4-m7` inválidos (rc=2).
- Mutantes escritos pelo QA para as linhas sem mutante (spec em `$TMPDIR`, nada gravado no repositório): `:74` (trocar a condição do interpretador por `False`) morreu; `:76` (nome `forge-check_`) morreu; `:77` (`else args`) SOBREVIVEU. Daí o A2.
- `--cobertura --base 234dbe0` lista `sem mutante` em `:74`, `:76` e `:77`.
- Sem interface de usuário: acessibilidade e E2E não se aplicam.
- Para liberar: atualizar os 3 mutantes à forma atual do código, somar o mutante de `:77` com o teste que o mata, e rodar a spec até rc 0.
