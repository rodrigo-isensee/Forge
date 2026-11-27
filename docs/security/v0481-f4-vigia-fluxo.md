---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-f4-vigia-fluxo
commit: 8d755e503e51f53e37af2befea60ba7622b26dc8
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-27
---
# Review de segurança: v0481 (E34.4, #931, F4 do hook `vigia`, 1ª rodada)

Escopo lido: o diff da branch contra `origin/develop` (`hooks/vigia.py`, `tests/test_hook_vigia_f4.py`, a fixture `tests/hooks/vigia/time-parado-pr-do-dono-silencio.json`, os mutantes `tests/mutantes/v0481-f4-vigia-fluxo*.json` e o M3/M8 de `v0480-vigia-time-parado.json`, o fragmento do changelog). O resto do diff contra o Base-sha veio pelo merge da develop e tem parecer próprio.

Gatilhos: controles do Forge (hook `vigia`, que bloqueia o `Stop` do Jarvis), dado externo de rede (`gh pr list`) que chega ao contexto do modelo.

## Achados
- A1 (bloqueante) hooks/vigia.py:617 · explorável: S1. O vigia conta PR de fork (sem filtro de isCrossRepository) e manda o Jarvis disparar autor ou integração nele: quem abre PR no repositório público prende o Stop a cada vez e leva agente a pegar código de fora.
- A2 (bloqueante) hooks/vigia.py:717 · explorável: S2. A catraca do CI reprova (R-QA): a guarda da base hooks/vigia.py:618 (agentes_rodando(hook, raiz) != 0) foi apagada sem mutante declarado que a catraca reconheça; o M3 trocado não conta como declaração da guarda apagada.

## Sondas
- S1 · python3 -I sonda.py <cópia>: papel_do_pr e prs_parados (subprocess.run falso) com PR isCrossRepository=true, base develop, sem check e outro com ACTION_REQUIRED · espera: fora do aviso · obtido: ['#7 integração', '#8 autor']
- S2 · gh api jobs/140336773208/logs (catraca do head 8d755e50) · espera: catraca verde · obtido: R-QA: guarda de hooks/vigia.py mudada sem mutante declarado: apagada · hooks/vigia.py:618(base) · agentes_rodando(hook, raiz) != 0

## Detalhe dos achados
**A1, PR de fork no aviso (média).** Evidência: `CAMPOS_DO_PR` (`hooks/vigia.py:617`) não pede `isCrossRepository` nem o dono da branch de origem, e `prs_parados` (`hooks/vigia.py:670`) aceita todo PR aberto com `number` inteiro; `papel_do_pr` devolve `integração` para PR sem nenhum check (`hooks/vigia.py:650`) e `autor` para o de check `ACTION_REQUIRED` (o CI de fork à espera de aprovação está em `QUEBRADO`). Caminho: qualquer conta do GitHub abre um PR contra `develop` de um repositório público (o Forge ou um projeto que usa a fábrica); em cada `Stop` do Jarvis com vaga no teto, o vigia bloqueia com `time parado: PR sem agente: #N integração; retome sem esperar o dono`. Ganho do atacante: custo de tokens a cada vez (um bloqueio por turno, o `stop_hook_active` só evita o laço) e um empurrão do próprio controle do Forge para o Jarvis disparar um agente sobre código de fora (o `autor` que "conserta o CI" baixa e roda a branch do fork na estação; a `integração` é pedida para PR que nem passou pelo CI). O texto do aviso em si é seguro: só o número inteiro e o papel de lista fixa chegam ao modelo; título, branch e rótulo nunca saem no aviso. Correção mínima: somar `isCrossRepository` a `CAMPOS_DO_PR` e, em `prs_parados`, contar só o PR com `pr.get("isCrossRepository") is False` (ausente ou outro valor não conta: dúvida cala), com teste do fork (os dois casos da S1) e mutante da guarda. Esforço P. Dono: autor do E34.1.

**A2, catraca reprovada (defeito provado pelo CI).** Evidência: job `catraca` do run 45947916646 no head `8d755e50`, linha do log copiada na S2. A guarda antiga virou `livres = [] if vivos else ...` (`hooks/vigia.py:717`) e o M3 foi realinhado para ela, mas a catraca lê a condição apagada da base sem mutante que a declare. Correção mínima: o que `bin/forge-mutante --cobertura --base origin/develop` listar (mutante declarado para a condição, ou isenção com motivo); não é caso de rótulo `afrouxa-regra`, porque a guarda continua no código. Esforço P. Dono: autor do E34.1.

**O que conferi e passa.** Chamada do `gh` em lista de argumentos, sem shell, `stdin` nulo, `GH_PROMPT_DISABLED=1`, prazo de 5 s dentro dos 10 s do hook; falha, ausência do `gh`, saída fora de JSON ou estouro do prazo caem em `calado` (erros.log, sem bloqueio: dúvida não bloqueia). Instância presa: o `id` passa por `ID_DE_AGENTE` antes de virar caminho e o `tipo` por lista positiva (`_TIPO`) antes de ir ao aviso; `os.lstat` não segue link. A parte de cartões só roda com zero agentes, como antes. Testes afetados rodados na cópia: `tests.test_hook_vigia_f4` e `tests.test_vigia_parado`, 50 testes, OK.

CI do head `8d755e50` (run 45947916641): as cinco partes da suíte, passos, verificações longas, instalação, `python 3.14`, teto de pulados e árvore já provada verdes; `catraca` vermelha (A2); `bateria (pareceres)` e `bateria` vermelhas pela falta dos pareceres deste head.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do diff, sonda em processo (biblioteca padrão) e o log do CI pelo `gh`. Varredura de segredo e de dependência sem objeto: o diff não toca credencial, configuração nem dependência.
