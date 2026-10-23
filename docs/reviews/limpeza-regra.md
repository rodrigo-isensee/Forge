---
tipo: review
contrato: 1
pedido: limpeza-regra
branch: melhoria/limpeza-regra
commit: 15dab7588a2aa2956584ada289d63afeaf3ea15f
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-23
---
# Review: limpeza-regra

## Achados
- A1 (bloqueante) docs/retomada-de-sessao.md:285 · classe: texto que repete a regra sem a exceção · a tabela diz que apagar branch enviada "sempre exige a confirmação do usuário"; contradiz a R-VERIFY nova para branch com PR mesclado e head igual ao headRefOid
- A2 (recomendado) docs/propostas/retomada-de-sessao.md:185 · classe: proposta que cita a regra antiga · cita "Confirme com o usuário antes de apagar ou reescrever branch" como regra vigente; documento de proposta, sem efeito de regra, alinhar ou deixar datado

## Parecer
Reprovado por um bloqueante (A1), texto pequeno. Revisão por leitura do diff `origin/develop...15dab75` (6 arquivos de texto mais fragmento); nenhuma regra "ferramenta" citada aqui, a suíte rodou no pedido de origem (1693 OK, segundo o histórico do pedido) e roda de novo no pre-push.

Lido como agente que segue a regra num projeto:
- R-VERIFY: a exceção é clara (PR mesclado, head remoto igual ao `headRefOid`, decisão do dono de 2026-10-23, remete à R-FLUXO) e os dois casos que seguem pedindo confirmação estão ditos (reescrever; apagar sem PR mesclado). Bom.
- R-FLUXO "Depois do merge" e "No projeto": a conferência do head vem antes de apagar a remota e vale também para o projeto. A ordem dos parênteses no item (1) (exceção antes do comando `git push origin --delete`) é um pouco truncada, mas não ambígua.
- Jarvis, tech-lead e `docs/fechamento-integrador.md` (passo 7) dizem o mesmo; o passo 7 liga a conferência de sha do `forge-fechar` à exigência da R-VERIFY, e `bin/forge-fechar` já confere sha antes de apagar (linhas 237, 379, 420), então o texto bate com o comportamento.
- `grep -rn "Confirme com o usuário antes de apagar"`: restam só a própria R-VERIFY (com a exceção) e `docs/propostas/retomada-de-sessao.md:185` (A2). `templates/projeto/` não repete a regra (confere com o pedido). O hook `conformidade.py` só barra apagar `main`/`develop`/`homolog`, sem conflito.
- Fragmento `changelog.d/limpeza-regra.md` presente e correto. Rótulo `afrouxa-regra` do dono ainda precisa ir no PR (pedido LIMPEZA-REGRA-PR); o título do PR deve destacar o afrouxamento.
- Sem teste novo para a exceção: texto de regra protegido por invariantes de `tests/config.json`, não tocado aqui por restrição do pedido.
