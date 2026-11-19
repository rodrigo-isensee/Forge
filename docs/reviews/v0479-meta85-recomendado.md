---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-meta85-recomendado
commit: eba8b7d01c0dd892615d9846c97c8eeb17dd6f34
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-19
---
# Review: v0478 E35.2 e E35.8 (META85-RECOMENDADO-VIRA-CARTAO, head eba8b7d0)

Lido: `git diff eca1d21b..cdea2f38` (17 arquivos, só texto, `tests/config.json` e um teste). Ordem do dono (pedido v0478, E35): recomendado de review e QA vira cartão depois do merge; o de segurança é corrigido antes.

## Consistência
- A regra mora em `R-REVIEW` (a frase do recomendado, agora invariante; cito o ID, R-REVIEW e R-SEGURANCA) e chega igual ao Jarvis (passo 6), aos três portões, a `R-SEGURANCA`, à skill do brief de volta (`--incluir <parecer>:A<n>` só para a segurança, opção que o `forge-check brief gerar --volta` já tem), ao `trabalho-em-paralelo` e aos modelos de parecer de review, QA e segurança (projeto e Forge).
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

## Revalidação E35.8 (head eba8b7d0)
Lido só `forge-check parecer delta` (cdea2f38..eba8b7d0, 6 arquivos no domínio). O detalhe do rigor por classe e de quem acha os gatilhos sai de `R-REVIEW` e `R-SEGURANCA` para `skills/engineering-practices/rigor-por-classe.md`; a cópia de `forge-copia clone --instalar` vai para `ritmo-e-corte.md`; o brief de volta cita a revalidação sem repetir `R-REVIEW`. Nada some: cada trecho tirado está no arquivo de destino citado pela regra.
- `python3 -m unittest tests.test_metricas_texto`: 2 testes, OK.
- `python3 -m unittest test_forge.AntiDuplicacao` (em `tests/`): 2 testes, 1 falha, fora do domínio deste parecer: `docs/security/v0479-meta85-recomendado.md:25` copia a frase do recomendado de `R-REVIEW` (linha 16); conserto é do parecer de segurança (citar o ID). Este parecer, no domínio de código e testes, segue aprovado; o CI fica vermelho até esse conserto.
- Depois do merge de `fc05832a` (revalidação da segurança, E35.9, cita o ID): `test_forge.AntiDuplicacao` 2 testes, OK.

## Achados
- A1 (recomendado) templates/projeto/docs/devops/_modelo.md:17 · O recomendado do parecer de devops segue "não devolve" sem destino (nem cartão nem correção antes); alinhar ao review e QA (vira cartão) ou dizer o que vale, e citar no agents/devops-engineer.md.
- A2 (recomendado) docs/regras/R-REVIEW.md:14 · "Uma passada" diz que só os bloqueantes voltam no brief; o recomendado de segurança também volta (linha 16): "os bloqueantes e o recomendado da segurança voltam".

## Parecer
Aprovado. A regra está consistente nos textos que decidem a volta, nada protegido por teste foi cortado e o texto é neutro. A1 e A2 viram cartão depois do merge (META85).
