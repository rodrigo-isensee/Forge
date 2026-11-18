---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0478-testes-prazo
commit: 318721dbbb87ab4db3db719d6f0207e8def10423
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-18
---
# Review: v0478-testes-prazo (E12.8, revalidação)

Revalidação (H3, R-REVIEW) do head `318721db`. Li só o delta do `forge-check parecer delta`: `bf3ce6af..318721db`, com 6 arquivos no domínio (`.github/workflows/ci.yml`, `changelog.d/v0478-testes-prazo.md`, `tests/mutantes/v0478-testes-prazo.json`, `tests/mutantes/v0478-testes-prazo-2.json`, `tests/prova_de_carga.py` e `tests/test_hooks.py`). Fora do delta, nada foi relido. Não rodei a suíte; a prova dela é o CI do PR. Rodei os 4 testes novos ou mudados e eles passaram (`Ran 4 tests ... OK`). No `bin/forge-mutante --processos 1` sobre as duas specs, M1 a M10 morreram; M9 e M10 morreram por erro do teste declarado, que é comportamento (divisão por zero).

## Achados
- A3 (recomendado) tests/prova_de_carga.py:17 · Registre no comentário o limite do critério: com parcela da referência muito baixa, o sono a mais passa. Medi a S1 com 0,29 de aproveitamento na parcela de 0,07; ela passaria perto de 0,04. A linha PRAZO-CARGA já mostra a parcela no resumo do CI.

## Sondas
- S2 · S1 (`sleep 4; sleep 3.8;` no 1.o git) por `liberar_ou_provar_a_carga`, com 60 processos de CPU em 12 núcleos (loadavg 45) · espera: AssertionError, sem PRAZO-CARGA · obtido: AssertionError; parede=9.59 cpu=0.11 parcela=0.07 aprov=0.29 aceita=False

## Parecer
Aprovado. O A1 está resolvido. Antes, o critério só provava que o hook não tinha gastado CPU. Agora ele também prova a disputa pela CPU no mesmo intervalo, por dois sinais:
- a referência irmã, que só gasta CPU, fica com no máximo 0,5 do relógio;
- no tempo fora do sono, o hook aproveita ao menos metade da parcela que a referência teve.

Espera fora da CPU (sono, E/S, trava) não gasta CPU no ritmo da fila e reprova. A sonda S1 agora é recusada por teste de verdade (`test_liberar_ou_provar_a_carga_recusa_a_sonda_s1`), e o caso S1 medido entrou na tabela de recusas. Também a reproduzi com a máquina em carga alta (S2), e ela continuou recusada.

A escolha da referência no lugar do `ru_nivcsw` é do autor, e o resultado responde à pergunta que fiz: o `ru_nivcsw` dos filhos só existe depois do `wait` e conta trocas, não tempo, enquanto a referência dá uma medida direta da parcela da CPU.

O limite com carga muito alta existe e a S2 o mede: o aproveitamento de uma espera falsa sobe quando a parcela cai. Ele basta pelos motivos abaixo, e por isso o A3 é recomendado, não bloqueante.
- Um defeito de espera reprova em toda execução sem carga extrema, porque com a máquina livre a parcela fica perto de 1.
- Só passaria numa execução com uns 25 processos por núcleo.
- Mesmo nesse caso, sairia como linha PRAZO-CARGA com `referencia=` no resumo do CI.
- Um piso na parcela devolveria a instabilidade que o pedido corrige.

O A2 está resolvido: a linha PRAZO-CARGA ("recusa do vigia com disputa pela CPU medida na referência") e o fragmento do `changelog.d` dizem o que o critério mede.

O resto do delta:
- `prova_de_carga.py` fica fora do arquivo de teste por causa dos mutantes; os mutantes M5 a M10 cobrem uma guarda cada.
- O subprocesso da referência usa `-I` e ambiente limpo.
- O teste da referência cobre a morte cedo: a parcela fica `None` e a recusa é reprovada.
- O passo novo do CI só conta e lista, sem reprovar (o `${n:-0}` cobre o log ausente). Ele cumpre o A1 da segurança, e o mérito desse achado é do parecer de segurança.
