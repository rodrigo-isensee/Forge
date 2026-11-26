---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-d2-no-brief
commit: 6c2bbf42d868a13c8a6344c440789aa562ed5022
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-26
---
# Review: v0481 (E14.83, #903, D2-NO-BRIEF; classe C), revalidação por delta

Rodada anterior: aprovado em `7cacc94c` (E14.69, commit do parecer `fe150b0d`), com A1 a A3 recomendados. Esta rodada lê só o delta, como manda a ordem do dono de 25/11.

## Delta lido
- `forge-check parecer delta docs/reviews/v0481-d2-no-brief.md`: intervalo `7cacc94c..6c2bbf42`. No domínio: `agents/jarvis.md`, `bin/forge-check`, `changelog.d/v0481-d2-no-brief.md`, `docs/regras/R-FLUXO.md`, `skills/briefs-e-conferencia/SKILL.md`, `skills/briefs-e-conferencia/conferencia-da-entrega.md` (novo), `skills/trabalho-em-paralelo/ritmo-e-corte.md`, as duas specs de mutante e `tests/test_forge_pronto.py`, `tests/test_pre_envio_brief.py` e `tests/test_selo_e_entrega.py`. Ficam de fora os pareceres de QA e de segurança, que não são do meu domínio.
- Já lido em `7cacc94c`, sem mudança: `bin/forge_pronto.py` e o resto do `bin/forge-check`.

## Correção (E14.81)
- `bin/forge-check:10626-10627`: a conferência lê no head, pelo `git cat-file -e`, se há `.claude-plugin/plugin.json` e se falta `.forge/versao`. Com isso decide se o head é do Forge, mesmo sem cópia em disco.
- `bin/forge-check:10453`: sem pasta, com o head do Forge e sem `--so-leitura`, a conferência reprova e pede `--worktree`. No `--so-leitura` e no projeto, a linha só informa, como antes. Isso fecha o caminho em que a cópia do autor era um clone e o D2 não rodava sem reprovar.
- O caso `pasta=None` de `ProvaDoPronto` foi invertido como pedido: `test_sem_worktree_com_o_head_no_forge_reprova_pedindo_worktree` testa os dois ramos (reprova, e não reprova no `--so-leitura`). O teste de ponta a ponta `Entrega.test_sem_worktree_com_o_head_no_forge_nao_cumpre` mostra que a entrega não é gravada e que um projeto com o manifesto e o `.forge/versao` só recebe a linha informativa.
- **Guardas e mutantes (V2):** são 3 linhas de guarda mudadas, com 4 mutantes. Rodados no head com `bin/forge-mutante --processos 1`: M14, M15 e M16 (`:10453`, `:10453`, `:10627`) morreram, e M17 (`-3.json`, `:10626`) também. O M9, realinhado ao teste renomeado, morreu (`:10455`). `--cobertura --base 7cacc94c` deu as 3 linhas cobertas.
- **Testes do diff:** `python3 -m unittest tests.test_forge_pronto.ProvaDoPronto` mais os dois testes novos e mudados de `test_pre_envio_brief` e `test_selo_e_entrega`: 7 testes, OK.
- **Tamanho (H1):** cerca de 10 linhas de código em `bin/`. É o mesmo comportamento do item.

## Mudanças extras (ESCOPO+ E14.82): ficam ou saem
- **A1 da rodada anterior, fica.** São o `--worktree` em `agents/jarvis.md:30` e em `skills/briefs-e-conferencia/SKILL.md:19`, e o arquivo novo `conferencia-da-entrega.md`. A correção passa a exigir `--worktree` quando a cópia é um clone, e sem a receita o Jarvis cairia no `pendente:` novo. O arquivo também resolve o A1 antigo (a conferência em segundo plano, com log até `rc=`). Os cortes de palavras no jarvis.md não mudam o sentido: "numa passada" já está coberto por "em paralelo, no mesmo head". Os invariantes de `tests/config.json` continuam presentes.
- **A2 da rodada anterior, fica.** A PQ do D2 (`bin/forge-check:9718`) agora manda rodar o forge-check de um clone da develop com `--raiz`, e não o da branch. São 2 linhas de texto, com asserção em `tests/test_pre_envio_brief.py:101`.
- **A3 da rodada anterior, fica, com o cuidado de afrouxa.** A linha "salvo conflito, dependência ou base velha" (`docs/regras/R-FLUXO.md:26`) abre mais uma exceção ao "só na hora do merge" e, portanto, afrouxa a regra. Fica porque o pronto aprovado em `7cacc94c` já obriga a trazer a base velha, e sem a exceção a regra e a ferramenta se contradizem.
  - O invariante `**Atualize a branch com a integração só na hora do merge**` está intacto.
  - A medida e o critério de revisão estão em `ritmo-e-corte.md:21` (R-DECISAO).
  - O título do PR #903 ainda não traz o destaque que o CLAUDE.md exige para afrouxar uma regra. Corrijo isso no texto do PR antes do merge, que é papel meu: `[afrouxa-regra: R-FLUXO base velha]` no título e o motivo no corpo. Não precisa de commit nem de nova rodada.
- `docs/regras/R-FLUXO.md:23`, linha "No projeto": é só um corte de palavras e fica. O sentido se mantém.

## CI do head
Runs 45763465510 e 45763465454, em `6c2bbf42`, estão verdes: as 10 partes da suíte em 3.12 e 3.14, os passos, a bateria em 3.14, as verificações longas, a instalação, os dois tetos de pulados e a árvore provada. Ficam de fora três jobs, que esperam um parecer ou o rótulo:
- `bateria (pareceres)`: pelo log, falta este parecer no head e os de QA e segurança aprovados.
- `bateria`: agrega a de pareceres (`pareceres: failure`, o resto em `success`).
- `catraca`: R-CONFORMIDADE por mudança em `bin/forge-check`, que pede o rótulo `afrouxa-regra` do dono.
- ci: 6c2bbf42d868a13c8a6344c440789aa562ed5022 verde

## Achados
- A1 (recomendado) agents/tech-lead.md:34 · ainda diz "salvo conflito ou dependência", sem a exceção de base velha que o R-FLUXO ganhou; o mesmo em skills/engineering-practices/SKILL.md:67. Alinhar os dois resumos ao R-FLUXO:26.

## Parecer
**Aprovado** no head `6c2bbf42`. A correção E14.81 fecha o caso sem worktree, com teste dos dois ramos e os 4 mutantes novos mortos, e o M9 realinhado também morreu. As três mudanças extras ficam. A do R-FLUXO afrouxa a regra e entra com o destaque no título do PR, que eu aplico antes do merge. O A1 é recomendado e vira cartão depois do merge. Para o merge faltam os pareceres de QA e de segurança aprovados neste head e o rótulo do dono, que a catraca exige.
