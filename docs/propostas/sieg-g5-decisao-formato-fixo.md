# SIEG-G5: mensagem de decisão ao dono em formato fixo, conferida antes de sair

Estado: proposta · pedido v0478 (E135.1) · cartão `SIEG-G5-DECISAO-FORMATO-FIXO` (dono 16/11 15:40) · autor: software-architect
Origem: só a ideia G5 de um estudo externo de fábrica de agentes (anexo do pedido em `docs/anexos/`, linha 12), nada de código copiado.
Afrouxa? Não: nada sai de `docs/regras/`, de `tests/config.json` nem de controle. Hook novo: nenhum.

## Problema
Em 16/11 o Jarvis repetiu "continuo esperando as suas duas respostas" e mandou perguntas sem opção marcada
(estudo, linha 12). O formato existe em texto, mas nada confere a mensagem antes de ela sair. Hoje só se confere a
resposta do dono, e só depois.

## O que já existe (lido nesta cópia, develop 0e59c446)
| Peça | Onde | O que faz | O que não faz |
|---|---|---|---|
| Formato da pergunta | `skills/modo-iniciante/SKILL.md:31-38` | contexto, exemplo, opções, "Afrouxa o processo?", custo, recomendação | é texto, nada o confere |
| Uma a uma | `skills/falar-com-o-dono/SKILL.md:10` | uma decisão por mensagem (`R-DECISAO`) | idem |
| Resposta curta O4 | `skills/falar-com-o-dono/resposta-curta.md:7` | código `1a)`, marcas `[recomendada]`, `[reversível]`/`[irreversível]` | idem |
| Leitura da resposta | `bin/forge_dono.py:97-137` (`opcoes_da_pergunta`, `ler_resposta`) | lê `1a 2c`/`aprovo` contra a última `PERGUNTA AO DONO`; o ambíguo volta (rc 1) | só confere depois que o dono responde |
| Opções exclusivas | `bin/forge_dono.py:125-126` | duas opções da mesma questão = ambiguidade | não está escrito na pergunta |
| `decisoes --resposta` | `bin/forge-check:10572`, `bin/forge_dono.py:316-330` | a porta de entrada da leitura acima | idem |
| Gate da pergunta | `bin/forge-check:5278` (`anotar --tipo pergunta`) | recusa corte recomendado sem `origem:`… (E6, `forge_dono.py:198-208`) | não confere nada além do corte |
| Teto de tamanho | `hooks/meta.py:40` (`TETO_DA_MENSAGEM = 1200`, S6) | mede a mensagem no Stop | só mede, nunca recusa |
| Medida posterior | `bin/forge_transcricao.py:278-342` (`transcricao decisoes`) | conta respostas com mais de um grupo A/B/C ou grupo sem "Recomendo" | não vê código, marca nem tamanho |

## O que falta
1. **Conferência do formato antes de sair.** O único ponto que vê a pergunta antes do dono é o
   `anotar --tipo pergunta`, e ele só aplica a E6.
2. **Ligar a mensagem à pergunta anotada.** O Jarvis pode escrever no chat um texto diferente do que anotou, ou não
   anotar. Nenhuma regra diz que a mensagem de decisão é o literal que o anotar aceitou.
3. **Medir o que escapa.** `transcricao decisoes` não conta grupo de opções sem código `Na)` ou sem marca.

## Formato fixo (o literal da `PERGUNTA AO DONO`)
- F1: cada questão tem de 2 a 4 opções `Na)`, letras seguidas a partir de `a` (teto de opções).
- F2: cada questão tem exatamente uma opção `[recomendada]`.
- F3: cada opção tem exatamente uma das marcas `[reversível]` ou `[irreversível]`.
- F4: cada opção tem `afrouxa: não` ou `afrouxa: sim, <regra>` (modo-iniciante, item 4).
- F5: relação entre opções: as opções de uma questão se excluem, o que já vale em `forge_dono.py:125-126`. Opções que
  se combinam viram questões separadas. Escrever isso na skill basta; não precisa de marca nova.
- F6: o literal tem até 1200 caracteres, o mesmo número de `TETO_DA_MENSAGEM` (`hooks/meta.py:40`), num lugar só.
- F7: a E6 (corte recomendado com origem) continua do jeito que está, como uma das regras.
Fora do formato e deste corte: os números de tempo e tokens por opção (`skills/modo-iniciante/numeros.md`). Ficam para
uma versão seguinte, depois de medir F1 a F7.

## Onde a conferência roda
Na **ferramenta**, no gate que já existe: `forge-check anotar --tipo pergunta` (`bin/forge-check:5278`) passa a chamar
uma função `recusa_do_formato(literal)` de `bin/forge_dono.py` que reúne F1 a F7. A `recusa_de_corte` vira uma das
regras dessa função. Fica um ponto de recusa só, no mesmo lugar: não há hook novo nem trava nova (regra da retro de
21/11). A extensão do Stop que o estudo externo sugere (mesmo anexo, linha 12, última coluna) foi rejeitada: seria uma
trava nova, e nenhuma sai em troca.
Fluxo: anotar a pergunta, e só com rc 0 enviar ao dono **o mesmo literal**. Recusa (rc 2) é corrigida e anotada de
novo antes de qualquer envio. `decisoes --resposta` não muda: ela passa a ler sempre pergunta bem formada.
Pergunta já gravada não é conferida de novo: o retroativo fica fora.

## Por que o existente não basta
- A skill e a O4 são texto. Em 16/11 a pergunta saiu sem opção marcada mesmo com elas em vigor (estudo, linha 12).
- `ler_resposta` só vê a pergunta quando o dono já respondeu. Pergunta sem `[recomendada]` só aparece como
  ambiguidade na volta, com uma rodada perdida (`forge_dono.py:128-134`).
- S6 mede o tamanho, mas não recusa (`hooks/meta.py:10`). A medida posterior não vê código nem marca.
- Evidência de execução: esta entrega não rodou comandos (o papel não tem shell). Antes do C1, o tech-lead roda
  `forge-check transcricao decisoes` nos transcritos de 16/11 e registra a taxa de violação, que serve de linha de base.

## Corte (cada fatia entra sozinha na develop)
| Fatia | Agente | Entrega | Pronto quando (oráculo) |
|---|---|---|---|
| C0 | tech-lead | linha de base: `forge-check transcricao decisoes` sobre as sessões de 9/11 a 16/11 | a saída `total:` copiada no pedido |
| C1 | dev Python do Forge + qa-engineer | `recusa_do_formato` (F1 a F7) no `anotar --tipo pergunta`; a E6 dentro dela | `tests/test_anotar.py` e `tests/test_forge_dono.py` com um caso recusado por regra F1 a F7 e um aceito; o mutante de cada regra morre (`tests/mutantes/`); `.githooks/pre-push --suite` verde |
| C2 | tech-lead (texto) | `resposta-curta.md` e `falar-com-o-dono/SKILL.md:10`: "a mensagem de decisão é o literal aceito pelo `anotar`, enviado depois do rc 0"; F5 escrita | `tests/test_clareza.py` verde; invariante novo só se o dono pedir |
| C3 | dev Python do Forge | `transcricao decisoes` ganha `sem_codigo` (grupo sem `Na)` ou sem `[recomendada]`) e `acima_do_teto` | teste com transcrito sintético de cada caso; só números na saída |
Ordem: C0 primeiro. C1 e C3 podem rodar em paralelo. C2 depois do C1, porque o texto cita o comportamento.
Segurança: o literal já passa por `recusa_do_campo` e `recusa_da_forja` (`bin/forge-check:5254-5257`). C1 não
acrescenta leitura de arquivo nem rede (`R-CUSTO`). Gatilho de segurança: nenhum novo, confirmar com o security-engineer.

## Critério de parada (C1)
- bloqueia: pergunta ao dono fora do formato F1 a F7 gravada como `PERGUNTA AO DONO`.
- F1 · questão com menos de 2 ou mais de 4 opções, ou letra pulada · oráculo: `tests/test_forge_dono.py` (caso F1)
- F2 · nenhuma ou duas `[recomendada]` · oráculo: idem (caso F2)
- F3 · opção sem marca de reversão ou com as duas · oráculo: idem (caso F3)
- F4 · opção sem `afrouxa:` · oráculo: idem (caso F4)
- F6 · literal acima de 1200 caracteres · oráculo: idem (caso F6)
- F7 · corte sem origem (E6) · oráculo: os casos E6 de `tests/test_anotar.py` continuam verdes
- gatilho · oráculo: `forge-check anotar --tipo pergunta` sai com rc 2 e "nada gravado" em cada caso acima

## Critério de reversão
Reverter o C1 se, em 2 semanas, o `anotar` recusar uma pergunta que o dono considere bem formada (falso positivo
registrado no pedido). Também se a taxa `violacoes` do `transcricao decisoes` não cair em relação à linha de base do C0.

## Em aberto (vai ao dono só se o time não fechar)
- Teto de 4 opções e de 1200 caracteres: o 1200 já está no S6. O 4 é estimado, porque o exemplo da skill usa 2 ou 3 opções.
