---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-dir31-focus
commit: 0d5826f9ce401e259e888080149cef3d4ed37218
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-21
---
# Review: v0479-dir31-focus

Etapa E67.2 do pedido v0478 (DIR-31, entrega E67.1), base `develop` em bead3e53, head 0d5826f9 (um commit).

## Escopo lido
- `scripts/jarvis`: função `visao_de_foco` (Python `-I`, lê só `viewMode` e `tui` de local > projeto > usuário) e `--settings` só quando ninguém decidiu; arquivo ilegível ou Python com falha não decidem pelo dono e não barram a abertura (`|| foco=""` sob `set -e`); o JSON vai como um elemento de `args`, sem reinterpretação pelo shell.
- `templates/projeto/.claude/settings.json`: `"viewMode": "focus"`, sem `tui` (a tela cheia fica só no atalho).
- `agents/jarvis.md`: a 1ª pessoa e o português saem da abertura e entram na linha **Linguagem fácil** com "sem nome de branch, pasta nem jargão"; nada se perdeu.
- `README.md` e `changelog.d/v0479-dir31-focus.md`: por que vem ligada, onde desligar, extensão do VS Code.
- Tamanho (H1): cerca de 30 linhas de código, um comportamento; dentro do teto.

## Verificado
- Testes novos (`AtalhoAbreNaVisaoDeFoco`, `ModeloELinguagem`, `ReadmeVisaoDeFoco`): 10 testes, OK, no head.
- Mutantes declarados (11, um por guarda, em `tests/mutantes/v0478-dir31-focus.json` e `-2.json`): `bin/forge-mutante` no `-2.json` matou F9, F10 e F11 no head; F1 a F8 pelo relato do autor (histórico 07:03, 11 mortos).
- Suíte completa: fica no CI do PR (PR ainda não aberto); não rerrodada aqui.
- Commit único, Conventional Commits em português, com fragmento de changelog (`R-CONTRIB`); nada específico de projeto (`R-NEUTRO`); nenhum custo (`R-CUSTO`).

## Parecer
Aprovado. Faz o que a E67.1 pede, sem mais: visão de foco por padrão sem sobrepor a escolha gravada do dono, a tela cheia só com a visão valendo e sem `tui` decidido, e a regra de linguagem fácil no Jarvis. Os ramos de falha (arquivo ilegível, Python que falha, precedência local > projeto, variáveis de ambiente) têm teste de comportamento e mutante morto.
