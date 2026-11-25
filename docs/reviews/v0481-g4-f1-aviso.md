---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-g4-f1-aviso
commit: eb747918dc99b4fd57c67846a28f6e87bc1c4c4d
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-25
---
# Review: v0481 (E7.41, #885, G4 F1: modo aviso por grupo, só infra; classe C), revalidação por delta

Delta lido (`forge-check parecer delta docs/reviews/v0481-g4-f1-aviso.md`, sem o que veio da develop): intervalo `3682aeba..eb747918`, no domínio `hooks/conformidade.py`, `tests/test_hooks.py`, `docs/hooks-fixtures.md`, `tests/mutantes/v0478-guardas-conformidade.json`, `tests/mutantes/v0479-conformidade-sessao-forge-2.json`, `tests/mutantes/v0481-g4-f1-aviso-2.json` e `tests/mutantes/v0481-perfil-fifo.json`. Volta E7.36: a develop entrou com o #886 (A2 da segurança: o texto da recusa não lê o perfil por FIFO nem chama `git`), e o autor realinhou as specs de mutante (commits `e1721df1` e `9b93d179`). Por ordem do dono (25/11), conferi só a correção e o que o delta mudou. Parecer anterior: aprovado em `3682aeba` (E7.12).

## Conferência do delta
- **Mescla em `Guarda.barrar`** (`hooks/conformidade.py:1596-1620`): as duas mudanças ficaram juntas e na ordem certa. Primeiro decide o modo (`avisar` sai antes). Depois escolhe o texto pelo `perfil_iniciante` do #886, sem `git` e sem esperar FIFO, com o `PrazoVencido` engolido só na escolha. Depois grava o registro do G4 F1, que também engole o prazo. Por fim, `bloquear`. Nenhum dos dois passos troca a decisão. O `self.h.iniciante()` ficou só no `perguntar` e na leitura do `.forge/perfil` (`:1624`, `:1782`), fora do caminho da recusa.
- **Specs realinhadas** (AR-12, corrigido pelo autor antes do review): M1 do v0478 e M15 do v0479 seguem a mesma guarda nas linhas que ganharam `alvo=`/`grupo=`. O M16 do G4 F1 vai para a condição `perfil_iniciante`. O M2 e o M5 do perfil-fifo ganharam contexto para casar uma linha só. O M7 segue o `texto = texto or com_trecho(...)`. Cada `de` existe uma vez na fonte do head.
- **Mutantes (V2):** `bin/forge-mutante --processos 1 --ids` com os realinhados, no head `eb747918`: v0478 M1 morreu (`:4249`), v0479 M15 morreu (`:3211`), G4 F1 M16 morreu (`:1610`), perfil-fifo M2 morreu (`:1551`), M5 morreu (`:1611`) e M7 morreu (`:1614`).
- **Testes do item:** `python3 -m unittest tests.test_hooks.ModoPorGrupo tests.test_hooks.RecusaComFifoNoRegistro tests.test_hooks.RecusaComFifoNoPerfil tests.test_hooks.HookSessaoDoForge.test_travas_do_conformidade tests.test_conformidade_verde.EstadoDoAgentesNoClone`: 30 testes, OK (78 s).
- **`docs/hooks-fixtures.md`:** índice regenerado, com 3583 fixtures e as 3 `grupo-barrar-*` do item. Só contagem.
- **Tamanho (H1):** o delta próprio da branch não acrescenta código. São a resolução da mescla e 12 linhas de spec. O item continua no teto.
- **CI do head** (run 45652397890 e 45652397973, em `eb747918`): as 5 partes da suíte em 3.12 e 3.14, os passos, as verificações longas, a instalação, o teto de pulados e a árvore provada estão verdes. Ficam fora, à espera do parecer ou do rótulo, três jobs:
  - `bateria (pareceres)`: este parecer estava desatualizado (`docs/hooks-fixtures.md` mudou depois de `3682aeba`), e o da segurança não estava aprovado.
  - `bateria`: agrega o de pareceres (`pareceres: failure`).
  - `catraca`, pelo log: há mudança em `hooks/conformidade.py` e as chaves novas `modo_por_grupo`/`modo_por_grupo_descricao` em `hooks/conformidade.json`. Os pulos subiram de 38 para 41, e `tests/test_hooks.py` foi de (618, 6, 0) para (644, 9, 0). Os pulos novos são `skipUnless` de plataforma (sem FIFO ou alarme), e as asserções subiram. Por isso a catraca pede o rótulo `afrouxa-regra` do dono, que é o caminho da classe C. Nada disso é novo no delta.
- ci: eb747918dc99b4fd57c67846a28f6e87bc1c4c4d verde

## Achados
- A3 (recomendado) hooks/conformidade.py:1606 · do parecer anterior, sem mudança: o aviso vai ao stderr com saída 0, e o registro do aviso (:1605) fica sem o except PrazoVencido. Resolver na F4.
- A4 (recomendado) docs/propostas/g4-fatias.md:36 · do parecer anterior, sem mudança: a recusa falsa conta toda linha com alvo nulo, sem filtrar fonte=conformidade.
- A5 (recomendado) tests/test_hooks.py:4482 · do parecer anterior, sem mudança: a RecusaComFifoNoRegistro mede o gasto e não o confere.
- A6 (recomendado) tests/mutantes/v0481-g4-f1-aviso-2.json:76 · depois do realinhamento, o M16 tem o mesmo `de` e `para` do M4 de tests/mutantes/v0481-perfil-fifo.json:37. É o mesmo mutante duas vezes, um run a mais por volta. Fique com um só.

## Parecer
**Aprovado** no head `eb747918`. A mescla com o #886 preserva a recusa decidida antes do texto e do registro, e os mutantes realinhados morrem. A3 a A6 são recomendados e viram cartão depois do merge. Para o merge faltam o parecer de segurança aprovado e o rótulo `afrouxa-regra` do dono (catraca, classe C).
