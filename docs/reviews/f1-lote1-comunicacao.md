---
tipo: review
contrato: 1
pedido: f1-lote1-comunicacao
branch: melhoria/f1-lote1-comunicacao
commit: ac4f1ff
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-13
---
# Parecer de autor: lote 1 da fonte F1 (comunicação do Jarvis)

Escopo: complemento em `docs/regras/R-DECISAO.md` (teste de bloqueante, escada, base declarada, decisão só vale gravada), passo 1, relatório e comunicação em `agents/jarvis.md`, linha de gravação imediata em `docs/retomada-de-sessao.md`, decisões do dono no estudo, invariantes em `tests/config.json` e linha em `[Não publicado]`.

Conferido: 281 testes verdes; `scripts/validar-plugin.sh` passa. Sem mudança em hooks, catraca ou `.github/`; invariantes só acrescentam proteção, então não pedem rótulo. `jarvis.md` segue abaixo do limite de linhas. Texto sem termos de projeto nem nome da fonte (`R-NEUTRO`) e sem custo (`R-CUSTO`). O texto da regra fica só em `R-DECISAO`; o Jarvis cita o ID (ADR 0002).

Parecer de autor, feito pelo mesmo agente que escreveu a mudança; o review independente fica a cargo do `tech-lead` no PR.

## Review independente

Revisor: `forge:tech-lead`, sem ter escrito a mudança. HEAD revisado: `5e8c2c5`. 281 testes verdes no checkout do PR. Parecer: **reprovado**, por um ajuste pequeno.

**Bloqueia**
- `docs/regras/R-DECISAO.md`, complemento, teste de bloqueante: a condição 1 lista negócio, dados, interface, escopo, segurança, compatibilidade e ato irreversível, mas o primeiro item da regra manda ao usuário também custo, acesso e exceção a uma regra. Com "faltando uma, o time decide", essas três categorias passam a poder virar suposição, e a regra fica mais frouxa do que era. Sugestão: uma linha dizendo que o teste não se aplica a custo, acesso e exceção a regra (`R-CUSTO`, `R-CONFORMIDADE`), que sempre vão ao usuário, nem a fato de negócio que o usuário já declarou. Isso mantém a leitura aprovada em C1 = A: só o que é reversível e barato vira suposição.

**Recomendado**
- A escada começa em "fato do projeto" e não tem "o que o usuário disse", que a proposta (item 1) põe em primeiro. Incluir como degrau 0, ou dizer que o dito pelo usuário já encerra a decisão.
- A ordem do relatório (estado, precisa do usuário, feito, riscos) é aplicável nas 8 linhas, mas não diz onde entra a linha "Suposições" que o complemento manda pôr no relatório. Sugestão: dentro de "o que precisa do usuário", como "a confirmar", ou em riscos.

**Conferido sem ressalva**
- Uma por vez, opções e recomendação seguem intactas; só se acrescenta ao final. As três condições valem juntas e a escada cabe sem contradizer a regra (recomendar sempre, com base declarada, C3 = C).
- Decisão só vale gravada e pergunta de novo após compactação estão em `R-DECISAO`, em `agents/jarvis.md` (comunicação) e em `docs/retomada-de-sessao.md` (8.2, mesmo turno).
- O passo 1 grava modo, escopo e suposições com a base, antes do discovery, e o modo nunca sobe sozinho (item 10).
- O texto da regra fica só em `R-DECISAO`; o Jarvis cita o ID (ADR 0002). Nenhum nome da fonte nas linhas adicionadas fora do estudo, que já os continha. Invariantes só acrescentam proteção.

## Re-review independente

Revisor: `forge:tech-lead`, sem ter escrito a mudança. HEAD revisado: `ac4f1ff`. 281 testes verdes no checkout do PR. Parecer: **aprovado**.

**Bloqueante resolvido.** O complemento de `R-DECISAO` agora diz que o teste não se aplica a custo (`R-CUSTO`), acesso e credenciais, exceção a uma regra (`R-CONFORMIDADE`) nem fato de negócio já declarado pelo usuário: esses casos vão sempre ao usuário. O primeiro item da regra, as opções com recomendação e "uma por vez" seguem intactos; a única mudança é uma exceção que restringe o teste, então a regra não ficou mais frouxa. A varredura por "bloqueante" e "Suposições" nos demais arquivos não achou outro texto que reabra o teste (`agents/jarvis.md` só o cita por ID). As duas frases novas entram nos `invariantes` de `tests/config.json`.

**Recomendados atendidos.**
- A escada começa em "o que o usuário disse", antes do fato do projeto, e tem invariante.
- A linha "Suposições" entra no relatório logo depois de "o que precisa do usuário", no passo 6 e na seção de comunicação de `agents/jarvis.md`, com a mesma ordem nos dois lugares.

Nada novo a ajustar.
