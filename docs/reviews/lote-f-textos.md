---
tipo: review
contrato: 1
pedido: LOTE-F-TEXTOS
branch: melhoria/lote-f-textos
commit: 8129e4050b812f3b73921b8751b926da7798660e
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-23
---
# Review: LOTE-F-TEXTOS

## Achados

## Parecer
Aprovado. Diff só de `.md` (7 arquivos, 4 commits, um por F), sem código; a suíte (1594 OK) é citada do histórico do pedido, não refeita.

- F3 (e57a257): faz o que o pedido descreve. O passo 5 de `node-backend.md` e de `react-frontend.md` manda rodar só testes e tipos do pacote alterado durante o desenvolvimento e o pronto completo (`CLAUDE.md`) uma vez antes do commit final, com meta de até 2 execuções.
- F9 (1c54ef3): faz o que o pedido descreve. O caso "Pronto: não reproduz" está nas políticas de `kanban-scrum`, com prova no lugar do merge (passos, ambiente e versão, saída da ferramenta) e a coluna "Aguardando sua validação" como destino sem a prova; a coluna existe na skill (linha 30). Coerente com `R-MAIN`.
- F11 (3342918) e F12 (8129e40): fazem o que o pedido descreve no passo "Ambiente novo": dono (`sudo`, segredos), `tech-lead` (dependências), `devops-engineer` (banco), Docker antes do Claude Code ou shell novo após entrar no grupo `docker`, com as duas medidas.
- Passo novo 4 em `skills/novo-projeto/SKILL.md`: escolha certa. O brief dizia "onde ele já está", mas o roteiro de primeiro uso não tinha passo de ambiente. Criar o passo evita enterrar a orientação num passo de outro assunto, e o antigo 4 (salvar e desfazer) virou 5 sem referência numérica a ele em skills, agentes, docs ou testes (grep sem ocorrência).
- Neutralidade (`R-NEUTRO`): mantida; só aparecem papéis do time, `sudo` e Docker como ferramentas genéricas, nenhum nome ou regra de projeto. `R-CUSTO`: nada que cobre. Fragmento `changelog.d/lote-f-textos.md` presente; a versão não foi tocada (ADR 0006).

Recomendados (não bloqueiam, sem item em `## Achados`):
- `docs/melhoria-continua.md:20`: a linha nova da tabela de medição não estava no escopo do pedido (E1 a E4). Está coerente com a medida do F3, mas declare no PR que foi acrescentada.
- Na mesma linha, a fonte "`forge-check transcricao`" é imprecisa: `docs/transcricoes.md` documenta só `transcricao verificar`, que lista violações e não conta execuções do pronto. Troque por "transcrição ou relatório do autor" ou documente a contagem.
- Os cinco textos trazem a frase "Medida: ..." dentro da skill e do agente; é um padrão já usado no repositório, sem ação.
