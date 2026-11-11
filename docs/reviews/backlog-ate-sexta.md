---
tipo: review
contrato: 1
pedido: backlog-ate-sexta
branch: melhoria/backlog-lote-1111
commit: b0cf649d31e65f3342b1fd1666241bcd27a28a8a
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-11
---
# Review: backlog-ate-sexta (junção melhoria/backlog-lote-1111, E1.17)

Junção das 9 frentes (maq-i9-refazer-1 2e6e37b9, tm17-dado-neutro 42a987c6, varredura-caminho-pessoal 1c06dc18, tm25-pesados-stack 9fb3cc8a, orcamento-tempo-no-log 202dfd6a, fechar-medir-do-log fc004fbf, fechamento-540s af5ba3d3, revisor-sem-rerrodar f34b5029, diretrizes-jarvis-12-14 1f5f46fe), mais 0eb79b49 (contagem do test_reval_delta) e o merge b0cf649d da develop 36d976df (#488 e #489). Lido em worktree descartável, sem escrever na branch (Z10).

## Achados
- A1 (recomendado) agents/jarvis.md:14 · a origin/develop andou para 11ba4fa6 (20 commits além de 36d976df) e `git merge-tree --write-tree b0cf649d origin/develop` conflita em agents/jarvis.md:14-22 (corte de texto da E1.12 contra o "uma a uma" do #490); resolver no merge, no teto de caracteres.
- A2 (recomendado) agents/jarvis.md:16 · o corte da E1.12 tira "sobre falhas" e "; o scratchpad é temporário", que não existem em outro texto da fábrica; não é invariante nem afrouxa regra com ID, mas na resolução do A1 prefira manter o texto da develop e cortar outro trecho.
- A3 (recomendado) bin/forge-fechar:1 · 280 linhas de código e teste contadas pela M14 (bin, scripts, tests/*.py), acima de 150; o corpo do PR precisa de `teto: excedido, 280 linhas, junção de 9 frentes revisadas uma a uma`.
- A4 (recomendado) changelog.d/revisor-sem-rerrodar.md:2 · a frente afrouxa regra (R-QA, TEMPO-A A11 e A13): o título do PR destaca o afrouxamento e o rótulo `afrouxa-regra` é pedido ao dono.
- A5 (recomendado) tests/hooks/pesado/mesma-sessao-libera.json:1 · falhou na 1a de 2 rodadas de agentes+pesado no head sob carga (load 18; na base não) e passou sozinho, no pesado só (2x) e na 2a; os 4 agentes/*-pid também passaram na 2a: é sensível a ambiente, não regressão; vale cartão de instabilidade.

## Sondas

## Parecer
**Aprovado.** O merge da develop é limpo: `git show --remerge-diff b0cf649d` não tem linha (resolução igual à automática); o único arquivo tocado pelos dois lados é tests/test_hooks.py, mesclado sem conflito (o `exigir(self, "proc")` da develop e os testes novos da junção convivem). O head junta as 9 pontas exatas das frentes (pais dos merges conferidos contra as worktrees das frentes); o QA (docs/qa/backlog-ate-sexta-backlog-lote-1111.md, mesmo commit) comparou cherry-pick por cherry-pick e matou 18/18 mutantes (C7-1/2, P1-P6, M1-M8, M1-M2): citados, não rerrodados.

Desde as frentes, só mudou o 0eb79b49: a contagem de README.md em tests/test_conferir_reversao.py é 14 (`grep -o README.md | wc -l` = 14), igual à nova citação; é o suspeito real do test_reval_delta pedido na E1.17. Itens do Entregar com commit: merge da develop (b0cf649d) e test_reval_delta (0eb79b49); "sem envio" cumprido.

Leitura (checklist 1 a 12) do que alcança o diff: conferir-reversao devolve sem-veredito antes de rodar a suíte afetada quando o plano do revert cai na suíte inteira (R-TETO); a varredura `/(home|Users)/[[:alnum:]_][[:alnum:]_.-]*/` pega maiúscula, ponto, hífen e /mnt/<letra>/Users, e deixa passar `{tmp}/home/.config` e `<nome>`; o test_sugerir troca `C:/Users/bob` por concatenação só para o próprio arquivo não cair na varredura nova (dado de teste, aceitável); `--medir` do forge-fechar só aceita número de execução ou arquivo legível, para em marca ausente ou fora de FORMATO_DO_ORCAMENTO e não interpola o texto do log em comando. Docs (fechamento 170 s, revisor sem rerrodar, diretrizes 9 a 11 com medida e volta atrás) neutros (R-NEUTRO).

Ferramentas, saída citada: `scripts/verificar-contribuicao.sh 36d976df HEAD` → "ok: nenhum segredo nem caminho pessoal no diff contra 36d976df."; `shellcheck bin/forge-fechar scripts/verificar-contribuicao.sh` → rc 0; pesados.json válido. Testes dos arquivos tocados no head (sem suíte inteira): test_reval_delta, test_fechar_medir, test_conferir_reversao, test_sugerir, test_forge.VerificarContribuicao, test_hooks test_fixtures_do_tm25 e test_orcamento_sai_numa_linha_de_formato_fixo → "Ran 84 tests ... OK". Fixtures agentes+pesado: head 92 casos e base 89 casos com as mesmas 4 falhas agentes/*-pid na 1a rodada; pesado sozinho 24/24 OK duas vezes no head; 2a rodada agentes+pesado do head 92/92 OK (A5). A bateria completa fica para o CI do PR.
