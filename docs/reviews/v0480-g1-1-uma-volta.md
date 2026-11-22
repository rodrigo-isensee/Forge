---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-g1-1-uma-volta
commit: 57c0cbffa460dfdd6ea459f31e32f398f7262a4c
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-21
---
# Review: v0478 · G1.1 (no máximo 1 volta por item), etapa E100.2

Revisão única (ORDEM DO DONO 21/11 22:13): todos os achados estão aqui; a revalidação olha só o que mudar. Desenho: `docs/propostas/g1-g3-fluxo-rapido.md` (branch `melhoria/v0480-desenho-g1-g3`), seções 2 e 5.

## Achados
- A1 (bloqueante) bin/forge-check:4290 · O teto conta a cadeia do brief, não o item: `brief gerar --volta <brief original>` de novo gera outra "volta 1" (rc 0) e a conferência a aceita igual à primeira (S1). A ordem pede 1 volta por item. Recuse o `--volta X` quando outro brief em docs/briefs já tem `Volta-de: X`, nos dois caminhos.
- A2 (recomendado) bin/forge-check:4260 · A palavra "volta" sozinha autoriza: "DECISÃO DO DONO: nenhuma volta a mais para melhoria/x" vale 2 voltas, e a mesma linha em duas fontes conta duas vezes (S2, S3). Exija a frase que a própria recusa prescreve ("mais uma volta para <branch>") e conte linhas distintas.
- A3 (recomendado) agents/jarvis.md:31 · Segue "máx. 3 voltas por bug", em conflito com o R-QA novo (1 volta por item); o Jarvis é quem leva a decisão ao dono. Troque pela referência ao R-QA sem número.

## Sondas
- S1 · em BriefDeVolta: gerar() e escrever -2.md; gerar() de novo do mesmo original; conferir a saída como -3.md · espera: rc 1, "volta 2 recusada" ou "numeração contornada" · obtido: rc 0, "## Entregar (volta 1)", conferência idêntica à da 1.ª volta
- S2 · voltas_autorizadas({fontes:[(p,[(1,"DECISÃO DO DONO: nenhuma volta a mais para melhoria/x")])]}, "melhoria/x") · espera: 1 · obtido: 2
- S3 · voltas_autorizadas com a linha "DECISÃO DO DONO: mais uma volta para melhoria/x" em duas fontes · espera: 2 · obtido: 3

## Verificação
- Testes afetados: `tests.test_volta_por_delta.BriefDeVolta` (48 testes, inclusive os 3 novos) verdes no head 57c0cbff, rodados por herança na sonda, ambiente limpo e `python3 -I`. Suíte inteira: com o CI (sem PR aberto no momento, item sem run de CI para citar).
- Mutantes: `bin/forge-mutante tests/mutantes/v0480-g1-1-uma-volta.json` M1 a M7 morreram (M1 por erro sob `None`, o caso `""` cobre o comportamento); `-2.json` M8 e M9 morreram. Isenção do trecho movido para `numero_da_volta` correta.
- Tamanho (H1): cerca de 34 linhas líquidas de código em `bin/forge-check`, dentro do teto; 8 arquivos.
- Regras de leitura alcançadas pelo diff: R-QA e R-REVIEW coerentes entre si e com `autor-ate-o-merge.md`; invariantes de `autor-ate-o-merge.md` preservados; fragmento em `changelog.d/` com o nome da branch.

## Desvio declarado (a autorização exige "volta" além da branch)
Aceito. O desenho conta qualquer `DECISÃO DO DONO` que cite a branch; sem a palavra, uma decisão de corte ou de aceite sobre a mesma branch daria volta a mais sem o dono pedir. O desvio aperta e falha fechado. Ainda frouxo na negação e na contagem dupla (A2, recomendado).

## Parecer
Reprovado por A1: o teto é contornável pelo caminho mais natural (repetir o `--volta` com o brief original), e o requisito da ordem é o teto por item (R-REVIEW, requisito não atendido, S1). Correção sugerida: na `gerar_volta` e na `conferir_volta`, recusar a volta cujo anterior já tem sucessor em `docs/briefs/` (mesmo `Volta-de:`), com teste do ramo de falha e mutante por linha de guarda. A2 e A3 viram cartão depois do merge; cabem na volta se o autor quiser, sem reabrir o review.
