---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-bp12-dado-real
commit: 82277931ea878065aea1c2edfa5f14fbbd41759f
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-23
---
# Review de segurança: v0478 (PR #832, BP12 dado real antes de painel simulado, E144.5)

Escopo: diff `0ed441e9..82277931` (3 arquivos, só texto): `skills/ux-design/SKILL.md`, `templates/projeto/docs/constituicao.md`, `changelog.d/v0480-bp12-dado-real.md`. Sem código, hook, workflow nem analisador.

## Gatilhos
Gatilhos: nenhum de código; dado pessoal tocado só como texto de processo (LGPD, minimização), lido por isso.

## Veredito: só aperta ou neutro
- `templates/projeto/docs/constituicao.md:13` (portão novo): **aperta**. Painel de dado simulado sem prova vira hipótese; a prova é de coleta real ou de amostra anonimizada e registra só metadados (origem, data, quantidade), não o dado. Não pede cópia de dado pessoal ao repositório; empurra para a amostra anonimizada (minimização).
- `skills/ux-design/SKILL.md:13` (linha Empatizar, item novo): **aperta** (exige uma prova a mais no discovery), com a ressalva de redação em A1.
- `skills/ux-design/SKILL.md:17-18,24` (Validar, Especificar e a regra do trabalho técnico reescritas para o orçamento): **neutro**. Mesmo conteúdo; "correções e tarefas técnicas" virou "trabalho técnico", que cobre as duas; nenhum portão de segurança, regra com ID nem invariante saiu.
- `changelog.d/v0480-bp12-dado-real.md`: neutro.
- Neutralidade: nenhum nome de projeto, stack ou dado real no texto.

## Achados
- A1 (recomendado) skills/ux-design/SKILL.md:13 · O item "prova de dado real" omite "ou amostra anonimizada" e "origem, data, quantidade" da constituição; quem lê só a skill pode colar dado pessoal real em docs/ux/ (versionado). Corrigir: "prova de coleta real ou amostra anonimizada (só origem, data, quantidade)".

## Sondas

## Detalhe dos achados
**A1.** Evidência: `skills/ux-design/SKILL.md:13` diz "prova de dado real antes de painel simulado"; `templates/projeto/docs/constituicao.md:13` diz "prova de coleta real ou de amostra anonimizada (origem, data, quantidade)". Caminho: o `ux-designer` de um projeto segue a skill (não a constituição), coleta registros reais para provar o dado e os grava em `docs/ux/<demanda>/01-empatia.md`, que vai ao git e ao remoto; dado pessoal fica no histórico, contra a minimização da LGPD e sem eliminação viável. Severidade: baixa (depende de leitura literal; a constituição do projeto corrige). Correção mínima: alinhar o item da skill ao texto da constituição, citando a amostra anonimizada e que a prova registra só origem, data e quantidade. Esforço: P. Dono: `ux-designer` (texto), `tech-lead` (commit, por não ter Bash o autor). Recomendado: volta ao autor e é corrigido antes do merge (`R-REVIEW`).

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Testes dos arquivos tocados rodados no head 82277931: `PraticasDeEspecificacao`, `Neutralidade`, `NeutralidadeDoNucleo`, `Orcamento` (12 testes, OK). Suíte inteira no CI do PR #832 (em andamento na leitura; não rodada local, conforme o brief). Varreduras de segredo e dependências não se aplicam a diff só de texto sem segredo nem dependência.
