---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-d2-no-brief
commit: 7cacc94c8fe74c3fba5cd9368d5c388d1007b910
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-26
---
# Review de segurança: v0481 (E14.71, #903, D2-NO-BRIEF, 1ª rodada completa)

## Gatilhos
Gatilhos: controle (bin/forge-check: conferência da entrega e brief, R-CONFORMIDADE), guarda que analisa entrada (título do PR, base velha), execução de código da branch na sessão de quem confere.

## Lido
`git diff 34ab6714..7cacc94c` (merge-base com a develop; o merge 7cacc94c traz o #885 sem conflito): bin/forge-check (+50/-8), bin/forge_pronto.py (+41/-4), testes de forge_pronto, pre_envio_brief e selo_e_entrega, as specs de mutante e o fragmento do changelog.

## Achados
- A1 (bloqueante) bin/forge-check:10452 · Sem worktree (pasta None) o D2 não roda e não reprova: a entrega cumpre com D2 vermelho no fluxo real (cópia do autor é clone, sem git worktree; jarvis.md:30 não passa --worktree). O PQ cmd sem worktree reprova (:10499).

## Sondas
- S1 · python3 -I _sec75-v0481-d2nb-sonda.py <clone> (prova_do_pronto(None, "develop", False)) · espera: reprova (True) pedindo --worktree · obtido: [("pronto: não rodado aqui (--so-leitura, sem worktree ou fora do Forge)...", False)]
- S2 · git -C /workspaces/Forge worktree list --porcelain, procurando melhoria/v0481-d2-no-brief · espera: a worktree da branch · obtido: nenhuma (rc 1 no grep); a cópia do autor é clone próprio em wt/v0481-d2-no-brief
- S3 · comando_permitido(["bin/forge-check","pronto","--base","origin/develop"]) do scripts/reexecutar-provas.py · espera: a PQ do D2 cobrada por outra via · obtido: "comando fora da lista permitida" (não reexecutada, não reprova)

## Detalhe dos achados
**A1 (média; dono: tech-lead; esforço P).** A ordem do dono (25/11 07:52, cartão D2-NO-BRIEF) é "entrega com o D2 vermelho volta sem passar pelas revisões", e o changelog promete que a conferência "não cumpre com ele fora do rc 0". Em `prova_do_pronto` (bin/forge-check:10452), `pasta is None` cai no mesmo ramo do `--so-leitura` e de "fora do Forge": linha informativa, `reprova=False`. A pasta vem de `estado_da_worktree` (:10520), que sem `--worktree` só acha a branch por `git worktree list` do repositório de quem confere; no Forge, o autor trabalha num clone próprio (o sandbox deixa `.git/worktrees` só leitura; S2), e a forma documentada da conferência (agents/jarvis.md:30) não passa `--worktree`. A PQ do D2 que o brief ganha (:9718) também não segura: está fora da lista do reexecutar-provas (S3) e vira "fica com o relatório do autor". Caminho: um autor (agente) entrega com o pronto vermelho e relata outra coisa; a conferência grava `entrega conferida` e a entrega vai às revisões, exatamente o que a ordem proíbe. Mitigação parcial: o CI e as revisões seguem; por isso média, e bloqueante por ser o requisito do item num controle com gatilho.
Correção mínima: em `prova_do_pronto`, sem `so_leitura` e com `pasta is None`, reprovar quando o head da branch é do Forge (o `.claude-plugin/plugin.json` lido do git no `head`, não da worktree que não há), com o texto do :10499 ("sem worktree da branch para rodar (passe --worktree)"); fora do Forge segue a linha informativa. E a forma da conferência no agents/jarvis.md:30 e na skill briefs-e-conferencia passa `--worktree <cópia do autor>` na etapa codigo. Teste: a conferência da etapa codigo, numa cópia do Forge, sem worktree, sai 1 e não grava.

## O que aperta, o que é neutro, o que afrouxa
**Aperta:**
- Brief de código do Forge ganha a PQ do D2 (bin/forge-check:9718, :9943; só com `e_o_forge`); test_pre_envio_brief cobre dentro e fora do Forge.
- Conferência da etapa codigo roda o pronto quando há worktree (:10622) e reprova fora do rc 0 e no prazo estourado (:10459, :10463); a última linha do pronto passa por `sem_controle` (saída lida por modelo, sem imitar outra linha). test_d2_vermelho_na_copia_do_forge_nao_cumpre prova rc 1 e nada gravado.
- PRONTO-BASE-VELHA (bin/forge_pronto.py:50; forge-check:1236): só reprova. O `git fetch` usa `--end-of-options`, ramo por lista de caracteres, sem `-` inicial nem `..`; `versao_em` usa `ref:caminho` (base do pronto, que já passou pelo merge-base antes; na conferência sempre `origin/<base>`), sem injeção de opção alcançável.
- PR-TITULO-DO-BRIEF (forge_pronto.py:20, :73): regex linear (sem quantificador aninhado ambíguo), só reprova.

**Neutro:**
- Executar código da branch na sessão de quem confere: já havia (PQ cmd na worktree, D4); o `--so-leitura` continua sem rodar nada (:10452). O pronto roda o forge-check de quem confere (`Path(__file__)`), mas os passos chamam `bin/forge-testes` e os testes da branch, cujo rc a branch controla: o portão de verdade segue o CI.
- O pronto só roda com `.claude-plugin/plugin.json` na worktree: a branch que o apaga pula o D2, mas quebra a validação do plugin no CI e aparece no diff.
- `pr_da_branch` pede também `title` ao gh (mesmo teto de 10 s, sem custo, R-CUSTO); M18 e M19 da spec v0474-h1-ferramenta-3 acompanham a fonte.
- Prazo de 3600 s (:10444): espera longa de quem confere, sem efeito de segurança.

**Afrouxa:** nada. Nenhuma recusa anterior some; os novos ramos só reprovam ou informam. A1 é falta de aperto no caminho sem worktree, não afrouxamento do que existia.

## CI e testes
- ci: run 45751592922 no head 7cacc94c: suíte 3.12 e 3.14 (partes 1 a 5), bateria (passos), verificações longas, instalação 3.14, teto de pulados e árvore provada verdes; bateria (pareceres) vermelha pela falta destes pareceres (R-REVIEW, log do job) e a bateria agregada só por ela; catraca (run 45751632012) vermelha por R-CONFORMIDADE: bin/forge-check pede o rótulo afrouxa-regra do dono, não defeito
- Local, no clone em 7cacc94c: `python3 -m unittest tests.test_forge_pronto tests.test_pre_envio_brief tests.test_selo_e_entrega`: 235 testes, OK (os novos do D2-NO-BRIEF incluídos)

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do diff, sondas em arquivo (S1 a S3), módulos tocados; gitleaks e varredor de workflows não se aplicam (sem segredo nem workflow no diff).
