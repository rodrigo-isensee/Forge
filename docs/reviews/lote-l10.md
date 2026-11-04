---
tipo: review
contrato: 1
pedido: versao-033
branch: melhoria/lote-l10
commit: effbe5b1b16cedb1c84698afcf4921c053692c48
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-04
---
# Review: versao-033, lote L10 (E14 VOLTA-ETAPA-NOVA, Q14 = A)

Escopo lido: só o delta `51ef12d..effbe5b`, porque a branch está empilhada sobre o L09 (51ef12d), que está sobre o L08. Arquivos: `bin/forge-check`, `tests/test_volta_por_delta.py`, `tests/mutantes/lote-l10.json` e `changelog.d/lote-l10.md`. A referência é o modelo de ameaças em `docs/security/ameacas/versao-033.md`, seção E14, e o corpo do PR em `ferramentas/pr-lote-l10.md`.

## Achados
- A1 (recomendado) ferramentas/pr-lote-l10.md:4 · o corpo diz 96 linhas; o numstat de 51ef12d..effbe5b dá 97 (bin/forge-check 47+4, teste 46). Corrija o número antes de abrir o PR
- A2 (recomendado) bin/forge-check:1828 · a âncora é a primeira linha do Histórico que cita o nome do brief anterior, não só a de delegação (C-3 cita a de delegação como exemplo). Linha anterior à delegação adianta a âncora; o limite fica no plano do tech-lead
- A3 (recomendado) ferramentas/pr-lote-l10.md:31 · a linha `etapa <id> aberta` no jarvis.md fica para o PR de textos; registre essa pendência no pedido versao-033 para ela não se perder antes da release

## Limite da Q14 (controles e mudanças proibidas)
- C-1 (`fora_do_escopo_da_volta`): o bloco anterior é comparado como prefixo exato, linha a linha, sem normalizar. Só o `\r\n` final do bloco sai (`bloco_sem_final`). Subtestes: linha anterior editada, espaço a mais e acréscimo no meio. Mutante M1 morto.
- C-2: a linha nova só passa se for chave de `decisao`, que é a forma do gerador montada com o texto de `## Etapas` depois do `sem_controle`. A repetição reprova. Subtestes: texto diferente e etapa duas vezes. M2, M3 e M4 mortos.
- C-3: a prova vem só do `## Histórico` do pedido (`ETAPA_ABERTA` ancorada no início da linha) e vale só depois da linha que cita o brief anterior. Não vem do brief nem do mtime (T-3). Subtestes: aberta antes, sem prova, brief não registrado e fora da forma. M5, M6, M7 e M12 mortos. O pedido é lido pelo caminho já restrito às raízes (E2); o delta não mexe nisso.
- C-4: exclui `Cobre:` e `Etapa:`, e também id ou texto já presentes no `Entregar` ou no `Fora do escopo` do anterior. Subtestes: a etapa da própria volta e E1.1 do Entregar. M8 e M9 mortos.
- C-5: `gerar_volta` e `conferir_volta` chamam a mesma `etapas_novas_da_volta`. O teste gera, preenche e confere com rc 0. M11 morto.
- C-6: os cinco abusos reprovam com o motivo esperado e o acréscimo correto passa.
- T-1: ausente, porque as linhas antigas seguem byte a byte. T-2: ausente, porque `Objetivo` e `Relatório` seguem pelo ramo antigo e `Decisões e restrições` não muda (subtestes Objetivo e Relatório, M10 morto). T-3: ausente.
- Cada controle tem teste que reprova sem a mudança: os 12 mutantes da spec morreram.

## M14
São 97 linhas de código e teste (o JSON de `tests/mutantes/` e o changelog ficam fora), abaixo de 150. Há um comportamento só: o acréscimo de etapa nova no `Fora do escopo` da volta. Não toca `hooks/` nem `PROTEGIDOS`. O PR afrouxa sozinho, sem item que aperta, e pede o rótulo `afrouxa-regra`, que só o dono aplica.

## Texto do jarvis.md fora deste PR
Aceito. Sem a linha nova no Histórico, o gerador não propõe a etapa e a conferência reprova a linha acrescentada à mão. A falha é fechada e o comportamento atual se mantém. Juntar texto de agente a um PR de regra afrouxada misturaria duas classes de mudança. O registro da pendência está no A3.

## Comandos (saída citada)
- `python3 -I -m unittest discover -s tests -p test_volta_por_delta.py`: 68 testes, OK, rc=0.
- `bin/forge-mutante tests/mutantes/lote-l10.json`: rev=effbe5b1b16c, M1 a M12 morreram, rc=0.
- Shellcheck: não se aplica (não há shell no diff). Suíte inteira: fica com o QA (D-5).

## Parecer
Aprovado. O diff fica dentro do limite da Q14 e cada C-n tem teste que mata mutante. Nenhum T-n aparece no código, e a M14 é atendida. Os três achados são recomendações e não devolvem a entrega.
