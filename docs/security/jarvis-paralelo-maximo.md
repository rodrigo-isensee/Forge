---
tipo: revisao-seguranca
contrato: 1
pedido: jarvis-paralelo-maximo
branch: melhoria/jarvis-paralelo-maximo
commit: 7fd503451ad679f2b9aa93984dc0af132e69f7b2
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-21
---
# Review de segurança: jarvis-paralelo-maximo

## Gatilhos
Controles do Forge (`R-SEGURANCA`): o diff muda instrução de agente (`agents/jarvis.md`), que governa como o orquestrador dispara o time e aplica os portões, e a lista de invariantes em `tests/config.json`.

## Achados

## Detalhe dos achados
Sem achado bloqueante. Conferido no diff `f911dfa..7fd5034` (3 arquivos: `agents/jarvis.md`, `tests/config.json`, `changelog.d/jarvis-paralelo-maximo.md`).

- Teto e WIP intactos: a frase nova em `agents/jarvis.md:44` termina com "sempre dentro de `R-TETO` e `R-WIP`" e fica antes da lista "Sempre dentro de:" (linhas 45 a 47), que não mudou. Nada no diff altera o teto adaptativo, o "pesado um por vez" nem o limite de 1 cartão por agente.
- Série por arquivo intacta: a mesma frase manda esperar por "série por arquivo em comum", e a instrução de `bin/forge-check sobreposicao` e a serialização de branches com arquivos em comum seguem iguais na mesma linha.
- Portões intactos: as etapas 5 e 6 de "Como conduzir um pedido" (conferência, `R-REVIEW`, `R-SEGURANCA`, `R-QA`) não mudaram; um portão é dependência real, então "espere só por dependência real" não o dispensa. Paralelizar o preparo do brief seguinte não envia nem mescla nada antes do portão.
- Alcance das melhorias (`agents/jarvis.md:76`): a frase não muda o caminho de entrega (continua `melhoria/*` → `develop` → `homolog` → `main`, `R-FLUXO`, merge da `main` pelo dono, `R-MAIN`) e a classificação "vai para o Forge / fica no projeto" que vem logo depois segue valendo; `R-NEUTRO` (linha 83) continua barrando o que é específico de um projeto.
- Invariantes: as duas entradas novas em `tests/config.json` só acrescentam proteção; nenhuma foi removida nem afrouxada.
- Autorização: a edição de `agents/jarvis.md` tem a decisão do dono de 2026-10-21 00:25 registrada no pedido.
- Custo (`R-CUSTO`): nenhum; mais paralelismo continua limitado pelo teto de máquina, sem serviço pago novo.

Recomendação (baixa, não bloqueia; dono: `tech-lead`, esforço P): a expressão "sem conservadorismo" em `agents/jarvis.md:44` pode ser lida, por um modelo, como licença para disparar uma etapa antes do portão que a precede. A cláusula já cita `R-TETO` e `R-WIP`; acrescentar `R-REVIEW`, `R-SEGURANCA` e `R-QA` à mesma cláusula ("sempre dentro de ... e dos portões") fecharia a leitura ambígua sem mudar o comportamento. Caminho realista de dano: o próprio orquestrador manda QA ou merge antes do parecer; os portões mecânicos (`forge-check pr`, hooks) seguram o merge, por isso fica como recomendação.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Revisão por leitura do diff e do contexto do agente. `gitleaks`, `semgrep`, `zizmor`, `actionlint`, `osv-scanner` e `trivy` não estão no PATH deste ambiente (lacuna registrada); o diff é só texto, sem código, dependência, workflow nem segredo.
