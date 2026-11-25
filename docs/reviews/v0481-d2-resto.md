---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-d2-resto
commit: ec5c7040a3176579a18b8c2429a540ab7e2b44d6
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0481 (E11.10, #881, D2 `forge-check pronto`, primeira fatia; classe C)

Diff revisado: `30dde2189..ec5c7040a` (3 commits, 101 linhas de código pelo H1, abaixo do teto de 150). Não há parecer anterior de review nesta branch.

## O que foi conferido
- **Nenhuma checagem trocada nem afrouxada.** O diff só acrescenta: o subcomando `pronto` (`bin/forge-check`, `cmd_pronto` e o parser), o módulo `bin/forge_pronto.py`, o teste, o índice, o peso, o fragmento e as specs. A única linha mudada de código existente é a tupla `FORGE_CHECK` do `bin/forge-testes`, que ganha `test_forge_pronto` e não perde nenhum módulo. `pr`, `catraca`, `forge_tamanho` e `forge-testes` continuam como estavam; o `pronto` só os chama.
- **O rc 2 nunca vira aprovação.** No `cmd_pronto`, a base comum ilegível e o `--corpo` ilegível saem 2. No `conferir`, qualquer código diferente de 0 de uma checagem (o 2 do `forge-testes --afetados` ou do comando que não abre, também) entra em `reprovadas` e o resultado é 1. Sem corpo (sem `--corpo`, sem PR aberto, ou com o `gh` em erro), o resultado é 1, nunca 0. O pr-texto da catraca com rc diferente de 0 também reprova.
- **Mesma régua do CI.** O H1 usa `merge-base..HEAD`, o mesmo conjunto do `base...ref` do `pr`, com o mesmo `linhas_de_codigo`/`tem_motivo`/`aviso_de_linhas`. O pr-texto roda `tests/catraca.py --modo pr-texto` com `PR_BODY`, como no `catraca.yml`; a catraca só importa biblioteca padrão, então rodar com `-I` não muda nada.
- **Testes (checklist 7, 11, 12).** O `gh` falso confere o nome exato (`pr view develop`) e sai 3 em qualquer outra chamada. O subprocesso limpa `GIT_`, `FORGE_`, `GH_` e `GITHUB_`, passa por `sem_manutencao` e chama o Python com `-I`. O ramo de falha de cada guarda tem teste de comportamento, e nenhum teste lê o texto da fonte.
- **Mutantes.** `python3 -I bin/forge-mutante --processos 1` sobre as 3 specs: 18 de 18 morreram. `--cobertura --base 30dde2189`: rc 0, toda guarda com mutante declarado. Só `tests/pesos-d4.json` aparece como "não coberto", e é dado, não guarda. `python3 -m unittest tests.test_forge_mutante.ConferirTodas`: 4 OK. `forge-mutante --conferir --todas` sai rc 1 tanto na base quanto no head, com saída idêntica (26 linhas, specs antigas `v0457-escopo-ponto-3` e `z075-prepush-relogio`) e nenhuma linha das specs deste pedido: a branch não traz regressão.
- **Teste novo:** `python3 -m unittest tests.test_forge_pronto`: 14 OK.
- **CI:** não rerrodei a suíte, que roda no CI do #881. No head `ede4ac39` (este SHA mais o parecer de segurança), a suíte estava pendente. `catraca` e `bateria (pareceres)` estavam vermelhos à espera dos pareceres, o que é esperado num rascunho. O merge depende do CI verde.

## Achados
- A1 (recomendado) bin/forge-check:1240 · com o gh em erro (pr None, motivo), o corpo vira None e a saída diz "passe --corpo" com rc 1: não aprova, mas perde o motivo e não segue o rc 2 "não verificável" do próprio contrato; imprimir o motivo do pr_da_branch e sair 2.

## Sondas

## Parecer
Aprovado. O agregador faz o que o cartão pede: reúne as checagens que já existiam, sem regra nova e sem afrouxar nenhuma. Nenhum caminho de rc 2 ou de falha chega ao 0. A1 não bloqueia: o resultado continua sendo reprovar, só a mensagem e o código são imprecisos. Vira cartão depois do merge.
