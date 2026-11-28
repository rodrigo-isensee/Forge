---
tipo: review
contrato: 1
pedido: v048
branch: melhoria/v048-forge-copia-origem
commit: 997eb63ab95b171b5829ac901939a138d095df77
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-28
---
# Review: v048 (E4.4 e E4.7, PR #956, FORGE-COPIA-ORIGEM-LOCAL e FORGE-COPIA-D2)

## Volta 1 (E4.7, delta no head 997eb63a)
Delta lido: `forge-check parecer delta docs/reviews/v048-forge-copia-origem.md`, intervalo 6c8fd19c..997eb63a sem o que veio da develop: `bin/forge-copia`, `changelog.d/v048-forge-copia-origem.md`, `tests/mutantes/v0475-copia-pasta.json`, `tests/mutantes/v048-forge-copia-origem.json`, `-2.json`, `-3.json` e `tests/test_forge_copia.py` (commits 9bc85463, d9d3b884, 997eb63a). Cópia própria `wt/v048-forge-copia-origem-tech-lead-3` por `forge-copia clone ... --revisao`, no 997eb63a.
- ci: 997eb63ab95b171b5829ac901939a138d095df77 verde
- suíte: 997eb63ab95b171b5829ac901939a138d095df77 rc=0 módulos=test_forge_copia,test_textos_ci_custo,test_doutor_custo
- Origem do CI: runs 46143981499 (CI) e 46144033235 (Catraca) no headSha 997eb63a; suíte 5/5, instalação, teto de pulados, verificações longas, passos, catraca e catraca (conferência) verdes; `bateria (pareceres)` e `bateria` vermelhas só por `PARECERES: failure` (esperam este parecer).
- Ordem do dono 28/11 07:41 (diff toca bin/): catraca e catraca (conferência) verdes no head; o teste de custo está nas partes da suíte do CI, verdes, e `test_textos_ci_custo test_doutor_custo` local deu 16 OK.
- Afetados (local): `Worktree`, `Recusa` e `Cria` de `test_forge_copia`, 27 testes OK.
- Mutantes refeitos por mim (R-PROVA): `bin/forge-mutante --processos 1 --ids M8,M9,M21` nas três specs do pedido: M8 (linha 192), M9 (189) e M21 (194) morreram, rc=0; `--ids M6,M9` em v0475-copia-pasta: M6 (345) e M9 (189) morreram, rc=0. `--cobertura --base 17805e08` (o merge da develop): toda condição mudada do delta declarada (189, 192, 194; a 186 da base apagada).
- Leitura do delta: A1 da segurança resolvido. `update-ref <ref> <sha> ""` só cria a branch que não existe (sondado numa pasta temporária: a segunda criação sai 128 com "reference already exists"; nome inválido como `a..b` sai 128, a mesma recusa que o `-b` dava); o add roda sem `-b` sobre a branch já criada, sem rastreio (o `update-ref` não grava `.git/config`); o `update-ref -d <ref> <sha>` apaga só a branch que ainda aponta para o sha que ele gravou. O teste da sonda S8 embrulha o git no PATH, cria a branch antes do `update-ref -m` e prova rc 1, a branch do outro processo intacta e nenhum "apaguei"; mata o M9 da spec -2. A1 e A2 do QA resolvidos: o M6 lista `Recusa.test_origem_com_cara_de_opcao`; as três specs declaram `pedido: v048-forge-copia-origem`. Changelog e docstring acompanham. Tamanho: 56+ 11- em `bin/forge-copia` contra a base, dentro do teto (H1).
- A3 do QA (contagem do corpo): os 14 testes de `OrigemLocal`, `Worktree` e `D2` batem (4+5+5); restam duas contagens velhas no corpo (A2 abaixo), sem efeito no código.

## 1ª rodada (E4.4, head 6c8fd19c)

1ª rodada completa no head 6c8fd19c (Base-sha a90a7a93), classe C. Cópia própria criada por `forge-copia clone ... --revisao`.

## Ferramentas (citadas, sem refazer)
- CI da 1ª rodada: 6c8fd19ce2675be5c3206cf2fcba6679886ded1d verde
- Suíte da 1ª rodada: 6c8fd19ce2675be5c3206cf2fcba6679886ded1d rc=0, módulos test_forge_copia e test_forge_copia_nome
- Origem do CI: `gh pr checks 956` rc=0; runs 46136867176 e 46136867271 no headSha 6c8fd19c, `completed success`; suíte 5/5, catraca e catraca (conferência), instalação, teto de pulados, árvore provada.
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
- A2 (recomendado) tests/mutantes/v048-forge-copia-origem-3.json:46 · o corpo do PR #956 ficou com contagens velhas na volta 1: diz "M1 a M20" (há o M21, aqui) e "51 linhas acrescentadas" (são 56 em bin/forge-copia contra 21aada57). Sugestão: atualizar o corpo antes do fechamento.

## Parecer
Volta 1: aprovado no 997eb63a. Os três achados da volta (A1 da segurança, A1 e A2 do QA) estão resolvidos com teste de comportamento e mutantes mortos, refeitos aqui; CI do head verde fora os checks que esperam o parecer. O A2 é só do corpo do PR, recomendado: vira cartão ou se acerta no fechamento.

1ª rodada: aprovado. O código faz o que os cartões pedem, com teste de comportamento e mutante morto por guarda, CI do head verde e catraca verde. O A1 (sondado numa pasta temporária: bare com origin nasceu em b442dd7c, o head da fonte, e não em fa4870e8, o head do bare; bare sem origin saiu com rc 2, e com `file://` clonou) está dentro do texto decidido no brief ("ou recusar com a mensagem certa") e tem contorno, por isso é recomendado: vira cartão depois do merge.
