---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-d2-no-brief
commit: 6c2bbf42d868a13c8a6344c440789aa562ed5022
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-26
---
# Review de segurança: v0481 (E14.85, #903, D2-NO-BRIEF, volta por delta)

## Gatilhos
Gatilhos: controle (bin/forge-check: conferência da entrega e PQ do D2 no brief, R-CONFORMIDADE), regra com ID (docs/regras/R-FLUXO.md).

## Lido
`forge-check parecer delta` de 7cacc94c a 6c2bbf42 (revalida: sim). No domínio: bin/forge-check, agents/jarvis.md, docs/regras/R-FLUXO.md, skills/briefs-e-conferencia (SKILL.md e conferencia-da-entrega.md, novo), skills/trabalho-em-paralelo/ritmo-e-corte.md. Fora: changelog.d, testes e specs de mutante (lidos só para conferir a correção).

## Achados anteriores
- A1 (bloqueante, 7cacc94c) resolvido. bin/forge-check:10626 lê `.claude-plugin/plugin.json` e `.forge/versao` do head pelo `git cat-file -e` (o head é sha40, sem injeção de opção), e bin/forge-check:10453, sem worktree, fora do `--so-leitura` e com o head no Forge, reprova pedindo `--worktree`. A forma documentada passa `--worktree` (agents/jarvis.md:30, skills/briefs-e-conferencia/SKILL.md:19). Prova: test_sem_worktree_com_o_head_no_forge_nao_cumpre (rc 1, nada gravado; projeto com `.forge/versao` só informa) e test_sem_worktree_com_o_head_no_forge_reprova_pedindo_worktree, que cobre as sondas S1 a S3 da rodada anterior; mutantes M14 a M17 e M9 morrem.

## Mudanças extras (ESCOPO+ E14.82): ficam ou saem
- `--worktree` em agents/jarvis.md:30 e na skill (com conferencia-da-entrega.md): **fica**. É a outra metade da correção mínima do A1. As opções `--sem-gravar` e `--so-leitura` foram movidas para o arquivo novo, sem mudar de sentido.
- PQ do D2 com o forge-check de um clone da develop (bin/forge-check:9718): **fica**. Aperta: o forge-check da branch deixa de certificar o próprio portão.
- Exceção "base velha" no R-FLUXO (docs/regras/R-FLUXO.md:26) com a medida em ritmo-e-corte.md:21: **fica**. Para a segurança é neutra. Como regra, afrouxa: ver abaixo.
- Cortes de palavras ("numa passada", "por volta ou conflito", "padrão"): **ficam**. São neutros, e nenhum é trecho de `invariantes` (tests/config.json); o invariante "Atualize a branch com a integração só na hora do merge" continua.

## O que aperta, o que é neutro, o que afrouxa
**Aperta:**
- Sem worktree, a conferência da etapa codigo no Forge não cumpre e pede `--worktree` (bin/forge-check:10453). Antes, ela cumpria com o D2 sem rodar.
- O jarvis.md e a skill mandam passar `--worktree <cópia>`, então o D2 roda de fato na cópia do autor.
- A PQ do D2 usa o forge-check do clone da develop (bin/forge-check:9718), e não o da branch.

**Neutro:**
- Um head com `.forge/versao` é tratado como projeto e, sem worktree, só informa. Uma branch do Forge que o crie pula o D2 nesse caminho, mas o arquivo aparece no diff. Com `--worktree`, o critério continua sendo o manifesto na cópia. É análogo ao manifesto apagado, que já era neutro na rodada anterior.
- O `--worktree` aponta para a cópia do autor, que precisa estar no head e limpa (estado_da_worktree, sem mudança). Rodar ali código da branch já acontecia com as PQ cmd.
- O arquivo novo da skill e os cortes de palavras não mudam nenhum sentido.
- A segunda linha que reprova quando a worktree está fora do head ou suja é só redundância e não muda o resultado.

**Afrouxa:**
- R-FLUXO (docs/regras/R-FLUXO.md:26): "salvo conflito ou dependência" passou a "salvo conflito, dependência ou base velha". Isso amplia os casos em que a branch traz a integração antes do merge, então é um afrouxamento de texto de regra com ID. Não tem efeito de segurança: trazer a base pelo merge de sempre não pula hook nem portão, merge sem conflito não invalida parecer, e o conflito invalida por domínio (R-REVIEW, mesmo parágrafo). É também a consequência do aperto do próprio item (o pronto recusa base velha, bin/forge_pronto.py:51): sem a exceção, regra e ferramenta se contradizem. Por ser afrouxamento de regra, a decisão é do dono (R-DECISAO, R-CONFORMIDADE). O PR já depende do rótulo `afrouxa-regra` dele pelo bin/forge-check (Catraca 45763465454), e o título ou o corpo do PR deve citar também essa exceção e o motivo. O critério de revisão está em ritmo-e-corte.md:21 (mais de 1 volta por item leva ao dono a troca por conferir a marca só no merge).

## CI e testes
- ci: 6c2bbf42d868a13c8a6344c440789aa562ed5022 verde
- Run 45763465510: suíte 3.12 e 3.14 (partes 1 a 5), bateria (passos), verificações longas, instalação 3.14, teto de pulados e árvore provada verdes. Vermelhos: bateria (pareceres), pela falta dos pareceres deste head (R-REVIEW, R-QA, log do job), e a agregada só por ela. A Catraca (45763465454) está vermelha porque o bin/forge-check exige o rótulo `afrouxa-regra` do dono, não por defeito.
- Local, no clone em 6c2bbf42: `python3 -m unittest tests.test_forge_pronto tests.test_pre_envio_brief tests.test_selo_e_entrega` rodou 237 testes, OK; `bin/forge-mutante tests/mutantes/v0481-d2-no-brief-3.json tests/mutantes/v0481-d2-no-brief-2.json` matou M9 a M17.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas usadas: o delta do parecer, os módulos tocados e os mutantes das duas specs tocadas. gitleaks e o varredor de workflows não se aplicam, porque o delta não tem segredo nem workflow.
