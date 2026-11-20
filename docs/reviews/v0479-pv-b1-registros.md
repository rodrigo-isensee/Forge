---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-pv-b1-registros
commit: f7baaa533910b7af1777ad406f7bc940f8df669c
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 (E57.25, PR-VERDE B1 no head f7baaa53, revalidação)

Revalidação depois da volta do recomendado A1 da segurança (E57.19). Delta lido: `forge-check parecer delta docs/reviews/v0479-pv-b1-registros.md`, intervalo `1aed3a74..f7baaa53`, no domínio `bin/forge-testes`, `changelog.d/v0479-pv-b1-registros.md`, `tests/mutantes/v0478-pv-b1-registros-2.json` e `tests/test_testes_tocados.py`; fora dele nada foi relido (`R-REVIEW`, H3).

## Achados
- A1 (recomendado) bin/forge-testes:911 · sem mudança no delta: o import de `forge_apoio_testes` ainda grava `bin/__pycache__/` (S1 do parecer em 1aed3a74). Segue como cartão depois do merge.
- A2 (recomendado) bin/forge-testes:959 · sem mudança no delta: o `subprocess.run` de cada grupo segue sem `timeout`. Cartão depois do merge.
- A3 (recomendado) bin/forge-testes:925 · sem mudança no delta: o ramo `except subprocess.TimeoutExpired` segue sem mutante declarado nem teste do ramo de falha. Cartão depois do merge.
- A4 (recomendado) bin/forge-testes:959 · sem mudança no delta: falta a medida do p95 abaixo de 20 s (R3 do desenho). Cartão depois do merge.

## Parecer
Aprovado. A correção faz o que a segurança pediu, e só isso: `buscar_base` recusa, antes do `git fetch`, o ramo fora de `[A-Za-z0-9._/-]`, o que começa com `-` e o que contém `..`, e o `git fetch` ganhou `--end-of-options` (git 2.43 aqui; a opção existe desde a 2.24). Assim nem `--upload-pack=...` (execução de comando) nem `+x:refs/heads/y` (refspec que grava ramo local) chegam ao git. A recusa devolve um aviso e a comparação segue contra a base local, igual ao caminho sem rede; a base que não resolve sai 2, e o teste prova isso. O comentário do bloco agora diz certo que a busca e o `git()` usam o ambiente da sessão. O fragmento do changelog acompanha a mudança.

Teste novo: `test_ramo_que_seria_opcao_ou_refspec_e_recusado_sem_buscar` exercita o comportamento com quatro entradas, uma por disjunção da guarda: `--upload-pack=touch PWNED;...`, `+develop:refs/heads/sobrescrita`, `-x` e `a..b`. Ele confere a saída 2, o aviso, que o arquivo de prova não existe, que nenhum ramo foi criado e que nenhuma ref remota foi buscada; não lê o texto da fonte. Guardas do diff: a linha 920 é a única guarda nova e tem 4 mutantes declarados (R12 a R15, um por disjunção). O `-2.json` fica com 7 mutantes, abaixo de 8.

Verificação, neste head: o teste novo passou (OK em 1,5 s). `bin/forge-mutante --processos 1 --ids R12,R13,R14,R15 tests/mutantes/v0478-pv-b1-registros-2.json` matou os 4 mutantes em `bin/forge-testes:920`. `bin/forge-mutante --cobertura --base 1aed3a74` deu `coberta · bin/forge-testes:920`, sem condição descoberta. A suíte inteira fica para o CI do PR, sem rerrodar o SHA (`R-REVIEW`). Os recomendados A1 a A4 do parecer anterior não estão no delta e seguem como cartão, sem promoção.
