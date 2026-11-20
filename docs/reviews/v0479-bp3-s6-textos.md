---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-bp3-s6-textos
commit: add56507bb1db36604abe66ec804c9266a539e66
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 (E39.30), BP3 S6, textos da sessão durável

Head revisado `add56507`, base `004ce869`. Só texto: `agents/jarvis.md`, `skills/trabalho-em-paralelo/SKILL.md`, `skills/trabalho-em-paralelo/sessao-duravel.md` (novo), `docs/retomada-de-sessao.md`, `tests/config.json`, `changelog.d/`. Código 0 linhas (H1).

## Achados
- A1 (bloqueante) skills/trabalho-em-paralelo/sessao-duravel.md:24 · manda rodar `forge-check retomada` (e `--contar`), que não existe na develop nem em branch (S4 não começou): sonda S1. A proposta põe S6 depois de S4 e S5; integrar antes disso dá ao Jarvis comando inexistente. Traga a develop com S4 e S5 e revalide.
- A2 (bloqueante) skills/trabalho-em-paralelo/sessao-duravel.md:16 · "Como saber: o aviso de abertura do hook doutor": no desenho (proposta 3.4) o aviso só diz "fora do tmux", nunca se outro Jarvis roda; lido assim, toda sessão fora do tmux recusa, contra a D4 (avisar, não bloquear, salvo Jarvis no tmux). Tire o doutor do "como saber" ou faça a S5 citá-lo.
- A3 (bloqueante) docs/retomada-de-sessao.md:5 · cita `docs/propostas/v0479-bp3-sessao-duravel.md`, ausente na branch e na develop (só na `melhoria/v0479-bp3-sessao`, sonda S2); a referência fica morta se a S6 entrar antes da proposta. Mesma condição do A1.
- A4 (recomendado) docs/retomada-de-sessao.md:5 · duas regras de conflito na mesma linha ("vale a proposta" da BP3 e "vale este documento" contra a proposta antiga); nomeie a antiga (`propostas/retomada-de-sessao.md`) na segunda para não ler como contradição.

## Sondas
- S1 · `bin/forge-check retomada --contar` no head add56507 · espera: contagem e rc=0 · obtido: `invalid choice: 'retomada'`, rc=2
- S2 · `test -e docs/propostas/v0479-bp3-sessao-duravel.md` no head add56507 · espera: rc=0 · obtido: rc=1
- S3 · `grep -c -i tmux hooks/doutor.py` no head add56507 · espera: o doutor sabe de tmux · obtido: 0

## Parecer
Reprovado no head `add56507`. O texto segue as decisões do dono de 20/11 07:47 (D1, D3, D4 com a exceção do segundo Jarvis, D5) e o corte da proposta; o defeito é de ordem: S6 depende de S4 e S5 (tabela de corte da proposta) e cita comando, aviso e arquivo que ainda não existem (A1, A3). O A2 é de conteúdo: o sinal citado não carrega a informação que a regra precisa, nem no desenho.

Caminho: com S4, S5 e a proposta na develop, a branch traz a develop uma vez (`R-FLUXO`, dependência), corrige o A2 e volta para revalidação pelo delta. Os recomendados da segurança (A1 nome da sessão com `.`/`:`, A2 invariante da linha "dado do registro") cabem na mesma volta, se o autor quiser; não os promovo.

**Conferido.** Decisões D1 a D5 contra o `## Decisões` do pedido (linha de 20/11 07:47): batem. Remoções em `SKILL.md` ("cópia em `ritmo-e-corte.md`" e "Onde está: `forge-check proximo`") não perdem regra: o `proximo` segue no título de `agents/jarvis.md:24`. Changelog em fragmento, sem tocar o `CHANGELOG.md`. Neutralidade: sem termo de projeto.

**Testes.** Sem suíte local (brief; não há PR nem CI nesta branch). Rodados: `test_jarvis_nucleo` (43, OK) e `test_forge` com `RegrasInviolaveis`/`Neutralidade` (10, OK). Mutante manual: trocar "O registro de agentes não se edita à mão" em `sessao-duravel.md` derruba `test_trechos_obrigatorios`; arquivo restaurado.
