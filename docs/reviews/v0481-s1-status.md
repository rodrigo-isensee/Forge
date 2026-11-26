---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-s1-status
commit: 0b412b4a210a147c26fb53074f698f6b50b39ab5
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-26
---
# Review: v0481 S1a, `forge-check status` (PR #910, E20.3, 1.ª rodada)

Escopo: `8ae4d6c6..0b412b4a` (merge-base com a `develop`): `bin/forge_estado.py` (novo, 135 linhas), `bin/forge-check` (subcomando `status`, 10 linhas), `bin/forge-testes` (ESCOPO+ E20.2: módulo no FORGE_CHECK e mapa do `forge-contador`), `tests/pesos-d4.json`, `tests/test_forge_status_estado.py` (19 testes), 4 specs de mutantes (32) e o fragmento `changelog.d/v0481-s1-status.md`. Tamanho: 148 linhas de código, dentro do teto H1.

## Como foi verificado
- `python3 -m unittest tests.test_forge_status_estado` no head: 19 testes, OK.
- `bin/forge-mutante --processos 1 tests/mutantes/v0481-s1-status*.json`: 32 de 32 mortos. `--cobertura --base 8ae4d6c6`: toda guarda coberta; só `tests/pesos-d4.json` fora (dado, sem guarda).
- Só leitura e sem rede além de leitura: o status chama `gh api .../commits/develop` (GET), `gh pr list`, `gh release view`, o `forge-contador` (só `git` de leitura) e `forge_dono.cmd_abertas` (só leitura, recusa link). Nada grava. A saída passa pelo `seguro` do forge-check.
- Os testes usam gh falso: `ctx()` injeta `gh_json` falso, e o `PeloForgeCheck` põe `pasta_com_gh()` no PATH, com HOME temporário, ambiente limpo e `-I`.
- CI do head lido em `gh pr checks 910`: parte 3/5 vermelha em 3.12 e 3.14; causa no log abaixo (A1).

## Achados
- A1 (bloqueante) docs/indice-forge.md:42 · bin/forge_estado.py novo sem linha no índice: suíte parte 3/5 (3.12 e 3.14) vermelha, 3 falhas em test_indice_forge ("desatualizado; rode scripts/indice-forge.py", job 139933654051). Rode scripts/indice-forge.py e commite o índice.
- A2 (bloqueante) bin/forge_estado.py:100 · fromisoformat sem guarda: pergunta ao dono com data inválida (2026-02-30) derruba o status com ValueError, rc 1, sem as linhas 5 e 6 (S1). O requisito pede `não verificável` e rc 0. Converter o ValueError em NaoVerificavel, com mutante e teste do ramo.
- A3 (recomendado) bin/forge_estado.py:100 · a hora da pergunta, sem fuso, recebe o fuso de `agora`; sem `--agora` vale o fuso da máquina, e a idade muda conforme o fuso do container. Declarar o fuso do registro e convertê-lo.

## Sondas
- S1 · pedido com `- PERGUNTA AO DONO (2026-02-30 09:00): A ou B?` e `forge-check --raiz <tmp> status --agora 2026-11-26T12:00-03:00` · espera: rc 0, seis linhas, decisões `não verificável (...)` · obtido: rc 1, três linhas e traceback `ValueError: day is out of range for month` em forge_estado.py:100

## Parecer
Reprovado. O desenho está bom: módulo pequeno, uma função por linha, a falha de leitura vira `não verificável`, o relógio entra por argumento e os testes cobrem cada guarda com o ramo de falha. Os dois bloqueantes têm prova. A1 deixa o CI vermelho por causa do índice gerado, que não foi atualizado. A2 é uma linha sem guarda que viola o "nunca erro: rc 0" do próprio contrato. Quando os dois forem corrigidos, a revalidação lê só o delta.

- ci: 0b412b4a210a147c26fb53074f698f6b50b39ab5 vermelho (suíte parte 3/5 em 3.12 e 3.14: test_indice_forge, A1; partes 1/5 e 4/5 ainda pendentes na leitura; `bateria (pareceres)` e `catraca` esperam o parecer e o rótulo)
