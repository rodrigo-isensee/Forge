---
tipo: revisao-seguranca
contrato: 1
pedido: v0457
branch: melhoria/v0457
commit: 9f5e7f6b9c2e4fdeb26a5819fd71fceee77d2b1e
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-11
---
# Review de segurança: v0457 E23.6 (junção da 0.45.7)

Head revisado `7c6dd9df` (igual ao `origin/melhoria/v0457`), base `36d976df`. Leitura estática, sem escrita na branch: worktree destacada em `~/.forge-contrib/wt/sec-v0457-junc`. A junção traz 21 frentes já revisadas uma a uma; aqui se confere a montagem: os merges, o que mudou depois das frentes e se o head junta tudo sem perder correção.

## Gatilhos
`R-SEGURANCA`: a junção toca controles do Forge (`hooks/conformidade.py`, `hooks/parecer.py`, `hooks/_comum.py`, `hooks/doutor.py`, `.githooks/pre-push`) e afrouxa um invariante de `tests/config.json` (`R-TETO`).

## Parecer
Aprovado (vale para `9f5e7f6b`; a seção "Revalidação por delta" abaixo traz a volta 1).
- **Frentes completas.** As 24 branches locais `melhoria/v0457-*` (as 21 frentes, `e1b` e a `envio-sandbox` que veio pela develop) têm a ponta como ancestral do head. Fora da junção, por escopo do pedido: E8.4 (espera a E8.2 na develop), E9.2 (sem envio) e E3.2 (o campo `ritmo` não está em `templates/projeto/.forge/config.json`).
- **Merge da develop (`7c6dd9df`).** Segundo pai `36d976df` (#488 e #489). Merge limpo: `git merge-tree --write-tree 792bc9a1 36d976df` dá a mesma árvore do commit (`1d301b6c`), e `git show --cc` vem vazio. Os dois arquivos que os dois lados tocam (`tests/test_hooks.py` e `tests/test_testes_tocados.py`) só recebem da develop as chamadas `exigir(self, "proc")`. A lista fechada da ENVIO-DO-SANDBOX continua íntegra no head: `tests.test_apoio_sandbox` passa, com 22 testes.
- **Merges das frentes.** 17 dos 21 são limpos (mesma árvore do recálculo). Quatro foram resolvidos à mão, conferidos com `--remerge-diff`:
  - `f518cefe` (dora): só `bin/forge-testes` e a contagem de `tests/test_testes_tocados.py`, com as duas listas somadas.
  - `c2287ee9` (f6-5): só a contagem.
  - `4bb2fe40` (rverify-fp): só `docs/hooks-fixtures.md`.
  - `e0c45519` (profundidade × rverify-fp), o único em controle, em `hooks/conformidade.py:1101-1102` e `:2662-2668`. A resolução fica com a mais restritiva das duas: acima de `PROFUNDIDADE`, `barrar(*PROFUNDIDADE_EXCEDIDA)` encerra com saída 2 em toda sessão. A `GuardaDaProva` também deixa passar essa recusa, e as outras recusas seguem a semântica da E16.1. O mutante M7 da rverify-fp sai porque o trecho que ele mutava não existe mais. O P3 da profundidade foi refeito para o código novo e morre.
  - O índice `docs/hooks-fixtures.md` está em dia (`scripts/indice-fixtures.py --conferir`).
- **Mudanças depois das frentes** (E23.1 e E23.2, `6f457571..792bc9a1`, 13 arquivos). São mapa de testes, contagens, ambiente git dos testes (`sem_manutencao`), `ids()` reconhecendo `R-WIP` e textos encurtados.
  - Dois pontos tocam controle. O primeiro: os motivos dos invariantes de `hooks/parecer.py` (FILA-27 A2) trocam `R-CONTRIB` por `R-LIMITES`, e os padrões continuam iguais (`tests/config.json:684-686`).
  - O segundo: o invariante "A suíte inteira segue serial" vira três (`tests/config.json:401-403`). O afrouxamento está declarado com motivo e medida em `changelog.d/v0457-e4.md:3`, e a decisão do dono é de 2026-11-10 (E4.1).
  - O texto encurtado de `docs/regras/R-TETO.md:16` perdeu "sem medida, uma depois da outra", mas o código falha fechado: `scripts/suite-partes.py:147-151` não dá folga sem medida.
- **Controle novo sensível revisto na montagem.** `so_do_usuario` (`hooks/_comum.py:2477-2490`) recusa pasta de outro dono ou gravável por outros, e as pastas acima também, salvo com sticky bit. Junto com a recusa de link e de `.`/`..` (`:2466`), a pasta só entra no fim do PATH. O `CLAUDE_ENV_FILE` recebe a pasta com `shlex.quote` (`hooks/doutor.py`, `caminhos_na_sessao`). Não achei caminho de ataque.
- **Testes dos arquivos tocados.** Todos passaram:
  - 62 testes: `test_fixtures_da_profundidade`, `test_fixtures_do_rverify_falso_positivo`, `test_ritmo`, `test_forge_dora`, `test_reval_delta`, `test_testes_tocados.Mapa` e `test_r_limites`.
  - 182 testes: `test_hooks_fila27`, `test_vigia`, `test_doutor`, `test_forge_dono` e `test_esperar_estado`.
  - Mutantes `v0457-profundidade`: P1 a P5 mortos. Mutantes `v0457-rverify-fp`: M1 a M5 mortos e M6 equivalente, com motivo.
  - Tudo rodou com load1 < 12. Os 4 fixtures `agentes/*` do `test_hooks` (sandbox) ficaram fora, como diz o brief.
- **Segredos e CI.** Nenhum padrão de token ou chave nas linhas adicionadas. O diff não toca `.github/`. O shellcheck passa em `.githooks/pre-push` e em `bin/forge`.

## Revalidação por delta (volta 1: 7c6dd9df..9f5e7f6b)
Head `9f5e7f6b` (igual ao `origin/melhoria/v0457`), leitura em worktree destacada `~/.forge-contrib/wt/sec-v0457-r2`. O delta é o merge da develop `6cfde7e0` (segundo pai `2b896503`: #490 a #494, backlog-lote-1111 e ci-lote-e1), mais `047df241` (M2) e `9f5e7f6b` (índice).
- **A1 fechado.** `docs/regras/README.md:20-22` fica com os links `R-LIMITES.md#r-copia-...` e `#r-verify-...` (as âncoras existem em `R-LIMITES.md:26` e `:59`) e com o `R-DECISAO` da develop ("uma a uma, com opções e recomendação, sem prazo que decida"). O `docs/regras/R-DECISAO.md` do head é idêntico ao da develop.
- **Nada ficou mais fraco nos conflitos (`--remerge-diff`).** Três conflitos, todos de texto: o README acima; `docs/economia-de-tokens.md` (as regras 9 a 11 da develop ficam e o Ritmo vira a 12, com `skills/falar-com-o-dono/SKILL.md:20` citando a 12); `tests/test_reval_delta.py` (contagens somadas das duas listas, `test_conferir_reversao.py` em 14, a da develop, e a entrada da R-WIP mantida).
- **Fora dos conflitos, o head é a develop.** `git diff 2b896503 9f5e7f6b` não toca `.github/`, `agents/`, `docs/regras/R-DECISAO.md`, `R-QA.md`, `bin/forge-fechar` nem `scripts/suite-paralela.py`: o `agents/jarvis.md` voltou ao teto e ao texto da develop, e o CI da develop (ci.yml, passos baratos, `needs`) chega sem mudança.
- **Invariantes de `tests/config.json`.** Os que a develop acrescentou (modo-iniciante, falar-com-o-dono, "Sem resposta, fica pendente", "Uma por vez", "Sem prazo vencido") seguem no head. Os que a junção já tinha seguem (R-LIMITES, FILA-27 A1/A2, três da suíte em partes). Não sumiu invariante de nenhum lado.
- **Mapa de testes.** O M2 de `tests/mutantes/v0457-testes-mapa.json` agora inclui a linha seguinte (`modulo = "test_" + sub.group(1)`), com o `de` presente uma vez em `bin/forge-testes`; M1 a M8 morrem.
- **Testes rodados (os dos arquivos tocados).** `test_reval_delta`, `test_testes_tocados` e `test_r_limites` (160 testes, ok), `test_forge` inteiro (OK, com `AntiDuplicacao` e o regras-ID) e `scripts/indice-fixtures.py --conferir` (em dia). Load1 abaixo de 12.
- Os pareceres e os fragmentos que a develop traz (`docs/security/v046*.md`, `backlog-ate-sexta.md`) são dela e já tinham gatilho revisto; não os reabri.

## Achados

## Sondas

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas usadas: git (`merge-tree`, `--remerge-diff`), shellcheck, `bin/forge-mutante` e unittest, todas locais e passivas. Ausentes do PATH, e não instaladas (`R-CUSTO`): gitleaks, osv-scanner, semgrep, zizmor, actionlint e trivy. Os segredos foram procurados por grep de padrões nas linhas adicionadas, e o CI do projeto segue como o portão das varreduras.
