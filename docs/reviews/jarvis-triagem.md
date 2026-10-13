---
tipo: review
contrato: 1
pedido: jarvis-triagem
branch: melhoria/jarvis-triagem
commit: 5873c63
parecer: reprovado
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
