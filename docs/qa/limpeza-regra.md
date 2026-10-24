---
tipo: qa
contrato: 1
pedido: limpeza-regra
branch: melhoria/limpeza-regra
commit: 502185f51a163862707d60e0ce8d5dd7281dfd30
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-23
---
# QA: limpeza-regra

## Achados
- A1 (recomendado) bin/forge-fechar:57 · classe: script x texto · o script só recusa main, develop e homolog como --ref; com `master` e PR falso MERGED ele apagou a branch local e tentou a remota, enquanto os textos dizem nunca master; o Forge não tem master, então só vale ao endurecer o script (fora deste pedido)

## Critério → teste → resultado
Não há especificação de UX nem CA-n (mudança de texto de regra); as obrigações são as da decisão do dono e do escopo E1/E2 do pedido.

| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Branch de trabalho com PR mesclado e head igual: apaga sem perguntar | CT-01 | head remoto = local = headRefOid | passou |
| Head remoto diferente do PR: pergunta | CT-02 | head remoto além do PR | passou |
| Commit local a mais: pergunta | CT-03 | head local além do PR | passou |
| develop, homolog, main nunca apagadas, mesmo como head de PR mesclado | CT-04 | branch longa | passou |
| master nunca apagada | CT-05 | branch longa sem guarda no script | passou nos textos; script sem guarda (A1) |
| Cinco textos dizem a mesma coisa em cada caso | CT-06 | lista de exceção, headRefOid, commit local a mais | passou (ressalvas do review A3 a A5, recomendadas) |
| Testes que leem os arquivos tocados | CT-07 | n/a | passou |

## Cenários e resultado real
- CT-07: `bin/forge-testes --base origin/develop` (dirigido: test_changelog, test_doutor, test_forge, test_modelos_citados, test_novo_projeto, test_sobreposicao_quadro): 597 testes, OK (skipped=1), 106 s. A suíte completa roda no pre-push, não aqui. Mudança só de texto: sem vermelho antes do verde nem mutação (sem código de produção no diff).
- CT-01 a CT-05: repositório de sonda em `$TMPDIR/qa-limpeza/` (HOME próprio, remoto bare local, sem rede), com `gh` falso (`FORGE_FECHAR_TESTE=1`) e `bin/forge-fechar T --ref <branch> --limpar` do commit testado, que implementa a limpeza descrita na `R-FLUXO` e em `docs/fechamento-integrador.md`.
  - `melhoria/ok` (MERGED, head igual): remota, worktree e local apagadas, rc 0.
  - `melhoria/remdif` (remoto à frente do PR): nada apagado, rc 3, comandos impressos (pergunta ao dono, como o texto).
  - `melhoria/localmais` (commit local não enviado): remota apagada (head remoto = PR), local pendente, rc 3 (`R-FLUXO` passos 1 e 2).
  - `develop`, `homolog`, `main`: recusadas, rc 1, nada apagado.
  - `master`: sem recusa; a local foi apagada e a remota tentada (o remoto bare recusou só por ser a HEAD dele). Achado A1.
- CT-06: leitura dos cinco textos contra cada caso. `R-VERIFY:13`, `R-FLUXO:18` e `:24`, `jarvis.md:72` e `tech-lead.md:29` trazem a lista (main, master, develop, homolog, integração do projeto), o `headRefOid` e a restrição à branch de trabalho; `jarvis`, `tech-lead`, `R-FLUXO` e `fechamento-integrador:20` trazem o commit local a mais pedindo confirmação (a `R-VERIFY` trata só do head remoto, correto). O `fechamento-integrador` descreve o script e não cita a lista de branches (o script recusa três delas). Em cada caso simulado a resposta dos textos é a mesma do script, exceto `master` (A1). Os achados A3, A4 e A5 do review (lista residual e "já na base") continuam recomendados, sem efeito sobre a resposta de nenhum caso.

## Parecer
Aprovado: nenhum bug aberto; um achado recomendado (A1), de script, fora do escopo de texto do pedido. Sonda descartável em `$TMPDIR/qa-limpeza/`.
