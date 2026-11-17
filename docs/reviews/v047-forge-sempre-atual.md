---
tipo: review
contrato: 1
pedido: v0474
branch: melhoria/v047-forge-sempre-atual
commit: 2bcad3855c8a1e54062b90ff3b1b6baab9eedd82
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-17
---
# Code review: FORGE-SEMPRE-ATUAL (diretriz 30, ADR 0017), E1.51

Primeiro parecer do item na branch (não havia parecer anterior a usar como delta). Escopo lido: `bin/forge_sempre_atual.py`, `bin/forge-sempre-atual`, `bin/forge-atualizar`, `bin/forge-voltar-versao`, `bin/forge_versoes.py`, `bin/forge-check` (aviso da branch do modelo), `bin/forge-testes` (mapa), `hooks/doutor.py`, `scripts/jarvis`, `scripts/jarvis-forge`, `scripts/instalar-atalho.sh`, `scripts/preparar-estacao.sh`, ADR 0017 e a emenda na 0005, as specs de mutante e os testes do núcleo e do oráculo na parte do modelo.

## Achados
- A1 (bloqueante) bin/forge_sempre_atual.py:776 · ADR 0017 item 10 pede a branch a partir da origin/develop, mas o forge-upgrade (bin/forge-upgrade:164) usa a develop local e, sem ela, sai 2 por HEAD solto: clone só com main nunca recebe a branch, e develop local defasada vira a base (S1, S2); o oráculo só usa forge-upgrade falso
- A2 (recomendado) bin/forge_sempre_atual.py:298 · no prazo do passo, p.kill() mata só o filho; com start_new_session, um killpg no grupo levaria os netos (git, node da CLI) juntos
- A3 (recomendado) bin/forge_sempre_atual.py:453 · a contagem de adiamentos usa o tipo do escopo (project) como chave: um projeto livre zera o contador de outro adiado e o aviso do doutor não diz qual projeto
- A4 (recomendado) scripts/jarvis:29 · atualizar_plugin repetida igual em scripts/jarvis-forge:183, e o leitor do installPath repetido em scripts/instalar-atalho.sh:16 e scripts/preparar-estacao.sh:289; uma fonte só evita que as cópias divirjam
- A5 (recomendado) bin/forge_versoes.py:587 · a ligação do .local ao hook do projeto (Q2, E6.10) é outro comportamento, separável do núcleo; se ficar, o corpo do PR o nomeia no teto

## Sondas
- S1 · clone só com main, worktree --detach em origin/develop, bin/forge-upgrade <worktree> · espera: rc=0 e branch forge/upgrade-0.47.3 · obtido: rc=2, "branch de integração seria 'HEAD solto'", sem branch
- S2 · develop local um commit atrás da origin/develop, mesmo passo · espera: origin/develop ancestral da forge/upgrade-0.47.3 · obtido: não; a branch nasce da develop local

## Parecer
Reprovado por A1, só. O resto do desenho segue a ADR 0017: nenhum `marketplace remove`, catálogo fixado por `add <url>#v<alvo>` e update só com o `ref` lido igual ao alvo; ambiente dos filhos por lista positiva (AR-3); estado em caminho fixo com recusa de link e de outro dono; ocupação que adia na dúvida; C-INI com volta e fixação gravada antes de mexer no catálogo; rodada que nunca derruba o atalho. A ADR traz "Por que o existente não basta" com evidência e critério de reversão (R-DECISAO).

A1 · `bin/forge_sempre_atual.py:776-779` com `bin/forge-upgrade:163-180` · a worktree temporária fica em HEAD solto na `origin/develop`, mas o `forge-upgrade` escolhe a base pela `refs/heads/develop` local: sem ela, recusa (S1) e a abertura registra `falhou:modelo` em toda abertura; com ela defasada, a branch nasce de um commit velho (S2) e, com commits locais não enviados, leva-os ao PR que o `tech-lead` envia. O oráculo (`tests/test_oraculo_sempre_atual.py:1085`) e o núcleo usam um `forge-upgrade` falso, por isso a combinação nunca rodou. Sugestão: o `forge-upgrade` aceitar a base explícita (por exemplo `--base origin/develop`) e a ferramenta passá-la, com um teste que roda o `forge-upgrade` de verdade nos dois casos das sondas. Severidade: bloqueia (requisito da ADR 0017 item 10 com gatilho reproduzido).

Teto (M14): 3952 linhas contadas (`git diff --numstat --no-renames 45615e20...2bcad385`, só `bin/`, `hooks/`, `scripts/` e `tests/*.py`), das quais 2149 são os dois módulos de teste novos. Cortar o núcleo, as entradas e os avisos não compensa agora: são um comportamento só (a atualização na abertura) e já passaram pelas etapas E6.1 a E6.10 e pela consolidação E1.17; o motivo no PR basta, com `teto: excedido, 3952 linhas, <motivo>`. A parte que ainda cabe fora é a Q2 (A5), pequena e independente.

Verificações: `python3 -m unittest tests.test_sempre_atual tests.test_atualizar tests.test_doutor tests.test_forge_mutante.ConferirTodas` no head 2bcad385: `Ran 286 tests in 130.389s`, `OK (skipped=3)`. A suíte inteira fica para o CI do PR. O `docs/engineering/praticas.md` não traz regra "decidida por", então não há saída de ferramenta a citar. Mutantes: 8 specs na branch (seis `v047-sempre-atual-*`, `fixacao-do-dono`, `v047-atualizar-hook-local`), conferidas pelo `ConferirTodas` verde; a lista e os ramos de falha são do QA (E1.53).
