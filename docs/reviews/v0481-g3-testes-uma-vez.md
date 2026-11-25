---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-g3-testes-uma-vez
commit: 55f87ffd19d79ad27a20521c45ee65004521bc00
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-25
---
# Review: v0481

## Sondas
- S1 · `gh pr checks 893` no head 55f87ffd · espera: verdes fora `bateria (pareceres)`, `bateria` e `catraca` · obtido: suíte (10 partes), teto de pulados, instalação e as outras baterias pass; falham só os três, por esperarem os pareceres e o rótulo `afrouxa-regra`
- S2 · `bin/forge-mutante --processos 1`, M5 da spec 1, M15 e M16 da -2, M17 a M19 da -3 · espera: mortos · obtido: os 6 morreram. O M19 morreu por erro (TypeError em `COMMIT.match(None)`), que é a guarda que ele declara
- S3 · `bin/forge-mutante --conferir --todas` no head e na base 220ba3fa · espera: igual · obtido: as 26 linhas são idênticas, todas de specs de outros pedidos. `--conferir --base 220ba3fa`: os trechos do diff estão no lugar; `--cobertura --base 220ba3fa` rc=0
- S4 · testes afetados (`LeOCiNoCmdPr`, `LeuOCi`, `ChecksForaDaLinhaDoCi`, `LeOCiNoBrief`), com ambiente limpo · espera: verde · obtido: 19 testes OK

## Parecer
Delta ef45eec5..55f87ffd lido. Os dois achados da volta anterior foram fechados.

**A1.** `CHECKS_FORA_DA_LINHA_DO_CI` (bin/forge-check:2174) é a fonte única do texto. A constante entra no brief (`LINHA_LE_O_CI`), na recusa do `pr`, na nota do esqueleto e nas duas skills, e o `ChecksForaDaLinhaDoCi` amarra cada um desses lugares a ela. O teste também confere que cada nome é um job real dos workflows, o que impede a lista de divergir do CI. A isenção vale só para a linha `- ci:` do parecer. O merge continua exigindo todos os checks (`checks_do_head` e os passos 4 e 6 do `forge-fechar`).

**A3.** `cobra_a_linha_do_ci` (bin/forge-check:2185) falha fechada. Um `commit:` fora da forma de sha, sem `commit:` ou com erro do git cobra a linha, e só o "não achou" do `git grep` (rc 1) isenta. O teste prova também que `--cached` não vira opção do grep. O CI faz checkout com `fetch-depth: 0`, então o commit antigo existe lá.

A isenção não solta nada que a develop barra hoje, porque o parecer isento segue com a PARECER-SO-COM-CI-VERDE inteira (`test_commit_anterior_a_regra_segue_com_o_ci_verde_do_head`).

Forjar um `commit:` antigo também não dá fuga. O `commit_vale` desatualiza o parecer se o patch da branch no domínio mudou depois desse commit. Branch aberta depois da regra só tem commits que já a trazem. O que sobra é a própria transição pedida: branch aberta antes da regra, com o mesmo patch revisado. Ela se encerra sozinha quando essas branches fecham.

A skill qa-testing perdeu 3 caracteres e nenhuma regra. O invariante "no mesmo head do review" e os demais da lista em `tests/config.json` seguem no texto, e o `R-QA` continua citado.

O aviso da catraca sobre `Gerar.test_parecer_sem_pr_diz_que_a_suite_fica_para_o_ci` é do delta anterior e é legítimo. O QA agora tem outro texto sem PR, coberto por `LeOCiNoBrief`, e o caso sem PR passou para a segurança, que fica fora do G3.

- ci: 55f87ffd19d79ad27a20521c45ee65004521bc00 verde
