---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-bp10-desenho
commit: b7c3c707f8b99499bf39102a48996d042aca8618
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-23
---
# Review: v0478 (E139.5, desenho da BP10)

Item só de texto (`docs/propostas/bp10-higiene-segredo.md`, 55 linhas, Base-sha 0e59c446), um parecer só (ORDEM DO DONO 21/11 22:13, item 1). Nenhum hook, script, teste ou CI mudou; teto H1 não se aplica (só documentação).

## Ferramentas citadas
- `python3 -m unittest tests.test_forge.Neutralidade tests.test_forge.NeutralidadeDoNucleo` no head 6273bbea: `Ran 6 tests`, `OK`.
- `bin/forge-check docs`: saída 0. A suíte inteira fica no CI do PR #828.

## Troca de trava da fatia C2 contra a regra do dono de 21/11
DECISÃO DO DONO 2026-11-21 20:54, item 3: trava nova de processo só entra se tirar ou simplificar outra. O C2 declara-se trava nova, aponta a que sai (`.githooks/pre-push:360-372`, SENTINELA-CAMINHO-LOCAL), marca a troca como pergunta ao dono (`R-DECISAO`) e cai para aviso se ele recusar. A forma atende à regra.

Conferi o mérito no código da base:
- A primeira passada (`.githooks/pre-push:212-234`) roda o `scripts/verificar-contribuicao.sh` lido da `develop` no delta de cada ref, com o script inteiro (segredo, `.env` e caminho pessoal, `scripts/verificar-contribuicao.sh:2-3`), e recusa o envio. A segunda passada roda o mesmo script, lido da árvore, no delta desde a `develop`; as duas rodam no envio leve padrão (antes do `exit 0` de `:401-405`).
- A segunda só pega algo a mais quando a própria branch muda o script (padrão novo) ou quando a base não tem o script (só nos fixtures de `tests/test_pre_push_afetados.py:429-445`). O CI (`.github/workflows/ci.yml:727-737`) cobre esse resíduo, mas depois do envio: segredo do padrão novo já estaria no remoto (A1).
- Conclusão: a trava que sai é quase toda redundante; a troca é legítima e o custo líquido cai no Forge. O teste da segunda passada (`tests/test_pre_push_afetados.py:429-445`) sai junto, e o pronto (g) já prevê a suíte do pre-push verde.

## Revalidação (E139.15, head b7c3c707)
Delta lido: `forge-check parecer delta docs/reviews/v0480-bp10-desenho.md`, intervalo `6273bbea..b7c3c707`, no domínio só `changelog.d/v0480-bp10-desenho.md` (novo, 2 linhas, seção `### Adicionado`). O nome bate com a branch sem prefixo e o texto descreve o que o PR entrega (proposta, sem mudança de hook). Ferramentas: `bin/forge-changelog conferir --base 0e59c446 --branch melhoria/v0480-bp10-desenho` saída 0 (`ok: 1 fragmento(s) novo(s)`); `python3 -m unittest tests.test_changelog` `Ran 89 tests`, `OK`. O delta não toca a proposta; os achados A1 a A5 seguem como estavam.

## Achados
- A1 (recomendado) docs/propostas/bp10-higiene-segredo.md:39 · "a segunda só antecipa o que o CI barra" omite o resíduo: branch que muda scripts/verificar-contribuicao.sh e traz, no mesmo envio, segredo do padrão novo chega ao remoto antes do CI (a 1a passada lê o script da develop, .githooks/pre-push:215). Citar na pergunta ao dono.
- A2 (recomendado) docs/propostas/bp10-higiene-segredo.md:38 · levar o script de segredo para bin/ muda o caminho que a 1a passada lê da develop (.githooks/pre-push:215), o passo do CI (ci.yml:732) e os testes; o corte não diz a transição (as duas cópias por uma versão, ou o pre-push lendo os dois caminhos).
- A3 (recomendado) docs/propostas/bp10-higiene-segredo.md:22 · tornar público não é ato confirmado: hooks/conformidade.py:3377 e :3384 chamam barrar; e não há regra para gh repo create --public (public no hook só em :328, :393, :3376, :3383). Corrigir a evidência e o pronto (c) do C3 (:42-43).
- A4 (recomendado) docs/propostas/bp10-higiene-segredo.md:38 · o C2 cria recusa num hook de git do projeto; a ORDEM DO DONO 21/11 22:13 (item 4) diz que os hooks só orientam e a proteção vem do sandbox e do GitHub. A pergunta ao dono deve citar as duas decisões, não só a de 20:54.
- A5 (recomendado) docs/propostas/bp10-higiene-segredo.md:35 · C1 e C2 são mecanismos novos sem critério de reversão (R-DECISAO): por exemplo, C1 sai se gerar aviso falso no corpus real de uma semana; C2 volta a aviso se recusar em falso N vezes. A data de revisão (:3) não basta.

## Sondas

## Parecer
Aprovado. O desenho cumpre o cartão BP10: três frentes com evidência `arquivo:linha` conferível (conferi `:11-25`; a contagem 819 de 2631 commits com o link de sessão bate na base), corte em fatias independentes com pronto testável e casos de abuso, custo zero (`R-CUSTO`) e texto neutro (`R-NEUTRO`, testes verdes). A troca de trava do C2 segue a regra 3 do dono de 21/11 e fica, como deve, para a decisão dele. Os cinco achados são `recomendado`: ajuste de texto que o autor da fatia faz ao abri-la, ou cartão depois do merge; nenhum muda o corte nem é defeito com gatilho neste PR, que só tem texto.
