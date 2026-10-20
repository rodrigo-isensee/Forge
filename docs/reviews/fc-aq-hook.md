---
tipo: review
contrato: 1
pedido: fc-aq-hook
branch: melhoria/fc-aq-hook
commit: f058327f0dbed7dcc9e7eec11140eac02e6b358d
parecer: aprovado
revisor: forge:tech-lead (outra instância)
data: 2026-10-20
---
# Review do FC-AQ-HOOK: o papel aq grava as propostas no clone de contribuição

Escopo: `50997b7...f058327` (base 50997b72e65d11a7cace0bbc5d4aaf5a55b68d60), 5 arquivos em 2 commits (308d621 feat(hooks), f058327 docs(adr)). Quem revisa não é o autor (D-ETAPAS-INST). O review de segurança (E1.3) corre em paralelo e não é refeito aqui.

Veredito sobre `f058327`: **APROVADO**, sem bloqueante; 2 recomendados.

## Ferramentas (saída citada, não refeita)
- Teste novo na árvore de `f058327`: `python3 -m unittest tests.test_hooks.Hooks.test_aq_grava_so_nas_duas_pastas_do_clone_de_contribuicao` → `Ran 1 test` / `OK`.
- O mesmo teste com o `hooks/conformidade.json` da base (50997b7): `FAILED (failures=2)`, subtestes `[propostas]` e `[arquitetura]`, o que confirma o PQ-1 do pedido (falha na develop o permitido, passa na branch).
- Suíte completa e `scripts/validar-plugin.sh`: evidência do autor na entrega E1.1 (952 OK; validar-plugin OK), conferida pelo Jarvis (R-PROVA); ficam com o QA e o CI.

## Conferência do pedido
- E1 conforme: `hooks/conformidade.json:15`, `escrita_permitida.aq` tem exatamente 4 entradas, as duas de antes e `~/.forge-contrib/docs/propostas/` e `~/.forge-contrib/docs/arquitetura/`; nada mais no json mudou. Nenhum código de hook mudou (o diff não toca `hooks/*.py`); `fora_da_lista_de_escrita` já trata entrada `~/...` pela forma `home` (`hooks/conformidade.py:568`), então a suposição do Discovery se confirma: é só política.
- A lista só restringe: roda depois de `caminhos`, que segue barrando `~/.forge-contrib/docs/pedidos/` e `~/.forge-contrib/docs/briefs/` para quem não é o jarvis (`hooks/conformidade.json:48,50`). A ampliação não abre nada que `caminhos` proteja.
- E2 conforme: `tests/test_hooks.py:831-853` cobre as duas pastas liberadas (código 0) e as recusas: outra pasta do clone (`docs/pedidos/`, `docs/reviews/`), `KANBAN.md`, fora do clone (`~/outra/docs/propostas/`), travessia `..` e link simbólico de `propostas` para fora (recusa com a mensagem da lista, prova de que a decisão é pelo caminho resolvido).
- `tests/test_forge.py:158` só troca o valor esperado pela lista exata de 4 entradas; a igualdade estrita continua (ampliar a lista de novo exige mudar o teste no mesmo PR).
- E3 conforme: `changelog.d/fc-aq-hook.md` com o nome da branch e seção `### Alterado`; a ADR 0009, seção 6, item 6 (`docs/adr/0009-conformidade-dos-agentes.md:70`) descreve a lista nova, citando o cartão; a linha é reescrita só por acréscimo de texto.
- Nenhum invariante saiu: `tests/config.json` fora do diff; nenhuma regra de `docs/regras/` tocada. Neutralidade: `~/.forge-contrib/` é convenção da fábrica (já presente em `hooks/_comum.py:187` e na própria política); a escolha das duas subpastas é decisão do dono de 2026-10-20 ("A"), que responde ao achado 1 do review `docs/reviews/aq.md`.
- Commits limpos, Conventional Commits em português, uma mudança coerente por commit.

## Achados

## Detalhe dos achados
- Recomendado (tests/test_hooks.py:841): o caso "travessia" sai de `propostas/` para `pedidos/`, que `caminhos` já barra; o subteste passaria mesmo sem a lista de escrita. Um alvo sem dono em `caminhos` (ex.: `~/.forge-contrib/docs/propostas/../reviews/x.md`, esperando "o papel aq escreve só em") provaria que a lista decide pelo caminho normalizado. Ajuste de uma linha numa próxima volta.
- Recomendado (tests/test_hooks.py:837,841): o trecho esperado `"R-"` é genérico demais (qualquer recusa casa); vale fixar o motivo do bloqueio de `caminhos` para o caso não passar por recusa de outra origem.
