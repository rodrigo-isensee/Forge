---
tipo: review
contrato: 1
pedido: vv-2
branch: melhoria/vv-2
commit: e925152b3886dc7de006676f213328fec0c58d34
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-19
---
# Code review: VV-2 (volta por delta)

Diff revisado: `7226ba7...e925152` (6 commits, 31 arquivos, 1625+/31-). Brief do autor: `vv-2-tech-lead-1.md`, "Entregar" 1 a 7. Desenho: `docs/planos/vv-2.md`; modelo de ameaças: `docs/security/ameacas/vv-2.md` (cópias em `~/.forge-contrib/docs/`).
Ferramentas rodadas nesta revisão, em e925152: `python3 -m unittest tests.test_volta_por_delta tests.test_testes_tocados` → `Ran 74 tests ... OK`; `forge-check docs` → rc 0; `git merge-tree --write-tree origin/develop HEAD` (develop em 0c77d23, release 0.21.0) → merge limpo. Suíte inteira (861 OK) e `scripts/validar-plugin.sh` não refeitos (R-TETO; provas do autor, o QA as refaz no head). Segurança: parecer próprio do `security-engineer` (E2.2), não refeito aqui; a lista negra `FORGE_CHECK_GRAVA` (risco c do autor) é dele.

## Contra o plano e o "Entregar"
- **E1 (`forge-check entrega`, A1 a A6, B1, B4):** cumprido. `cmd_entrega` faz as duas checagens de base, valida o `--desde` pela `conferida` mais recente do `## Histórico` (sha40, ancestral do head), reprova `--desde` nas etapas de branch inteira, a `conferida` commitada na entrega (`pedido_na_entrega`, falha fechada se o `git log` falhar) e o intervalo vazio na etapa `codigo`; `ok (parecer de ...)` exige a mesma autoria (hash do texto com `strip`, igual ao `cmd_pr`) e não esconde remoção (A6). Refs por `rev-parse --verify --end-of-options`, git interno com `--no-ext-diff --no-textconv -z` e `--`.
- **Hook (A1, B2):** cumprido. `caminhos` ganha `docs/pedidos/`, `docs/briefs/` e as cópias em `~/.forge-contrib/docs/`, só `jarvis`; nenhum outro agente ou skill grava nessas pastas (conferido por `grep -rn "docs/pedidos\|docs/briefs" agents skills`). `so_leitura.comandos` só ganha `entrega` e `delta` (teste novo em `tests/test_hooks.py` fixa a lista inteira). 14 fixtures.
- **E2 (`delta`, `brief --anterior`, B3, B5):** `delta` cumprido. `brief --anterior` funciona só com o anterior dentro de `docs/briefs/` da raiz; com a cópia do Forge em `~/.forge-contrib/docs/briefs/` (o caso real deste repositório) dá rc 2 (A2). O `--volta` e o `Volta-de:` já aceitam essa pasta (`caminho_de_brief`), o `--anterior` não.
- **E5:** cumprido (`pq_de_merge`, nas etapas de merge do `gerar` e do `gerar --volta`).
- **E3 (`gerar --volta`, C1 a C5):** cumprido na mecânica, com testes de cada caso. Mas o bloco `## Achados` colide com o cabeçalho de mesmo nome que o modelo de parecer de segurança já tem, em outro formato (A1).
- **E4 (agentes, docs, changelog):** os quatro agentes e o `docs/hooks.md` estão coerentes com o código; `changelog.d/vv-2.md` é neutro (R-NEUTRO). Faltam os modelos de parecer (A1). `agents/jarvis.md` (uma frase: gravar a `conferida` no Histórico no formato que o `CONFERIDA` casa e usar `gerar --volta`) e `bin/forge-testes` (o módulo novo no mapa do `bin/forge-check`, exigido por `tests/test_testes_tocados.py`): conferidos, corretos e no tamanho mínimo (DECISÃO TÉCNICA do Jarvis no pedido).
- **Testes:** os 10 casos do plano estão em `tests/test_volta_por_delta.py` (classes `Entrega`, `Pareceres`, `Delta`, `BriefAnterior`, `PqDeMerge`, `BriefDeVolta`, `TextoDosAgentes`), mais os itens 8 (só leitura) e 10 (regressão) da lista da E2.2. Nenhum teste cobre parecer em formato antigo com cabeçalho `## Achados` nem o `--anterior` em `~/.forge-contrib` (são os dois bloqueantes).
- **Commits:** um por item, Conventional Commits em português, na ordem do plano; corpo explica o porquê.

## Suposições do autor
1. `--desde` "não ancestral do Base-sha" em vez de "descendente": aceita; é o que deixa o Base-sha regravado depois do merge da base funcionar (A5), e o caso "anterior ao Base-sha" segue reprovando (teste).
2. Reprovado sem o bloco sai `não verificável`; `forge-check docs` só cobra quem adotou o formato: aceita como transição, mas a premissa "sem o bloco" não vale para segurança, cujo modelo já tem `## Achados` (A1).
3. `DECISÃO TÉCNICA` copiadas pela ordem das linhas depois da que cita o sha256 do anterior: aceita (mais seguro que comparar datas sem hora).
4. Volta cita os `E<n>` da entrega original numa linha de cobertura: aceita; a entrega original já foi conferida e o corte por IDs continua valendo para o que não foi.
5. `--volta` e `--anterior` valem em `docs/briefs/` da raiz ou de `~/.forge-contrib`: não aceita; vale para o `--volta`, não para o `--anterior` (A2).
6. Fixtures do AQ com a mensagem nova: aceita; seguem rc 2.
7. `bin/forge-testes`, `docs/hooks.md` e a frase do `agents/jarvis.md`: aceita (ver E4).

## Achados
- A1 (bloqueante) templates/projeto/docs/security/_modelo.md:18 · o modelo (e docs/security/_modelo.md:18) já tem ## Achados em prosa: todo parecer de segurança reprovado no formato atual é recusado pelo gerar --volta e reprova a conferência da volta; atualizar os modelos de reviews, qa e security e tratar o formato antigo; reproduzir: R1
- A2 (bloqueante) bin/forge-check:2680 · brief --anterior só aceita docs/briefs/ da raiz; o anterior em ~/.forge-contrib/docs/briefs/ (o fluxo do Forge que o conferente.md manda rodar) dá rc 2; usar caminho_de_brief, como o --volta, e testar; reproduzir: R2
- A3 (recomendado) bin/forge-check:441 · médio: arquivos_da_entrega passou a usar -z, e nome com acento deixa de vir entre aspas (core.quotePath); muda gatilhos e pr para melhor, mas sem teste nem linha no changelog; reproduzir: R3
- A4 (recomendado) bin/forge-check:1018 · baixo: brief com Volta-de conferido sem --ref sai "volta: pareceres não verificáveis" sem reprovar, e o conferente.md não diz como tratá-la; dizer que é não verificável no veredito ou reprovar; reproduzir: R4

## Reprodução
- R1: `cd ~/.forge-contrib/wt/vv-2 && python3 -c 'import importlib.machinery as M;m=M.SourceFileLoader("fc","bin/forge-check").load_module();print(m.problemas_do_bloco(*m.achados_do_parecer(open("docs/security/aq.md").read()),{"parecer":"reprovado"},True)[:2])'` → `['linha do bloco ## Achados fora do formato ...', ...]` (o mesmo com `templates/projeto/docs/security/_modelo.md`; 16 pareceres de `docs/security/` têm o cabeçalho e nenhum casa o formato). Parecer novo que siga o modelo e acrescente uma linha `- A1 (...)` faz o `forge-check docs` falhar (modo de transição: com um achado lido, a linha de prosa vira erro), e com ele o `forge-check pr`.
- R2: `cd ~/.forge-contrib/wt/vv-2 && python3 bin/forge-check brief ~/.forge-contrib/docs/briefs/vv-2-tech-lead-2.md --pedido ~/.forge-contrib/docs/pedidos/vv-2.md --destino forge:tech-lead --anterior ~/.forge-contrib/docs/briefs/vv-2-tech-lead-1.md; echo rc=$?` → `brief: --anterior ".../vv-2-tech-lead-1.md": fora da raiz ou de docs/briefs/` e `rc=2`; com `cd ~/.forge-contrib` e caminhos relativos, rc 0.
- R3: repositório com `docs/decisões.md` alterado na branch: `git diff --name-only base...HEAD` imprime `"docs/decis\303\265es.md"` (o código antigo comparava esse texto com prefixos), o novo imprime `docs/decisões.md`.
- R4: `tests/test_volta_por_delta.py` `test_conferencia_reprova_anterior_bloco_e_achado`, último caso (`ref=None`): a linha sai e o rc não muda por ela.

## Parecer
**Reprovado** por A1 e A2. O núcleo (E1, hook, `delta`, E5, a mecânica do E3) está correto, testado e não afrouxa nada: o `--desde` só nasce de linha que só o Jarvis grava e as etapas de branch inteira ficam travadas por máquina. A volta é pequena: os três modelos de parecer no formato novo e uma decisão sobre o `## Achados` antigo (ignorar linha de prosa sem prefixo `- A<n>`, ou tratar bloco sem nenhum achado lido como `não verificável`; a escolha toca C3 e passa pelo `security-engineer`), mais o `--anterior` pelo `caminho_de_brief`, cada um com teste. A3 e A4 podem entrar na mesma volta ou virar corte.
Para a E2.2 em curso: o parecer de segurança desta rodada, escrito pelo modelo atual, não deve misturar a prosa do modelo com linhas `- A<n> (...)` no `## Achados`, ou o `forge-check docs` desta branch o recusa (R1). Para a E2.4: a develop andou (0c77d23) e o merge é limpo; trazê-la uma vez antes da revalidação.
