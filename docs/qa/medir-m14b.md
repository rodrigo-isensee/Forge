---
tipo: qa
contrato: 1
pedido: MEDIR-M14B-REV
branch: melhoria/medir-m14b
commit: eaaccc6677ab02ac009cd62e1d2142cc5a173ef8
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-23
---
# QA: MEDIR-M14B-REV

## Achados

## Critério → teste → resultado
Não há especificação de UX nem contrato de API; a obrigação é a linha `MELHORIA: M14b` do estudo (cinco medidas) e o escopo de `MEDIR-M14B`.

| Obrigação (M14b) | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| 1. custo por pedido, `--pedido` casa os cartões | `tests/test_medidas_m14b.py` (casamento) + execução real sobre transcrições | pedido sem cartão, id inválido, prefixo sem hífen, controle no nome | passou |
| 2. esperas pelo dono e credencial | `test_medidas_m14b.py` (esperas) + execução real sobre `historico.md` | histórico ausente, espera aberta, continuidade entre colunas | passou |
| 3. PRs `fix` que corrigem PR mesclado | `test_medidas_m14b.py` (corrigidos) + execução real | ref inexistente, `cita` x `arquivo` | passou |
| 4. defeito escapado (registrar e resumo) | `test_medidas_m14b.py` (escape) | campo recusado sem eco do valor, link simbólico, sem `KANBAN.md` | passou |
| 5. rótulos `afrouxa-regra` reais | `test_medidas_m14b.py` (afrouxamentos) + execução real com 83 PRs | JSON ruim, PR sem commit local, erro do git | passou |
| Textos citam as medidas (Jarvis, agile-coach, tabela) | último grupo de `test_medidas_m14b.py` | n/a | passou |
| Suporte: `bin/forge-testes` e `test_testes_tocados.py` | `MapaDoForgeCheck`, `test_testes_tocados` | módulo novo fora do mapa | passou |

## Cenários e resultado real
Ambiente: worktree detached em `eaaccc6`, Python 3.14, base `origin/develop` 7423c44.

- Suíte completa: `bin/forge-testes --base origin/develop` (escolheu a completa porque `bin/forge-testes` mexe no mapa): `Ran 1623 tests in 850.835s`, `OK (skipped=1)`. O skip é anterior a esta branch; actionlint ausente no PATH só pulou o lint do workflow.
- Vermelho antes do verde: com o `bin/forge-check` da `origin/develop` no lugar do da branch, `python3 -m unittest tests.test_medidas_m14b` deu `Ran 29 tests`, `FAILED (failures=36, errors=3)`; com o da branch, `OK`. O arquivo foi restaurado (`git status` limpo).
- Mutação: o Forge não tem ferramenta de mutação gratuita configurada; não rodada. Fica dito, não suprido.
- Acessibilidade e E2E: não se aplicam (CLI, sem interface).

### As cinco medidas sobre o histórico real
O histórico do quadro está em `~/.forge-contrib/forge`; o `docs/kanban/historico.md` não existe na árvore do repositório, e a worktree devolve "ausente", sem erro.

1. **Custo por pedido** (`transcricao custo <pasta> --pedido`, 177 transcrições, 1,7 a 2,2 s). Usável: `FIX-SUITE-LOCAL` deu 84,7 M de tokens (principal 61,6 M, subagentes por tipo, 1 relançamento do tech-lead, 0 compactações) e `VOLTAS-CLASSE` 91,0 M, ambos com a janela dos cartões casados. Falta: (a) as janelas de pedidos concorrentes se sobrepõem e o principal se mistura (o próprio comando avisa "4 outros cartões em movimento"), então o número por pedido é teto, não exclusivo, e a soma dos pedidos passa do total; (b) `MEDIR-M14B` não tem cartão no histórico, logo o próprio pedido não é medível (`sem movimento de cartão`); (c) o padrão sem `<pasta>` falha em `~/.forge-contrib/forge` (`caminho inexistente`), igual na `develop` (anterior à branch), então é preciso passar a pasta das sessões.
2. **Esperas** (`--raiz ~/.forge-contrib/forge`, 78 linhas, 49 cartões, 0,3 s). Usável, com amostra pequena: dono=3 (739,1 min fechada, mais duas abertas), credencial=0, outra=4 (1287,1 min). A espera do dono só existe quando o motivo diz "Aguardando o dono". Falta: `FIX-SUITE-LOCAL` figura como espera aberta do dono, embora o PR #288 esteja mesclado (o quadro não registrou o fim), e `PARECER-MERGE-BASE` idem; sem fechar a espera no quadro, o minuto cresce sem parar. Credencial zero pode ser "nunca esperou" ou "nunca registrou"; hoje o dado não distingue.
3. **Corrigidos** (`corrigidos`, ref 7423c44, 0,5 s). Usável só pela coluna `cita`: 185 PRs, 31 `fix`, 4 `cita`, 26 `arquivo`, 1 `nenhuma`. O mínimo defensável é 4 de 31 (13%) como prova e até 26 como indício ruidoso; a linha de base deve publicar os dois números separados, nunca somar.
4. **Escapes** (`escape resumo`). Funciona, mas sem dado: 0 escapes, 2 pedidos prontos, taxa 0,00. Isso é "não medido" (o registro começa agora, `docs/kanban/escapes.md` não existe), não "zero defeito"; a linha de base não deve publicar 0%.
5. **Afrouxamentos** (`afrouxamentos --rotulados` com 83 PRs rotulados lidos do GitHub, 1 min 40 s): `real=11` (todos `R-CONFORMIDADE`), `so-protegido=41`, `sem-violacao=2`, `sem-commit=29`, `erro-git=0`. Usável como faixa: de 54 PRs avaliados, 11 (20%) eram afrouxamento real; os 29 `sem-commit` (35% dos rotulados) não têm o commit no clone local e ficam sem veredito. O estudo falava em 82 rótulos, hoje são 83. Falta: a comparação do sha da `homolog` com o da `develop` da linha do estudo (já anotada pelo review como medida à parte).

## Bugs
Nenhum aberto (`docs/qa/bugs/` não ganha arquivo). Os pontos acima são limites de dado, não defeito do código; os que pedem ação ficam como recomendação, sem bloquear.

## Recomendações (não bloqueiam)
- Registrar no quadro o fim da espera do dono (`forge-check movimento`) e fechar as duas esperas abertas antes de gravar a linha de base.
- Publicar o custo por pedido como teto, citando o aviso de cartões concorrentes.
- Publicar escapes como "não medido" até haver registro.
- Buscar as refs dos PRs antes de gravar o número de afrouxamentos reais, para reduzir os 29 `sem-commit`.
