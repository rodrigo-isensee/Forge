---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-textos-correcao
commit: 061f0091bbe46b3936106595434fcc5d993233fc
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-15
---
# Review: v047 (lote DOC1, E2.157)

Escopo: `bf475209...061f0091`, dois commits do lote DOC1 (E2.74): `6d2bb403` (E8-TEXTO-ANTIGO, ADR 0012) e `061f0091` (CORRECAO-ANTES-DOS-PORTOES, skill `trabalho-em-paralelo` e ponteiro no `tech-lead`). Parecer completo: não havia parecer anterior. Revisor: instância que não fez a entrega.

Diff (numstat): `agents/tech-lead.md` 11/10, `skills/trabalho-em-paralelo/SKILL.md` 8/7, `docs/adr/0012-main-por-merge-commit.md` 2/2, `tests/test_textos_034.py` 26/0, `changelog.d/v047-textos-correcao.md` 5/0. Código e teste contados (M14): 26 linhas, dentro da orientação. Sem guarda nova (só texto e teste de texto), sem mutante a declarar.

## Verificação
- Itens do Entregar contra os commits: E8-TEXTO-ANTIGO em `6d2bb403`, CORRECAO-ANTES-DOS-PORTOES em `061f0091`; nenhum item sem commit.
- E8-TEXTO-ANTIGO: a conferência da ADR 0012 agora pede a regra "branch atualizada com a base" desmarcada no `portoes`, o que bate com o passo 8 de `docs/protecao-de-branch.md`; a nota da E8 diz que o `portoes` vale para as três branches, o que bate com o passo 4 do mesmo arquivo. Decisão da ADR intacta.
- Compactação do `tech-lead` e da skill: sem regra perdida; invariantes de `tests/config.json` conferidos por expressão nos dois arquivos (0 ausentes). `agents/tech-lead.md` fica com 8615 caracteres, igual ao teto `agente_caracteres` de `docs/regras/orcamento.json` (no limite, sem folga para o próximo texto).
- Testes do item, rodados no head 061f0091: `tests/test_textos_034.py` 9 OK; `tests/test_orcamento_instrucao.py` 8 OK; `tests/test_forge.py Orcamento Neutralidade` 5 OK; `tests/test_forge.py RegrasInviolaveis` 3 OK; `test_jarvis_nucleo`, `test_permissao_agentes_md`, `test_jarvis_n_jar_a` OK. Suíte completa: fica no CI do PR (ainda sem PR; sem CI a citar).
- Teste novo (checklist 11): o `assertNotIn` da ADR procura a frase antiga exata, que de fato sumiu; os dois testes da regra nova ancoram a linha e o ID `R-REVIEW`.

## Achados
- A1 (recomendado) skills/trabalho-em-paralelo/SKILL.md:15 · "toda, achado `recomendado` incluso" perdeu o objeto: o fragmento e o cartão dizem "correção que muda arquivo da branch". Sem ele, "toda" fica ambíguo; o teste não fixa o trecho. Sugestão: "toda correção que muda arquivo da branch".
- A2 (recomendado) agents/tech-lead.md:27 · "o item entra pronto na `develop`" troca o sentido de "entra quando fica pronto" (momento da integração contínua, `R-FLUXO`) por um estado. Sugestão: voltar a "quando fica pronto" e cortar o caractere em outra frase.
- A3 (recomendado) skills/trabalho-em-paralelo/SKILL.md:15 · a retro (C5) pede eval que acusa mudança após o último parecer, com métrica e revisão em 2026-11-20; entrou só regra em texto, sem medida nem vencimento (`R-DECISAO`). Sugestão: o cartão segue aberto para o eval.

## Sondas

## Parecer
Aprovado no head 061f0091. Os dois textos fazem o que o lote DOC1 pede, o texto da ADR 0012 bate com `docs/protecao-de-branch.md` e a compactação não tirou invariante nem passou do teto. Os três achados são recomendados e não devolvem: A1 e A2 são ajustes de redação (sentido perdido na compactação); A3 registra que a parte de eval do cartão CORRECAO-ANTES-DOS-PORTOES não está nesta entrega e não deve fechar o cartão. Sem bloqueante. Nenhuma classe recorrente nova para `docs/engineering/achados-recorrentes.md`.
