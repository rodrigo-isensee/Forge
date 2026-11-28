---
tipo: revisao-seguranca
contrato: 1
pedido: v048
branch: melhoria/v048-qa-testing-sob-demanda
commit: 87575570ef9ac5b24f09ab56e9f7354dab3a2987
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-28
---
# Review de segurança: v048 (QA-TESTING-SOB-DEMANDA, PR #958), 1ª rodada completa

Gatilhos: texto de controle da fábrica (teste-oráculo EXT-1 e mutantes declarados) em arquivo com invariantes (`skills/qa-testing/SKILL.md`).

Escopo lido: o diff inteiro contra a base 21aada57 (3 arquivos: `skills/qa-testing/SKILL.md`, `skills/qa-testing/referencia.md` novo, `changelog.d/v048-qa-testing-sob-demanda.md`). O diff não toca hook, `bin/`, `.githooks/`, workflow, `tests/` nem `docs/regras/`.

## Resultado
- **Regras com ID e invariantes:** nenhum ID de regra sai da SKILL.md (o único ID que some é o exemplo `CT-01`, que foi junto com o modelo para `referencia.md`); os 12 trechos de `invariantes` de `skills/qa-testing/SKILL.md` em `tests/config.json` seguem no head, incluídos os dois com motivo (prova de não edição do oráculo, com os três comandos, e a gravação da rodada longa em `relatorios/`). A prova de não edição do oráculo (`oraculo: <caminho> commit <sha40> blob <sha40>` e os três comandos) continua na SKILL.md:36, que é o que o meu papel e o QA conferem no parecer final.
- **Texto movido:** os dois modelos (plano e bug) e os dois itens do oráculo (onde e como, review) estão palavra por palavra em `referencia.md` (só a quebra de linha muda). No trecho do mutante, o equivalente é idêntico; nas saídas do `--cobertura`, `lista a condição ... ("declarado, não provado"; ...)` virou `a condição ... sai "declarado, não provado"; ...`: mesmo sentido, sem efeito de segurança; o QA já o registrou como A1 do parecer dele (fidelidade é do review e do QA, não deste portão).
- **Quando ler:** a SKILL.md diz quando ler cada seção (22: ao abrir o plano; 35: ao escrever o oráculo; 70 e 73: formato e saídas do equivalente e do `--cobertura`; 81: ao abrir o relatório). A exceção é A1: o gatilho da 35 não cobre o review do oráculo.
- **Orçamento:** medi com o `medir()` de `tests/test_orcamento_instrucao.py`: qa-engineer 21463 (base) -> 20068 (head), marcadores 41 -> 34, teto 21480.
- **Catraca e custo (ordem do dono 28/11 07:41):** o diff toca arquivo protegido por invariantes; catraca `--modo regras` contra a base rc 0 no meu clone; testes de custo (`test_brief_gerar_custo`, `test_doutor_custo`, `test_textos_ci_custo`, `test_forge -k test_custo`) OK no meu clone.
- **CI do head:** run 46142076201 e 46142076207 com `headSha` 87575570ef9ac5b24f09ab56e9f7354dab3a2987, todos os jobs obrigatórios verdes (5 partes da suíte, bateria, catraca, catraca conferência, instalação, teto de pulados).

## Mutações refeitas por mim (R-PROVA; restauradas, árvore limpa ao fim)
- Troquei o título `## Mutantes declarados nos pedidos de controle` na SKILL.md: `RegrasInviolaveis.test_trechos_obrigatorios` cai (FAIL no subteste do trecho). Restaurado: OK.
- Acrescentei 1500 caracteres à SKILL.md: `test_orcamento_instrucao` cai com `qa-engineer: total_caracteres = 21569 passa do teto 21480`. Restaurado: OK.
- Troquei o ponteiro `referencia.md` da linha 22 por um arquivo inexistente: `test_todo_caminho_citado_em_agentes_skills_e_regras_existe` segue verde (o ponteiro sem barra não é conferido). O ponteiro do head aponta para arquivo que existe; a lacuna do teste não é deste diff e vai como melhoria no relatório.

## Achados
- A1 (recomendado) skills/qa-testing/SKILL.md:35 · o gatilho de leitura diz só "ao escrever o oráculo", mas o review do oráculo (citar o sha, conferir os casos de abuso, não aprovar contra o próprio oráculo sem lê-lo) foi para referencia.md:30, que diz "ou ao revisar um"; quem revisa não é mandado ler.

## Sondas

## Detalhe dos achados
**A1.** Evidência: `skills/qa-testing/SKILL.md:35` termina em "ao escrever o oráculo"; `skills/qa-testing/referencia.md:30` diz "Leia ao escrever o oráculo (EXT-1, no Forge) ou ao revisar um", e a regra do review está em `referencia.md:37-38`. Antes do diff, essa regra estava no texto que o `qa-engineer` carrega sempre. Caminho: na rodada final, o QA que confere um oráculo (o dele ou o da segurança) segue o gatilho da SKILL.md, não abre `referencia.md` e aprova sem dizer se o oráculo cobre os casos de abuso; um oráculo fraco deixa passar a guarda que não cobre o abuso. Severidade: baixa (perde-se um passo de conferência; a prova de não edição continua carregada). Correção mínima: na SKILL.md:35, trocar "ao escrever o oráculo." por "ao escrever o oráculo ou ao revisar um." (cerca de 16 caracteres; o total fica perto de 20084, abaixo do teto 21480). Esforço: P. Dono: tech-lead (autor da E5.1). Recomendado da segurança: volta ao autor e é corrigido antes do merge.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Ferramentas: git, unittest da biblioteca padrão, `tests/catraca.py`, `gh` (leitura do CI). Lacuna: o varredor de segredos não está no PATH (o diff é só texto em markdown, sem configuração nem credencial).
