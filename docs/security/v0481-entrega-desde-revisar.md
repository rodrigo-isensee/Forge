---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-entrega-desde-revisar
commit: c056f38d285c454744e3a343b705621d2cacda49
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-26
---
# Review de segurança: v0481 E16.1 (o Desde da entrega a partir do Revisar-sha), 1ª rodada completa

Escopo lido: `git diff 34ab6714..c056f38d` (merge-base com a develop): `bin/forge-check` (`desde_do_parecer_aprovado` e a chamada em `cmd_entrega_conferir`), `tests/test_selo_e_entrega.py` (`CicloDo878`, 12 testes), `tests/mutantes/v0481-entrega-desde-revisar*.json` (ED1 a ED12), `tests/pesos-d4.json`, o fragmento do changelog.

Gatilhos: controle do Forge (conferência de entrega do `forge-check`, R-SEGURANCA).

## Achados
- A1 (bloqueante) bin/forge-check:2732 · Parecer reprovado do Revisar-sha some da conta se, depois dele, for apagado, renomeado para `_*.md` ou gravado com `contrato: 0`: a conferência passa com Desde no revisado e o trecho fora do declarado não é relido (S1 a S4). Some `veredito_trocado` por tipo.

## Sondas
- S1 · python3 -I /root/.forge-contrib/wt/_sec78-v0481-desde-sonda.py <clone> (test_s1: ciclo do 878 com segurança reprovado no head) · espera: rc 1, fora do declarado docs/indice.md · obtido: rc=1, escopo: fora do declarado no brief "docs/indice.md" (controle)
- S2 · mesma sonda, test_s2: ciclo com segurança reprovado e, depois, o parecer regravado com `contrato: 0` (ainda reprovado) · espera: rc 1, Desde de sempre · obtido: rc=0, resultado: cumpriu, docs/indice.md fora do intervalo
- S3 · mesma sonda, test_s3: ciclo com segurança reprovado e, depois, `git mv docs/security/x.md docs/security/_x.md` · espera: rc 1, Desde de sempre · obtido: rc=0, resultado: cumpriu, _x.md aceito como anexo do portão
- S4 · mesma sonda, test_s4: ciclo com segurança reprovado e, depois, `git rm docs/security/x.md` · espera: rc 1, Desde de sempre · obtido: rc=0, resultado: cumpriu, docs/indice.md fora do intervalo

## Detalhe dos achados
**A1.** Evidência: `bin/forge-check:2732` monta a lista só com `documentos(raiz, tipo, head)` (que pula `README.md` e `_*.md`) e `validar_documento(...)[0]` (que devolve None para frontmatter ilegível e para `contrato: 0`); `bin/forge-check:2740` só vê o veredito de quem sobrou. O contrato da função (docstring e `test_parecer_nao_aprovado_mantem_o_desde_da_conferida`) é "todos os pareceres da branch e do pedido aprovados"; um reprovado do mesmo `commit:` escondido depois do Revisar-sha não entra na conta, e `commit_vale` aceita a mudança porque `docs/security/`, `docs/qa/` e `docs/reviews/` são LIVRES. Caminho: um agente com escrita na branch (o autor ou quem arruma a branch) tira o reprovado da árvore ou o desabilita; a `entrega conferida` do head é gravada com o Desde no commit que um portão reprovou, o trecho conferida..revisado (no S1, `docs/indice.md` fora do declarado) nunca é relido, e a linha gravada vira o Desde das voltas seguintes. O portão do merge (`forge-check pr`) segue exigindo os pareceres, por isso a severidade é média, mas é exatamente o caminho novo que solta o que deveria cair no Desde de sempre. Correção mínima: antes de devolver o revisado, para cada tipo de `PASTA_E_REGRA` (`review`, `qa`, `revisao-devops`, `revisao-seguranca`), `if veredito_trocado(raiz, revisado, head, None, revisado, "aprovado", branch, tipo): return None`; a função já lê todas as versões da pasta (subpastas, apagados, renomeados) de `revisado..head` com `--full-history` e falha fechada. Teste: os três casos S2, S3 e S4 em `CicloDo878` (rc 1 e `FORA_DO_878`) e um mutante que tire a linha. Esforço P. Dono: autor da E16.1 (dev do `forge-check`).

## O que aperta, o que é neutro, o que afrouxa
- **Aperta:** nada; a função só pode mover o Desde para a frente.
- **Neutro:** sem conferida anterior, None (`test_sem_conferida_anterior_nao_ha_desde_do_parecer`); `commit:` diferentes, review ausente, parecer não aprovado no head, revisado fora do head, na base ou atrás da conferida, sem brief selado de cada portão: Desde de sempre (testes da classe e mutantes ED1 a ED12); código depois do revisado devolve o Desde de sempre (`commit_vale` sem `dominio`, ED11), e tudo de revisado..head segue conferido; as provas PQ, a worktree e o `base_sha_como_desde` não mudam. Parecer de outra branch ou pedido vindo da develop não conta (teste próprio).
- **Afrouxa (decisão do dono, opção A):** o trecho conferida..revisado deixa de ser relido contra o escopo declarado do brief e contra o `pedido_na_entrega` (commit que toca `docs/pedidos/`); a garantia passa a ser a aprovação dos portões selados no revisado, que leem o diff inteiro da branch. Também move o Desde com só os portões presentes (review obrigatório): um portão de segurança ainda não pedido não o impede; o `forge-check pr` continua cobrando o parecer. **Afrouxa sem querer:** o A1.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Teste do módulo tocado: `python3 -m unittest tests.test_selo_e_entrega` (188 testes, OK); a sonda roda os 12 de `CicloDo878` verdes. Ferramentas: só leitura do diff e a sonda local; sem varredura externa.
- ci: c056f38d285c454744e3a343b705621d2cacda49 verde
CI no head exato: as 10 partes da suíte (3.12 e 3.14), `bateria (passos)`, `bateria (verificações longas)`, `bateria (python 3.14)`, `instalação (python 3.14)`, os tetos de pulados e `árvore já provada na develop` verdes. Vermelhos que não são do código: `bateria (pareceres)` (R-REVIEW: sem parecer aprovado de review no head), `bateria` (agrega o de pareceres) e `catraca` (R-CONTRIB: o corpo do PR sem `## Projeto de origem` e `## Como medir`).
