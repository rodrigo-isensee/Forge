---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-pv-a1-adr
commit: ac1069d300ba52321c145959c446dbecf2dfb838
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: v0478 (E57.11, PR-VERDE A1, emenda das ADR 0018 e 0008)

Diff lido: `5ccac0bf..ac1069d3` (ADR 0018, ADR 0008 seção 3, fragmento do changelog); 0 linha de código. Sem suíte local (brief); sem PR, logo sem CI a citar. Lido também: a decisão do dono de 2026-11-20 13:51 (pedido v0478, condição da D1), o desenho `docs/propostas/v0479-pr-verde-de-primeira.md` (D1) na `melhoria/v0479-pr-verde-de-primeira` e o parecer de review E57.10 (`docs/reviews/v0479-pv-a1-adr.md`, A1).

## Gatilhos
Gatilhos: controle de autorização do dono, hook de conformidade, catraca do CI (afrouxa-regra).

## Achados
- A1 (bloqueante) docs/adr/0018-autorizacao-do-dono-gravada.md:114 · E3 diz que o commit do agente não muda o conteúdo: falso (S1-S4). `git add` com filtro, `--chmod` e `update-index --cacheinfo` passam no hook num caminho `quem: []` e põem outro blob. O declarar deve pôr o arquivo no índice; o hook barra o git que escreve o índice do caminho.
- A2 (recomendado) docs/adr/0018-autorizacao-do-dono-gravada.md:116 · E5 confere o blob contra D-<Id> só no forge-fechar, mas o tech-lead abre PR por `gh pr create` direto (`acoes.pr_criar`). Pôr a mesma conferência no pre-push (não contornável, R-VERIFY) e no `gh pr create` do hook.
- A3 (recomendado) docs/adr/0018-autorizacao-do-dono-gravada.md:134 · O Sha256 cobre só o corpo (item 2, E4 e); `Commit`, `Ramo` e `Validade-utc` mudados não são vistos no CI. Escrever isso na linha "Origem no CI" do modelo de ameaças, para a barreira local (E5) ser lida como a única.

## Sondas
- S1 · `git -c core.attributesFile=$TMPDIR/attr -c filter.z.clean='sed s/2026-11-20/2027-11-20/' add docs/autorizacoes/x.md` (attr: `docs/autorizacoes/* filter=z`) · espera: índice igual à árvore · obtido: índice com `Validade-utc: 2027-11-20`, árvore com 2026-11-20
- S2 · hook conformidade, Bash de `forge:dev`: `git update-index --cacheinfo 100644,e69de29bb2d1d6434b8b29ae775ad8c2e48c5391,docs/security/aceites/x.md` (pasta `quem: []`) · espera: saída 2 · obtido: saída 0
- S3 · hook conformidade, Bash de `forge:dev`: `git -c filter.z.clean=cat add docs/security/aceites/x.md` · espera: saída 2 · obtido: saída 0
- S4 · hook conformidade, Bash de `forge:dev`: `git add --chmod=+x docs/security/aceites/x.md` · espera: saída 2 · obtido: saída 0

## Detalhe dos achados
**Confirmação pedida (a E3 cumpre a condição do dono na D1?)** A condição tem quatro partes. (1) Só o dono ou a ferramenta gravam: escrita na E3 (`:114`), com a sessão principal também barrada (`quem: []` vale para o papel `jarvis`, `sem_agent_type` em `hooks/conformidade.json`), o que é o certo, porque a sessão principal também é agente. (2) O hook barra pelo caminho: escrita, em toda grafia, contra Write, Edit e Bash. (3) Teste com agente recusado: escrito, um por papel, gravar, alterar e apagar, oráculo da classe `escrita-por-agente` (`:93`). (4) Segurança confirma por escrito: posta no parecer do PV-A3, antes do PV-A4. **Cumpre na intenção, mas não no texto**: a última frase da E3 entrega ao agente o `git add` e o commit do arquivo dizendo que "não mudam o conteúdo", e as sondas provam que mudam. Corrigido o A1, a E3 cumpre a condição; a confirmação de que o hook barra de fato continua no parecer do PV-A3, como a E3 já manda.

**A1 (bloqueante).** Evidência: `docs/adr/0018-autorizacao-do-dono-gravada.md:114` (última frase) e `:128` (linha "Escrita por Write, Edit ou Bash" do modelo de ameaças, que lista `git checkout`, `git restore` e `git apply`, mas não o que escreve o índice). Sondas: S2 a S4 rodaram o hook atual (o harness `test_hooks.Fixture` do clone) com um agente `forge:dev` contra `docs/security/aceites/x.md`, a pasta `quem: []` mais parecida com a futura `docs/autorizacoes/`; `git rm`, `git rm --cached`, `git mv`, `git checkout -- <caminho>`, `git restore <caminho>` e `rm` saem 2, mas `git add`, `git add --chmod=+x`, `git -c filter.z.clean=... add` e `git update-index --cacheinfo` saem 0. S1 prova, num repositório descartável em `$TMPDIR`, que o filtro de limpeza do `git add` grava no índice um conteúdo diferente do arquivo escrito pela ferramenta, sem tocar a árvore. Caminho de ataque: um agente com Bash (qualquer papel) põe no índice, pelo caminho nomeado, uma versão do arquivo com `Validade-utc` estendida, `Commit` trocado ou modo 100755, comita e envia; o `Sha256` só cobre o corpo (A3), então o CI aceita; o único freio é o E5, contornável (A2). Resultado: arquivo de autorização "gravado por agente e aceito", exatamente o que a condição do dono e o critério de reversão (`:148`) proíbem. Isso também inverte a premissa do A1 do review E57.10: o `git add` do caminho não "cairia na barreira" hoje, passa; e não é "só leitura", então não pode ser liberado como tal. Severidade: alta (afrouxa o portão do dono sem o OK). Correção mínima (texto da E3 e da linha `:128`; o código é do PV-A3): (a) o `declarar` (e o `retirar`) põe o próprio arquivo no índice, com `-c core.attributesFile=/dev/null`, sem filtro e modo 100644, e confere `git ls-files -s` contra o blob do `D-<Id>`; o agente só roda `git commit` sem caminho e `git push`; (b) o hook barra, para qualquer agente, todo comando do git que nomeia o caminho de `docs/autorizacoes/` e escreve o índice ou a árvore: `add` (com qualquer opção, inclusive `--chmod`, `-f`, `-N`, `-p`), `update-index`, `rm`, `mv`, `checkout`, `restore`, `apply`, `stash push -- <caminho>`, `reset -- <caminho>`, e qualquer `-c filter.*` ou `-c core.attributesFile` na linha que cita o caminho; (c) o modelo de ameaças ganha essas formas na linha `:128` e o oráculo `escrita-por-agente` (`:93`) as testa. Esforço: P (texto). Dono: `software-architect` (ADR), código no PV-A3 (`tech-lead`).

**A2 (recomendado).** Evidência: `:116` (E5 só no `bin/forge-fechar`) e `hooks/conformidade.json` (`acoes.pr_criar: ["tech-lead"]`). Caminho: o commit sem o caminho no comando (`git commit -a` com filtro, árvore montada à mão, linha `:129`) só é pego pelo E5; o tech-lead pode abrir o PR por `gh pr create` direto e pular o `forge-fechar`. Severidade: média. Correção mínima: a conferência do blob contra `D-<Id>` roda também no `.githooks/pre-push` (que o agente não pula, `R-VERIFY`) e no `gh pr create` do hook quando a branch tem arquivo em `docs/autorizacoes/`. Esforço: P. Dono: `software-architect` (texto da E5), código no PV-A5.

**A3 (recomendado).** Evidência: item 2 (`:15`, `Sha256` "do corpo") e E4 (e) (`:115`). Caminho: os campos que a catraca usa para liberar (`Commit`, `Ramo`, `Validade-utc`) ficam fora do hash; um hash do arquivo inteiro também não ajudaria no CI (quem muda o arquivo recalcula), então a integridade do cabeçalho é só local (blob do `D-<Id>`). Severidade: baixa (já é o limite "Origem no CI"; falta dizer que inclui o cabeçalho). Correção mínima: acrescentar à linha `:134` "inclui cabeçalho mudado (`Commit`, `Ramo`, `Validade-utc`); a integridade é só a do blob do `D-<Id>`, na camada local (E5)". Esforço: P. Dono: `software-architect`.

O resto do modelo de ameaças (`:121-134`) cobre a condição: alvo, ato, `Commit` pela P9, arquivo já na base, validade, integridade, custo (`R-CUSTO` não liberável, N-CAT1) e transição estão com barreira e item; nada se libera antes do PR de cada item (`:106`). Os A2 a A4 do review E57.10 não mudam a segurança (o A3 do review, retirada só no envio, fica coberto pela validade e pelo teto de 48 h do `uso-unico`).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: o harness de hooks do clone (`tests/test_hooks.py`, `Fixture`) e o git, locais; sondas num script fora do repositório e num repositório descartável em `$TMPDIR`. Sem varredura de segredo ou de dependência: o diff é só texto de ADR.
