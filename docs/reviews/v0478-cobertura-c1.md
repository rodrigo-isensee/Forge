---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0478-cobertura-c1
commit: 67ef9dfbfc2d252ed7d82a7bd34269b5801291db
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-18
---
# Review: v0478 (E9.2, COBERTURA-ESTUDO C1, T1 como portão)

Diff `4182a6b9...c4ddc61d`: `tests/catraca.py` (+35 linhas de código, abaixo do teto H1, um comportamento), `tests/test_catraca.py` (classe `T1NoTextoDoPr`, 10 testes), duas specs de mutantes (11 guardas), `docs/engineering/praticas.md` (linha do T1) e o fragmento `changelog.d/v0478-cobertura-c1.md`.

## Conferido
- **Aperta, não afrouxa.** O modo `pr-texto` passa a somar `violacoes_do_t1` às violações do texto; nada sai. A regra de código, teste e classe é a do `forge-check` (`codigo_sem_teste`, `classe_para_o_t1`), sem duplicar mecanismo. Falha fechada: diff dos testes ilegível levanta `ErroDeGit`, que o `_main` torna vermelho; classe ilegível vale N. O passo só roda com `base_ref == develop`, então as promoções não mudam. O workflow já reage a `edited`, então a seção `## Sem teste` escrita depois reavalia o PR. Nenhuma linha de `invariantes` nem de `docs/regras/` foi tocada.
- **Citação por arquivo.** `citado` exige o caminho inteiro (bordas `[\w./-]`); `secao` tira os comentários HTML, então o comentário do modelo não conta como justificativa. O motivo é medido sem os caminhos (`MINIMO_SECAO`).
- **Custo de tempo.** O autor declara 0,41 s → 0,78 s (mediana de 5). Remedido aqui, mediana de 5, mesmo corpo, `--base 4182a6b9`: base 0,29 s → head 0,57 s. O acréscimo de cerca de 0,3 s vem de carregar o `forge-check` e calcular a classe. Num job de cerca de 1 min, é desprezível e não abre run novo (`R-CUSTO`).
- **Testes e mutantes.** `python3 -m unittest tests.test_catraca.T1NoTextoDoPr`: 10 testes OK. Mutante M4 aplicado à mão numa cópia (`if not faltam:`): `test_motivo_curto_barra` falha, então o mutante morre. A fila `R-TETO` estava ocupada, então a bateria do `forge-mutante` fica com o QA (E9.4). Cada guarda do diff tem mutante com teste do ramo de falha, e nenhum teste lê o texto da fonte.
- **Suíte.** Não rodei a suíte inteira, como o brief manda: vale o CI do PR.
- **Ressalva do autor sobre `.github/pull_request_template.md`.** Ela procede. O comentário da linha 14 ainda descreve a seção como aviso do `forge-check pr` que o review confere. Não diz que o CI barra nem que é preciso citar cada arquivo. Isso não quebra nada, porque `secao` ignora o comentário, mas induz o autor ao erro (A1).

## Revalidação no head 67ef9dfb (E9.6)
Delta lido: `forge-check parecer delta docs/reviews/v0478-cobertura-c1.md`, intervalo `c4ddc61d..67ef9dfb`, 8 arquivos no domínio (modelo do PR, `catraca.yml`, fragmento, `praticas.md`, `catraca.py`, as duas specs de mutantes, `test_catraca.py`).
- **A1 resolvido.** `.github/pull_request_template.md:14` diz que a seção é obrigatória, que a catraca do CI barra o PR sem ela e que cada arquivo vai com o caminho inteiro e o motivo.
- **A2 resolvido.** A violação do T1 aponta `docs/engineering/praticas.md` (`catraca.py`, `violacoes_do_t1`), com o teste `test_violacao_aponta_a_regra_nas_praticas`.
- **A3 resolvido.** O passo de regras grava `CATRACA_DA_BASE` antes de rodar o script, e o passo `pr-texto` roda `python3 "${CATRACA_DA_BASE:-tests/catraca.py}" --modo pr-texto --base "$(git rev-parse HEAD^1)"`. Assim a catraca e o `forge-check` ao lado dela vêm da base, e o `--raiz` padrão (`.`) continua no checkout do PR, onde está o diff. O `catraca.py` da base `4182a6b9` aceita `--base` no `pr-texto`. Sem catraca na base, ou se o `worktree add` falha antes do `echo`, o passo volta ao script do PR, como o passo de regras. Efeito previsto: neste PR, o CI roda o `pr-texto` da develop, ainda sem T1, então o portão só vale a partir do PR seguinte. É o mesmo comportamento da introdução do passo de regras.
- **Novo no delta.** `com_motivo` mede o motivo por linha e por arquivo citado na linha. O A2 da segurança é atendido: um motivo genérico não cobre N arquivos. Os mutantes novos M12 a M16 têm teste do ramo de falha. Rodei `python3 -m unittest tests.test_catraca.T1NoTextoDoPr`: 12 testes OK. Apliquei à mão, numa cópia, o M12 (`len(resto) >= MINIMO_SECAO`): `test_motivo_vale_por_arquivo` falha, então o mutante morre. A bateria do `forge-mutante` fica com o QA, e a suíte, com o CI do PR, que ainda não foi aberto.

## Parecer
Aprovado. A mudança torna portão de CI um aviso que já existia, reaproveita a regra única do `forge-check`, falha fechada e tem cada guarda coberta por mutante e teste do ramo de falha. O custo medido fica em cerca de 0,3 s por run. Na revalidação do head 67ef9dfb, os três achados recomendados (A1 a A3) foram resolvidos e não aparece achado novo.
