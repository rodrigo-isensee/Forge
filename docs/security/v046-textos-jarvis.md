---
tipo: revisao-seguranca
contrato: 1
pedido: v046
branch: melhoria/v046-textos-jarvis
commit: afdaa3abf9e27dd195380c1fe01ac631082b4198
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-12
---
# Review de segurança: v046 (textos do Jarvis, E21.3 e revalidação E21.7)

Diff revisado na 1ª rodada: `origin/develop...be5bb7ee` (base a1318e88), só texto: `agents/jarvis.md`, `docs/regras/README.md` (parágrafo `R-WIP`), `skills/trabalho-em-paralelo/SKILL.md` e o fragmento `changelog.d/v046-textos-jarvis.md`. Classe C.

Revalidação por delta (E21.7): `forge-check parecer delta` de `be5bb7ee..afdaa3ab` (volta E21.5). No domínio: `docs/regras/README.md` e `skills/trabalho-em-paralelo/SKILL.md`; fora: `changelog.d/v046-textos-jarvis.md` e `tests/test_jarvis_nucleo.py` (lidos mesmo assim). `agents/jarvis.md` sem mudança no delta.

## Gatilhos
Texto de regra e do Jarvis que governa travas da fábrica (`R-WIP`, `R-TETO`, `R-DECISAO`, `R-MAIN`, `R-CONFORMIDADE`). Nenhum código, hook, workflow ou ferramenta mudou; as travas que barram de fato (hooks, `forge-check`, CI) ficam como estão.

Conferência das travas no texto (1ª rodada, segue válida no head novo):
- `R-TETO` e piso de memória: o parágrafo `R-WIP` (README.md:29) mantém "respeitando o `R-TETO` inteiro"; a skill mantém "enquanto couber no teto". A espera por memória obedece ao piso, não o contorna.
- Uma escrita por branch e série por arquivo: o texto exige branch própria sem arquivo em comum com outro em voo e um por vez no que é comum; aperta, não afrouxa. `R-REVIEW` (quem implementou não revisa o próprio cartão) segue no parágrafo.
- `R-DECISAO`, `R-MAIN`, `R-CONFORMIDADE`: o que vai à pessoa (decisão, rótulo, merge na `main`, comando em arquivo travado) e o bloco "Com a pessoa" ficam intactos; a edição recusada em `agents/**` segue "relata e para, sem contornar".

Conferência do delta (E21.7):
- A1 resolvido: SKILL.md:19 traz o prazo na própria forma do laço e diz o que fazer quando vence ("confira o estado"). Sem espera sem fim: o laço sai pela condição ou pelo prazo; com o marcador `N` copiado sem troca, o bash o lê como 0 e o laço sai na hora (sonda S1), falha segura. O `until` com condição que dá erro só segue até o prazo.
- A2 resolvido: SKILL.md:19 volta a dizer que na pausa por limite de uso nada novo é disparado, só conferências e integradores, com a gravação de onde parou e a retomada só com a cota nova; o "encha as vagas" fica na frase anterior, fora da pausa. Sem caminho para disparo durante a pausa.
- Jarvis × subagente: a espera em segundo plano vale só para o Jarvis; o subagente segue a skill `esperar-estado`, cuja regra 2 proíbe `run_in_background` para esperar e limita a chamada a 170 s. Sem contradição; nenhum subagente fica com processo pendente em segundo plano.
- SKILL.md:10: "se serializam" virou itens com arquivo em comum que vão juntos (lote por arquivo) ou em que o segundo espera o primeiro entrar; aperta a série por arquivo. O relançamento do portão parado em 53 min passa a exigir conferir antes que o anterior não roda mais, o que evita duas instâncias no mesmo item.
- SKILL.md:17: as 150 linhas ficam como referência que orienta sem travar; mesmo sentido de antes, e nenhuma ferramenta usava o número como trava.
- README.md:29 (`R-WIP`): a volta sem a instância original vai a uma nova com o mesmo brief; continua sendo autoria (não review), então `R-REVIEW` não é tocado. A lista do um por vez só foi reordenada (mesmos itens). As medidas novas são só leitura. A linha da tabela (README.md:13) perdeu a menção ao hook, mas o parágrafo segue dizendo que o `forge-check kanban` e o hook `quadro` barram; nenhuma trava sai.
- Cortes para caber: SKILL.md com 3006 caracteres (teto 3006); as frases tiradas da skill (volta à mesma instância e CI do PR, "por script") têm fonte única no `R-WIP` ou mantêm o efeito ("sem contornar").
- `tests/test_jarvis_nucleo.py`, classe `Diretrizes18e19`: prende as frases das travas (prazo no comando, nada novo na pausa, gravar onde parou, subagente na `esperar-estado`, volta a instância nova); só lê arquivos do repositório, sem ambiente nem rede.

## Achados

## Sondas
- S1 · `bash -c 'unset N; fim=$((SECONDS+N)); echo fim=$fim s=$SECONDS'` · espera: prazo já vencido (marcador esquecido não prende o laço) · obtido: `fim=0 s=0`

## Detalhe dos achados
Sem achado aberto. A1 e A2 da 1ª rodada (ambos recomendados) foram corrigidos em afdaa3ab (SKILL.md:19).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Delta lido por `forge-check parecer delta` e `git diff be5bb7ee..afdaa3ab` numa worktree destacada no head revisado; rodado só `tests.test_jarvis_nucleo` (`R-TETO`), 17 testes OK. Varreduras de segredos e de workflow não se aplicam (só texto e teste de texto, sem workflow tocado).
