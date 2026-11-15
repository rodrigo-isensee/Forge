---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-conferencia-dois-pedidos
commit: a7872bf5094a4f84d48a802a1fcf810b0d1e1fb3
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-14
---
# Code review: conferência com briefs de dois pedidos na branch (CONFERENCIA-DOIS-PEDIDOS, E1.277)

Escopo: pedido v047, etapa E1.289 (`R-REVIEW`), classe C, sobre o head `a7872bf5` (Base-sha `c5c3a449`), instância que não fez a entrega. Li o diff inteiro de `origin/develop...a7872bf5`: um commit, 5 arquivos (`bin/forge-check` +57 -13, `tests/test_conferencia_dois_pedidos.py` +210, duas specs de mutante e o fragmento do changelog). QA e segurança correm em paralelo sobre o mesmo head; não os refaço.

## Achados
- A1 (recomendado) bin/forge-check:2576 · `COMMIT_NO_ENTREGAR` e `PEDIDO_NO_ENTREGAR` (2575) casam em todo o Entregar, não só no item do parecer: um brief selado que cite um commit antigo também o ancora; efeito só de escopo; sugestão: ler só o item que declara o `nome`
- A2 (recomendado) bin/forge-check:2588 · `etapas_dos_briefs_da_branch` relê todos os `docs/briefs/` das raízes a cada parecer conferido (centenas de briefs no v047); sugestão: calcular uma vez por conferência e passar o resultado
- A3 (recomendado) bin/forge-check:1359 · o diff tem 280 linhas contadas (M14, acima de 150); o corpo do PR precisa de `teto: excedido, 280 linhas, <motivo>` quando o PR for aberto

## Sondas

## Parecer
**Aprovado.** Faz o que a E1.277 pede, sem afrouxar a conferência (`R-PROVA`):
- `pedido_da_conferencia` (bin/forge-check:1384-1388): com um pedido só nos briefs da branch, nada muda; com dois ou mais, fica só o único que tem brief de `Etapa: codigo` na branch, e sem exatamente um a falha fechada segue, com a mensagem listando todos os pedidos. A escolha usa briefs não selados (como antes), mas o pedido escolhido passa depois pela conferência inteira dos briefs selados dele, então um brief plantado não abre caminho: dois `codigo` falham fechado e um `codigo` falso leva a um pedido sem selo para a branch.
- `parecer_mandado_pelo_portao` (bin/forge-check:2579-2604) entra só depois do anexo do portão já existente, só em etapa de código, só para parecer fora do controle (`com_controle`), e exige: frontmatter com o tipo da pasta, a branch da ref e veredito válido; brief **selado** no histórico do pedido citado (`briefs_selados_da_entrega`), com `Agente destino:` do papel do tipo, `Pedido:` igual ao pedido do selo (`mesmo_pedido`) e o arquivo declarado no escopo; `pedido:` e `commit:` do parecer iguais aos do brief; e nenhum veredito trocado no mesmo commit. O que muda em relação ao anexo anterior é só o pedido onde o registro do Jarvis foi selado; o selo continua sendo a âncora. A validade do parecer como portão (`forge-check classe`/`pr`) não passa por aqui.
- `caminho_do_pedido` com id nu sempre devolve um `Path`, e o arquivo ausente cai no `except OSError`; o pedido da release sem arquivo não derruba a conferência.
- Testes cobrem os ramos de falha por comportamento (sem ler a fonte), com o ambiente limpo (`LIMPO`, sem `GIT_`/`FORGE_`); as asserções de "fora" afirmam o texto exato e o rc 1. Nenhum invariante de `tests/config.json` foi tocado.

Verificação (regra 5 de `docs/economia-de-tokens.md`; sem PR nem CI ainda, cito o PQ do autor e rodo o teste novo e os mutantes):
- `python3 -m unittest tests.test_conferencia_dois_pedidos` no head: `Ran 19 tests in 56.935s` `OK`.
- `bin/forge-mutante --processos 1` nas duas specs: M1 a M16 `morreu` (16/16).
- `bin/forge-mutante --cobertura --base c5c3a449…`: todas as guardas mudadas `coberta` (M4 a M16); a única `apagada` é o `len(ids) > 1` da base, trocado pela guarda nova coberta pelo M5. Sai com rc=1 por marcar as linhas `declarado, não provado` (a cobertura roda separada da execução dos mutantes, que mataram todos).
- Commit `a7872bf5` em Conventional Commits, em português, um comportamento (a conferência numa branch com dois pedidos); fragmento `changelog.d/v047-conferencia-dois-pedidos.md` presente. Integrar na develop depende da resposta do dono à pergunta de 14/11 22:08 (`R-FLUXO`), fora deste review.
