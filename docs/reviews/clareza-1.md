---
tipo: review
contrato: 1
pedido: clareza-1
branch: melhoria/clareza-pacote-1
commit: 4a83650c49af18bdf537b8b2394cc347cead94c8
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-16
---
# Review: pacote 1 de clareza (C-1, C-2, C-3, C-7, C-9, C-8, S-19)

Escopo: `b16d20f...4a83650` (base b16d20f22a3f3d540ffdca42a70ec653ded0c0cf), 8 arquivos em 3 commits (`8101abe`, `f4d0dc5`, `4a83650`). O revisor não é o autor. Comparei o diff com o "Entregar" de `clareza-1-tech-lead-1.md` e com as decisões do dono gravadas no pedido.

Veredito sobre `4a83650`: **REPROVADO**. Há 2 achados que bloqueiam: um pedaço do C-5 (atalho), que está fora do escopo, entrou no recibo; e o formato de pergunta (C-3) ficou sem invariante. Há também 4 achados recomendados. Tudo volta ao autor. Este revisor não corrige o diff.

## Ferramentas (citadas, não refeitas)
- `python3 -m unittest tests.test_clareza tests.test_forge -q`: `Ran 239 tests in 22.848s` / `OK`. Durante a execução, o sandbox negou uma saída de rede para `api.anthropic.com`, que não afetou o resultado. A suíte completa e o `scripts/validar-plugin.sh` ficam com o QA e o CI.
- A segurança (`R-SEGURANCA`; gatilho: `docs/regras/` e `tests/config.json`) tem parecer próprio do `security-engineer`, que roda em paralelo. Não a refiz.

## Conferido e ok
- C-1: o modelo de pedido traz as cinco marcas, a linha "Clareza" e a definição de cada marca (`templates/projeto/docs/pedidos/_modelo.md:7,13-20`). O passo 1 do Jarvis manda preencher (`agents/jarvis.md:33`).
- C-2: o recibo "vou fazer: ...; não vou fazer: ...; é isso?" vem antes de acionar o time, e a frase literal entre aspas vem com as duas leituras, inclusive para erro de ditado (`agents/jarvis.md:33`). Ver o achado 1 sobre a exceção.
- C-3 e FORMATO-DECISAO: a seção "Como perguntar" (`skills/modo-iniciante/SKILL.md:30-46`) tem contexto, exemplo, opções com efeito, "Afrouxa o processo?" e o custo de eficiência de cada opção em faixa e média, a recomendação com o degrau, "Faltam N perguntas." e a saída "decidam vocês". Vale nos dois perfis, o que segue a suposição do pedido. O `agents/jarvis.md:108` faz a referência. O exemplo (encomenda atrasada) é neutro.
- C-7 e C-9 entraram em `docs/regras/R-DECISAO.md:26-28` só por acréscimo (o diff não remove nenhuma linha). Os não delegáveis (custo, acesso, exceção a regra, ato irreversível) estão literais. A ordem ampla só cobre `confirmado`/`delegado`, e o que é novo ou irreversível volta como pergunta, uma por vez. A frase está no `agents/jarvis.md:108`. "Uma por vez", "decisão só vale gravada" e a escada continuam intactos.
- C-8 e S-19: `agents/agile-coach.md:14` mede por pedido as cinco grandezas a partir das tags. O alerta de 30% de `delegado` vem do estudo (seção C-7, "Como medir", marcado como valor inicial). A forma das tags está no modelo (`_modelo.md:21-26`) e a ordem de gravar está no `agents/jarvis.md:33`. Não existe skill própria de retrospectiva, e o "se houver" do pedido cobre isso.
- Nada de C-4 (portão de 90%, teto de perguntas) nem de C-6 (conferente contando marcas, `forge-check pedido clareza`) entrou. `hooks/`, `bin/` e `.github/` não foram tocados.
- `tests/config.json` recebeu só acréscimos (o diff não tem linha `-`). Os invariantes novos protegem os trechos novos de jarvis, modelo, agile-coach e R-DECISAO.
- A marca no fim do item de escopo (`E1. <item> · \`confirmado\``) não quebra o `forge-check brief`: a correspondência com o escopo é por substring (`referencias_do_item`, `bin/forge-check:1697-1708`), e `ASPAS` não captura crases.
- O fragmento `changelog.d/clareza-pacote-1.md` traz "Afrouxa o processo? Não" e o custo de eficiência (1 a 3 min por pedido, média 2), como manda a decisão do dono de 2026-10-16.
- O `agents/jarvis.md` continua com 108 linhas. A linha 33 ficou longa (cerca de 1,7 mil caracteres), o que o brief aceita para caber no teto, mas ainda se lê em ordem: registrar, marcar, recibo, tags, cartões.

## Achados

1. `agents/jarvis.md:33`: **bloqueia**. "**Recibo antes de acionar o time** (salvo leitura, ou ação reversível dita literalmente)". Essa exceção é a definição do C-5, o atalho fechado ("Leitura, ação de orquestração reversível dita literalmente", estudo, seção C-5). O C-5 está fora do escopo (pacote 2, ligado junto com o C-4, depois de 2 semanas de medição). Além disso, a decisão C-2 "A" não traz exceção. Sugestão: tirar o parêntese. Se o recibo de uma linha para leitura fizer falta, isso vira item do pacote 2.
2. `tests/config.json:168`: **bloqueia**. O Entregar 6 pede invariantes para os trechos novos, mas a seção "Como perguntar" de `skills/modo-iniciante/SKILL.md`, que é o centro da decisão C-3 e do "Afrouxa?" com custo de eficiência, não ganhou nenhum. Só o `tests/test_clareza.py` a protege, enquanto os outros quatro arquivos ganharam invariantes. Sugestão: acrescentar à lista existente da skill, por exemplo `"## Como perguntar"`, `"\\*\\*Afrouxa o processo\\?\\*\\*"`, `"\\*\\*custo de eficiência\\*\\*"`, `"Faltam N perguntas\\."` e `"decidam vocês"`.
3. `agents/jarvis.md:33` e `tests/config.json:187-195`: **recomendado**. A ordem do C-1 ("Marque cada item de escopo, fora do escopo e critério de pronto com ...") e a tag `PERGUNTA:` no Jarvis não têm invariante nem asserção (o `test_clareza` confere as tags, mas não a ordem de marcar). Sugestão: invariante para "Marque cada item de escopo, fora do escopo e critério de pronto".
4. `templates/projeto/docs/pedidos/_modelo.md:35,41`: **recomendado**. O texto diz que todo item de Fora do escopo e de Critério de pronto termina com uma marca, mas as linhas de exemplo dessas seções não têm marca (a de Escopo, `:11`, e a de Suposições, `:38`, têm). Quem copia o modelo segue o exemplo. Sugestão: acrescentar `· \`confirmado\`` (ou outra marca) às duas linhas.
5. `templates/projeto/docs/pedidos/_modelo.md:46-47` com `agents/agile-coach.md:14`: **recomendado**. A seção `## Registro de clareza` do modelo já vem com a linha `PERGUNTA: AAAA-MM-DD · <resumo>`. O pedido copiado nasce com uma "pergunta" falsa, que a medição vai contar. Além disso, "tag ausente é 'não medido', nunca zero" faz um pedido que de fato teve zero perguntas sair como "não medido" para sempre. Sugestão: deixar no modelo um marcador que não é tag (por exemplo `<uma tag por linha, forma acima>`) e, no agile-coach, dizer "seção ausente é 'não medido'; seção presente sem a tag é zero".
6. `docs/regras/R-DECISAO.md:28` e `agents/jarvis.md:108`: **recomendado** (só registro, sem mudança pedida). "Item novo dentro de ordem ampla volta como pergunta" pode trazer ao usuário item que não passa no teste de bloqueante (que o mandaria para suposição). É a decisão C-9 do dono e não é uma contradição de texto, porque o complemento é mais específico. Fica como ponto para a medição do C-8 observar (perguntas por pedido).

## Pendências
- Nenhuma regra de ferramenta ficou sem comando. A suíte completa e o `validar-plugin` ficam com o QA e o CI.
