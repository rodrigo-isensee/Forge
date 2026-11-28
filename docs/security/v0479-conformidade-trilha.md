---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-conformidade-trilha
commit: dd1fc980fa57547c88dbf3d98fe35577b05fe522
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: v0478 (E63.24, revalidação da trilha do conformidade)

Volta por delta. As rodadas anteriores (até o head `a247ae11`, A1 a A18 e S1 a S22) ficam no git e não são recopiadas aqui.

Gatilhos: hook de conformidade (analisador de comando), R-VERIFY, R-FLUXO, pastas de controle do Jarvis (VV-2), catraca do CI (afrouxa-regra).

## Delta lido
`forge-check parecer delta` (`a247ae11..dd1fc980`): no domínio, só `docs/hooks.md` (uma linha, a 56). O resto do intervalo são os três pareceres da rodada anterior. `hooks/conformidade.py`, `hooks/conformidade.json`, as fixtures e o corpus não mudaram.

## Achados anteriores
- A18 (recomendado, fechado) docs/hooks.md:56. O texto agora diz que o link criado por cópia na mesma linha não recusa e lista as formas: `cp -a`, `cp -P`, `cp -d`, `cp -r`, `cp --no-dereference`, `rsync -a`, `tar -x` e `os.symlink` no `python3 -c`. É a mesma lista da correção mínima da rodada `7a739fca`. Também aponta o cartão CONFORMIDADE-LINK-POR-COPIA, que está no quadro da pasta de controle (`~/.forge-contrib/KANBAN.md:163`, com registro em `docs/kanban/historico.md:1988`). O "o link criado na mesma linha recusa (A17)" do fim do parágrafo agora fica restrito pela frase anterior, então não diz mais do que o hook cobre.

Sem achados novos.

Sem suíte local, como pede o brief. Ainda não há PR, então não há CI para citar.

## Confirmações (head dd1fc980)
Confirmação: só aperta. Do `a247ae11` ao `dd1fc980`, o código do hook, a política, as fixtures e o corpus não mudaram. O delta só declara em documentação um limite que já valia na develop. Por isso continuam valendo as conclusões das rodadas `7a739fca` e `a247ae11`: a trilha não abre nem reabre porta frente à develop `c8e8a08d`, e o custo do corpus fica em 0,093%.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas locais: `forge-check parecer delta` e `git diff`. Lacunas: gitleaks, semgrep, zizmor e actionlint estão fora do PATH. O delta não toca workflow, dependência nem segredo.
