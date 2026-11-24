---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-g2-0-adr-status
commit: 72b4a439fe0dda2bf6d4a0110faa6e92d75970a7
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0481 (E6.4, PR #872, ADR 0019 parecer como status do commit; classe T), revalidação por delta

Delta lido: `forge-check parecer delta docs/reviews/v0481-g2-0-adr-status.md` deu `revalida: sim (este parecer barrou: o último parecer não é aprovado)`; li só `git diff 36f0c14a..72b4a439` (ADR 0019, fragmento em `changelog.d/` e o parecer anterior, E6.2). O review não roda a suíte (R-REVIEW); o CI do head é o do PR.

## Parecer
Aprovado. Os três achados do parecer anterior (head 36f0c14a) foram resolvidos na volta E6.3.

A1 (resolvido) · linhas 5, 12, 20, 75, 87 e 90. A tese deixou de dizer que a aprovação vence: agora diz que a regra de hoje (domínio do tipo, merge simulado da ADR 0004, R-REVIEW) mantém o parecer e que o custo é a rodada de portão para ler o delta; o caso do #867 aparece como três rodadas com `revalida: não`. O item 4 da Decisão diz que a regra de validade não muda e que só muda quem a aplica (a ferramenta herda no lugar da rodada). A medida passou a ser "rodadas de portão por head novo com `revalida: não`", com esperado zero depois do G2.3. O fragmento do `changelog.d/` acompanha.

A2 (resolvido) · linhas 91 a 93 e a linha de Leituras. A medida de tempo cita só o que a ferramenta imprime, e conferi cada campo na fonte: `lead_develop_h_p50` (`bin/forge_governanca.py:616`, mediana em horas), `relogios:` com `aberto_ate_develop`, `pronto_ate_develop` e `meta=30` (`bin/forge-check:61`) e `ci=<execuções>/<falhas>` do `metricas --gh` (`bin/forge_governanca.py:762`). O que falta virou pendência com dono (`tech-lead`) e momento (depois do G2.4): contagem por causa (o `revalidacoes` casa só `revalid`, `bin/forge_governanca.py:43`), P75, tempo desde o primeiro commit e CI por head. A leitura manual de a) e d) está descrita passo a passo.

A3 (resolvido) · linha 63. A consequência da D3 a) agora prende o G2.4 e o G2.5, com a referência à seção 5 do desenho.

No delta não há achado novo.
