---
tipo: revisao-seguranca
contrato: 1
pedido: pn1-desde-base
branch: melhoria/pn1-desde-base
commit: ee49b7ef07337f4abf940b5da94036fbba641028
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-29
---
# Review de segurança: pn1-desde-base

Escopo: `git diff 99315cfb42c6852c7d7959cd6dca8161e2bd5c08...ee49b7ef07337f4abf940b5da94036fbba641028` (P-N1: o `forge-check entrega` aceita o Base-sha do brief como Desde quando a branch nasce dele e não há conferida ancestral do head; texto de `agents/conferente.md`).

## Gatilhos
Controle do Forge (`R-SEGURANCA`): `bin/forge-check entrega` decide o intervalo que o conferente lê (`R-PROVA`), e `agents/conferente.md` instrui a conferência.

## Achados
- A1 (recomendado) bin/forge-check:839 · conferida antiga ancestral do Base-sha (branch anterior integrada por merge, não por squash) segue recusando o Desde igual ao Base-sha; lado seguro, só usabilidade, fora da P-N1

## Detalhe dos achados
**Invariante central (verificada):** no ramo novo (`bin/forge-check:1076`) `valido` fica `None`, e daí em diante o cálculo é idêntico ao da chamada sem `--desde`: `de = base_sha`, `arquivos_da_entrega(..., None)`, contagens com três pontos, `revisados` da `merge-integracao` como na branch inteira. A única diferença de saída é a linha informativa `base: Base-sha do brief (sem conferida na branch)`, que não reprova nem aprova nada. O Desde pelo Base-sha, portanto, nunca confere menos do que a primeira conferência: o intervalo Base-sha..head cobre todo o trabalho novo da branch.

**Casos de borda (todos no lado seguro):**
- Branch que não nasce do Base-sha: `e_ancestral(base_sha, head)` falso (`bin/forge-check:839-840`) cai no ramo antigo e sai `escopo: --desde sem conferência anterior` (rc 1); além disso a linha `escopo: Base-sha fora da branch` já reprova. Coberto por `test_branch_que_nao_nasce_do_base_sha_segue_recusada` e pelo mutante M4.
- Base-sha forjado ou inexistente: barrado antes, em `sha_do_commit(base_sha) != base_sha` (rc 2). Sonda com sha de zeros: `entrega: ref ilegível ...`, rc 2. Base-sha que existe mas não é ancestral de `origin/<Base>`: o ramo novo não confere isso, mas a linha `escopo: Base-sha fora da branch` (reprova) é gravada antes e independe dele.
- Conferida ancestral do head: o ramo novo não vale (mutante M3) e o Desde segue sendo a conferida. Sonda no pedido real (conferida `ee49b7e` = head) com `--desde` igual ao Base-sha: `escopo: --desde sem conferência anterior`, rc 1.
- Conferida antiga ancestral do Base-sha: também é ancestral do head, então o ramo novo não vale, e `desde_valido` a exclui; resultado `--desde sem conferência anterior` (rc 1). Lado seguro (A1).
- Linha `base do delta fixada pelo dono`: não conta como conferida no ramo novo (mutante M6); com ela no Histórico e Desde igual ao Base-sha, o intervalo é a branch inteira, que contém o delta fixado: confere mais, nunca menos. Pedir o Desde fixado continua passando por `desde_valido`, sem mudança.
- Conferida com sha que não existe ou fora do head (reescrita da branch, squash): o ramo novo vale e o intervalo é a branch inteira. Um autor que reescreva a história para tirar a conferida do head só consegue ser conferido por inteiro.
- A checagem `--desde gravado na própria entrega` (`pedido_na_entrega`) não roda no ramo novo, e não precisa: ela protege o encurtamento do intervalo, que aqui não existe; o pedido segue lido da cópia principal.

**Texto de `agents/conferente.md:85`:** a exceção só autoriza rodar com o Desde igual ao Base-sha e copiar a linha `base:`; a leitura de todos os `escopo: confira` continua obrigatória e o próprio comando recusa o Base-sha quando a última conferida está no head. Não dispensa conferência.

**A1, detalhe.** Evidência: `bin/forge-check:839`. Caminho de ataque: nenhum (a falha é recusar, não aceitar). Severidade: informativa. Correção mínima, se o dono quiser o caso: tratar como "sem conferida na branch" também a última conferida ancestral do Base-sha (o intervalo continua o da branch inteira). Esforço: P. Dono: `tech-lead`. Não devolve.

**PA-7 (`docs/engineering/achados-recorrentes.md`):** AR-3 (sem lista negativa nova), AR-5 (sem python novo em caminho de hook), AR-7 e AR-8 (sem git com pasta implícita nova: `e_ancestral` recebe `raiz`) não se aplicam; AR-1 conferido: os seis mutantes da spec cobrem as quatro condições de `desde_e_a_base` e a escolha da última conferida.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do diff, `python3 -m unittest tests.test_conferencia_base_dono` (28 testes, OK) e duas sondas do `forge-check entrega` no head. `gitleaks` e `semgrep` não estão no PATH (lacuna registrada; o diff não traz credencial nem configuração).
