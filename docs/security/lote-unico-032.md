---
tipo: revisao-seguranca
contrato: 1
pedido: lote-unico-032
branch: melhoria/lote-unico-032
commit: 9f32431def2214ca564c4d1968c48b726e2d8d45
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-03
---
# Review de segurança: lote-unico-032 (E2.1 do pedido lote-unico-032-REV, volta 2)

Revalidação por delta (`forge-check delta --parecer`, intervalo `0c90721..9f32431`) da volta 2: o merge da develop `6ef56a0` (#427 a #429) e as 8 correções (0e7f04a L16, 7eae698 L18, d58718a L13, 7d0f599 L15, bcad27a L49, c0c180e L35, 9b1e375 L31, 9f32431 L17), contra o modelo de ameaças `docs/security/ameacas/lote-unico-032.md`. O parecer anterior (`5b36740`, sobre `0c90721`) fica como base. Leitura do diff e testes dos módulos tocados (D-5); a suíte inteira é do QA. Veredito: **reprovado**, um bloqueante (A5, L35); as quatro recomendações anteriores seguem, a A1 só em parte resolvida.

## Gatilhos
`R-SEGURANCA`: controles do Forge tocados no delta (`bin/forge-check`, `tests/config.json`, `tests/test_forge.py`, `tests/mutantes/`). O merge da develop traz `hooks/_comum.py`, `hooks/conformidade.py`, os casos de `tests/hooks/conformidade/` e `.github/workflows/ci.yml`, mas cada um igual ao da develop `c6244ac` (os de `hooks/`, `tests/test_hooks.py`) ou a união das duas pontas (`ci.yml`, `tests/test_catraca.py`): já passaram pelos pareceres próprios aprovados (`docs/security/heredoc-comentario.md`, `heredoc-donos.md`, `ci-suite-no-teto.md`). Nenhuma classe de `hooks/` é deste lote.

## Achados
- A1 (recomendado) bin/forge-check:1941 · `fila` (L18) ainda executa o `.githooks/pre-push` da raiz quando o texto contém `[ "$1" = "--status" ]`; a marca é texto e um hook alheio a copia. Resolve o defeito do review (o hook do modelo não roda), não a forma (C-18): ler a trava com flock LOCK_NB.
- A2 (recomendado) bin/forge-check:553 · `gatilhos` casa o `gatilhos_seguranca` do plano técnico só pelo pedido exato; com o id trocado pelo slug o plano com `pedido: <id>` some. Casar pelo id e pelo slug (sem mudança no delta).
- A3 (recomendado) bin/forge-mutante:649 · `--processos K` (L33) não confere a trava da suíte (C-33b só no texto de `skills/qa-testing/SKILL.md`); sem mudança no delta.
- A4 (recomendado) bin/forge-check:2058 · o `custo total` (L16) soma `custo do trecho: N tokens` lido de toda a célula, motivo livre incluído; um `--motivo` com esse texto infla a medida. Ler só o sufixo que o `movimento` grava (sem mudança no delta).
- A5 (bloqueante) tests/test_forge.py:535 · L35, requisito (OK-11, A6 do review) e controle do Forge: a contagem do legado de `agents/jarvis.md` é 73 e o arquivo tem 51 trechos sem motivo; 22 trechos novos entram sem regra nem porque e o teste passa. Exigir contagem igual à real.

## Detalhe dos achados
**A5 (bloqueante, novo no delta).** Evidência: `tests/config.json:666` (`"agents/jarvis.md": 73`) e `tests/test_forge.py:534-535`, que só reprova quando os trechos sem motivo passam da contagem (`> n`). Hoje `agents/jarvis.md` tem 54 trechos em `invariantes`, 3 com motivo em `invariantes_motivo_trecho`: 51 cobertos pelo legado, contra 73 permitidos (os 22 trechos que a L51 levou para as skills não baixaram a contagem). Prova (a função `problemas_de_motivo` da branch sobre o `tests/config.json` da branch): hoje `[]`; com 22 trechos novos em `agents/jarvis.md` sem motivo, `[]`; com 23, a recusa. Os outros 33 arquivos do legado batem com a contagem. Caminho: quem acrescenta invariante ao núcleo do Jarvis (o arquivo de mais trechos e mais regras) nasce sem `regra` e `porque`, o oposto do que a correção c0c180e diz entregar ("trecho novo em arquivo do legado traz regra e porque"); a soma das contagens também não tem teto, então subir um número no `config.json` abre vaga sem aviso. Severidade baixa (o invariante segue protegido; falta só a justificativa), mas é requisito da especificação num controle do Forge com gatilho, por isso bloqueia. Correção mínima: (1) a contagem do legado passa a 51 em `agents/jarvis.md` e o teste exige igualdade (`!= n` em vez de `> n`), para a contagem só cair junto com os trechos; (2) um teto da soma, como o `LEGADO_SEM_MOTIVO_MAXIMO` dos arquivos (ex.: `LEGADO_TRECHOS_MAXIMO` = a soma corrigida), e um caso no `test_invariante_novo_sem_regra_ou_sem_porque_reprova` com contagem acima da real. Esforço P. Dono: tech-lead (dev do lote). Nada sai nem afrouxa em `invariantes` (conferido: nenhum trecho sumiu, `termos_proibidos_hash` igual, só entram `invariantes_motivo_trecho` e o legado vira contagem por arquivo).

**A1 (recomendado, em parte resolvido).** Evidência: `bin/forge-check:1940-1944`. O review (A2) provou que no projeto o hook do modelo rodava o `pre-push.local` e dava trava presa; a marca resolve esse caso (o `templates/projeto/.githooks/pre-push` não tem a marca, conferido; teste novo `test_hook_alheio_sem_o_status_do_forge_nao_e_executado_nem_vira_trava_presa`). Contra um autor hostil a marca não é fronteira: um hook com a linha `[ "$1" = "--status" ]` e outro código roda no `forge-check fila`. Mesmo usuário e mesma máquina, sem ganho de privilégio: segue recomendação, critério igual ao da volta 1. Correção mínima igual: ler a trava em Python (`fcntl.flock(LOCK_EX|LOCK_NB)` e soltar, com a recusa de link e de dono da `scripts/suite-paralela.py`), sem executar o hook. Esforço P. Dono: tech-lead.

**A2, A3, A4.** Sem mudança no delta (A3: `bin/forge-mutante` igual a `0c90721`); evidência, caminho e correção como na volta 1 (`5b36740`). A A4 mudou só de linha (`:2058`).

## Por correção (contra o modelo de ameaças)
- **6ef56a0 (merge da develop).** Pais `ebe3214` e `c6244ac`. `hooks/_comum.py`, `hooks/conformidade.py`, `tests/test_hooks.py` e os casos de `tests/hooks/conformidade/` iguais aos da develop; `ci.yml` = a lista do L01 mais os `timeout-minutes` 20/25/25 do #429 (nenhuma permissão, ação ou gate a mais); `tests/test_catraca.py` = as duas linhas (A7 do QA, A1 do devops); `tests/config.json` igual ao da branch (a develop não o mudou desde `b2580c6`). Sem resolução que perca lado.
- **0e7f04a (L16).** A soma passa por `somar_uso`, só os campos de `CAMPOS_USO`, inteiros positivos (bool fora); `usage` já exigido dict na leitura (`bin/forge-check:3677`). O valor gravado segue número ou `lacuna` (C-16b); gravação só pelo `movimento` (C-16a). Teste com o formato real (`server_tool_use` aninhado). Cumprido.
- **7eae698 (L18).** Ver A1. C-18 (não toma nem apaga a trava): o `--status` do Forge só testa; T-18 não ocorre.
- **d58718a (L13).** Só a expressão das linhas que reprovam (`:4021`); é medida, nenhuma recusa vira aviso (T-10), nada de trecho sai.
- **7d0f599 (L15).** A listagem soma `RAIZES_DE_BRIEF` (`~/.forge-contrib` ou a `--raiz-pedidos`); os nomes seguem filtrados por `[A-Za-z0-9._-]+` e sem link; só stdout, nenhum portão lê (C-15a a C-15c).
- **bcad27a (L49).** Só leitura do histórico já carregado (C-49).
- **c0c180e (L35).** Ver A5. C-35 cumprido na parte "nada sai nem afrouxa"; a exigência nova por trecho tem a vaga de 22.
- **9b1e375 (L31).** Só o teste apontado pelo M6 da spec; teto de produção e `hooks/` intactos (C-31).
- **9f32431 (L17).** O estado `em curso` exige verbo de início na linha; o texto segue dado, por `sem_controle`, e a saída só stdout (C-17a, C-17b).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: `forge-check delta --parecer` (vigente 0.31.0, `~/.local/share/forge/vigente/bin/`), leitura do diff `0c90721..9f32431` e do merge contra os dois pais, prova do A5 com a `problemas_de_motivo` da branch, e os testes dos módulos tocados (D-5): `tests.test_decisoes`, `test_fila_ocupacao`, `test_proximo`, `test_sobreposicao_quadro`, `test_voltas`, `test_forge.RegrasInviolaveis`, `test_forge.MedirAlucinacao`, `test_catraca.Workflows`: 105 testes, OK (rc 0). Lacunas: `gitleaks`, `actionlint`, `zizmor`, `semgrep` e `osv-scanner` fora do PATH; o CI cobre o passo de segredos.
