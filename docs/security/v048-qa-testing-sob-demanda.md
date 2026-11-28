---
tipo: revisao-seguranca
contrato: 1
pedido: v048
branch: melhoria/v048-qa-testing-sob-demanda
commit: 2c6b6f8193c1f3c4046cd436bef423193274d079
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-28
---
# Review de segurança: v048 (QA-TESTING-SOB-DEMANDA, PR #958), volta 1 (delta)

Gatilhos: texto de controle da fábrica (teste-oráculo EXT-1 e mutantes declarados) em arquivo com invariantes (`skills/qa-testing/SKILL.md`).

Delta lido: `forge-check parecer delta` no intervalo 87575570..2c6b6f81, 2 arquivos do domínio (`skills/qa-testing/SKILL.md` +1 -1, `skills/qa-testing/referencia.md` +3 -3). O delta não toca hook, `bin/`, `.githooks/`, workflow, `tests/` nem `docs/regras/`.

## Resultado
- **A1 (rodada anterior): corrigido.** `skills/qa-testing/SKILL.md:35` termina agora em "ao escrever o oráculo ou ao revisar um.", o mesmo gatilho de `referencia.md:30`; quem revisa o oráculo é mandado ler a regra do review.
- **Frase das saídas do `--cobertura` restaurada:** `referencia.md:45-47`, normalizada a quebra de linha, é idêntica ao trecho "lista a condição ... `isenta velha`, rc 1)." de `skills/qa-testing/SKILL.md:91` na `origin/develop` (comparação por script: igual). As saídas citadas batem com `bin/forge-mutante:715` ("declarado, não provado") e `:895` (rc 1 com `isenta velha`). Sem efeito de segurança.
- **Orçamento:** `medir()` de `tests/test_orcamento_instrucao.py` no head: qa-engineer 20085 caracteres (teto 21480), 34 marcadores.
- **Catraca e custo (ordem do dono 28/11 07:41):** o delta toca arquivo protegido por invariantes; `tests/catraca.py --modo regras --base 21aada57` rc 0 no meu clone; `test_orcamento_instrucao`, `test_brief_gerar_custo`, `test_doutor_custo`, `test_textos_ci_custo` (27 testes) e `test_forge -k test_custo` OK; `RegrasInviolaveis.test_trechos_obrigatorios` OK.
- **Mutação refeita por mim (R-PROVA):** desfiz o "ou ao revisar um" na SKILL.md:35: `test_trechos_obrigatorios` e `test_orcamento_instrucao` seguem verdes (nenhum teste prende o gatilho de leitura; é orientação, não controle executável). Restaurado; árvore limpa.
- **CI do head:** run 46146179731 com `headSha` 2c6b6f8193c1f3c4046cd436bef423193274d079: suíte (5 partes), bateria (passos, python 3.14, verificações longas), catraca, catraca (conferência), instalação, teto de pulados e "árvore já provada na develop" verdes. `bateria (pareceres)` (e o agregado `bateria`) vermelha só porque os pareceres do head ainda apontam para 87575570 (o de review está `reprovado`): é a espera pelos pareceres desta volta, não defeito do diff (`catraca.py --modo pareceres` local diz o mesmo).

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Ferramentas: git, unittest da biblioteca padrão, `tests/catraca.py`, `gh` (leitura do CI). Lacuna: o varredor de segredos não está no PATH (o delta é só texto em markdown).
