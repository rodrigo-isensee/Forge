---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-limpar-clone-parecer
commit: 86f50b244f7b814d8733a656aae8c1d9111c1df5
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-25
---
# Review de segurança: v0481 (#890, E14.13, volta por delta)

Delta lido: `git diff fe1f2275..86f50b24` (E14.10): `bin/forge-fechar:651,691-693`, `docs/fechamento-integrador.md` passo 7, o fragmento do changelog, `tests/test_forge_fechar.py:152-167`, `tests/test_fechar_limpar_clone.py:1-3,32-35`, `tests/mutantes/v0474-mp6-disco-3.json` (M18) e `tests/mutantes/v0481-limpar-clone-parecer.json` (M1, M1b). Já lido na rodada anterior (fe1f2275, no git): o `^$merged_heads` da linha 697 (neutro), sem mudança neste delta.

Gatilhos: apagar dados (o `rm -rf` do clone em `~/.forge-contrib/wt`), controle de conformidade (teste de guarda da MP6).

## O que aperta, o que é neutro, o que afrouxa
- **Aperta (em relação a fe1f2275):** `--exclude='refs/tags/arquivo/*'` (`bin/forge-fechar:693`) devolve à conta toda tag local fora do espaço `arquivo/*`; o commit só numa tag de outro nome, leve ou anotada, prende o clone de novo, como na base 8833d0f6 (S1, S2). `test_commit_so_em_tag_local_fica` voltou idêntico ao da base (o `git diff 8833d0f6..86f50b24` não o toca) e o M1b (exclusão ampla) morre nele; o M18 da MP6 voltou a apontar para o trecho vivo e morre (`bin/forge-fechar:693`).
- **Neutro:** `tag_com_ref_velha` voltou à tag `v9` da base (a tag que a origin alcança sai pelas pontas, LIMPAR-CLONE-NAO-LISTADO); comentário da 651/691, passo 7 da doc e changelog agora dizem o que o código faz.
- **Afrouxa (em relação à base, resíduo aceito pelo próprio desenho):** só o commit numa tag local nunca enviada criada no espaço `refs/tags/arquivo/*`, que é o espaço das tags de arquivo da origin (S3). O prefixo é exato: `arquivox/t` e a tag `arquivo` sem barra ficam (S4, S5); a branch local `arquivo/b` fica (S6, o exclude é só de tag). Sem caminho de ataque realista: só quem já escreve no clone cria a tag, e ele mesmo poderia apagar o clone.
- **Catraca:** `python3 tests/catraca.py --base origin/develop --ramo melhoria/v0481-limpar-clone-parecer` sai 0; check `catraca` do PR `pass`. Sem afrouxamento de garantia protegida a sinalizar.

## Achados anteriores
- A1 (bloqueante, fe1f2275) bin/forge-fechar:692: resolvido em 86f50b24 (exclusão restrita a `refs/tags/arquivo/*`, teste da base restaurado, M1b morto por ele).

## Sondas (executadas em 86f50b24, todas no esperado)
- S1 · `python3 /root/.forge-contrib/wt/_sec-v0481-limpar-sonda2.py -v` (ambiente de `LimparClones`), commit só na tag leve `t-local` · espera: rc=3 clone=pendente · obtido: rc=3 clone=pendente, clone existe
- S2 · mesma sonda, tag anotada `marco-local` · espera: rc=3 clone=pendente · obtido: rc=3 clone=pendente, clone existe
- S3 · mesma sonda, tag `arquivo/t-local` · espera: rc=0 clone=ok · obtido: rc=0 clone=ok, clone apagado
- S4 · mesma sonda, tag `arquivox/t` · espera: rc=3 clone=pendente · obtido: rc=3 clone=pendente
- S5 · mesma sonda, tag `arquivo` · espera: rc=3 clone=pendente · obtido: rc=3 clone=pendente
- S6 · mesma sonda, branch local `arquivo/b` · espera: rc=3 clone=pendente · obtido: rc=3 clone=pendente

## Riscos aceitos e ferramentas
Nenhum risco aceito. Rodados no clone revisado (86f50b24): `python3 -m unittest tests.test_forge_fechar.LimparClones tests.test_fechar_limpar_clone` (29 OK); `bin/forge-mutante tests/mutantes/v0481-limpar-clone-parecer.json` (rc 0: M1, M1b, M2 morreram); `bin/forge-mutante tests/mutantes/v0474-mp6-disco-3.json` (M18 morreu em `bin/forge-fechar:693`); catraca local rc 0. Suíte inteira: só no CI; na leitura, o run 45560336367 do #890 tinha as partes da suíte pendentes e `bateria (pareceres)` vermelho (pareceres do head ainda ausentes); o merge exige esse CI verde (`R-FLUXO`), e este parecer não o substitui. Ferramentas fora do PATH: gitleaks, shellcheck, semgrep, zizmor (lacuna; o delta não toca segredo nem workflow).
