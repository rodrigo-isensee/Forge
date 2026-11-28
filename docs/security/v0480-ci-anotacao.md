---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-ci-anotacao
commit: 3487d89164ca7a88c317a071707d168196fa08f3
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-23
---
# Review de segurança: v0478 (E137.15, PR #821, anotações da parte no CI)

Escopo: o diff `0e59c446..3487d891` (E137.2): `scripts/suite-partes.py:481-483` (uma linha de código, duas de comentário), um teste em `tests/test_suite_partes.py:398`, o mutante `tests/mutantes/v0480-ci-anotacao.json` e o fragmento `changelog.d/v0480-ci-anotacao.md`. Os commits posteriores (`cec59313`, `088d2e03`, `a54ddd67`) só trazem pareceres de devops, review e QA.

## Gatilhos
Gatilhos: CI (script que decide e emite anotações do check run da suíte)

## Só aperta ou neutro
**Neutro.** O `main` passa a ler uma cópia do ambiente tirada antes do discover, em vez da referência viva ao `os.environ`. Nenhuma regra, porta ou limite muda: o código de saída da parte não depende do `GITHUB_ACTIONS` (só a impressão das anotações, `scripts/suite-partes.py:232` e `:407`); `CI` (`:385`), `FORGE_SUITE_PULADOS` (`:405`) e o ambiente do filho (`:267`) leem os mesmos valores que o processo recebeu do workflow, agora sem a interferência de um módulo de teste importado. O isolamento do `tests/test_catraca.py:30` (tira `GITHUB_ACTIONS` para os testes) continua valendo para os testes, que seguem lendo o `os.environ`; a cópia só serve às decisões do próprio script.

## Achados

## Sondas

## Detalhe dos achados
Sem achado. Pontos conferidos:
- Injeção de comando de workflow pelas anotações que voltam a sair: o texto da falha passa por `escapar_dado` e o título por `TITULO_SEGURO` (`scripts/suite-partes.py:226-227`), controles já existentes e não tocados; as anotações de tempos só levam ids de unidade e durações. Um PR de fork que quisesse emitir `::` já poderia fazê-lo pelo stdout de um teste próprio; o item não abre canal novo.
- Segredos: a cópia é um `dict` em memória, sem gravação nem impressão; o ambiente repassado ao filho (`:267`) é o mesmo de antes.
- Cópia rasa tirada na entrada de `main`, antes de qualquer `discover`: sem janela em que um import altere o que o script decide.

## Provas
- `python3 -m unittest tests.test_suite_partes.Brinquedo5.test_modulo_que_tira_github_actions_no_import_nao_cala_as_anotacoes`: `Ran 1 test ... OK`.
- `python3 -m unittest tests.test_suite_partes` (módulo tocado): `Ran 50 tests ... OK`.
- Mutante M1 morto: conferido no parecer de QA (`docs/qa/v0480-ci-anotacao.md`) e no de review, não refeito.
- Suíte inteira: só no CI. No momento da leitura, os check-runs de `3487d891` e `088d2e03` estavam cancelados pelos envios de parecer e o de `a54ddd67` na fila; a aprovação vale para o conteúdo de segurança, e o merge segue condicionado à bateria verde no head final (portão do CI, não deste parecer).

## Riscos aceitos e ferramentas
Sem risco aceito. Ferramentas: leitura do diff, `gh api` (check-runs) e os testes do módulo. Não usadas por não se aplicarem ao diff: `gitleaks`, `zizmor`, `actionlint` (nenhum workflow nem segredo tocado).
