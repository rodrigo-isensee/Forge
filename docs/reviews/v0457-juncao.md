---
tipo: review
contrato: 1
pedido: v0457
branch: melhoria/v0457
commit: 9f5e7f6b9c2e4fdeb26a5819fd71fceee77d2b1e
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-11
---
# Review: v0457 (E23.7, revalidação da junção das 21 frentes da 0.45.7)

Este parecer foi escrito fora da branch, que o brief deixou só para leitura (Z10). A instância que revisa não fez a junção. Na branch, o docs/reviews/v0457.md já é o parecer do envio leve que veio da develop (343da6d3). O parecer da junção precisa de outro nome, por exemplo docs/reviews/v0457-juncao.md.

## Delta lido
7c6dd9df..9f5e7f6b, revisto pelo E23.4 em 7c6dd9df. O `forge-check parecer delta` não roda com o parecer fora da raiz do Forge ("use um parecer de docs/reviews... dentro da raiz"), então o delta foi lido com `git diff` e `--remerge-diff`:
- 047df241: tests/mutantes/v0457-testes-mapa.json, `de` e `para` do M2 com a linha seguinte (A1).
- 6cfde7e0: merge da origin/develop 2b896503. O `git merge-tree` de 047df241 com 2b896503 difere do merge gravado só nos 5 arquivos que foram resolvidos à mão. Os outros 63 arquivos do delta são o auto-merge da develop.
- 9f5e7f6b: docs/hooks-fixtures.md regenerado. Agora são 2331 fixtures, e as do `pesado` (TM-25) vêm da develop.

## Achados
- A2 (recomendado) bin/forge-check:1 · sem mudança desde 7c6dd9df. A catraca conta como "apagada" as condições que o F6 moveu do forge-check para bin/forge_*.py. A S2 de agora dá 1 violação de R-QA, toda em bin/forge-check (224 apagadas). O corpo do PR deve dizer ao dono que o rótulo `afrouxa-regra` cobre essas 224 movidas.
- A3 (recomendado) changelog.d/v0457-e4.md:3 · sem mudança. O título do PR precisa destacar que R-TETO deixa de ser sempre serial. O rótulo cobre os invariantes que foram para R-LIMITES/README e os 6 arquivos de regra apagados.

## Sondas
- S1 · forge-mutante tests/mutantes/v0457-testes-mapa.json (--processos 1, rev 9f5e7f6b) · espera: M1 a M8 morrem · obtido: rc 0; M1 a M8 · morreu, M2 em bin/forge-testes:267
- S2 · `regra_guardas_dos_hooks` da catraca da head, base 2b896503, head 9f5e7f6b · espera: nada em bin/forge-testes · obtido: 1 violação, só bin/forge-check (as 224 apagadas do A2); bin/forge-testes:267 saiu
- S3 · forge-mutante --cobertura --base 2b896503 · espera: rc 0 · obtido: rc 2 ("mais de 8 isentas somadas nas specs do diff"), o mesmo teto da S3 anterior, que é da junção e não do delta

## O que foi conferido
- **A1 (bloqueante em 7c6dd9df): fechado.** O `de` do M2 agora tem 33 caracteres que não são espaço. Ele aparece uma vez só em bin/forge-testes, assim como os `de` de M1 a M8. O mutante morre (S1), e a guarda saiu da catraca (S2).
- **Resoluções do merge 6cfde7e0** (`--remerge-diff`):
  - docs/regras/README.md: R-COPIA e R-VERIFY continuam apontando para R-LIMITES.md, e R-DECISAO ficou com o texto da develop ("uma a uma ... sem prazo que decida"). A develop não mexeu em R-COPIA.md nem em R-VERIFY.md, que a junção apagou. Nada se perdeu.
  - docs/economia-de-tokens.md: as regras 9 a 11 são as da develop e o Ritmo passou a ser a 12. A única citação por número, skills/falar-com-o-dono/SKILL.md:20, foi para a 12. Não sobrou nenhum "regra 9" apontando para o Ritmo.
  - tests/test_reval_delta.py: ficaram as 14 citações de test_forge e as linhas da R-WIP da junção, e test_conferir_reversao foi para 14, como na develop. O teste passa.
  - tests/fixtures/metricas-texto.json: o agents/jarvis.md da head é igual ao da develop (`git diff 2b896503 9f5e7f6b -- agents/jarvis.md` vazio). A entrada 7795/182 está igual à da develop, sem o teto subir.
  - Auto-merge sem conflito em tests/config.json (invariantes de R-DECISAO e falar-com-o-dono da develop) e em skills/falar-com-o-dono/SKILL.md: test_forge passa.
- **Testes rodados aqui** (um processo por vez, worktree destacada, carga entre 10 e 14 em 12 núcleos):
  - test_reval_delta, test_metricas_texto, test_indice_fixtures e test_testes_tocados: 168 OK, 1 pulado por sandbox (/proc).
  - test_forge e test_jarvis_nucleo: 595 OK, em 1004 s.
  - As 2 falhas de test_catraca vêm da develop (E18.5 da v046, conforme o brief). Elas não foram rodadas.
- **Tamanho (M14):** 5133 linhas de código e teste (`git diff --numstat --no-renames 2b896503...9f5e7f6b`). O corpo do PR precisa de `teto: excedido, 5133 linhas, junção de 21 frentes da 0.45.7`.

## Parecer
Aprovado. O A1 está corrigido e provado pela mutação e pela catraca. O merge da develop resolveu os 3 conflitos sem perder nenhum dos dois lados. A renumeração do Ritmo foi seguida pela única citação, e o teto do jarvis.md voltou ao da develop. A2 e A3 continuam recomendados e tratam do título e do corpo do PR e do que o rótulo `afrouxa-regra` do dono cobre.
