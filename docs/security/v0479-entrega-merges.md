---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-entrega-merges
commit: 7bfe5cc8f5d288500c63894a8ff985576d958aa6
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: v0478 (E62.21), melhoria/v0479-entrega-merges (revalidação)

Gatilhos: controle do Forge (`bin/forge-check entrega`), afrouxa o escopo do autor (ENTREGA-MERGE-DA-DEVELOP, ENTREGA-MERGE-DE-PARECER-ANINHADO).

Volta por delta. Rodada anterior (reprovado em `590d1954`, A1 e A2 bloqueantes, A3 a A5 recomendados) fica no git. Delta lido: `forge-check parecer delta` de `590d1954..7bfe5cc8`, no domínio `bin/forge-check` (`remoto_da_branch`, `vindos_do_remoto_da_base`, `conferido_mais_novo`, `vale_pelo_conferido`, texto da linha sem âncora) e `tests/test_forge_check_base_igual.py`; fora do domínio, só changelog, mutantes e `tests/test_selo_e_entrega.py` (lido nas classes de abuso que rodei). Nenhum bloqueante novo: as sondas S1 a S3 da rodada anterior e a de A4, refeitas no head novo, agora reprovam a entrega.

## Estado dos achados anteriores
- A1 (bloqueante): corrigido. `bin/forge-check:7390` aceita só a linha cujo ref é exatamente `refs/heads/<branch>`; testes `tests/test_selo_e_entrega.py:1353` e `:1366`. S1 refeita: `ls-remote` lista `refs/heads/a/refs/heads/develop` antes da develop e o `entrega` sai `fora do declarado no brief "agents/fora.md"`, `não cumpriu`.
- A2 (bloqueante): corrigido. `bin/forge-check:2873` exige um só merge-base (`--all`) e `:2877` exige que ele esteja na 1.a linha de pais da develop remota; testes `:1394`, `:1402`, `:1420`. S2 refeita (merge-base igual ao commit lateral X, head com "fraco") sai `fora do declarado no brief "agents/guarda.md"`, `não cumpriu`; S3 (KANBAN.md apagado por X) sai `fora do declarado no brief "KANBAN.md"`, `não cumpriu`.
- A3 (recomendado): corrigido. `bin/forge-check:2880` exige blob não vazio no head (`"" != blob_de(...)`); teste `:1408`.
- A4 (recomendado): corrigido. `bin/forge-check:2520-2535` só aceita o conferido mais novo que muda o arquivo, com o mesmo blob no merge, no outro pai e nele; testes `:1953`, `:1964`, `:1981`. Sonda de A4 refeita (merge de P2 resolvido à mão com o blob de P1) agora recusa: `o merge ... traz "docs/reviews/x.md" fora dos pareceres conferidos`.
- A5 (recomendado): corrigido. `bin/forge-check:3270` diz "segue no escopo, salvo o igual ao merge-base com a base do `git ls-remote origin`", coerente com a linha de integração pelo remoto.

Sem brecha nova vista no delta: a ponta remota exata, o merge-base único na 1.a linha de pais e o blob presente fecham as três formas provadas; o que ainda sai do escopo é um estado real da develop remota, que o autor não reescreve (`R-MAIN`, pre-push e proteção do servidor). O teste novo `tests/test_forge_check_base_igual.py` (nome definido uma vez no módulo) fecha a classe de defeito que desligou o `commit_vale` na rodada anterior.

Sobre o rótulo afrouxa-regra: a mudança continua aceitando mais do que hoje (o trazido da develop remota sai do escopo do autor e o parecer aninhado vale pelo conferido mais novo); com os limites acima, avalio o afrouxamento como contido. A avaliação é para a lista do dono, que decide o rótulo.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Suíte: não rodei a suíte inteira (fica no CI); CI do head não consultado (sem PR e sem credencial do `gh` no sandbox). Rodei `MergeDaBaseDepoisDoBrief`, `MergeDeParecerAninhado` e `tests/test_forge_check_base_igual.py` (45 testes, OK) e as sondas da rodada anterior por subclasses fora da árvore. Ferramentas ausentes no PATH: gitleaks, semgrep, zizmor, actionlint (lacuna; o delta não toca workflow nem traz segredo à leitura).
