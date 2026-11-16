### Corrigido
- Texto antigo da E8 na ADR 0012 (E8-TEXTO-ANTIGO, v047 E2.74): a conferência do dono antes da release pede a regra "branch atualizada com a base" desmarcada no `portoes` (passo 8 de `docs/protecao-de-branch.md`), em vez de tratá-la como ligada; a nota da E8 diz que a conferência vale para as três branches.

### Adicionado
- Correção antes dos portões (CORRECAO-ANTES-DOS-PORTOES, v047 E2.74, retro da 0.47.0 C5): a skill `trabalho-em-paralelo` manda toda correção que muda arquivo da branch, achado `recomendado` incluso, entrar antes dos portões, nunca após o último parecer (`R-REVIEW`); o `tech-lead` aponta para ela numa linha. O texto do agente e da skill foi compactado para caber nos tetos de caracteres, sem tirar regra.
