---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-develop-relogio
commit: 76cbce17155b2a769e40155c7fcb47b8bb904f46
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-19
---
# Review de segurança: v0479-develop-relogio (v0478 E33.3)

Gatilhos: testes de controle dos hooks (vigia do prazo do merge, orçamento de CPU do corpus da volta única).

Escopo: diff `c720891e..3298def5` (4 arquivos, só testes, mutante e fragmento de changelog); nenhum hook, regra ou código do Forge muda.

## Resumo
Pergunta do brief: algum controle passa a deixar escapar o que pegava? Não.
- Sonda S1 (`tests/test_hooks.py:1315-1334`): a parcela da referência fica fixa em 0,36 (a medida do review) e o `carga_explica_a_recusa` (`tests/prova_de_carga.py:61-70`) decide pela CPU e pelo relógio reais do hook. O sono extra de 3,8 s conta como tempo acordado (`sono_do_git_lento` lê só o 1.o `sleep`, `tests/test_hooks.py:110`), e a carga real só baixa a CPU e sobe o relógio: o aproveitamento cai, a recusa da S1 fica mais firme sob carga, não mais fraca. O mutante M1 (aproveitamento mínimo para 0) morre: a S1 depende do aproveitamento, não só do portão da parcela. Antes, com a máquina livre, a S1 reprovava pelo portão da parcela sem exercitar o aproveitamento; agora o exercita sempre.
- Corpus (`tests/test_hooks_volta_corpus.py:122-138`): `menor_custo` (`tests/apoio_volta_unica.py:50-59`, já na develop e usado no orçamento dos heredocs) roda até 3 vezes e só para abaixo do limite; o limite não muda e cada rodada confere o número de casos (`assertEqual` dentro de `medir`), então correção do corpus continua conferida em toda medida. A carga só soma CPU; regressão acima do limite passa dele nas 3. A folga ganha é só contra ruído de cerca de 1 % no limite (180,79 s e 181,40 s contra 180 s).

## Achados
- A1 (recomendado) tests/prova_de_carga.py:58 · Fora do diff: com parcela real perto de 0,1, a divisão da CPU fixa da subida do hook aceita a S1 como carga nos testes que usam a referência ao vivo; o teste que o expunha (instável) agora fixa 0,36. Sugestão: piso de parcela ou CPU mínima absoluta no carga_explica_a_recusa.

## Sondas

## Detalhe dos achados
A1: evidência `tests/prova_de_carga.py:55-70` e o próprio docstring da S1 (`tests/test_hooks.py:1318-1321`, "a muito carregada ... aceitava a S1"). Caminho: não há atacante; é qualidade do portão de testes. Uma regressão que faça o hook dormir (não gastar CPU) além do prazo poderia passar como `PRAZO-CARGA` num runner com parcela muito baixa, nos fixtures que liberam pela carga. Pré-existente, não introduzido aqui; o conserto só tirou o sinal instável. Severidade baixa · esforço P · dono: qa-engineer (cartão novo, fora deste PR).

## Revalidação (head 76cbce17, E33.8)
Delta lido: `forge-check parecer delta` desde 3298def5; no domínio só `tests/test_hooks.py` (`changelog.d/` e `tests/mutantes/` fora). Nenhum hook, regra ou código do Forge muda: nenhum hook passou a aceitar o que recusava.
- A S1 (`tests/test_hooks.py:1319-1351`) injeta relógio (8,34 s), CPU (0,13 s) e parcela (0,36) medidos no review (`PAREDE_DA_S1_S`, `CPU_DA_S1_S`, `PARCELA_DA_S1`, `:109`); a decisão do critério fica independente da máquina. O hook e a recusa do vigia seguem reais: o teste guarda o retorno de `rodar` e exige `returncode == 2` e `não decidiu em PRAZO_DO_MERGE_S s` no stderr, e que só uma recusa chegue ao critério.
- O controle continua provado: com CPU e relógio fixos, só o aproveitamento (0,13 / (8,34 - 4,0) / 0,36 < mínimo) separa o sono da carga; o mutante M1 (`tests/prova_de_carga.py:70`) segue morrendo.
- Rodados: `tests.test_hooks.Hooks.test_liberar_ou_provar_a_carga_recusa_a_sonda_s1` OK (10,5 s, carga 6,6); `bin/forge-mutante tests/mutantes/v0478-develop-relogio.json` M1 morreu. Suíte inteira: no CI do PR.
- A1 segue como estava (recomendado, fora do diff); sem achado novo.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Rodados só os testes tocados: `tests.test_hooks.Hooks.test_liberar_ou_provar_a_carga_recusa_a_sonda_s1` OK (8,6 s, carga 2,9 em 12 núcleos); `tests.test_hooks_volta_corpus.CorpusDaVoltaUnica.test_corpus_nos_dois_hooks` OK (41 s de relógio); `bin/forge-mutante tests/mutantes/v0478-develop-relogio.json`: M1 morreu. Suíte inteira: no CI do PR. Sem segredo no diff (leitura direta; o diff não toca configuração nem workflow).
