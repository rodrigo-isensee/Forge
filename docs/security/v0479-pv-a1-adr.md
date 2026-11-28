---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-pv-a1-adr
commit: 2675e3ca9b12b61edd58b96251e23c05390185bc
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: v0478 (E57.18, PR-VERDE A1, revalidação depois da volta única)

Delta lido: `forge-check parecer delta docs/security/v0479-pv-a1-adr.md`, intervalo `ac1069d3..2675e3ca`; no domínio, só `docs/adr/0018-autorizacao-do-dono-gravada.md` e `docs/adr/0008-governanca-de-contribuicoes.md` (texto de ADR, 0 linha de código); fora, o fragmento do changelog. Já lido na rodada anterior (E57.11, commit `e3cb0998`, no git): o resto das duas ADR e o modelo de ameaças. Sem suíte local (brief); sem PR, logo sem CI a citar.

## Gatilhos
Gatilhos: controle de autorização do dono, hook de conformidade, catraca do CI (afrouxa-regra).

## Detalhe dos achados
**Achados anteriores.**
- A1 (bloqueante): **resolvido.** A E3 (`docs/adr/0018-autorizacao-do-dono-gravada.md:114`) tirou a frase falsa ("não mudam o conteúdo") e traz as três partes da correção mínima: (a) o `declarar` e o `retirar` põem o próprio arquivo no índice com `-c core.attributesFile=/dev/null`, sem filtro, modo 100644, e conferem `git ls-files -s` contra o blob do `D-<Id>`; o agente só roda `git commit` sem caminho e `git push`; (b) o hook barra todo `git` que escreve o índice ou a árvore com o caminho; (c) a linha "Escrita por Write, Edit ou Bash" do modelo de ameaças (`:128`) ganhou o `git` do índice, e o oráculo `escrita-por-agente` (`:93`) lista a família inteira da sonda anterior: `add` com qualquer opção (`--chmod`, `-f`, `-N`, `-p`), `update-index` (`--cacheinfo`), `rm`, `mv`, `checkout`, `restore`, `apply`, `stash push`, `reset`, `-c filter.*` e `-c core.attributesFile`. As sondas S1 a S4 da rodada anterior caem, como classe, nesse oráculo. A ADR 0008 (`docs/adr/0008-governanca-de-contribuicoes.md:56`) foi alinhada.
- A2 (recomendado): **resolvido.** A E5 (`:116`) põe a conferência do blob contra o `D-<Id>` também no `.githooks/pre-push` e no `gh pr create` do hook, e a linha "Escrita sem o caminho no comando" (`:129`) cita as três barreiras; a `Retirada:` ainda não enviada vale na camada local pelo evento `R-<Id>`.
- A3 (recomendado): **resolvido.** A linha "Origem no CI" (`:134`) declara que o cabeçalho (`Commit`, `Ramo`, `Validade-utc`) fica fora do `Sha256` e que a integridade dele é só a do blob do `D-<Id>`, na camada local.

**A E3 cumpre agora a condição do dono na D1?** Sim, no texto. (1) Só o dono ou a ferramenta gravam: escrito, com a sessão principal também barrada (`quem: []`), e agora sem a brecha do índice, porque quem põe o arquivo no índice é a ferramenta e o agente não nomeia o caminho em nenhum `git` que escreva. (2) O hook barra pelo caminho: em toda grafia, contra Write, Edit e Bash, inclusive o `git` do índice e da árvore. (3) Teste com agente recusado: um por papel, gravar, alterar e apagar, e cada forma do `git` listada no oráculo `escrita-por-agente`. (4) A confirmação de que o hook barra de fato continua no parecer do PV-A3, antes do PV-A4, como a E3 manda; este parecer aprova o texto, não o código, que ainda não existe. O que escapa da barreira pelo caminho (comando sem o caminho, `git commit -a`, `git add -A`, árvore montada à mão, commit de outra branch) segue como linha própria do modelo de ameaças (`:129`), pega só na camada local pelo blob do `D-<Id>`; no CI é limite declarado (`:134`), o mesmo "origem só na camada local" que a D1 aceitou.

**Delta novo, sem achado.** E6 (`:117`): a constante da transição nasce vazia no PV-A4 e, vazia, a catraca aceita arquivo ou rótulo. Isso só prolonga o estado de hoje (rótulo aceito), não libera nada novo; o risco é a data nunca ser gravada, e quem confere é o review do item seguinte. Para o parecer do PV-A4: um teste que acuse a constante vazia depois de o PV-A4 estar na `develop` fecharia esse esquecimento. Ordem de merge (`:106`): o desenho entra antes da emenda; sem efeito de segurança.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: `forge-check parecer delta` e o git, locais. Nenhuma sonda nova: o delta é só texto de ADR, o hook não mudou, e a prova de que ele barra é do PV-A3. Sem varredura de segredo ou de dependência pelo mesmo motivo.
