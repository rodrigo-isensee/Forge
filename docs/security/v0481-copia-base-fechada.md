---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-copia-base-fechada
commit: 483a5614b7941fc5ff299ea15ef3305f0a85cce2
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-25
---
# Review de segurança: v0481 (E14.36, #896, forge-copia diz o sha em que criou a branch; classe C)

Lido: `b224ee09..483a5614` inteiro (`bin/forge-copia` +3, `tests/test_forge_copia.py` +24, `tests/mutantes/v0481-copia-base-fechada.json`, `changelog.d/v0481-copia-base-fechada.md`). Primeira rodada de segurança da branch; sem parecer anterior. O clone desta revisão (`~/.forge-contrib/wt/v0481-copia-base-fechada-sec`) foi criado com o `bin/forge-copia` da develop (`b224ee09`), `clone --revisao`: nasceu em `483a5614`, o head remoto da branch.

Gatilhos: controle do Forge (criação de cópia de trabalho; ref de onde a branch nasce).

## Conferência
- **COPIA-SHA (`bin/forge-copia:337-338`)** roda só depois de todas as recusas (`:296-322`), do clone (`:325`) e do `switch --no-track -c` bem-sucedido (`:328`); `ponto` aí nunca é `None`. Só lê (`git rev-parse HEAD` pelo `ler`, sem shell, lista de argv) e escreve na saída de erro a branch já validada, um sha e a ref de partida; sem segredo, sem caminho novo, sem escrita. O código de saída e o `--instalar` seguem iguais; `rev-parse` que falhasse só deixaria o sha vazio na mensagem.
- **Só aperta ou neutro, por escrito: neutro.** Nenhuma guarda mudou: o diff em `bin/` é só a linha do docstring (`:11`) e as duas linhas acima. Nada que barra hoje deixa de barrar; os três testes novos prendem o que já valia (branch do remoto nasce no head dela com `--base develop`; base curta que não resolve: rc 1, sem clone e sem "criei").
- Testes: `python3 -m unittest tests.test_forge_copia` → 88 testes, OK. Mutantes: `bin/forge-mutante tests/mutantes/v0481-copia-base-fechada.json` → M1 e M2 morreram (`:337`, `:338`).

## Parecer
- ci: 483a5614b7941fc5ff299ea15ef3305f0a85cce2 verde

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática, teste do módulo tocado e mutantes; nenhuma varredura externa.
