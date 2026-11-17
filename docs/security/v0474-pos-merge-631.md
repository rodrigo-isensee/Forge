---
tipo: revisao-seguranca
contrato: 1
pedido: v0474
branch: melhoria/v0474-pos-merge-631
commit: 01b4e8aec3cd625f9a0bcf8359b88673d1e15d0b
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-17
---
# Review de segurança: v0474 (E1.42, depois do merge do #631)

Gatilhos: tests/config.json (invariantes trocados), texto do agente que integra na develop (tech-lead).

## Achados

## Sondas

## Detalhe
Escopo: delta 9fd5d771..56559cfd de `refs/pull/631/head` (875d5b15 e 56559cfd; os merges da develop no meio não tocam os arquivos abaixo), entrado sem portão no squash 01b4e8ae. `git diff 56559cfd 01b4e8ae -- agents/tech-lead.md tests/config.json skills/trabalho-em-paralelo` sai vazio.

- **Invariantes (`tests/config.json:361`, `:585-587`, `:823`):** sai do tech-lead "No máximo 12 branches abertas e 20 agentes" (`porque` em R-TETO); entra o caminho do ponteiro (R-FLUXO). A skill `ritmo-e-corte.md` passa a proteger "Até 20 agentes ao mesmo tempo" e "Agente livre termina o que está aberto", ao lado de "no máximo 12 branches com trabalho aberto". Conferi os 25 padrões do tech-lead e os 8 da skill contra a develop: todos casam. O teto do H6 segue também no Jarvis sob R-TETO (`tests/config.json:190`, `:796-797`, `agents/jarvis.md:37`), que é quem dispara agentes e abre branches. Nenhum controle sumiu; a proteção mudou de lugar e ficou mais larga (o "agente livre" passou a ser protegido na skill).
- **Texto do tech-lead:** a description perde a lista de decisões de commit e troca "a main só muda com validação do usuário" por "que é do usuário"; `R-MAIN`, `R-VERIFY`, "quem mescla na `main` é o usuário" e as ferramentas do frontmatter seguem iguais (invariantes casam). O item 5 aponta a skill `engineering-practices` em vez da lista da descrição do PR; não é controle de acesso. A linha do ritmo e corte vira ponteiro; o texto da skill é igual ou mais estrito (CI vermelho; branch nova só quando uma entra na develop).
- **Afrouxamento:** nenhum no conteúdo. O que diminui é o alcance no contexto do tech-lead, sem caminho de ataque (teto de processo, não fronteira de confiança). Concordo com A1 e A2 do review (`docs/reviews/v0474-pos-merge-631.md`), recomendados, sem achado novo.
- **Processo:** os dois commits entraram depois do último parecer (`R-REVIEW`); este parecer fecha o buraco depois do fato.
- **Suíte:** CI do #631 verde no head mesclado (suíte 3.12 e 3.14, partes 1 a 5, catraca, bateria, instalação: SUCCESS). Não rerrodada.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Só texto e JSON; sem varredura necessária, sem lacuna.
