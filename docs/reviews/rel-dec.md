---
tipo: review
contrato: 1
pedido: rel-dec
branch: melhoria/rel-dec
commit: 767f38738032796b9de22b05a81d91b1258e4bec
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-28
---
# Review: rel-dec (REL-R4 e REL-D1A)

Rodada 2, revalidação por delta sobre o parecer anterior (commit `fcc5980ee53f58cb021b7c96e19ca81d712d07e8`, gravado em `41ef3a5`).

Delta lido: `forge-check delta --parecer docs/reviews/rel-dec.md` = `fcc5980..767f387`: `agents/tech-lead.md:32`, `docs/promocao-integrador.md:16,18,20`, `docs/regras/R-FLUXO.md:13`, `scripts/promover-homolog.py:18-19,242-245,261-264`, `tests/config.json:415`, `tests/test_promover_homolog.py:260-267,285-291`. Já lido na rodada 1 e não relido: o resto do diff `ed7fbd8...fcc5980` (REL-R4 em `R-FLUXO.md:27` e `tech-lead.md:29`, as 3 invariantes trocadas, o fragmento `changelog.d/rel-dec.md`). Os pareceres de QA e de segurança que entraram no intervalo não são revisados aqui.

## Achados
- A4 (recomendado) docs/regras/R-FLUXO.md:27 · "só na hora do merge (git fetch + merge da develop)" soa como merge sempre; o forge-fechar só pede o merge com arquivo em comum; fica fora desta volta (decisão técnica de 2026-10-28 10:22)
- A6 (recomendado) scripts/promover-homolog.py:217 · a descrição do passo 5 no --dry-run ainda diz "pendente sai com 3"; com a volta 2, pendente imprime o comando --auto e sai com 0 (docs/promocao-integrador.md:16)

## Revalidação dos achados da rodada 1
- A1 (bloqueante): resolvido. `scripts/promover-homolog.py:242-245` (nenhum check ainda) e `:261-264` (pendente, catraca sem pedir rótulo) imprimem `gh pr merge develop --auto --merge --match-head-commit <sha>` e saem com 0; vermelho segue parando com 1 (`:248`). Testes novos: `test_check_pendente_imprime_o_merge_automatico_sem_mesclar` e `test_sem_checks_ainda_imprime_o_merge_automatico` conferem o comando com o sha da `origin/develop` e que o `gh` falso não recebeu `pr merge`. O caso da catraca pedindo o rótulo segue com 3 e sem o comando: o merge automático esperaria a catraca obrigatória de qualquer jeito, então é escolha aceitável, não defeito.
- A2 (bloqueante): sai pela decisão do dono de 2026-10-28 10:15 (o dono põe `bateria (python 3.14)` nos checks obrigatórios do ruleset da `homolog`); sem mudança de texto, como a decisão manda. Pendência de configuração do dono, não do código.
- A3 (recomendado): resolvido. `R-FLUXO.md:13` traz o comando com `--match-head-commit <sha>`, `tech-lead.md:32` cita o comando da `R-FLUXO` e `docs/promocao-integrador.md:18` traz o mesmo comando.
- A5 (recomendado): resolvido. `tests/config.json:415` acrescenta a invariante do limite do merge automático à `homolog` (a frase de `R-FLUXO.md:13`, citada pelo ID, não copiada); só acrescentada, nenhuma invariante removida.
- A4: segue como recomendação, fora desta volta.

## Parecer
Aprovado. Os dois bloqueantes saíram (A1 pelo código e pelo teste, A2 pela decisão do dono) e os recomendados A3 e A5 entraram. O A6 é texto de ajuda do `--dry-run` e não devolve.

O que confere no delta:
- Código de saída documentado igual nos dois lugares (docstring `scripts/promover-homolog.py:18-19`, `docs/promocao-integrador.md:20`): 0 para armar o merge automático, 1 parou (inclui vermelho), 3 só para o rótulo do dono.
- O script continua sem mesclar nem aplicar rótulo; o `--match-head-commit` prende o sha conferido.
- Testes do item: `python3 -m unittest tests.test_promover_homolog` (25 OK); `python3 -m unittest tests.test_forge.RegrasInviolaveis tests.test_forge.GuiaDaPromocao` (OK). A suíte completa fica no pre-push e no CI.
- Teto M14 (`git diff --numstat --no-renames ed7fbd8...767f387`): `scripts/` 14+10, `tests/config.json` 4+3, `tests/*.py` 11+6 = 48 linhas, abaixo de 400; sem `hooks/` nem caminho de `PROTEGIDOS`.
- Commits: `fix(promocao)` e `test(fluxo)`, em Conventional Commits, um por achado.
- Achados recorrentes (`docs/engineering/achados-recorrentes.md`): nenhuma classe repetida; nenhuma linha AR nova.

O PR precisa do destaque no título e do rótulo `afrouxa-regra` (decisão do dono de 09:10; invariantes trocadas).

Segurança e QA: pareceres próprios (E2.1 e E3.1, em paralelo), não refeitos aqui.
