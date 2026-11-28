---
tipo: review
contrato: 1
pedido: v048
branch: melhoria/v048-forge-copia-origem
commit: 6c8fd19ce2675be5c3206cf2fcba6679886ded1d
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-28
---
# Review: v048 (E4.4, PR #956, FORGE-COPIA-ORIGEM-LOCAL e FORGE-COPIA-D2)

1ª rodada completa no head 6c8fd19c (Base-sha a90a7a93), classe C. Cópia própria criada por `forge-copia clone ... --revisao`.

## Ferramentas (citadas, sem refazer)
- ci: 6c8fd19ce2675be5c3206cf2fcba6679886ded1d verde (`gh pr checks 956` rc=0; runs 46136867176 e 46136867271 no headSha 6c8fd19c, `completed success`; suíte 5/5, catraca e catraca (conferência), instalação, teto de pulados, árvore provada).
- Ordem do dono 28/11 07:41 (diff toca bin/): catraca do CI verde e `python3 tests/catraca.py --modo regras --base a90a7a93 --head HEAD` rc=0 local; o teste de custo (`tests.test_hooks_volta_corpus`) está nas partes da suíte do CI, verdes; local passou do teto de 160 s sem falha e não foi refeito.
- Afetados: `python3 -m unittest tests.test_forge_copia tests.test_forge_copia_nome` 112 testes OK.
- Mutantes: `bin/forge-mutante --processos 1` nas três specs: M1 a M20 morreram; `--cobertura --base a90a7a93`: toda condição mudada coberta (330 isenta com motivo, coberta pelo M16); `--conferir --base a90a7a93`: trechos no lugar, inclusive as 4 specs antigas editadas no E4.3.

## Leitura (checklist da skill engineering-practices)
- Escopo: as quatro correções do brief do E4.1 (origem local pela URL do remoto ou recusa; branch do remoto como ponto de partida também na worktree; a worktree que falha apaga só a branch nova; `--d2` destacado na base), nem mais nem menos. Docstring do módulo e fragmento do changelog atualizados.
- Desenho: `worktree()` reusa `ponto_de_partida` e `falha_do_ponto` do clone, sem duplicar regra; o `update-ref -d` com o sha antigo só apaga a branch se ela ainda aponta para o ponto, e só quando ela não existia antes. `origem_real` devolve (valor, motivo) no padrão de `destino_dentro`.
- Guardas: uma por mutante (R-QA), cada uma com teste de ramo de falha por comportamento (subprocesso com `python3 -I` e ambiente próprio), nenhum lendo a fonte.
- Tamanho (H1): 51+ 11- em `bin/forge-copia`, dentro do teto; os três comportamentos vêm juntos por decisão do brief do E4.1 (dois cartões juntados).
- Commits: Conventional Commits em português, um por passo (fix, testes, alinhamento das specs, merge da develop pelo E4.2).
- Segurança e credenciais do clone pela URL do remoto: parecer da segurança (E4.5), não refeito aqui.

## Achados
- A1 (recomendado) bin/forge-copia:169 · repositório bare local em --origem vira o remoto origin dele: bare clonado (com origin) clona da fonte dele, não do bare dado; bare sem origin é recusado, e antes clonava. Contorno: file://. Sugestão: só converter quando `rev-parse --is-bare-repository` é false.

## Parecer
Aprovado. O código faz o que os cartões pedem, com teste de comportamento e mutante morto por guarda, CI do head verde e catraca verde. O A1 (sondado numa pasta temporária: bare com origin nasceu em b442dd7c, o head da fonte, e não em fa4870e8, o head do bare; bare sem origin saiu com rc 2, e com `file://` clonou) está dentro do texto decidido no brief ("ou recusar com a mensagem certa") e tem contorno, por isso é recomendado: vira cartão depois do merge.
