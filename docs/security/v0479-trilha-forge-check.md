---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-trilha-forge-check
commit: d2f79996cc41129fab309d802639e83228d981c8
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: v0478 E91.10 (TRILHA-FORGE-CHECK, revalidação do A1)

Gatilhos: controle do Forge (bin/forge-check: falha fechada do `parecer conferido`, VOLTAS-REVISOR-WT M1/M8, K-156).

Delta lido (`forge-check parecer delta`): `95994eec..d2f79996`. No domínio só entrou `bin/forge-check`: `de_outra_branch(raiz, linha, branch, ref)` (`:2427-2444`) e a `ref` passada por `pareceres_conferidos` (`:2012`, `:2418`), `ultimos_do_historico` (`:2447-2454`), `conferidos_fora_da_ref` (`:2466`) e `linhas_de_entrega` (`:3372`, o head). Testes, mutantes e changelog ficam fora do domínio. As rodadas anteriores estão no git.

Achados anteriores: A1 (bloqueante, `bin/forge-check:2431` em 95994eec) corrigido. A decisão saiu do nome do arquivo e passou para o `branch:` do parecer na `ref` e nas bases do fluxo. Nos casos tentados, ela segue a correção mínima pedida.

Veredito da mudança: em relação a 95994eec, ela só aperta. Todas as linhas que a regra por nome descartava indevidamente (as sondas antigas S1 a S4, aqui S1, S3, S4 e S5) voltam a contar como ilegíveis. Em relação à develop, ela afrouxa uma coisa só, que é a cura do K-156 por desenho (S2): a develop não tem `de_outra_branch` e conta como ilegível toda linha com P que o git não lê. Esta branch descarta a linha quando cada parecer citado existe na ref ou numa base e tem `branch:` diferente em todas elas. Esse afrouxamento não abre o portão. O arquivo descartado não tem, na ref, o `branch:` desta branch, então não satisfaz o `da_branch` do `pr` (E11, `:2033-2035`). O M1/M8 (`:2017`) também só vale para o P com `branch:` igual. O parse é o mesmo `ler_frontmatter` nos três pontos, e por isso maiúsculas e chave repetida dão a mesma leitura no filtro e no portão.

## Sondas
- S1 · `docs/reviews/v0478.md` com `branch:` da própria branch na ref · espera: ilegiveis=1 · obtido: ilegiveis=1
- S2 · `docs/reviews/k156.md` só com `branch: melhoria/outra` na ref (K-156) · espera: ilegiveis=0 · obtido: ilegiveis=0
- S3 · `docs/security/V0479-Trilha-Forge-Check.md` (ausente) · espera: 1 · obtido: 1
- S4 · `docs/security/x/v0479-trilha-forge-check.md docs/qa/outra.md` (subpasta) · espera: 1 · obtido: 1
- S5 · `docs/security/v0479-trilha-forge-check-2.md` com `branch:` igual · espera: 1 · obtido: 1
- S6 · `docs/reviews/mista.md`, `branch:` outra na ref e igual na develop · espera: 1 · obtido: 1
- S7 · `branch:` igual com espaços antes e depois · espera: 1 · obtido: 1
- S8 · `branch:` em maiúsculas · espera: 0, consistente com o `pr`, que compara exato · obtido: 0
- S9 · `branch:` repetido (igual, depois outra; e o inverso) · espera: 0 e 1, pois vale a última chave, como no `pr` · obtido: 0 e 1
- S10 · sem frontmatter; `branch:` vazio; parecer ausente · espera: 1 · obtido: 1, 1, 1
- S11 · `--ref` em outra branch, onde o arquivo tem `branch: melhoria/terceira` · espera: 0, consistente com o `pr` da mesma ref · obtido: 0
- S12 · `xdocs/reviews/k156.md docs/reviews/k156.md`; `docs/reviews/k156.md.bak`; `docs/security/aceites/k156.md`; `k156.md` com `v0478.md` · espera: 1 · obtido: 1, 1, 1, 1

## Detalhe
As sondas foram executadas sobre um repositório descartável em TMPDIR. Elas chamam `ultimos_do_historico` e `de_outra_branch` do `bin/forge-check` em d2f79996, com a branch `melhoria/v0479-trilha-forge-check` e a linha `- 2026-11-21: <citação> aprovado: parecer conferido dddd(40)` (P ilegível). Nenhuma delas prova bloqueante.

O que sobra é falso positivo e não falha aberta. Se dois itens do mesmo pedido gravam o parecer com o mesmo nome (`docs/<pasta>/<pedido>.md`) e esta branch já reescreveu o arquivo, a linha do item mesclado por squash volta a dar "rode git fetch" (S6). Isso é falha fechada, fora do caminho de ataque.

Suíte: a suíte local não rodou (o brief diz "sem suíte local"), e o `gh run list` da branch não mostrou execução. Rodei os dois testes novos de abuso, `tests.test_revisor_wt` `test_sha_ilegivel_de_outra_branch_nao_conta_e_o_da_branch_sim` e `test_parecer_conferido_de_outra_branch_do_pedido_nao_conta`, e os dois passaram (OK). O CI do PR continua obrigatório para o merge.

## Riscos aceitos e ferramentas
Sem risco aceito. Não estão no PATH: gitleaks, semgrep, zizmor, actionlint e osv-scanner. Isso é lacuna, sem efeito aqui: o delta não toca workflow, dependência nem credencial.
