---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-g4-trava-real
commit: 883429dd029b1625946a23bd32a04c9251ca2ccb
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0481 (E7.3, G4 em fatias, classe T)

Escopo: `docs/propostas/g4-fatias.md` (novo, 155 linhas) e `changelog.d/v0481-g4-trava-real.md`, base 8d7914bc, um commit (883429dd, E7.1). Só documentação: sem código, sem guarda, sem mutante. Primeira rodada; não havia parecer anterior na branch. Conferido contra o desenho `docs/propostas/g4-trava-real-bp8.md`.

## O que foi conferido
- **Referências de linha do hook:** as 30 citadas nas fatias F2 a F10 (2093, 2107, 2411, 2446, 2551, 2589, 2655, 2709, 2712, 2734, 2970, 2991, 2995, 3085, 3100, 3115, 3117, 3138, 3140, 3383, 3391, 3394, 3412, 3684, 3695, 3759, 3768, 3771, 3779, 4147) lidas em `hooks/conformidade.py` do 8d7914bc: cada uma é o `barrar` que a fatia diz. Confere.
- **Cartões:** os 19 citados existem no quadro. F2/F3 (leitura e texto), F4 (RULESET-TAGS-V), F5/F0 (CONFORMIDADE-S22-FLUXO na `main`), F6 (RULESET-DEVELOP-APAGAR-REESCREVER pelo D1) e os da F10 condicionados a G2/D10 conferem. A CONFORMIDADE-COPIA-RECURSIVA-GIT não confere (A2).
- **Comandos do dono:** D1 (PUT com `homolog`, `non_fast_forward`, `deletion` e os três checks com fonte 15368; ruleset `pr-develop`), D4, D5, D6, D7 e D9 têm o comando e a conferência por leitura; D3 remete aos passos 1 a 5 do desenho (telas, sem comando possível), D2 e D10 são decisões, D8 remete ao README ("Rede restrita de verdade", existe, com o `jq`). Adicionar a `homolog` ao 26701749 não trava a promoção: o `ci.yml` roda `bateria (python 3.14)` em todo `pull_request` (só pula no push da `develop`). Confere.
- **Medida:** o comando da seção 2 roda; ver A4.

## Achados
- A1 (bloqueante) docs/propostas/g4-fatias.md:71 · F6 põe `git push --mirror` em aviso para qualquer destino e diz que afrouxa só R-VERIFY; o `--mirror` envia refs/tags/* e cria tag `v*`, que o servidor não barra (D2 aberto) e que a seção 5 diz ficar barrada. Manter `--mirror` barrado até o D2 (também na F5:67, onde ele não tem destino literal).
- A2 (bloqueante) docs/propostas/g4-fatias.md:73 · F7 fecha CONFORMIDADE-COPIA-RECURSIVA-GIT dizendo que só sobra o pre-push do clone; `cp -r tp/. .` na pasta do Forge grava `.git/forge/` (gravável, a própria seção 1 linha 18; marca de sessão, T9). Deixar o cartão aberto com essa parte ou declará-la lacuna aceita, como a D10.
- A3 (recomendado) docs/propostas/g4-fatias.md:20 · "138 pontos barrar(" com a quebra 64+19+11+9+6+3 = 112; os 138 contam também a definição e as chamadas sem regra literal. O desenho contou 111 com o critério da quebra; diga 112 (+1 desde 21/11) ou explique as duas contagens. Mesma classe do DESENHO-G4-NUMEROS.
- A4 (recomendado) docs/propostas/g4-fatias.md:32 · a linha de base não é reprodutível: o mesmo comando hoje dá 822 chamadas e 104 recusas (o `comandos.jsonl.1` girou); e nada no registro separa recusa falsa de recusa com efeito para `git commit`/`git push`. Gravar a linha de base com o arquivo e o sha256, e dizer na F1 qual campo marca "falsa".

## Sondas
- S1 · scratchpad/sonda-mirror.sh: repositório local com tag v9.9.9, `git push --mirror <bare local>`, `git --git-dir=<bare> tag -l` · espera: a F6 só afrouxa R-VERIFY (nenhuma tag enviada) · obtido: v9.9.9 no remoto

## Parecer
Reprovado. A proposta é boa e quase toda confere com o desenho: as linhas do hook, os grupos, a ordem e a maior parte dos comandos do dono estão certos. Duas afirmações estão erradas exatamente no que o brief pergunta: o que a F6 afrouxa (A1, o `--mirror` abre a criação de tag que a proposta diz manter barrada) e um cartão que a F7 diz fechar (A2, a cópia recursiva ainda grava `.git/forge/` na pasta do Forge). A correção é de texto, em duas linhas. A3 e A4 viram cartão depois do merge.
