---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-brief-sonda-escrita
commit: 61ab461ec3cbc099baf4c24aa7dc7e7803427dbf
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-28
---
# Review de segurança: v0481 (BRIEF-SONDA-ESCRITA, #952), 1ª rodada completa

Gatilhos: controle do Forge (barreira de escrita do `brief selar`, R-BRIEF; analisador de brief)

Escopo lido: o diff inteiro de `b414714c..61ab461e` (`bin/forge-check`, `bin/forge-testes`, `tests/test_brief_sonda_escrita.py`, os dois JSON de mutantes, o fragmento do changelog), mais o entorno que a isenção usa: `SONDA_NO_ENTREGAR` (`bin/forge-check:4183`), `conferir_volta` (`bin/forge-check:4845`), `pareceres_da_volta` (`bin/forge-check:4485`), `avaliar_brief` (`bin/forge-check:9418`) e o argumento `--parecer` do `brief` (`bin/forge-check:11311`).

## Achados
- A1 (bloqueante) bin/forge-check:4921 · o conjunto `lidas` aceita sonda de parecer de outro pedido: com `--parecer` a `pareceres_da_volta` não filtra `pedido:`, e a entrada dessa sonda sai da barreira de escrita; brief de volta com caminho em .git/hooks sela (S1). Filtrar por `pedido == pedido_id` e sem problemas.

## Sondas
- S1 · harness BriefDeVolta: Entregar com (sonda review <sha> S7) copiando a entrada de docs/reviews/outro.md (pedido: outro-pedido, cita .git/hooks/pre-push); brief --ref melhoria/x --parecer docs/reviews/outro.md · espera: rc=1, escrita barrada · obtido: rc=0, volta: ok

## Detalhe dos achados
**A1.** Evidência: `bin/forge-check:4921` monta `lidas` de todos os `pareceres` devolvidos por `pareceres_da_volta`; no ramo `if arquivos:` (`--parecer`, `bin/forge-check:4490-4500`) o parecer é lido da ref sem conferir `campos["pedido"] == pedido_id` (o ramo padrão, `bin/forge-check:4510`, confere). A conferência da recomendação incluída, logo abaixo (`bin/forge-check:4932`), já faz esse filtro (`pedido`, `tipo` e sem `problemas`); a das sondas não. Caminho de ataque: quem sela o brief (o Jarvis, ou quem rode `forge-check brief selar`) escolhe `--parecer` apontando para qualquer parecer da ref, de qualquer pedido, cuja `## Sondas` cite um caminho protegido; a linha `(sonda ...)` copiada desse parecer passa no par (tipo, id, entrada), a entrada sai de `caminhos_do_entregar` e o `escrita: barrada` some; o brief sela mandando gravar em `.git/hooks/`. Controle (mesma fixture, linha comum com o mesmo caminho): `escrita: barrada ".git/hooks/pre-push"`, rc=1; antes desta mudança a sonda também saía barrada. Exige um parecer já commitado com essa entrada na ref; o vetor amplo (escrever no `.git` pela cópia) segue com a GIT-CONTROLE (v048), como diz o brief. Severidade: média (trava contornável pelo próprio seletor de entrada, sem precisar escrever parecer novo). Correção mínima: em `conferir_volta`, montar `lidas` (e, por coerência, o laço PAR-P1 de `bin/forge-check:4914`) só com os pareceres em que `p["campos"].get("pedido") == pedido_id` e `not p["problemas"]`; teste novo em `tests/test_brief_sonda_escrita.py` com o caso da S1 (parecer de outro pedido via `--parecer`, espera rc=1 e `escrita: barrada`). Esforço: P. Dono: `tech-lead` (autor do E45.53).

Conferido sem achado (as formas pedidas no brief):
- linha forjada com prefixo de sonda e id que o parecer não tem: rc=1, `volta: sonda S8 de review não está nos pareceres lidos`;
- sonda com entrada diferente (mesmo id): rc=1 (`difere do parecer` e `não está nos pareceres lidos`), coberto por `tests/test_brief_sonda_escrita.py:46-55`;
- tipo trocado (`sonda qa` com a entrada do parecer de review): rc=1;
- caminho no `espera:` da linha de sonda: segue barrado (só o grupo 4 sai);
- sem `--ref` ou sem `Volta-de:`: a isenção não liga (`bin/forge-check:9141`), coberto por `tests/test_brief_sonda_escrita.py:39-44`;
- com `--ref` e `Volta-de:`, todo retorno antecipado de `conferir_volta` (Volta-de fora do formato, anterior ilegível ou com outro sha256, ref que não é commit, erro na leitura dos pareceres) reprova: a isenção nunca vale sem o par conferido;
- `secoes_por` e `blocos_literais` pegam o primeiro cabeçalho de cada nome e quebram linha do mesmo jeito: a linha isenta na escrita é a mesma conferida no par;
- a linha `- arquivos:` segue lida do texto cru (`bin/forge-check:9068`).

Suíte: as partes 1 a 5 da suíte e a bateria longa do CI do head `61ab461e` passaram; os checks vermelhos (`bateria`, `bateria (pareceres)`, `catraca`) são os portões de parecer, que este parecer e os paralelos alimentam. Rodei só as sondas acima, num módulo descartável fora da branch, sobre o harness `BriefDeVolta`.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Revisão estática e sondas locais com a biblioteca padrão; sem varredura de segredo nem de dependência (o diff não toca credencial, dependência nem workflow).
