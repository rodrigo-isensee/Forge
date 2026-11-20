---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-sandbox-controle
commit: 32c3528eaa65c8c85367465c506856befdd33818
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: v0479-sandbox-controle

Revalidação (E29.19) no head 32c3528e, por delta: `forge-check parecer delta` de 64fca890..32c3528e. O delta traz 0eedfdea (o dono aplicou o patch em `.claude/settings.json`) e o merge da develop 004ce869 (32c3528e). A ferramenta contou inteiro o merge f493e00 (aviso de base) e listou `hooks/_comum.py`, `hooks/agentes.py`, `bin/forge-testes` e `docs/hooks.md`; conferido contra a develop (`git diff 004ce869 HEAD`), o que a branch muda nesses arquivos é o mesmo já aprovado em 64fca890, mais a união das importações. A rodada anterior está no git (parecer de b506717e).

## Gatilhos
Gatilhos: configuração do sandbox do Bash (controle de escrita), estado dos hooks de R-TETO, lista fechada de testes que podem pular (afrouxa-regra).

## Resumo
- **`.claude/settings.json` (0eedfdea):** o blob do head (161117cc) é exatamente o alvo de `docs/devops/v0479-sandbox-controle.patch` (`index 6a569cb..161117c`), sobre a mesma base da develop (6a569cbb). `denyWrite` passa de `.forge/` para `.forge/`, `.git/forge/run`, `~/.forge/maquina`: só soma negação, nada sai de `allowWrite` nem de `denyRead`. O merge não tocou o arquivo.
- **Merge (32c3528e):** o único conflito é a importação de `_comum` em `hooks/agentes.py:71-72`, resolvido pela união `ler_trava` + `raiz_declarada`; as duas existem (`hooks/_comum.py:146`, `:2502`) e o módulo compila. O que a develop trouxe já tem os pareceres dos PRs de origem.
- **O PR só aperta? Sim, no efeito.** Contra a develop: `denyWrite` novo no Forge e no modelo de projeto (`.forge/config.json`, `.forge/run/agentes.json`, `.forge/run/pesado.json`, `~/.forge/maquina`); `gravar_json` com `O_EXCL|O_NOFOLLOW`; `agentes.json` de 0 byte segue ilegível (falha fechada); `forge-testes` passa a mapear mais testes. `ler_trava` (0 byte ou `null` = sem trava) é a adaptação ao ponto de montagem do runtime, já aprovada (A2) e coberta pelo `doutor`, que cria os arquivos antes do primeiro Bash. Nenhuma regra perde força no CI.
- **`PODEM_PULAR` 18 -> 20 (`tests/apoio_sandbox.py:48-49`): afrouxamento formal, neutro em substância.** É formal porque a lista fechada cresceu, e a docstring (`tests/apoio_sandbox.py:12-14`) exige `afrouxa-regra` para isso: o rótulo está correto e coberto pelo OK do dono (19/11). É neutro porque: (1) os dois IDs são testes novos deste PR (`tests/test_sandbox_controle.py:346`, `:376`), não testes antigos que ganharam saída; (2) `exigir` reprova com `CI`/`GITHUB_ACTIONS` definido (`tests/apoio_sandbox.py:117-119`), então no CI eles rodam ou derrubam a suíte, nunca pulam; (3) `teto_pulados` segue 2 (`tests/config.json:930`, sem mudança); (4) a sonda nova `bwrap` só serve aos IDs da lista (A4, `ListaFechada`). Pulam só fora do CI, onde o bubblewrap aninhado é negado. Sem os dois, a trava ficaria sem nenhuma prova de recusa: no saldo, a lista acrescenta cobertura.
- Testes rodados no head: `tests.test_sandbox_controle` e `tests.test_apoio_sandbox` (37, OK, 2 pulados: `bwrap: Creating new namespace failed`). CI do PR no head: suíte em andamento; `catraca` falha por texto do PR (seções "Projeto de origem" e "Como medir", R-CONTRIB, não é segurança) e `bateria (pareceres)` aguarda os pareceres neste head. A prova da recusa dentro do bubblewrap só vem do CI verde, obrigatório para o merge.
- **A2 fechado:** `docs/devops/v0479-sandbox-controle.md:61` cita `.forge` (pasta de `.forge/config.json`). O resíduo do A5 (S2, corrida entre `unlink` e `open`) segue no cartão da identidade da pasta.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Suíte inteira: não rodada (brief); CI do head em andamento. Ferramentas: varredor de segredos e linters de workflow fora do PATH (lacuna; o delta não toca workflow nem segredo); bubblewrap aninhado negado aqui (lacuna para sondar dentro do sandbox).
