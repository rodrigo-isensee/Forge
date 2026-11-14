---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-folga-jarvis
commit: 16b7ca7443c01eb8a8e532d82ac0ea69948e4722
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-14
---
# Review de segurança: v047 (folga do texto do Jarvis e FOCO-NAS-DECISOES, revalidação E1.192)

Revalidação por delta `8a223677..16b7ca74` (merge da develop `f4b0c2ae`, com conflito em `tests/test_reval_delta.py` resolvido pelo integrador). `forge-check parecer delta` rc=0: no domínio só `templates/projeto/CLAUDE.md` (linha **Ambiente** vinda da develop: orientação de desligar a atualização automática da extensão, sem credencial, comando nem afrouxamento de regra); fora dele, `tests/test_forge.py` e `tests/test_reval_delta.py`. Reli a resolução do conflito por `git show --remerge-diff 16b7ca74`: a união das duas entradas de `CITACOES_CONHECIDAS` (`tests/apoio_jarvis.py` da branch e `tests/test_ambiente_sem_auto_update.py` da develop), sem perder linha de nenhum lado; o diff `f4b0c2ae..16b7ca74` em `tests/test_forge.py` é o mesmo já revisado no 8a223677 (catraca `LEGADO_TRECHOS_MAXIMO` só desce, 284 para 225). Suíte: sem PR nem CI; rodei `tests.test_reval_delta` (10, OK) e `tests.test_forge` (RegrasInviolaveis, Agentes, PraticasDeEspecificacao) com `tests.test_ambiente_sem_auto_update` (14, OK).

## Gatilhos
`R-SEGURANCA`: controles do Forge (teste de presença das regras com ID e das diretrizes).

## Achados
- A1 (recomendado) tests/apoio_jarvis.py:84 · corrigido no 8a223677: a presença do ID só conta em agents/jarvis.md e skills/*/SKILL.md (TEXTO_DO_JARVIS); o merge 16b7ca74 não toca o arquivo. Fica registrado, sem pendência
- A2 (recomendado) tests/fixtures/diretrizes-do-dono.json:164 · diretrizes 26, 27 e 28 entram como pendente (MAX_PENDENTES = 7); sem mudança no delta; decisão de escopo sem caminho de ataque, levar ao dono pelo Jarvis (`R-DECISAO`)

## Sondas
- S1 · git show --remerge-diff 16b7ca74 -- tests/test_reval_delta.py · espera: as duas entradas de CITACOES_CONHECIDAS mantidas · obtido: apoio_jarvis.py e test_ambiente_sem_auto_update.py presentes, só os marcadores de conflito removidos

## Detalhe dos achados
**A1 e A2.** Sem mudança desde o parecer do 8a223677 (commit `34cf0c6e`); o merge não toca `tests/apoio_jarvis.py`, `tests/test_jarvis_nucleo.py`, `tests/config.json` nem as fixtures pelo lado da branch. Nenhum bloqueante.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: git, a biblioteca padrão do Python e os testes do repositório. `gitleaks` ausente no PATH (lacuna; o delta é texto de modelo e teste, sem credencial).
