---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-meta85-recomendado
commit: cdea2f3807f456c317365703ce96398ce5cea80d
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-19
---
# Review: v0478 E35.2 (META85-RECOMENDADO-VIRA-CARTAO, head cdea2f38)

Lido: `git diff eca1d21b..cdea2f38` (17 arquivos, só texto, `tests/config.json` e um teste). Ordem do dono (pedido v0478, E35): recomendado de review e QA vira cartão depois do merge; o de segurança é corrigido antes.

## Consistência
- A regra mora em `R-REVIEW` ("a de review e QA vira cartão depois do merge; a de segurança é corrigida antes", agora invariante) e chega igual ao Jarvis (passo 6), aos três portões, a `R-SEGURANCA`, à skill do brief de volta (`--incluir <parecer>:A<n>` só para a segurança, opção que o `forge-check brief gerar --volta` já tem), ao `trabalho-em-paralelo` e aos modelos de parecer de review, QA e segurança (projeto e Forge).
- Lacuna: o parecer de devops (A1) ficou com o texto antigo, sem destino para o recomendado.

## Cortes para caber no orçamento
Os trechos retirados ("o hook `agentes` avisa", "teto que o `forge-check docs` e o pre-push barram", "uma linha por achado" no tech-lead, o caminho `test_erros_por_papel.py`, "como no review", `(R-REVIEW)` no `R-WIP`) não estão em `invariantes` nem em teste: busca no `tests/`, `hooks/` e `bin/` da base sem ocorrência. As 2 frases novas em `invariantes` entram e nenhuma sai; todas as invariantes da head casam (script sobre `tests/config.json`).

## Comandos (head cdea2f38, cópia por `git archive`)
- `python3 -I tests/test_achado_teto_doc.py`: 8 testes, OK.
- Mutantes: tirar ", o de segurança volta" do passo 6 do Jarvis e trocar "salvo a de segurança" por "nem a de segurança" no `autor-ate-o-merge.md`: 2 falhas, os dois mortos.
- `python3 -I tests/test_jarvis_nucleo.py` (teto de caracteres do Jarvis): 43 testes, OK.
- `python3 -I tests/neutralidade.py`: rc=0. Neutro: nenhum nome de projeto, stack ou regra de negócio.
- Suíte inteira: no CI do PR (`forge-testes --listar` pede a completa, `tests/config.json` mudou).
- H1: 0 linhas de código; um comportamento.

Gatilho: nenhum.

## Achados
- A1 (recomendado) templates/projeto/docs/devops/_modelo.md:17 · O recomendado do parecer de devops segue "não devolve" sem destino (nem cartão nem correção antes); alinhar ao review e QA (vira cartão) ou dizer o que vale, e citar no agents/devops-engineer.md.
- A2 (recomendado) docs/regras/R-REVIEW.md:14 · "Uma passada" diz que só os bloqueantes voltam no brief; o recomendado de segurança também volta (linha 16): "os bloqueantes e o recomendado da segurança voltam".

## Parecer
Aprovado. A regra está consistente nos textos que decidem a volta, nada protegido por teste foi cortado e o texto é neutro. A1 e A2 viram cartão depois do merge (META85).
