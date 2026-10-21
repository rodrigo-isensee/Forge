---
tipo: review
contrato: 1
pedido: regra-lote-por-arquivo
branch: melhoria/regra-lote-por-arquivo
commit: 6f61294442b6753b27725d1725b88bfbe056a558
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-21
---
# Review: lote por arquivo (REGRA-LOTE-POR-ARQUIVO, E1.2)

Primeira rodada sobre a entrega inteira, `26f7189..6f61294` (commits `23539c2`, `3a8e278`, `6f61294`). O revisor não é o autor (outra instância, D-ETAPAS-INST). A segurança do texto de agente é do `security-engineer` (E1.3, `docs/security/`); aqui só é citada. O Forge não tem `docs/engineering/praticas.md`: não há regra "ferramenta" a citar, e o review usa o checklist da skill `engineering-practices`.

## Achados

## O que foi lido
- `agents/jarvis.md:33` (E4, fim do passo 1 de "Como conduzir um pedido"): na abertura de cada pedido o Jarvis confere com o time se o pedido cabe num lote com algo que ainda não está em andamento; só agrupa itens no mesmo estágio (os dois sem discovery ou os dois com discovery feito), nunca um sem discovery com um já descoberto; vale para o Forge e para os projetos. Bate com a decisão do dono de 09:30 nos três pontos (conferir com o time, "não está em andamento", não misturar estágio) e com a de 00:11 (vale para todos os projetos). A leitura de "senao faz sentido" registrada no pedido (NAO-ENTENDI) é a que o texto usa.
- `agents/jarvis.md:48` (E1, bullet em "Trabalho em paralelo (padrão)"): uma branch, um commit por item com os testes dele, review, segurança e QA do lote uma vez, um PR com o título citando os itens, saída do item com defeito por revert, nada de item com decisão do dono pendente, e "Nenhum portão cai". Cobre todos os elementos da decisão de 08:26 e do E1. Nenhum portão some: review, segurança e QA continuam obrigatórios, só passam a rodar uma vez sobre o conjunto, e cada item segue com os próprios testes (decisão de 2026-10-15, nada afrouxa o processo).
- `agents/jarvis.md:96` (E2): a exceção à linha "uma melhoria por PR" aponta para a seção do E1. A linha de origem continua lá, e o problema observado e a medida do efeito seguem exigidos.
- `agents/jarvis.md:44` ficou intocado, como pede o "Fora do escopo" (série por arquivo, `R-TETO`, `R-WIP`). Os dois convivem: a série vale para branches já em andamento; o lote, para itens que ainda não começaram.
- `tests/config.json`: dois invariantes novos em `agents/jarvis.md`, o rótulo do bullet (asteriscos escapados no `3a8e278`, porque o teste compila o trecho como regex) e a frase de abertura do E4. Nenhum item removido nem afrouxado.
- `changelog.d/regra-lote-por-arquivo.md`: fragmento com duas linhas em "Alterado", uma por regra; o `CHANGELOG.md` não foi editado.
- Neutralidade e custo (`R-NEUTRO`, `R-CUSTO`): texto genérico, sem nome de projeto nem stack, e nada pago.
- Commits: Conventional Commits em português, um por mudança coerente.

## Testes
- Numa cópia em `$TMPDIR` (`git archive 6f61294`): `python3 -m unittest tests.test_forge` · `Ran 419 tests` · `FAILED (errors=2)`. Os dois erros são de `SandboxDoBash` (`test_deny_write_so_estado_nao_versionado`, `test_gitignore_cobre_pontos_de_montagem_sem_ignorar_versionados`) e vêm da cópia não ser um repositório git. Não têm relação com o diff. `RegrasInviolaveis` passa.
- Vermelho na mesma cópia, com o rótulo trocado para `**Lote:**` e a frase do E4 trocada para "Na abertura, confira": `FAIL: test_trechos_obrigatorios` duas vezes, uma por invariante novo. Ou seja, os dois guardam o texto que dizem guardar.
- Suíte completa no pre-push do autor: 1267 OK (registro do pedido, 10:17). Não a refiz.

## Recomendações (não bloqueiam)
- R1 `agents/jarvis.md:48`: o bullet não diz se o lote ocupa um cartão ou um por item. Com `R-WIP` (1 cartão por agente) isso pesa: sugiro deixar escrito, numa próxima melhoria, que é um cartão do lote com os itens na Obs.
- R2 `agents/jarvis.md:48`: "conjunto pequeno" não tem limite. Dá para medir na retrospectiva da 0.28.0 (tamanho dos lotes, voltas por revert) antes de fixar um número.
- R3 `agents/jarvis.md:44`: a frase da série por arquivo poderia apontar para o lote como alternativa para os itens que ainda não começaram. Ficou fora do escopo deste pedido, e com razão.

## Parecer
Aprovado. O texto bate com as decisões do dono de 08:26 e 09:30, nenhum portão cai, e os invariantes passam e falham quando devem.
