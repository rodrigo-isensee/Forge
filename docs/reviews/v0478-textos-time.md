---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0478-textos-time
commit: 932c43c7b8550a2c9e2759ed38825fe969cfe8ad
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-18
---
# Review: v0478 (E19.2, melhoria/v0478-textos-time)

Diff lido: `0c47762a...932c43c7` (2 commits, 6 arquivos, +23 -11): TECH-LEAD-GATILHO-RITMO em `agents/tech-lead.md`, RECIBO-NO-MEIO-DA-RODADA em `agents/jarvis.md` e `skills/falar-com-o-dono/`, invariantes novos em `tests/config.json`, fragmento em `changelog.d/`.

## Achados
- A1 (recomendado) agents/jarvis.md:37 · "e avisa o dono" perdeu o "você": o sujeito gramatical passa a ser "a versão". Sugestão: devolver "e você avisa o dono" (custa 5 caracteres) ou "e o Jarvis avisa".
- A2 (recomendado) agents/jarvis.md:33 · "Antes, leia a skill kanban-metricas" perdeu o gatilho ("antes de pedi-la", a retrospectiva); "Antes" de quê fica implícito. Sugestão: "Antes de pedi-la, leia" ou "Antes da retro, leia".

## Parecer
Aprovado. Conferi cada trecho encurtado contra a base: nenhuma regra saiu. Em `agents/tech-lead.md`, as trocas ("desenvolvimento" → "código", "junto do" → "com", "pelo arquiteto" → "o arquiteto", "entra pronto" → "entra", "entregue" → "passe", "quando ela tem um conjunto verde" → "com um conjunto verde") mantêm ator, gatilho e ID de regra (`R-FLUXO`, `R-REVIEW`, `R-MAIN`); a condição de "pronto" segue explícita (pareceres da classe e CI verde). Em `agents/jarvis.md`, "se a entrega muda interface" → "se muda a interface" mantém `R-REVIEW`; A1 e A2 são perdas de clareza, não de regra, e não bloqueiam. Nenhum texto removido era invariante em `tests/config.json` (grep sem ocorrência das frases antigas em `tests/` e `docs/regras/`). Os três invariantes novos trazem `regra` e `porque` (L35) e casam com o texto da branch. O gatilho do tech-lead ficou igual ao do Jarvis ("antes de abrir item novo ou juntar na `develop`"), como pede o cartão. A recusa de pôr `trabalho-em-paralelo` no `skills:` está justificada com a medida do orçamento no fragmento (`R-DECISAO`).

Sem guarda de código no diff (só texto e configuração de teste): sem mutante a declarar. Suíte inteira: fica para o CI do PR (sem PR nesta etapa). Rodei só as classes que o diff toca: `python3 -m unittest tests.test_forge.RegrasInviolaveis tests.test_forge.Orcamento tests.test_forge.Neutralidade tests.test_forge.Agentes tests.test_forge.RegrasComId` → `Ran 17 tests ... OK`.
