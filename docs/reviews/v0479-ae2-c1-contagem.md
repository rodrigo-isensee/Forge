---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-ae2-c1-contagem
commit: aa8e521a99a2708e2ed14c872d3b50989e4aefbd
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 (E56.2, AE2 C1 e C3 no head aa8e521a)

Diff contra a base 5ccac0bf: `bin/forge_contador.py` (145 linhas de código, dentro do H1), `tests/test_contador.py` (30 testes), 24 mutantes em 3 specs, índice, pesos e fragmento de changelog. Lidos o desenho `docs/propostas/v0479-ae2-contador.md` (seções 4.1, 5, 7 e 8, na branch `melhoria/v0479-ae2-contador`) e o brief do autor (E56.1).

Suíte: sem CI (sem PR) e sem suíte local, pelo brief; rodado só o teste novo, `python3 -m unittest tests.test_contador`: 30 testes, OK. Mutação: a ferramenta é do autor (V2), não refeita aqui; cada guarda nova tem mutante declarado com teste de comportamento.

## Achados
- A1 (bloqueante) bin/forge_contador.py:65 · `--merged={ref}` não acha a marca: no Forge a tag fica no merge da main (v0.47.11, fora da develop). Aqui dá v0.45.5, versão 0.45.6, 211 PRs; o certo é 0.47.12 com 13 (S1-S3). Sugestão: maior tag sem `--merged` e `{tag}..{ref}`; teste com tag fora da develop.
- A2 (bloqueante) templates/projeto/.forge/config.json:1 · pendente: o C3 do desenho e o Entregar do E56.1 pedem `teto_da_versao` (20) no modelo de projeto; não há commit no arquivo, e o projeto não descobre a chave. Ordem do dono 09:56: entra pelo modelo de projeto.
- A3 (recomendado) bin/forge_contador.py:77 · O desenho fala em trailer; o código aceita `Cartão:` em qualquer linha da mensagem (corpo incluso). Registrar a escolha no docstring ou restringir ao bloco final de trailers, antes do C4 e do C5 lerem a mesma função.
- A4 (recomendado) bin/forge_contador.py:125 · `O_NOFOLLOW` só cobre o último componente: `.forge` como link para outra pasta é seguido. Avaliar com a segurança se o caso de abuso "configuração por link" do C3 inclui a pasta.

## Sondas
- S1 · `python3 -I -c "import sys; sys.path.insert(0,'bin'); import forge_contador as c; r=c.contar('.'); print(r['marca'], r['versao'], len(r['prs']))"` no clone em aa8e521a · espera: v0.47.11 0.47.12 13 · obtido: v0.45.5 0.45.6 211
- S2 · `git merge-base --is-ancestor v0.47.11 origin/develop` · espera: ancestral (o desenho supõe tag alcançável da develop) · obtido: não ancestral (2fae3f93 é o merge do #711 na main)
- S3 · `git log --first-parent --format=%s v0.47.11..origin/develop`, PRs no assunto · espera: os PRs da 0.47.12 · obtido: 13 (#703, #712 a #723), igual à contagem pelo git `origin/main..origin/develop`

## Parecer
Reprovado. O núcleo está limpo: `git` sem `GIT_*` herdadas, com limite de tempo e `--end-of-options`; registros por NUL; só a primeira linha da develop; ID na forma do `movimento`; teto de 10 citações; leitura da configuração por fd, com tipo e tamanho conferidos e sem traceback. Cada guarda tem teste do ramo de falha.

Dois bloqueantes. O A1 é defeito provado no próprio Forge (S1 a S3): a marca do desenho, "a maior tag alcançável de origin/develop", não existe no fluxo `develop` → `homolog` → `main`, onde a tag fica no merge da main. O contador erra a versão e conta 211 PRs em vez de 13. Isso dispara o critério de reversão (b) da seção 8 do desenho, que reabre o C1. Correção sugerida: escolher a maior tag na forma entre todas (sem `--merged`) e manter `{tag}..{ref}`, que já exclui da contagem os commits da develop que a main recebeu. O arquiteto confirma a emenda da seção 4.1. Os testes hoje criam a tag na própria linha da develop; falta um caso com a tag num merge fora dela. O A2 é um item do Entregar sem commit (`R-REVIEW`).

A3 e A4 são recomendados: não devolvem a entrega e viram cartão depois do merge.
