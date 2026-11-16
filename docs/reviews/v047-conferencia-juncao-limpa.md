---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-conferencia-juncao-limpa
commit: 1477a480d39ff926143246c5c0ed1c72d2e71bfd
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-16
---
# Review: v047 (conferência de junção limpa, E2.302; review E2.329)

## Achados

## Sondas

## Parecer
**Revalidação no head 1477a480 (E2.346, por delta).** Lido só `forge-check parecer delta`: intervalo `d093ee81..1477a480`, no domínio `bin/forge-check`, `tests/mutantes/v047-conferencia-juncao-limpa.json` e `tests/test_selo_e_entrega.py`. O A1 anterior (recomendado) está resolvido: `test_segundo_pai_ancorado_mas_fora_da_base_recusa` isola o `e_ancestral(pais[1], base_ref)` com a âncora presente, e o mutante J6 o aponta. Novo: `merge-tree` roda com `--attr-source=<árvore vazia>` (segurança A1), coberto por `test_gitattributes_da_arvore_de_trabalho_nao_resolve_conflito` e pelo mutante J7; falha do `hash-object` dá `--attr-source=` vazio, o git falha e a função recusa (falha fechada). Q3 declarado equivalente com motivo (conflito grava árvore com marcadores, diferente da commitada). Conferi que os trechos `de` de J6, J7 e Q3 aparecem uma vez cada em `bin/forge-check` (AR-12). Teste rodado aqui: `python3 -m unittest tests.test_selo_e_entrega.JuncaoLimpa`, 9 testes OK (16 s). O `bin/forge-mutante` não rodou aqui: a trava R-TETO estava na fila (posição 2 de 9); é verificador do autor (V2). Suíte inteira: CI do PR, ainda sem PR; não rerrodada. Sem achado novo; sem linha AR nova.

**Parecer original (head d093ee81):**
Aprovado no head d093ee81. Parecer completo (não havia parecer anterior). Intervalo `d4b5dac6..d093ee81` (merge-base com a `origin/develop` igual ao Base-sha), 3 commits em Conventional Commits, um comportamento só.

O que muda: `juncao_limpa` aceita o intervalo `<conferida>..<head>` quando cada commit do primeiro pai é merge de dois pais, o segundo ancestral da `origin/<base>` e de um Base-sha selado (`bases_seladas_depois`), e a árvore do merge é igual à de `git merge-tree --write-tree` dos dois pais. O ramo novo em `linhas_de_entrega` só entra com intervalo sem arquivos, sem falha do git e com o Desde presente em `entregas_conferidas` (forma gravada pela ferramenta). `cmd_entrega_conferir` calcula as âncoras uma vez e as passa a `ponto_da_integracao` e a `linhas_de_entrega`; o `cmd_entrega` sem conferência segue com `ancoras=()`, então lá nada muda. Falha fechada em todo ramo: commit comum, octopus, merge de outra coisa, conflito (`merge-tree` sai com 1), resolução à mão (árvore diferente), git sem `--write-tree` (anterior a 2.38) ou erro do git dão False, e o resultado volta ao `pendente:` de antes. A `origin/develop` é ref local reescrevível; a exigência da âncora selada fecha esse caminho; a segurança é do E2.330 (parecer dele, não refeito aqui).

Testes: `JuncaoLimpa` (7 casos: duas junções e uma junção limpa cumprem e gravam o head; sem âncora, conflito resolvido com `--ours`, merge que tira o arquivo da develop sem conflito, conferida fora da forma e a função direta com intervalo vazio, sem base, sem âncora e commit comum seguem recusando) e `MergeDaBaseDepoisDoBrief` rodados aqui com `python3 -m unittest`: 15 testes OK (115 s). Cada ramo de falha tem teste de comportamento, não de texto da fonte. Mutantes: 5 declarados (J1 a J5), um por linha de guarda mudada (2475, 2478, 2481, 2842, 9174); conferi que cada trecho `de` aparece uma vez em `bin/forge-check`. O `bin/forge-mutante` não rodou aqui: a trava R-TETO estava ocupada por outra sessão (fila 1 de 3); é verificador do autor (V2) e não volta ao review. Suíte inteira: fica para o CI do PR, ainda sem PR (o brief pede "sem PR"); não rerrodada.

PA-7 (`docs/engineering/achados-recorrentes.md`): AR-1 e AR-2 conferidos (lista completa por linha, ramo de falha com teste); AR-4: o subprocesso novo do teste usa `self.env` da base `Conferencia`; AR-12: trechos da spec batem com o head. Nenhuma classe repetida; sem linha AR nova.

Tamanho (M14): 27+6 em `bin/forge-check` e 108 em `tests/test_selo_e_entrega.py` dão 141 linhas, dentro de 150. Fragmento `changelog.d/v047-conferencia-juncao-limpa.md` presente.
