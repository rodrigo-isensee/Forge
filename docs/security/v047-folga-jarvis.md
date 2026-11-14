---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-folga-jarvis
commit: 8a223677c7320a968c0984ac538892ed403c6540
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-14
---
# Review de segurança: v047 (folga do texto do Jarvis e FOCO-NAS-DECISOES, revalidação E1.183)

Revalidação por delta `ebeb9161..8a223677` (volta da E1.176). `forge-check parecer delta` rc=0: nenhum arquivo do domínio mudou; fora dele, `tests/apoio_jarvis.py`, `tests/test_jarvis_nucleo.py` e `tests/mutantes/v047-folga-jarvis.json`, que reli por serem o controle do A1. Suíte: sem PR nem CI; rodei `tests.test_jarvis_nucleo` (40 testes, OK, 1 pulo esperado sem `FORGE_DIRETRIZES_DONO`), a sonda S1 e os 3 mutantes.

## Gatilhos
`R-SEGURANCA`: controles do Forge (teste de presença das regras com ID e das diretrizes).

## Achados
- A1 (recomendado) tests/apoio_jarvis.py:84 · corrigido no 8a223677: a presença do ID só conta em agents/jarvis.md e skills/*/SKILL.md (TEXTO_DO_JARVIS); S1 agora reprova e o mutante novo cobre o índice no conjunto. Fica registrado, sem pendência
- A2 (recomendado) tests/fixtures/diretrizes-do-dono.json:164 · diretrizes 26, 27 e 28 entram como pendente (MAX_PENDENTES = 7, test_jarvis_nucleo.py:27); a decisão de 14/11 08:38 nomeia só 2, 11, 23 e 24, e a de 13/11 19:52 pede presença de 1 a 26: levar ao dono pelo Jarvis (`R-DECISAO`)

## Sondas
- S1 · git archive de 8a223677; tirar as crases de `R-SEGURANCA` em agents/jarvis.md e skills/*/SKILL.md; problemas_das_regras(raiz, conjunto_do_jarvis(raiz)) · espera: ["R-SEGURANCA: não aparece no Jarvis nem nas skills citadas"] · obtido: o mesmo (índice no conjunto; árvore real: [])
- S2 · mutantes M1, M2 e M3 de tests/mutantes/v047-folga-jarvis.json aplicados um a um em cópia de 8a223677, rodando o teste listado · espera: os 3 mortos · obtido: M1 morto, M2 morto, M3 morto

## Detalhe dos achados
**A1 (era bloqueante no ebeb9161, corrigido).** `tests/apoio_jarvis.py:20` define `TEXTO_DO_JARVIS` (fullmatch em `agents/jarvis.md` ou `skills/<nome>/SKILL.md`) e `:84` filtra o conjunto por ele; o índice `docs/regras/README.md` continua no conjunto (pela R-WIP, que também está no Jarvis e em `trabalho-em-paralelo`), mas não conta mais para a presença. `tests/test_jarvis_nucleo.py:339` põe o índice no conjunto sintético e exige a reprovação do ID ausente, depois a aprovação com o ID numa skill. É a correção mínima pedida; rebaixado a recomendado só como registro.

**A2.** Sem mudança desde o parecer do ebeb9161: decisão de escopo, sem caminho de ataque; vai ao dono pelo Jarvis (`R-DECISAO`). Não bloqueia.

O foco do brief anterior (invariantes movidos sem sumir, legado e catraca só descendo, texto movido sem mudar palavra) vale: o delta não toca `tests/config.json`, `agents/`, `skills/` nem as fixtures.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: git, a biblioteca padrão do Python e os testes do repositório. `gitleaks` ausente no PATH (lacuna; o delta é teste, sem credencial).
