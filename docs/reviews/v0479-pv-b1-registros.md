---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-pv-b1-registros
commit: 1aed3a743d433c903454422acad73859c12b67b9
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 (E57.12, PR-VERDE B1 no head 1aed3a74)

Escopo: `bin/forge-testes --registros` (+95 linhas de código, dentro do teto H1), a classe `Registros` em `tests/test_testes_tocados.py`, as specs `tests/mutantes/v0478-pv-b1-registros{,-2}.json` (11 mutantes) e o fragmento `changelog.d/v0479-pv-b1-registros.md`. Conferido contra a linha B1 do desenho aceito (`docs/propostas/v0479-pr-verde-de-primeira.md`, na `origin/melhoria/v0479-pr-verde-de-primeira`).

## Achados
- A1 (recomendado) bin/forge-testes:910 · "nada grava (sem bytecode)" falha: o import de `forge_apoio_testes` (linha 79) grava `bin/__pycache__/` (S1). O teste (linha 1875) não vê: a ferramenta fica fora do repositório de brinquedo. Sugestão: `sys.dont_write_bytecode = True` antes do import.
- A2 (recomendado) bin/forge-testes:954 · o `subprocess.run` de cada grupo não tem `timeout`: um teste travado prende a conferência e, quando o B3 a puser no envio, prende o envio. Sugestão: prazo por grupo, com estouro como saída 2 (sem veredito).
- A3 (recomendado) bin/forge-testes:920 · o ramo `except subprocess.TimeoutExpired` (retorno de aviso) não tem mutante declarado nem teste do ramo de falha (guardas do diff, um mutante por linha).
- A4 (recomendado) bin/forge-testes:954 · R3 do desenho pede p95 abaixo de 20 s medido no item; não há medida registrada, e uma execução neste clone, com a máquina carregada (18 agentes), deu 45 s. Medir e, se passar, cortar o grupo mais lento para o CI antes do B3.

## Sondas
- S1 · `rm -rf bin/__pycache__; env -u PYTHONDONTWRITEBYTECODE python3 bin/forge-testes --registros --listar; git status --porcelain --ignored` · espera: nada (só leitura) · obtido: rc=2 e `!! bin/__pycache__/`
- S2 · `python3 bin/forge-testes --registros` no clone em 1aed3a74 · espera: rc=0 abaixo de 20 s (R3) · obtido: `registros rc=0 em 45 s (9 conferências ...)`

## Parecer
Aprovado. O modo faz o que a linha B1 pede: roda os testes do próprio CI (nunca cópia da regra) em grupos paralelos, o `forge-changelog conferir --base` e o peso de todo módulo de teste novo; busca a `origin/<ramo>` antes e, sem rede, avisa e confere contra a local; separa 1 (desatualizado) de 2 (sem veredito); recusa combinação com outras opções. O ambiente herdado (`GIT_*`, `FORGE_*`) não chega aos testes dos grupos (AR-4), e o teste prova isso pelo próprio brinquedo; os subprocessos do teste rodam com ambiente limpo e `python3 -I`. As guardas novas têm mutante declarado, salvo A3. A regra do peso (todo módulo novo) é mais estrita que a do CI (até 20% sem peso), como o desenho pede.

Verificação: `python3 -m unittest tests.test_testes_tocados.Registros` neste head, 10 testes, OK em 34 s; a suíte inteira fica para o CI do PR (`R-REVIEW`, sem rerrodar o SHA). Os quatro achados são recomendados (A1 é bytecode em pasta ignorada, efeito igual ao dos outros modos do script; A2 e A4 só pesam no envio, que é o B3) e viram cartão depois do merge.
