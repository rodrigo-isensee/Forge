---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-promover-sem-auto
commit: a438dcc37ffd41ea37bd580521824fd217fd300b
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-22
---
# Review: v0478 · E118.3 · PROMOVER-SEM-AUTO-MERGE

Diff `38c37de9..a438dcc3`: `scripts/promover-homolog.py`, `docs/promocao-integrador.md`, `tests/test_promover_homolog.py`, specs de mutante e fragmento do changelog.

## Achados
- A1 (recomendado) docs/regras/R-FLUXO.md:16 · a regra ainda diz que a homolog é promovida por PR com merge automático, o oposto do script e do guia novos e da ordem permanente do dono (21/11 20:15); cartão para alinhar o texto da regra (R-DECISAO), fora deste diff.
- A2 (recomendado) scripts/promover-homolog.py:306 · os obrigatórios vêm só do piso CHECKS_EXIGIDOS; um check exigido pelo ruleset da homolog que ainda não apareceu não entra em `faltam`. O GitHub segura o merge, mas não a conta com bypass; cartão para ler também os exigidos do destino.

## Conferência
- Requisito (ordem do dono de 21/11 20:15 e 22/11 06:01, merge automático proibido): nenhum caminho imprime `--auto`; o merge direto sai só com cada obrigatório em `pass` no evento `pull_request` e fica preso ao head (`--match-head-commit`). Pendente, sem check ou obrigatório ausente saem com 4, sem comando de merge; `skipping` num obrigatório para com 1.
- Fonte única: a lista é lida do `bin/forge-fechar` (`CHECKS_EXIGIDOS`, linha 97), sem cópia. Se a lista falta, está vazia ou o arquivo não se lê, a leitura para (falha fechada); uma lista em várias linhas também para, nunca libera.
- Código: funções pequenas, `esperar_checks` ficou sem os parâmetros que não usava, sem código morto. Docstring, guia (passo 5, passo 7, códigos de saída, seção Teste) e changelog estão em dia com o comportamento.
- Testes: pendente, sem check, só push, obrigatório ausente, obrigatório pulado, lista ausente, vazia ou ilegível e nenhum `--auto` em todos os caminhos, dry-run incluído. Os falsos de `gh` usam o nome exato do check, a mesma regra do script (item 12).
- Mutantes: M1 a M8 e M9 e M10, um por guarda; a cobertura do diff não tem guarda sem mutante; o M2 antigo (`--auto`) saiu de `promover-auto.json` junto com a guarda que ele protegia, de propósito.

## Provas
- `python3 -m unittest tests.test_promover_homolog` (ambiente limpo): `Ran 47 tests ... OK`.
- `bin/forge-mutante --cobertura --base 38c37de9`: só linhas `coberta`, mais `spec editada · tests/mutantes/promover-auto.json` (remoção do M2, explicada acima).
- `bin/forge-mutante --conferir --base 38c37de9`: `conferidas: o trecho de cada spec do diff está no lugar`.
- `bin/forge-mutante --ids M10,M8`: `M10 · morreu · :323`, `M8 · morreu · :311`. A rodada completa das specs fica com o QA (E118.4). A suíte inteira roda no CI do PR.

## Parecer
Aprovado. O item faz o que o pedido pede e só aperta: o merge automático sai de todos os caminhos, e o merge direto exige a lista de obrigatórios da fonte única. A1 e A2 viram cartões depois do merge. A remoção do M2 em `promover-auto.json` pode fazer a catraca pedir rótulo; isso fica com a segurança e o dono, não com este parecer.
