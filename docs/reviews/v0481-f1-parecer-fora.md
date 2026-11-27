---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-f1-parecer-fora
commit: e26310c229a8fae6bcbc2168d9a2db3d16875f2a
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-26
---
# Review: v0481 (E29.2, #925, F1 corte 1: leitura do parecer no status)

## Achados
- A1 (bloqueante) bin/forge_pareceres.py:139 · a linha nova repete `for s in p if isinstance(s, dict)]` da linha 93, e o `de` do M27 de tests/mutantes/v0481-g2-1-publicar-5.json deixa de ser único: CI vermelho em test_forge_mutante.ConferirTodas (suíte 3.12 e 3.14, parte 4/5). Torne o `de` do M27 único (incluir `faltam`).
- A2 (bloqueante) docs/indice-forge.md:1 · o índice não foi regerado com `ler`, `conferir` e `frontmatter`: CI vermelho em test_indice_forge (test_indice_esta_em_dia e test_conferir_da_rc_0_em_dia, parte 2/5); `scripts/indice-forge.py --conferir` local: desatualizado. Rode `scripts/indice-forge.py` e commite.
- A3 (recomendado) bin/forge_pareceres.py:141 · `login in contas` casa por substring se `contas` vier como str (sonda S1); o 1º chamador (corte 7) deve passar conjunto, ou `ler` recusa o que não é set/frozenset.
- A4 (recomendado) bin/forge_pareceres.py:117 · `pr["number"]` e `(c.get("user") or {}).get` (120, 141) soltam KeyError ou AttributeError, não Recusa, com resposta malformada do `gh`; o M19.1 pede Recusa. Falha fechada mesmo assim; alinhe ao `publicar`, que converte essas exceções.

## Sondas
- S1 · `contas="minhaconta-admin"`, creator `conta`, filtro da linha 141 · espera: fora · obtido: aceito (substring) (/root/.forge-contrib/v0481-tl324-sonda.py)

## Parecer
Reprovado por A1 e A2: o código da leitura está correto e só aperta, mas o head deixa a suíte vermelha em duas partes por efeito do diff, sem relação com a espera de parecer.

- Escopo: faz o que o E29.1 pede para o 1º corte, a leitura sem chamador; plano de 11 cortes no corpo do PR, com comportamento, arquivos, estimativa e dependências. Fora do F1 (G3, F3) declarado. Bom.
- Tamanho (H1): 50 linhas de código em `bin/forge_pareceres.py`, um comportamento só, dentro do teto. Os dois consertos não mudam isso.
- Lógica: filtro pelas contas antes do mais novo de cada contexto (C1, C2), contexto por igualdade exata (C3), `fullmatch` na descrição e no `target_url`, sem seguir a URL (só o id vai à API do repositório do `origin`), `html_url` igual, sha256 do corpo normalizado igual ao do `publicar`, frontmatter com commit, branch, pedido, tipo e veredito iguais ao head e ao status. Os campos casam com os modelos de review, qa e segurança. Status mais novo inválido mascara o válido mais velho: falha fechada, correto.
- Testes: classe `Ler` com 25 testes de comportamento; o falso de `gh` roteia pelo caminho exato do comentário (checklist 12). Base vermelha: as funções `ler`, `conferir` e `frontmatter` não existem em ee05ee84 (0 ocorrências), log do autor `FAILED (errors=33)`.
- Mutantes M1 a M17: todos morrem; M13 a M17 por erro, aceitável aqui (o ramo removido quebra o fluxo).
- Commits: 2, Conventional Commits em português, escopo e etapa.

## Provas
- `python3 -m unittest tests.test_forge_pareceres` no e26310c2: Ran 65 tests, OK (/root/.forge-contrib/v0481-tl324-afetados.log).
- `bin/forge-mutante --processos 1 --base ee05ee84… <3 specs>`: M1 a M17 morreu; `--cobertura`: toda condição coberta (/root/.forge-contrib/v0481-tl324-mutantes.log, /root/.forge-contrib/v0481-tl324-cobertura.log).
- CI no e26310c2 (run 45912046492): suíte partes 1, 3 e 5 verdes nas duas versões, bateria (passos), verificações longas, instalação e árvore verdes; partes 2/5 e 4/5 vermelhas por A2 e A1 (logs dos jobs 140229170410 e 140229170407); `bateria (pareceres)` espera parecer.
