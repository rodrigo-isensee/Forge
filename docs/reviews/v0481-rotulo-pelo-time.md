---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-rotulo-pelo-time
commit: c58e140907dc71b44160b5bad0859321732048ac
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-26
---
# Review: v0481 (E24.7, #918, revalidação por delta: volta 1 e a develop trazida)

Delta lido: `forge-check parecer delta docs/reviews/v0481-rotulo-pelo-time.md`, intervalo `ab5871d1..c58e1409`, sem o que veio da base (merge da `develop` `707fea56`, sem conflito, merge-base = Base-sha). No domínio: `docs/adr/0018-autorizacao-do-dono-gravada.md` (1 linha) e `tests/test_autorizacao.py` (+25). Sem código de produção no delta, sem guarda mudada, sem mutante novo a declarar. Clone de revisão: `/root/.forge-contrib/wt/v0481-rotulo-pelo-time-tech-lead`, no head `c58e1409`. A 1.ª rodada (aprovada no `ab5871d1`) fica valendo para o resto do diff.

## CI e ferramentas (citadas, não refeitas)
- ci: c58e140907dc71b44160b5bad0859321732048ac verde
- `gh pr checks 918`, run `45867133788` com `headSha` = `c58e1409`: suíte 3.12 e 3.14 (5/5 cada), `bateria (passos)`, `bateria (python 3.14)`, `bateria (verificações longas)`, `instalação (python 3.14)`, `teto de pulados` (3.12 e 3.14), `árvore já provada na develop` e `catraca` verdes. Vermelhos que esperam este parecer: `bateria (pareceres)` e o agregado `bateria`.
- Teste do diff: `python3 -m unittest tests.test_autorizacao` com ambiente limpo (`env -i`) · 28 testes, OK; as duas sondas novas passam.

## Leitura do delta
1. ADR 0018:203: o estado da emenda agora diz que R1 só produz efeito depois do merge de R3 na `develop`; até lá a concessão pode estar ativa, mas o rótulo segue com o dono item a item. Fecha o A1 da segurança (469fa04) sem mudar código, e bate com o código: nenhum hook nem a catraca consome o ato `rotulo-pelo-time` (conferido na 1.ª rodada; o delta não toca `bin/`).
2. Sondas S1 e S2 da segurança viraram testes em `RotuloPeloTime`, com raiz temporária própria (`mkdtemp` + `addCleanup`) e o auxiliar `no_repositorio` (ambiente limpo, teto do git). S2 traz o controle (sem `.forge/versao`, o mesmo `origin` é o Forge). Determinísticos; a URL `file:///tmp/...` é só texto do `origin`, nada é escrito em `/tmp`.
3. Commit `fix(autorizacao)` em português com pedido e etapa; o merge da `develop` não toca o diff revisado.

## Achados
- A3 (recomendado) tests/test_autorizacao.py:478 · S1 fixa como esperado o defeito A1 da 1.ª rodada (host qualquer antes de `github.com` vale como o Forge). Quem fizer o cartão do A1 inverte este teste; dizer isso na docstring para ninguém ler o verde como garantia.

## Parecer
Aprovado no head `c58e1409`. A volta 1 faz o que o brief pede: a emenda segura R1 até R3 e as sondas da segurança ficam no corpus. A3 é recomendado e vira cartão junto do A1 depois do merge.
