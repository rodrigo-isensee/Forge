---
tipo: review
contrato: 1
pedido: jarvis-triagem
branch: melhoria/jarvis-triagem
commit: 38b49a8
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-13
---
# Parecer de autor: triagem de cada pedido no Jarvis

- **Mudança:** seção "Triagem de cada pedido" antes de "Como conduzir um pedido" (faço eu x passo para `forge:<agente>`, aviso em uma linha, sem agente certo avisa e propõe caminho); "Comunicação com o usuário" exige citar o agente nas respostas que delegam.
- **Proteção:** dois invariantes novos em `agents/jarvis.md` no `tests/config.json`; só acrescenta, nada afrouxado.
- **Verificação:** 310 testes OK e `scripts/validar-plugin.sh` passa. Hooks intactos; CHANGELOG em `[Não publicado]`.

## Review independente

Parecer: **reprovado**. Testes no head 5873c63: 310 OK (`python3 -m unittest discover -s tests`).

1. `agents/jarvis.md:3` (descrição do frontmatter) · diz que o Jarvis "cuida do versionamento no git" · contradiz a triagem (`agents/jarvis.md:27`), que passa versionamento, release e merge ao `tech-lead`; é o texto que o roteamento lê, então o objetivo do PR não se cumpre · sugestão: trocar por "cuida do quadro, da configuração do time e da comunicação; versionamento, release e merge vão ao `tech-lead`" · severidade: **bloqueia**.
2. `agents/jarvis.md:27` · a cláusula "que são do `tech-lead`" não está em `tests/config.json`; os dois invariantes protegem só o título e a frase "diga sempre ao usuário…" · sugestão: proteger também "inclusive versionamento, release, merge e integração" · severidade: recomendado.
3. `agents/jarvis.md:81` (autonomia) · manda o Jarvis "implemente numa branch e abra o PR", em tensão com "Você não implementa" (`:8`) e com a triagem · a tensão já existia antes do PR; não bloqueia, mas a triagem deveria apontar que a implementação vai ao agente e o PR ao `tech-lead` · severidade: recomendado (dívida anterior, pode ir em PR próprio).
4. `agents/jarvis.md:27` e `:96` · a instrução de citar o agente aparece duas vezes ("diga sempre ao usuário…" e "Toda resposta que delega cita o agente pelo nome") · sugestão: manter uma só, na triagem · severidade: recomendado.

O resto confere: a seção é curta e clara; não contradiz o restante do arquivo (o Jarvis continua sem implementar, `:8` e `:63` "você, só quadro e configuração do time"); os invariantes protegem o trecho certo; CHANGELOG em `[Não publicado]`.

Pedido ao autor: corrigir o item 1 (bloqueia) e, se possível, os itens 2 e 4 no mesmo PR.

## Re-review independente

Parecer: **aprovado**, no head 38b49a8 (`fix(jarvis): descrição e autonomia alinhadas à triagem; invariante do tech-lead`). Testes no head 38b49a8: 310 OK (`python3 -m unittest discover -s tests`).

Os quatro itens do review anterior:

1. Descrição do frontmatter (`agents/jarvis.md:3`): corrigida. Não diz mais que o Jarvis cuida do versionamento; diz que coordena e que versão, release e merge são do `tech-lead`. Atende ao item bloqueante.
2. Duplicação (`agents/jarvis.md:27` e `:96`): a frase "Toda resposta que delega cita o agente" saiu; ficou só a da triagem. Atende.
3. Autonomia (`agents/jarvis.md:81`): a linha agora manda acionar o `tech-lead`, que implementa e abre o PR, e diz "você não". A tensão com "Você não implementa" foi reduzida. Ver o achado novo abaixo.
4. Invariante (`tests/config.json`): protegido "que são do `tech-lead`", além de "diga sempre ao usuário para qual agente passou". Protege o trecho certo. A sugestão de proteger também "inclusive versionamento, release, merge e integração" não foi aplicada; é recomendado, não bloqueia.

Achado novo (recomendado, não bloqueia): `agents/jarvis.md:81` manda o `tech-lead` implementar melhorias e abrir o PR, mas `agents/tech-lead.md:28` diz "Não implementa features". A autonomia fala de melhorias de fábrica e a limitação, de features; ainda assim, o texto do `tech-lead` deveria dizer que implementa só melhorias de fábrica ou que delega a implementação. Pode ir em PR próprio.

Checks do PR: no head 38b49a8, todos os jobs (CI, Catraca, validação do plugin, testes estruturais e demais) falharam em 2 a 4 s, sem nenhum passo executado. O push em `develop` de `de0e519` falhou do mesmo jeito (4 s, sem passos), então a causa parece ser da plataforma do GitHub Actions (runner ou cobrança), e não do código. Os logs não puderam ser lidos daqui. A bateria local está verde. Por isso este parecer não autoriza a mesclagem: o `tech-lead` mescla só com os checks verdes (R-FLUXO).

Pedido ao Jarvis: resolver a falha dos checks no GitHub (conta ou runner) e, depois, rerodar `gh pr checks 97`. Quando estiverem verdes, a mesclagem segue com `gh pr merge 97 --squash`.
