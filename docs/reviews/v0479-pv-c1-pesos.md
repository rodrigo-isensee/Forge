---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-pv-c1-pesos
commit: a94644bcdf3a3407f4ea92ed98389050e5c644f6
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 (E57.34, PR-VERDE C1, pesos da suíte por PR)

Diff lido: `5ccac0bf..a94644bc`, 5 arquivos (+77/-12). Código de controle: 1 linha em `scripts/suite-paralela.py` (texto do resumo do CI); o resto é teste, skill e fragmento do changelog. Sem guarda nova em código de controle, logo sem mutante exigido; teto H1 folgado. Sem suíte local (brief); a suíte inteira fica no CI do PR.

## Conferência
- Pedido (E57.3, D4 do desenho): o limite global de 20% sem peso sai; entram duas regras por PR, módulo novo precisa de peso e módulo com peso na base não o perde. `violacoes_de_peso` faz isso, e o sem peso que já vinha da base passa (`R-REVIEW` checklist 1).
- `modulos_de_teste` repete o critério de `modulos()` de `scripts/suite-paralela.py:112` (raiz e pacotes com `__init__.py` em todo nível, nome com ponto); `test_modulos_de_pacote_e_da_raiz` cobre a raiz, o pacote, a pasta sem `__init__`, o nome inválido e o arquivo fora de `tests/`.
- Base: `merge-base HEAD refs/remotes/origin/develop`. Os jobs da suíte no CI (`partes-doze`, `partes-quatorze`, `rapida-partes-*`) fazem checkout com `fetch-depth: 0`, que traz `refs/remotes/origin/*`; no PR o merge-base é a ponta da develop, na develop é o próprio HEAD. Sem base, o teste falha fechado e diz `git fetch origin develop`.
- Subprocessos de `git` com `ambiente_limpo()`; `minimo(head, 100, ...)` guarda o percurso de `tests/` (checklist 11).
- Skill `ritmo-e-corte.md`: o comando citado bate com os argumentos de `scripts/pesos-do-ci.py` (`--repo`, `--saida`, linhas 175 e 177). A regra que sai (os 20%) está dita no changelog e na docstring (`R-DECISAO`).
- Commits: dois, Conventional Commits em português, um por mudança coerente.

## Provas lidas
- `python3 -m unittest tests.test_forge.PesosDaSuite` no head a94644bc: `Ran 3 tests ... OK`.
- Sonda na árvore real (base 5ccac0bf, 224 módulos, 47 sem peso herdados): módulo novo `test_sonda_zz` sem peso dá `(['test_sonda_zz'], [])`; tirar o peso de `test_textos_034` dá `([], ['test_textos_034'])`. As duas regras reprovam o que devem.

## Sondas

## Parecer
Aprovado no head a94644bc (`R-REVIEW`). Faz o que o C1 pede, sem mais; o teste do ramo de falha existe para as duas regras, e a base vem do CI com o histórico inteiro.
