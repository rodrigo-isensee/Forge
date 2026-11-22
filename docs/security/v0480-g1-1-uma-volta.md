---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-g1-1-uma-volta
commit: 57c0cbffa460dfdd6ea459f31e32f398f7262a4c
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: v0478 E100.3 (G1.1, no máximo 1 volta por item)

Rodada única (ORDEM DO DONO 21/11 22:13): todos os achados estão aqui. Escopo: `2d73a35e..57c0cbff` (`bin/forge-check`, `docs/regras/R-QA.md`, `docs/regras/R-REVIEW.md`, `skills/briefs-e-conferencia/autor-ate-o-merge.md`, `tests/test_volta_por_delta.py`, specs de mutantes, `changelog.d/`), contra o desenho `origin/melhoria/v0480-desenho-g1-g3:docs/propostas/g1-g3-fluxo-rapido.md` (seção 2, item 1).

Gatilhos: código de controle do Forge (`bin/forge-check`), `docs/regras/`.

Suíte: não rodada aqui (a suíte inteira roda só no CI; o PR ainda não existe). Vale a entrega conferida: `- 2026-11-21 23:21: entrega conferida 57c0cbffa460dfdd6ea459f31e32f398f7262a4c` (`docs/pedidos/v0478.md:3975`). Rodei os 3 testes novos de `tests/test_volta_por_delta.py` (`BriefDeVolta`): OK.

## Achados
- A1 (bloqueante) bin/forge-check:4260 · a autorização casa qualquer linha DECISÃO DO DONO que cite a branch e tenha "volta" em qualquer sentido: negação ("sem nova volta"), a opção (a) ou (b) do próprio dono, o verbo ("o dono volta") e a branch com "volta" no nome liberam a volta 2 (S1 a S4)
- A2 (bloqueante) bin/forge-check:4290 · a numeração sai só do brief que o Jarvis passa em --volta: gerar de novo a partir do brief original dá outra "volta 1", e o conferir_volta (:4417) não recusa; o teto e a recusa de numeração contornada do desenho não valem (S5)
- A3 (recomendado) bin/forge-check:4253 · a autorização é texto escrito pelo Jarvis com a leitura dele (limite declarado na ADR 0018); amarrar a volta extra a uma concessão `forge-check autorizacao` (mensagem literal do dono) ou declarar o limite no R-QA

## Sondas
- S1 · voltas_autorizadas(fontes=["- 2026-11-21 23:00: DECISÃO DO DONO: sem nova volta para melhoria/v1-x; cortar e reabrir menor"], "melhoria/v1-x") · espera: 1 (volta 2 recusada) · obtido: 2 (volta 2 passa)
- S2 · voltas_autorizadas(fontes=["DECISÃO DO DONO (2026-11-21 23:00): melhoria/v1-x aceita com cartão, nada de voltas"], "melhoria/v1-x") · espera: 1 · obtido: 2
- S3 · voltas_autorizadas(fontes=["DECISÃO DO DONO (2026-11-21 23:00): melhoria/v0480-g1-1-uma-volta entra antes do G1.2"], "melhoria/v0480-g1-1-uma-volta") · espera: 1 · obtido: 2
- S4 · voltas_autorizadas(fontes=["DECISÃO DO DONO (2026-11-21 23:00): o dono volta na segunda; melhoria/v1-x espera"], "melhoria/v1-x") · espera: 1 · obtido: 2
- S5 · BriefDeVolta: gerar() -> volta 1 gravada em -2.md; gerar() de novo com --volta no brief original; conferir(saida, nome=-3.md) · espera: recusa (volta 2 sem decisão) · obtido: rc 0, "## Entregar (volta 1)", sem "numeração contornada" nem "recusada"

## Detalhe dos achados

**Forja e reaproveitamento (o foco do pedido).** Subagente não forja a linha: o pedido e os briefs da pasta de controle são só do jarvis (`hooks/conformidade.py:3806`, `CAMINHOS_DO_CONTROLE`), e a cópia `wt/` não tem `docs/pedidos/`. O Jarvis forja por construção (A3). Reaproveitar a linha de outro item exige o mesmo nome exato de branch (o limite de palavra em `:4259` recusa prefixo, sufixo e `origin/<branch>`, que falha fechado); uma linha legítima vale uma volta só (o teste de `:1007` do arquivo de testes prova a volta 3 recusada). Linha de dependência ou de registro citado também conta (`decisoes_cobradas`); sem ganho para quem não seja o Jarvis, fica sem achado. No corpus real (`docs/pedidos/v0478.md`), nenhuma branch citada em decisão ganha volta extra hoje.

**A1.** Evidência: `bin/forge-check:4246` (`VOLTA_NA_DECISAO = (?i)\bvoltas?\b`) e `:4260` (basta o nome da branch e a palavra na mesma linha). Caminho: o dono escolhe a opção (a) ou (b) que a própria recusa oferece (`:4267-4270`); o Jarvis grava a decisão citando a branch e "volta" ("cortar, sem nova volta"); o `brief gerar --volta` passa a aceitar a volta 2 contra a decisão. Na branch revisada, que tem "volta" no nome, qualquer decisão que a cite libera (S3). Severidade média: a trava falha aberta contra uma decisão do dono (`R-DECISAO`), sem atacante. Correção mínima: aceitar só a forma que a recusa manda gravar, ancorada logo depois do prefixo da decisão: `DECISÃO DO DONO[ (data)]: mais uma volta para <branch>` com a branch delimitada e o resto da linha livre só depois (o ` → "fala"` do registro); a palavra solta deixa de contar. Testes: S1 a S4 como casos que não autorizam, mais a forma canônica com e sem crase e ponto final, e a forma com data antes da frase. Esforço P. Dono: autor da E100.1.

**A2.** Evidência: `bin/forge-check:4290` (`n` = número do brief passado em `--volta` + 1) e `:4417-4422` (o `conferir_volta` compara só com o `Volta-de:` do próprio brief); o brief sem `Volta-de:` nem passa pelo `conferir_volta` (`:8707`). Caminho: o Jarvis, que gera e confere os briefs, passa o brief original em `--volta` a cada rodada (S5), ou escreve o brief seguinte sem `Volta-de:`; toda volta sai "volta 1", e o teto do `R-QA` e o requisito do desenho ("O `conferir_volta` recusa o brief que contorna a numeração") não valem. Severidade média (requisito do desenho não atendido, controle contornável em um comando). Correção mínima: contar as voltas pela branch, não pela cadeia escolhida: `n` = 1 + número de briefs em `docs/briefs/` do pedido com `Volta-de:` e a mesma `Branch:`, nos dois lugares (`gerar_volta` e `conferir_volta`, este sem contar o próprio arquivo); recusar no `conferir_volta` o `Volta-de:` que aponta para um brief que já tem volta (anterior que não é o último da branch); usar a `Branch:` do anterior, não a do brief novo (`:4420`) nem o `--branch` (`:4289`), para ler a autorização. Testes: S5, o brief sem `Volta-de:` da mesma branch depois de uma volta, e a `Branch:` trocada no brief novo. Esforço P a M. Dono: autor da E100.1.

**A3.** Evidência: `bin/forge-check:4253` (`voltas_autorizadas`) lê `decisoes_cobradas`, as linhas que o Jarvis escreve; a ADR 0018 (`docs/adr/0018-autorizacao-do-dono-gravada.md:79`) registra esse limite e criou o canal forte (`forge-check autorizacao gravar`, mensagem literal do dono). Proporcionalidade: a volta a mais só custa tempo e não afrouxa segurança (afrouxar são as opções (a) e (b)), por isso recomendado. Correção mínima: uma linha no `R-QA` e na skill dizendo que a autorização da volta é leitura do Jarvis, ou o ato `volta-extra` com alvo `<branch>` nas concessões da ADR 0018. Esforço P (texto) ou M (concessão). Dono: autor da E100.1.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do diff, sondas pela biblioteca padrão contra as funções do `bin/forge-check` e a classe de teste `BriefDeVolta` (fora da cópia). Não estão no PATH: `gitleaks` e `semgrep` (lacuna; sem segredo nem dependência no diff).
