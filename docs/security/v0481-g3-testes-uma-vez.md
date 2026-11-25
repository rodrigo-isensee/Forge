---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-g3-testes-uma-vez
commit: 55f87ffd19d79ad27a20521c45ee65004521bc00
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-25
---
# Review de segurança: v0481 (E8.8, #893, G3 primeira fatia, revalidação por delta ef45eec5..55f87ffd; classe C)

## Sondas
- S1 · `gh pr checks 893` (head 55f87ffd, o Revisar-sha) · espera: verdes fora `bateria (pareceres)`, `bateria` e `catraca` · obtido: os três fail, os outros 17 pass (suíte 3.12 e 3.14 nas 5 partes, teto de pulados, bateria (passos), (python 3.14), (verificações longas), instalação, árvore)
- S2 · `bin/forge-mutante tests/mutantes/v0481-g3-testes-uma-vez.json tests/mutantes/v0481-g3-testes-uma-vez-2.json tests/mutantes/v0481-g3-testes-uma-vez-3.json --ids M5,M15,M16,M17,M18,M19` · espera: morrem · obtido: todos morreram (M19 por erro do teste declarado)
- S3 · `python3 <scratchpad>/sonda_forja.py <clone>` (parecer novo com `commit:` anterior à regra) · espera: não foge do portão · obtido: com código depois do `commit:`, `commit: desatualizado` (R-REVIEW); sem código depois e sem CI verde, PARECER-SO-COM-CI-VERDE
- S4 · `bin/forge-mutante --conferir --todas --rev` em 55f87ffd, ef45eec5 e 220ba3fa · espera: igual à base · obtido: as mesmas 26 linhas nos três (pendências antigas v0457 e z075)
- S5 · `python3 -m unittest tests.test_forge_check_pr tests.test_pre_envio_brief` · espera: OK · obtido: 89 testes, OK; `tests.test_forge -k nvariant -k eto -k Neutral`: 76 testes, OK
- S6 · invariantes de `tests/config.json` (todas as strings, como regex) contra skills/qa-testing e engineering-practices em ef45eec5 e no head · espera: nenhum some · obtido: 41 e 34 padrões casavam na base, todos seguem casando

## Parecer
Delta lido: bin/forge-check, as duas skills, tests/test_forge_check_pr.py, tests/test_pre_envio_brief.py, os mutantes e o fragmento. A1 da rodada anterior (checks vermelhos por construção): resolvido, ver abaixo.
- ci: 55f87ffd19d79ad27a20521c45ee65004521bc00 verde

## Gatilhos
Gatilhos: controle do portão de merge (`forge-check pr`, `--previo`, passo 1 do `forge-fechar`; R-REVIEW, R-QA, R-CONFORMIDADE), texto dos briefs de parecer e skills de portão.

## Detalhe dos achados
**A1 (anterior, bloqueante): resolvido.** `CHECKS_FORA_DA_LINHA_DO_CI` (bin/forge-check:2174) é só texto: entra no brief (:9652), no esqueleto (:3731), na violação (:2202) e nas skills (engineering-practices:54, qa-testing:46), e nada a usa para filtrar checks. O `checks_do_head` e os passos 4 e 6 do `forge-fechar` não mudaram e seguem exigindo todos os checks para o merge. O agregador `bateria` depende de `bateria (passos)`, `bateria (pareceres)`, `bateria (verificações longas)`, suíte 3.12 e teto 3.12 (.github/workflows/ci.yml:856), e cada um deles, fora `pareceres`, aparece com nome próprio no `gh pr checks`, de modo que tirar o agregador da linha não esconde nenhum check (S1). O `test_cada_check_e_um_job_dos_workflows` prende os nomes aos workflows.

**A3, transição (`cobra_a_linha_do_ci`, :2185-2190).**
- Não solta o que a develop barra hoje: o parecer isento só deixa de receber a violação `sem_ci`, que não existe na develop. Ele continua na PARECER-SO-COM-CI-VERDE inteira (`falta_na_prova` / CI do head; `test_commit_anterior_a_regra_segue_com_o_ci_verde_do_head`, S3), como na develop.
- Forjar um `commit:` antigo num parecer novo não fura o portão. O `commit_vale` (R-REVIEW) dá por desatualizado o parecer cujo `commit:` tem código do domínio mudado depois dele, fora o que veio da base (S3). Para fugir, o `commit:` precisa ser o patch da branch sobre uma base anterior à regra, que é justamente o caso legítimo da transição. O ganho máximo é cair na regra da develop, e quem escreve o parecer já poderia declarar uma `- ci:` falsa, que é texto (neutro, como na rodada anterior).
- Fecha por padrão: `commit:` ausente ou fora da forma hex (o `COMMIT` só aceita `[0-9a-f]{7,40}`, então não entra opção no `git grep`, M17, `--cached` no teste), sha inexistente ou sha curto ambíguo (rc 128) cobram a linha. Só o rc 1 isenta (M16). `-F -e` e o `--` antes do caminho isolam padrão e caminho.
- O resultado depende do texto `PARECER-LE-O-CI` em `bin/forge-check` no `commit:`, e esse texto só existe a partir do commit E8.1 desta branch.

**O que aperta, o que é neutro, o que afrouxa.**
- Aperta: nada de novo neste delta além do que já apertava na rodada anterior. A isenção fecha por padrão.
- Neutro: a exclusão dos três checks, porque é só texto, não filtra checks e o merge exige todos. A isenção de transição, porque o parecer isento fica exatamente na regra da develop. O enxugamento da qa-testing manteve a substância (o QA lê o `gh pr checks` do `commit:` e o teste novo vira achado ou commit do autor) e todas as invariantes (S6). A isenção fica permanente no código, mas perde efeito sozinha quando as branches abertas antes da regra fecharem, porque um parecer novo com `commit:` antigo cai em desatualizado.
- Afrouxa: nada contra a develop. Contra a rodada anterior, o review e o QA podem gravar `- ci:` com `catraca` vermelha sem saber se o vermelho é só o rótulo. O merge segue barrado por ela.

## Riscos aceitos e ferramentas
Nenhum risco aceito. gitleaks, zizmor, actionlint, semgrep e shellcheck não estão no PATH. O diff não toca workflow nem segredo.
