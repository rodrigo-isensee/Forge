---
tipo: qa
contrato: 1
pedido: lote-coment-prepush
branch: melhoria/lote-coment-prepush
commit: bcdb3b9cd07aae4b8d3efd8af274888cd77807f1
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-27
---
# QA: lote-coment-prepush

Pedido LOTE-COMENT-PREPUSH-REV (E3.1). Só texto: README (Suíte do Forge) e docstring de `bin/forge-testes`; nenhum comportamento muda. Base 739b0b083d2baacefdf4f7482b2b2ac31ed8e02c, head bcdb3b9.

## Achados
- A1 (recomendado) README.md:68 · o texto diz que "qualquer outro arquivo" cai na suíte inteira, mas não cita que `docs/security/ameacas/` e `docs/security/aceites/` (além dos modelos `_*`) também caem, embora o hook os recuse no caminho curto; imprecisão leve, sem efeito no comportamento
- A2 (recomendado) .githooks/pre-push:236 · o comentário do hook ainda diz "decisão do dono, 2026-10-23: A" (a decisão vigente é a M8 de 2026-10-24); fora do escopo do lote (tocar o hook faria o pre-push cair na suíte inteira), fica para lote próprio

## Critério → teste → resultado
Sem especificação de UX nem `CA-n` neste pedido; as obrigações são as do escopo E1 do pedido.

| Obrigação | Teste | Resultado | Fronteira protegida |
|---|---|---|---|
| E1: README cita os casos de suíte inteira (`bin/forge-testes`, `tests/config.json`, `.githooks/`) e o caminho só de parecer (`docs/reviews/`, "só acrescenta pareceres") | `tests.test_forge.PrePushSoOsAfetados.test_readme_cita_os_casos_da_suite_inteira_e_o_caminho_so_de_parecer` | passa no head; falha na base (vermelho) | n/a |
| E1: docstring de `bin/forge-testes` cita M8, 2026-10-24 e "substitui" | `tests.test_testes_tocados.NaoEPortao.test_docstring_cita_a_decisao_m8_de_2026_10_24` | passa no head; falha na base (vermelho) | n/a |
| E1: só texto, nenhum comportamento muda | diff (5 arquivos: README, docstring, changelog, 2 testes) + módulos `test_forge` e `test_testes_tocados` inteiros | 510 testes OK | n/a |

## Conferência do README contra o hook (`.githooks/pre-push` no head)
- Branch fora de `melhoria/*`: `dirigido` exige `refs/heads/melhoria/*` (linha 252). Confere.
- Caminho sem regra no mapa e falha de leitura do plano: o plano só vale se a primeira linha começa por `forge-testes: dirigido (` (linhas 266-267); qualquer erro ou outra saída cai na suíte inteira. Confere.
- Diff que toca `bin/forge-testes`, `tests/config.json` ou `.githooks/`: linha 265 devolve 1, suíte inteira. Confere.
- Push só de parecer: `so_parecer` (210-235) exige prova de árvore, ref única existente, delta só em `docs/{reviews,security,qa,devops}/` e roda as classes `Neutralidade`, `Referencias`, `AntiDuplicacao`, `NeutralidadeDoNucleo`. Confere; a exceção de `ameacas/`, `aceites/` fica em A1.
- Sem ref e só remoção: linhas 140-155 do hook, texto antigo preservado. Confere.
- O README não descreve caso que o pre-push não faça.

## Vermelho antes do verde
`python3 bin/forge-testes --vermelho 739b0b083d2baacefdf4f7482b2b2ac31ed8e02c --modulos test_forge,test_testes_tocados` (rc 0):
```
vermelho: base=739b0b083d2b head=bcdb3b9cd07a módulos=test_forge,test_testes_tocados (restrito por --modulos)
revertidos à base: README.md, bin/forge-testes, changelog.d/lote-coment-prepush.md
mantidos no HEAD: tests/test_forge.py, tests/test_testes_tocados.py
tests.test_forge.PrePushSoOsAfetados.test_readme_cita_os_casos_da_suite_inteira_e_o_caminho_so_de_parecer · H=ok · B=falha · prova (asserção)
tests.test_testes_tocados.NaoEPortao.test_docstring_cita_a_decisao_m8_de_2026_10_24 · H=ok · B=falha · prova (asserção)
contagem: não prova (passa na base)=508; prova (asserção)=2
```

## Execução
`python3 -m unittest tests.test_forge tests.test_testes_tocados` no head: Ran 510 tests, OK. Suíte completa e CI não rodados aqui (o pre-push e o CI do PR cobrem). Mutação: não se aplica (sem código de `bin/` alterado além da docstring; nenhuma linha de guarda mudada).

## Parecer
Aprovado. Zero bugs; duas recomendações que não devolvem.
