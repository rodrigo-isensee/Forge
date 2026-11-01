---
tipo: review
contrato: 1
pedido: heredoc-rapido
branch: melhoria/heredoc-rapido
commit: c1eaaec72bbb54a878baee575a7ec4ca8713190e
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-01
---
# Review: heredoc-rapido

Etapa E1.2 (instância revisora, não a autora). Diff lido: `c454ccb..c51715f` e, na revalidação, o delta `c51715f..c1eaaec` (o que a branch acrescenta à develop).

## O que a branch entrega
Item E1 do pedido, passo 1 do desenho `docs/propostas/heredoc-rapido.md`: `Guarda._regras` guarda o resultado de `regras_do_forge` e `Guarda._raiz_home` guarda o par `(realpath da raiz, realpath do home)`, ambos preguiçosos, com sentinela `None`, na instância. O passo 2 (leitura da linha marcada) não entrou, como manda a decisão técnica do Jarvis de 2026-10-31 22:12. Nenhum teto de teste sobe: o `test_muitos_heredocs_recusam_dentro_do_orcamento` segue com 5,0 s.

## M14
`git diff --numstat --no-renames c454ccb c51715f`: `hooks/conformidade.py` 8+2, `tests/test_hooks.py` 21+0, total 31 linhas que contam (o `changelog.d/heredoc-rapido.md` fica fora). Abaixo de 150, sem linha de exceção (nem cabe: mexe em `hooks/`). Um comportamento só, uma classe em `hooks/` (cache por decisão na `Guarda`). Cumpre.

## Controles do modelo de ameaças (C-1 a C-6), lidos no diff
- C-1: cache em atributo da instância, preguiçoso, sentinela `None` distinta de `False`; sem variável de módulo, `lru_cache`, atributo no `hook` nem disco. Cumpre.
- C-2: o `externo is None` entrou dentro do valor guardado (`conformidade.py:441`), não fora dele. Hoje dá o mesmo resultado, porque `principal` grava `guarda.externo` (`:1798`) antes do `decidir` e o cálculo é preguiçoso; ver A1.
- C-3: ordem `raiz, home` mantida (`:494`) e o `realpath` dos dois; nenhuma outra função mudou. Cumpre.
- C-4: o diff não acrescenta atribuição a `self.h.raiz`, `self.externo` nem `os.environ`; `hook.raiz` muda só em `:1795`, antes da `Guarda` que decide nascer (`:1797`). Cumpre.
- C-5: casos de abuso são do QA (E1.4); o caso (e) já tem teste novo (`test_regras_e_raiz_sao_calculadas_uma_vez_por_decisao`): 4 instâncias com 50 destinos cada contam 4 leituras do manifesto e 4 `Path.home`, provando o cache por instância e a ausência de cache entre instâncias.
- C-6: passo 2 fora do diff. Cumpre.
- Achado de segurança novo: nenhum. A revisão de segurança é a E1.3 (`docs/security/`), não refeita aqui.

## Ferramentas (citadas, não refeitas)
- `python3 -m unittest tests.test_hooks.Hooks.test_regras_e_raiz_sao_calculadas_uma_vez_por_decisao tests.test_hooks.Hooks.test_muitos_heredocs_recusam_dentro_do_orcamento`: `Ran 2 tests in 10.269s` `OK` (local, load 3,4).
- `bin/forge-mutante --cobertura --base c454ccb...`: rc=1, `sem mutante · hooks/conformidade.py:440 · self._regras is None` e `sem mutante · hooks/conformidade.py:492 · self._raiz_home is None`. Falta a spec `tests/mutantes/heredoc-rapido.json`, que o desenho, seção (d), põe com o QA (M1, M2 e o M3 declarado equivalente); ver A2.

## Achados
- A1 (recomendado) hooks/conformidade.py:441 · o C-2 pede o `externo is None` conferido a cada chamada, fora do cache; hoje está dentro. Equivale enquanto o C-4 valer; mover para `return self.externo is None and self._regras` deixa o controle literal. Decisão da E1.3.
- A2 (recomendado) tests/mutantes/heredoc-rapido.json:1 · a cobertura de mutação saía rc=1 (linhas 440 e 492 sem mutante); resolvido: a spec entrou na E1.4 e a cobertura sai rc=0 no head novo.

## Parecer
Aprovado. A branch entrega o passo 1 do E1 com 31 linhas, um comportamento, sem subir teto, e o teste novo prova o cache por decisão. A1 e A2 não devolvem: A1 é equivalente hoje e cabe ao security-engineer decidir; A2 é a spec de mutantes que o desenho atribui ao QA, e o `forge-mutante --cobertura` precisa sair rc=0 antes da E1.5.

## Revalidação (head c1eaaec)
`forge-check delta --parecer docs/reviews/heredoc-rapido.md` listou só `tests/hooks/conformidade/home-por-link-simbolico-bloqueia.json`, `home-trocado-na-linha-bloqueia.json`, `so-forge-sessao-de-projeto-com-manifesto-forjado-libera.json` (fixtures novas) e `tests/mutantes/heredoc-rapido.json` (spec do QA). Lido o delta: fixtures só acrescentam casos, a spec traz H1 a H7 sobre `conformidade.py:440` e `:492`. Já lido (não relido): `hooks/` e `tests/test_hooks.py`, sem mudança desde c51715f (`git diff c51715f c1eaaec -- hooks tests/test_hooks.py` vazio). M14: o delta é só corpus e fixtures, as 31 linhas que contam seguem iguais. `bin/forge-mutante --cobertura --base c454ccb`: rc=0, linhas 440 e 492 cobertas. Parecer segue aprovado.
