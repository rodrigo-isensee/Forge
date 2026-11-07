---
tipo: revisao-seguranca
contrato: 1
pedido: release-0.42.0
branch: melhoria/release-0.42.0
commit: 7a189d413dce70cf200d74f0a4a29d97fd2d704c
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-07
---
# Review de segurança: release-0.42.0

A leva da 0.42.0 vai da main 0.34.0 (a74c752) até o commit de release 7a189d4. Ela reúne os PRs #460 (brief-forma-aceita), #461 (push-parecer-ja-no-remoto) e #462 (branch única 0.35 a 0.42), além do commit de release. A árvore de a74c752 é igual à de f24ffb8 (`git diff` vazio), o primeiro pai do merge do #460, então o diff da leva é o desses três merges mais o release. Cada PR tem os próprios pareceres. Aqui a pergunta é se a soma deles abre, nos controles do Forge, um caminho que nenhum PR abria sozinho, e se cada afrouxamento do CHANGELOG 0.42.0 tem a DECISÃO DO DONO que o cobre. Não sou autor de nada da leva.

## Gatilhos
`R-SEGURANCA`, controles do Forge. No diff a74c752..7a189d4 entram `bin/forge-check` (+1560), `bin/forge-fechar`, `bin/forge-testes`, `hooks/conformidade.py`, `hooks/conformidade.json`, `hooks/pesado.py`, `.githooks/pre-push`, `scripts/` (verificar-contribuicao, arvore-testada, conferir-promocao, placar-mutacao) e `tests/catraca.py`. Em `.github/`, a leva só toca o modelo de PR (3 linhas de texto, a linha `Rótulo:`). Não há workflow, e isso fica com o parecer de devops.

## Achados
- A1 (recomendado) bin/forge-check:5976 · delta_de_brief percorre só SECOES_BRIEF e ignora a seção nova Formas aceitas pelos hooks (#460, :5541-5542): mudar só ela entre o brief anterior e o novo dá `delta: nenhum` à rodada de confirmação; antes o texto caía no Pronto quando e aparecia no delta.
- A2 (recomendado) .githooks/pre-push:222 · o A1 do parecer do #461 segue aberto na leva: ls-remote em $2 aplica url.insteadOf depois do pushInsteadOf do push; falhar fechado se `git ls-remote --get-url -- "$destino"` diferir de $destino.

## Sondas

## Detalhe dos achados
**A1.** Evidência: `bin/forge-check:5541-5542` põe `SECAO_DAS_FORMAS` no `CABECALHO_BRIEF`, e `delta_de_brief` (`:5976-5988`) itera só `SECOES_BRIEF` (`:5537`). `conferir_brief` (`:6388`) também não lê essa seção. Sonda local, só leitura, com a função carregada do `bin/forge-check` de 7a189d4: dois briefs que diferem só na linha da seção (`git commit -m 'a'` trocado por `git push origin HEAD`) dão `['delta: nenhum']`. Caminho de ataque: quem escreve o brief (o Jarvis, ou uma instrução injetada nele) muda numa volta a forma oferecida, e a confirmação por delta (M12) não a mostra ao conferente. O impacto é baixo, porque o hook `conformidade` continua barrando as formas proibidas (`--no-verify`, `--force`, heredoc fora do `<<'EOF'` exato), seja qual for a forma escrita no brief. Severidade: baixa. Correção mínima, uma das duas: (a) `conferir_brief` reprova a seção quando ela difere do que `FORMAS_DE_COMMIT` gera; (b) `delta_de_brief` inclui `SECAO_DAS_FORMAS`. Esforço: P. Dono: `forge:tech-lead`.

**A2.** Evidência e reprodução no parecer `docs/security/push-parecer-ja-no-remoto.md` (A1, sobre d2460c9). O código não mudou até 7a189d4: o `ls-remote` está em `.githooks/pre-push:222`, e o pulo em `:232` e `:321`, sem a conferência `--get-url`. O caminho é o mesmo: só quem escreve a config ou a linha do `git push`. Esse ator já desliga o hook com `core.hooksPath`, e o CI do PR roda a suíte inteira. Severidade: baixa. Correção mínima: uma linha antes do laço de `ja_no_remoto`, `[ "$(git ls-remote --get-url -- "$destino" 2>/dev/null)" = "$destino" ] || return 1`, e um caso no teste com as duas regras encadeadas. Esforço: P. Dono: `forge:tech-lead`. Se não for corrigido, vai ao corpo do PR homolog → main como residual, junto do A10 do modelo da versao-035.

**Composição da leva.**
- Os três merges (#460 86724d7, #461 bb45aac, #462 a64c99a) têm a árvore igual à do merge automático (`git merge-tree --write-tree` sobre os dois pais). Nenhum foi resolvido à mão.
- #460 toca `bin/forge-check` (a seção de formas no brief gerado, mais a constante) e `bin/forge-testes` (o mapa). O review o deu sem gatilho e ele não tem parecer de segurança próprio. Li o diff inteiro: a seção é saída do `brief gerar`, e o hook não lê o brief para decidir o que aceita. Fora o A1, não há caminho novo. O `hooks/` não foi tocado.
- #461: o parecer de segurança aprovou em d2460c9. O delta d2460c9..a8fba0e (head do PR) só tem pareceres de review, QA e segurança, sem código. O A2 vem daí.
- #462: o parecer consolidado `docs/security/uniao-035-042.md` aprovou em 9e87a91. O delta 9e87a91..979c372 (head do PR) só tem pareceres. `hooks/`, `bin/`, `.githooks/`, `.github/`, `scripts/` e `tests/` são iguais nos dois commits. Os recomendados dos grupos g1 a g7 listados ali seguem valendo para a leva, e não os repito.
- Interação #461 × #462 no `.githooks/pre-push`: a varredura de segredo do delta (I3, #462) e o pulo `ja_no_remoto` (#461) convivem. O pulo sai antes da varredura, mas só quando o remoto já tem cada branch no mesmo sha ou num descendente, e nesse caso o conteúdo já está no remoto e o push não leva nada novo. Tag, ref nova e remoção misturada não pulam. O `shellcheck -S warning` deu rc 0 no pre-push de 7a189d4.
- Commit de release 7a189d4: muda só a versão em `.claude-plugin/plugin.json` e em `dev/.claude-plugin/plugin.json` (0.34.0 → 0.42.0), o `CHANGELOG.md` e a remoção dos dois fragmentos. As 65 linhas dos fragmentos removidos estão no CHANGELOG, com três linhas da ACELERA-P2 fundidas numa só pelo `forge-changelog`. Sobra só `changelog.d/README.md`.

**Afrouxamentos do CHANGELOG 0.42.0 e a decisão que cobre cada um** (linhas DECISÃO DO DONO em `~/.forge-contrib/docs/pedidos/`):
- PUSH-PARECER-JA-NO-REMOTO (Alterado): versao-035, 2026-11-05 15:20 (E3, afrouxa-regra).
- CONFERENTE-INCONSISTENTE (Alterado): versao-035, 2026-11-05 15:20 (E4, afrouxa-regra).
- Aprovação do brief lida no quadro do forge-contrib e decisão posterior que não reprova o brief em voo (Corrigido, BRIEF-DECISAO-POSTERIOR): versao-035, 2026-11-05 15:20 (E5).
- EST-M4, o delta só de texto que não envelhece review nem QA: versao-037, 2026-11-06 09:41 (decisão 4, entra na 0.37), e versao-035, 2026-11-07 16:28 (efeito sobre o R-PROVA aprovado, com cartão PROVA-COMMIT-EXATO na 0.43). A linha do CHANGELOG cita a reversão, mas não a data da decisão. Isso é só texto e não abre achado.
- ACELERA-E2B, `forge-check vazio`: decisão do dono de 2026-10-27, citada na própria linha.
- N-JAR-A (D3, Q2): decisões do dono de 2026-10-21, citadas na linha, com afrouxa-regra.
- R-REVIEW em toda entrega (EST-M6): decisão 7b do dono de 2026-11-06.
- REVALIDA-MESMA-INSTANCIA: decisão do dono de 2026-11-06 (decisão 27).
- Versão do cache do plugin (FC-VERSAO-CACHE-PLUGIN): versao-037, 2026-11-06 11:59 e 12:08.
- Não afrouxam controle: ACELERA-P1 (só imprime, nada é dispensado), `arvore-testada.py` e `conferir-promocao.py` (ainda sem chamador) e `comando_vivo` (sem chamador). As entradas de S8, I3, I4 (`forge-fechar`), EXT-1, VOLTAS-REVISOR-WT e PAR-P1/P2 apertam.

Nenhum afrouxamento da leva ficou sem a DECISÃO DO DONO.

## Riscos aceitos e ferramentas
Nenhum risco aceito novo. Os afrouxamentos listados acima têm decisão do dono e o rótulo afrouxa-regra nos PRs de origem (#461, #462). O residual A10 da versao-035 (o remoto recebeu o commit de quem não passou pelo hook) segue coberto pelo CI do PR.

Ferramentas: git (diff, merge-tree, ls-tree), leitura do código, `shellcheck -S warning` no `.githooks/pre-push` (rc 0) e uma sonda local do `delta_de_brief` (A1). Não rodei a suíte (R-TETO): o push de 7a189d4 rodou 1190 testes afetados, OK. Faltam no PATH o varredor de segredos, o SAST, o analisador de workflows, o auditor de dependências e o varredor de imagens. A lacuna fica registrada e as varreduras rodam no CI. A leva não traz dependência nova.

## Parecer
Aprovado. A soma dos três PRs e do commit de release não abre caminho novo nos controles do Forge além dos dois recomendados de severidade baixa (A1 novo, A2 herdado do #461), que não devolvem a entrega. Os merges não têm resolução manual, a versão bate com o CHANGELOG e todo afrouxamento tem a DECISÃO DO DONO que o cobre.
