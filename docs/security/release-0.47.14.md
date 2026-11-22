---
tipo: revisao-seguranca
contrato: 1
pedido: release-0.47.14
branch: melhoria/v0479-release-04714
commit: 5067fedacf87005b2a96c13e5af4b8d57b32d0fa
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: release 0.47.14 (versão inteira), marca no head 5067feda

Etapa E76.16 do pedido v0478. Volta por delta sobre o parecer da promoção no head `d35b56f6` (commit `619cb81f`), que fica no git. Mesmo veredito e conteúdo do parecer do pedido `docs/security/v0479-release-04714.md` (commit `c505ab46`, aprovado no `5067feda`), que traz a junção `ac544ac5`, o #775 igual ao revisado (patch-id `8b491567`) e a marca.

Gatilhos: hooks (`conformidade`, `doutor`, `agentes`), execução de comando (`bin/forge-check`, `bin/forge-copia`, `bin/forge-fechar`, `bin/forge-init`, `bin/forge-testes`, `bin/forge-pesado`, `scripts/jarvis`), apagamento de arquivo (`forge-copia limpar`, `forge-fechar --limpar`), regra afrouxada (#745, #752, #761, #767), release usada por todos os projetos.

## Detalhe dos achados
Sem achados.

- **Delta lido.** `forge-check parecer delta docs/security/release-0.47.14.md` em `d35b56f6..d3c4cbac`, sem o que veio da base: "nenhum arquivo do domínio mudou"; fora do domínio, `CHANGELOG.md` e `docs/engineering/placar-mutacao.md`. Da develop vieram #766 a #775, cada um com parecer próprio aprovado; a junção deles foi conferida nos pareceres do pedido `ef42cfad` (#766 a #774) e `c505ab46` (#775). `5067feda..d3c4cbac` só toca pareceres (`docs/{qa,reviews,security}/v0479-release-04714.md`).
- **Já lido (rodada `d35b56f6`, sem mudança):** junção por patch-id dos 14 itens #745 a #765, segredo e dependência.
- **Versão.** Os dois `plugin.json` (`.claude-plugin/` e `dev/.claude-plugin/`) em `0.47.14`, igual a `## [0.47.14] - 2026-11-21` do `CHANGELOG.md`, em português; `[Não publicado]` vazio; `changelog.d/` só com `README.md`.
- **Hooks medidos.** `bin/forge-check comparar v0.47.13 5067feda`: `so-aperta: medido base=39956e72 head=5067feda casos=215 aceites-novos=0`. A medida cobre só hooks; os afrouxamentos abaixo estão em `bin/`.

## Só aperta? (para o rótulo afrouxa-regra da promoção)
A versão não só aperta frente à 0.47.13; o rótulo afrouxa-regra é obrigatório na promoção.
- **Afrouxam:** #745, #752, #761 e #767 (classificação no parecer `ef42cfad`).
- **Só corrige:** #773.
- **Só apertam:** #754, #755, #756, #757, #758, #759, #760, #762, #763, #764, #765, #766, #768, #769, #770, #771, #772, #774 e #775.

A pendência da rodada anterior (OK do dono para o #752 e o #761) está resolvida para o rótulo da promoção pelas decisões do pedido v0478:
- DECISÃO DO DONO de 2026-11-21 19:43: o time aplica o rótulo afrouxa-regra nos PRs de versão e mescla homolog → main; degrau mantido; sem `--admin`, sem exceção do ruleset, sem `--force` nem `--no-verify`; hook ou proteção que barrar não se contorna.
- DECISÃO DO DONO de 2026-11-21 20:15: a permissão vale até 2026-11-23 09:00, só pelo caminho develop → homolog → main, com todos os checks do PR verdes (catraca incluída) conferidos logo antes, com os pareceres da versão aprovados; nunca exceção do ruleset nem `--admin`; hook da main que recusar deixa o PR verde para o dono; CI da main vermelho depois do merge reverte na hora pelo caminho normal e avisa; merge automático proibido em qualquer PR (`forge-fechar --armar`, `gh pr merge --auto`); lista dos merges na main com o motivo de cada rótulo na segunda.

## Riscos aceitos e ferramentas
Nenhum risco aceito nem pendente de aceite. A suíte inteira roda no CI do PR de promoção, que exige o CI verde. Localmente só a medida `comparar`. Lacuna: gitleaks, osv-scanner, semgrep, zizmor e actionlint fora do PATH. A versão não toca workflow nem dependência.
