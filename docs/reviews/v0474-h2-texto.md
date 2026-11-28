---
tipo: review
contrato: 1
pedido: v0474
branch: melhoria/v0474-h2-texto
commit: 5a590bf3e8465df0b7a283fefe871ef504b50ad4
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-17
---
# Review: v0474 (H2-texto, E2.40)

Code review (E2.42) do diff `ba968580...5a590bf3`: agents/jarvis.md (passo 6), agents/tech-lead.md ("Na volta"), skills/briefs-e-conferencia/SKILL.md, auxiliar novo skills/briefs-e-conferencia/autor-ate-o-merge.md, tests/config.json, changelog.d/v0474-h2-texto.md.

## Achados
- A1 (recomendado) agents/tech-lead.md:20 · "Na volta" junta o tech-lead revisor (retomado na revalidação) e o autor (volta de CI e conflito); uma frase separando os dois papéis evita ler que o revisor corrige achados de CI. Sem defeito: o auxiliar distingue.

## Sondas

## Parecer
Aprovado. Faz o que E2.40 pede (R-BRIEF, H2), nada além.

- Texto movido: o comando `forge-check brief gerar --pedido <p> --volta <brief anterior> --ref <branch> --parecer <arquivo>...` e "Recomendação não entra" saíram do `## Brief de volta` da SKILL.md e estão literais no auxiliar (linha "Uma volta por rodada"), agora protegidos por invariante nova. A invariante antiga `forge-check brief gerar` da SKILL.md segue casando (linha 11).
- Nenhuma regra nem invariante saiu: em tests/config.json o diff só acrescenta (14 padrões novos, todos com `invariantes_motivo` e regra R-BRIEF); a troca de `corrija os achados sem reler tudo` por `corrija sem reler tudo` no tech-lead não tocava invariante (a suíte de invariantes do CI confere).
- Diretriz 25: Jarvis e tech-lead trazem o resumo e apontam o auxiliar; tetos de instrução sem estouro (`tests.test_orcamento_instrucao` verde).
- Coerência com a parte de ferramenta (origin/melhoria/v047-h2-autor-fica, hooks/agentes.py): o aviso é `R-TETO`, código 0, `aviso: autor retomável (<branch>: <id>)`, some com lápide, autor ativo ou fora de `expiracao_horas`; o auxiliar descreve exatamente isso.
- Medida e critério de revisão (R-DECISAO) presentes no auxiliar: agentes por item mesclado, meta de 6, revisão se não cair em duas versões.
- Tamanho (H1): só tests/config.json conta, 23 linhas; dentro do teto.
- Fragmento de changelog presente; commit único em Conventional Commits em português.

Provas lidas: `python3 -m unittest tests.test_orcamento_instrucao tests.test_jarvis_nucleo tests.test_metricas_texto tests.test_frontmatter_agentes` → `Ran 56 tests ... OK`. Suíte inteira: fica no CI do PR.
