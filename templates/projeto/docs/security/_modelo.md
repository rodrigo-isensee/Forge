---
tipo: revisao-seguranca
contrato: 1
pedido: <id-do-pedido>
branch: <branch>
commit: <hash do HEAD revisado>
parecer: aprovado
revisor: forge:security-engineer
data: AAAA-MM-DD
---
# Review de segurança: <pedido>

Copie para `docs/security/<pedido>.md`. Formato: ADR 0004 do Forge; `forge-check docs` valida. Arquivos que começam com `_` ou sem frontmatter (postura, modelo de ameaças) são ignorados. Exigido quando há gatilho (`R-SEGURANCA`). `parecer: riscos-aceitos` só vale se o usuário escrever, à mão, `docs/security/aceites/<pedido>.md` com `pedido: <pedido>`, `commit: <o `commit` deste parecer>` e `aceite: sim` (parecer novo, outro commit, pede aceite novo) (nenhum agente grava essa pasta; `R-SEGURANCA`).

Formato do bloco `## Achados` (lido por máquina em `forge-check brief gerar --volta` e conferido por `forge-check docs`): uma linha por achado, `- A<n> (bloqueante|recomendado) <arquivo>:<linha> · <texto>`, sem quebra de linha nem caractere de controle, com até 300 caracteres no texto; só essas linhas entram no bloco (a prosa fica nas outras seções), e parecer reprovado traz ao menos um `bloqueante`. Parecer aprovado traz só linhas `(recomendado)` ou o bloco vazio.

Formato do bloco `## Sondas` (PAR-P1, conferido por `forge-check docs`): em entrega de analisador ou hook, uma linha por sonda executada que prova um bloqueante, `- S<n> · <comando ou entrada literal> · espera: <resultado esperado> · obtido: <resultado obtido>`, numa linha só, sem caractere de controle, com ` · espera: ` e ` · obtido: ` uma vez cada e até 300 caracteres depois do id; só essas linhas entram no bloco, e sem sonda o bloco fica vazio.

Bloqueio (`R-REVIEW`): `bloqueante` é só defeito provado, requisito ou segurança com gatilho; o resto é `recomendado` e não devolve. Promover recomendação a bloqueante exige `critério mudou:` com o motivo no achado.

Evidência: a evidência não muda para caber (`reproduzido` não vira `visto`); se o achado não cabe nos 300 caracteres, encurte o texto, nunca a prova.

## Gatilhos
Quais gatilhos da `R-SEGURANCA` a entrega toca.

Avisos (o pre-push e o `forge-check docs` barram): cite o ID da regra, sem copiar a frase dela; cada achado em até 300 caracteres de texto (conta o que vem depois do ` · `; o prefixo `A<n> (...) <arquivo>:<linha>` não conta). Onde um teste barra nome de stack em `docs/security/` e `docs/devops/` (é o caso do Forge), o parecer não cita nome de linguagem, gerenciador de pacotes nem ferramenta de stack: diga "a stack" ou "o gerenciador de pacotes".

## Achados

## Sondas

## Detalhe dos achados
Por achado, em prosa (fora do bloco `## Achados`): evidência (`arquivo:linha`; nunca o segredo) · caminho de ataque · severidade (crítica, alta, média, baixa, informativa) · correção mínima · esforço (P/M/G) · dono. Em parecer aprovado, as recomendações não bloqueantes ficam aqui, em prosa, ou no bloco `## Achados` como linhas `(recomendado)`.

## Riscos aceitos e ferramentas
Riscos aceitos e quem os aceitou; ferramentas usadas e as que faltaram no ambiente.
