# SIEG-G5: mensagem de decisão ao dono em formato fixo, conferida antes de sair

Estado: proposta · pedido v0478 (E135.1, volta E135.5) · cartão `SIEG-G5-DECISAO-FORMATO-FIXO` (dono 16/11 15:40) · autor: software-architect
Origem: só a ideia G5 de um estudo externo de fábrica de agentes (anexo do pedido em `docs/anexos/`, linha 12), nada de código copiado.
Afrouxa? Esta proposta, não: nada sai de `docs/regras/`, de `tests/config.json` nem de controle. A troca que ela pede (T3, "Trava que
sai") afrouxa: "sim, R-CONFORMIDADE", e vai ao dono. Hook novo: nenhum. Trava nova: sim (F1 a F4 e F6, ver "Trava que sai").

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
| Leitura da resposta | `bin/forge_dono.py:97-137` | lê `1a 2c`/`aprovo` contra a última `PERGUNTA AO DONO`; o ambíguo volta (rc 1) | só confere depois da resposta |
| Opções exclusivas | `bin/forge_dono.py:125-126` | duas opções da mesma questão = ambiguidade | não está escrito na pergunta |
| Gate da pergunta | `bin/forge-check:5278` (`anotar --tipo pergunta`) | recusa corte recomendado sem `origem:` (E6, `forge_dono.py:198-208`) | não confere nada além do corte |
| Teto de tamanho | `hooks/meta.py:40` (`TETO_DA_MENSAGEM = 1200`, S6) | mede a mensagem no Stop | só mede, nunca recusa |
| Medida posterior | `bin/forge_transcricao.py:255-342` (`transcricao decisoes`) | conta grupos A/B/C com mais de um grupo ou sem "Recomendo" | só vê letras A a F maiúsculas (`:255`); não vê `1a)`, marca nem tamanho |

## O que falta
1. **Conferência do formato antes de sair.** O único ponto que vê a pergunta antes do dono é o `anotar --tipo pergunta`, e ele só aplica a E6.
2. **Ligar a mensagem à pergunta anotada.** Nenhuma regra diz que a mensagem de decisão é o literal que o anotar aceitou.
3. **Uma régua que veja o formato novo.** `grupos_de_opcoes` devolve `[]` para `1a)`/`1b)` (sonda S1 do review E135.4).

## Formato fixo (o literal da `PERGUNTA AO DONO`)
- F1: cada questão tem de 2 a 4 opções `Na)`, letras seguidas a partir de `a`.
- F2: cada questão tem exatamente uma opção `[recomendada]`.
- F3: cada opção tem exatamente uma das marcas `[reversível]` ou `[irreversível]`.
- F4: cada opção tem `afrouxa: não` ou `afrouxa: sim, <regra>` (modo-iniciante, item 4).
- F5: as opções de uma questão se excluem (já vale em `forge_dono.py:125-126`); opções que se combinam viram questões separadas. Só texto na skill.
- F6: o literal tem até `TETO_DA_MENSAGEM` caracteres (1200), constante única (ver "Teto num lugar só").
- F7: a E6 continua do jeito que está, como uma das regras.
Fora deste corte: números de tempo e tokens por opção (`skills/modo-iniciante/numeros.md`), para depois de medir F1 a F7.

## Onde a conferência roda
No gate que já existe: `forge-check anotar --tipo pergunta` (`bin/forge-check:5278`) chama `recusa_do_formato(literal)` de
`bin/forge_dono.py`, que reúne F1 a F7 (a `recusa_de_corte` vira uma das regras). Sem hook novo; a extensão do Stop do
estudo externo foi rejeitada. Fluxo: anotar e, só com rc 0, enviar ao dono **o mesmo literal**; recusa (rc 2) é corrigida
e anotada de novo. `decisoes --resposta` não muda. Pergunta já gravada não é conferida de novo.

## Trava que sai (regra 3 da DECISÃO DO DONO 21/11 20:54, `docs/pedidos/v0478.md:717`)
F1 a F4 e F6 são cinco recusas novas com rc 2: uma trava de processo nova. Juntar a E6 na função nova não simplifica nada.
- Sai: **T3** do insumo de corte (`docs/retrospectivas/insumo-corte-de-travas-2311.md`, T3): a gramática do papel só de
  leitura (`hooks/_comum.py:689`, `hooks/conformidade.py:1954`) passa a aceitar `$?` e `$TMPDIR` fora de aspas simples;
  `$VAR` qualquer e a atribuição de `TMPDIR` seguem recusados. Risco baixo (lista fechada de dois nomes) e é o primeiro da
  ordem sugerida no insumo. Custo medido lá: 2 linhas de recusa falsa e 1 incidente (E78.6, E63.6, E63.8).
- Por que T3 e não o S6 ou a medida posterior: os dois só medem, não recusam; tirá-los não tira trava.
- A regra 3 foi escrita para cartão de retro e o SIEG-G5 é cartão do dono; a troca vale mesmo assim, a pedido do review.
- O C1 só entra na develop depois do merge do T3 (ou junto). T3 afrouxa: PR próprio com rótulo `afrouxa-regra`, motivo no
  título e pergunta ao dono (ver "Em aberto"). Se o dono recusar o T3, o C1 não entra até haver outra trava que saia.

## Teto num lugar só (F6)
`TETO_DA_MENSAGEM = 1200` passa de `hooks/meta.py:40` para `bin/forge_dono.py` (só biblioteca padrão, já importado pelo
`forge-check`). `hooks/meta.py` importa de lá pelo caminho `PLUGIN / "bin"`, como `hooks/doutor.py:106` faz com
`forge_versoes`. Direção: o hook importa do `bin`; o `bin` não importa do hook. Oráculo: teste que reprova `\b1200\b` em
`hooks/meta.py` e em `bin/forge-check` e exige `from forge_dono import TETO_DA_MENSAGEM` em `hooks/meta.py`; o mutante
que troca o valor em `forge_dono.py` muda o teto lido pelo `meta`.

## Por que o existente não basta
- A skill e a O4 são texto. Em 16/11 a pergunta saiu sem opção marcada mesmo com elas em vigor (estudo, linha 12).
- `ler_resposta` só vê a pergunta depois da resposta: sem `[recomendada]` vira ambiguidade na volta (`forge_dono.py:128-134`).
- S6 mede o tamanho, mas não recusa (`hooks/meta.py:10`). A medida posterior não vê `1a)` (S1 do review: devolve `[]`).
- Evidência de execução: esta entrega não rodou comandos (o papel não tem shell); a linha de base é o C0.

## Corte (cada fatia entra sozinha na develop)
| Fatia | Agente | Entrega | Pronto quando (oráculo) |
|---|---|---|---|
| C3 | dev Python do Forge | `transcricao decisoes` ganha `fora_do_formato`: resposta com grupo de opções (A a F ou `Na)`) que fere F1, F2 ou F6, contando grupo sem código `Na)` como fora | teste com transcrito sintético por caso, incluindo o texto da S1 (espera um grupo visto e 0 fora) e um grupo `A)`/`B)` (espera 1 fora); só números na saída |
| C0 | tech-lead | linha de base com a régua do C3: `forge-check transcricao decisoes` nas sessões de 9/11 a 16/11 | linhas `total:` e `fora_do_formato` copiadas no pedido |
| C1 | dev Python do Forge + qa-engineer | `recusa_do_formato` (F1 a F7) no `anotar`; teto movido para `forge_dono.py` | casos por regra em `tests/test_forge_dono.py` e `tests/test_anotar.py`, um aceito; mutante de cada regra morre (`tests/mutantes/`); teste do teto único; `.githooks/pre-push --suite` verde |
| C2 | tech-lead (texto) | frase em `skills/falar-com-o-dono/SKILL.md:11` (logo depois da `:10`) e `resposta-curta.md:8` (depois da `:7`); F5 escrita | `grep -cF "A mensagem de decisão é o literal que o anotar da pergunta aceitou com rc 0, enviado sem mudança."` dá 1 em cada arquivo; `tests/test_clareza.py` verde |
Ordem: T3 e C3 em paralelo; C0 depois do C3 (usa a régua dele); C1 depois do C0 e do T3; C2 depois do C1.
Segurança: o literal já passa por `recusa_do_campo` e `recusa_da_forja` (`bin/forge-check:5254-5257`). C1 não acrescenta
leitura de arquivo nem rede (`R-CUSTO`). Gatilho: o import `bin` no `hooks/meta.py` e o T3 vão ao security-engineer.

## Critério de parada (C1)
- bloqueia: pergunta ao dono fora do formato F1 a F7 gravada como `PERGUNTA AO DONO`.
- F1 · menos de 2 ou mais de 4 opções, ou letra pulada · oráculo: `tests/test_forge_dono.py` (caso F1)
- F2 · nenhuma ou duas `[recomendada]` · oráculo: idem (caso F2)
- F3 · opção sem marca de reversão ou com as duas · oráculo: idem (caso F3)
- F4 · opção sem `afrouxa:` · oráculo: idem (caso F4)
- F6 · literal acima de `TETO_DA_MENSAGEM` · oráculo: idem (caso F6) e o teste do teto único
- F7 · corte sem origem (E6) · oráculo: os casos E6 de `tests/test_anotar.py` continuam verdes
- gatilho · oráculo: `forge-check anotar --tipo pergunta` sai com rc 2 e "nada gravado" em cada caso acima

## Critério de reversão
Mesma régua do C0 (`fora_do_formato` do C3, sobre `com_grupo`). Reverter o C1 se, em 2 semanas depois do merge, a taxa não
cair em relação ao C0, ou se o `anotar` recusar uma pergunta que o dono considere bem formada (falso positivo no pedido).

## Em aberto (pergunta ao dono)
- Troca da regra 3: entra a trava F1 a F4 e F6, sai a T3 (afrouxa R-CONFORMIDADE). Recomendação: aprovar o par.
- Teto de 4 opções: estimado (a skill usa 2 ou 3 opções). O 1200 já é o do S6.
