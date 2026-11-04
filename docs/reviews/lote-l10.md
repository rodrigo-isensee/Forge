---
tipo: review
contrato: 1
pedido: versao-033
branch: melhoria/lote-l10
commit: 83a28d7537c95c9b30e96e2bf0bb16a7342802a2
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

## Revalidação (head f25db72)
- Delta lido, só o próprio do L10: 08aa2a4 (`ETAPA_ABERTA` agora fecha em `aberta\s*$`, e o subteste "prova fora da forma" ganha `aberta-nao` e `aberta.`), 59bec42 (M13 com o trecho que casa o código), 5e5d37e e fd7b144 (`tests/test_qa_lote_l10.py`: brief anterior exato, `exemplo-10`, e os sufixos `aberta-nao`, `abertura prevista`, `abertas`) e f25db72 (`test_qa_lote_l10` no `FORGE_CHECK` do `bin/forge-testes`, contagem 41 em `test_testes_tocados`).
- Já lido: o resto do delta 51ef12d..effbe5b, que não mudou. Os merges do L08 e do L09 ficam com os pareceres deles.
- A correção do L10-1 aperta a T-3, sem afrouxar nenhum C-n. O `\s*$` aceita só espaço no fim, e as linhas já vêm separadas por `splitlines`. O teste do QA herda a fixture de `BriefDeVolta` e o `load_tests` roda só a classe nova, sem repetir a suíte.
- `-p test_volta_por_delta.py`: 68 OK, rc=0. `-p test_qa_lote_l10.py`: 1 OK, rc=0. `-p test_testes_tocados.py`: 86 OK, rc=0.
- `bin/forge-mutante tests/mutantes/lote-l10.json`: M1 a M13 mortos, rc=0 (o M13 guarda a âncora no fim da linha).
- O `commit:` aponta para f25db72, e não para fd7b144. O f25db72 mexe em `bin/forge-testes`, que fica fora de LIVRES, e com fd7b144 o `commit_vale` daria o parecer como desatualizado. De f25db72 ao head só mudam `docs/qa/` e `docs/reviews/`. O f25db72 é posterior ao teste do QA, fd7b144, e por isso atende o E16.
- Os achados A1 a A3 seguem como recomendação. Com o delta próprio de agora, a conta do A1 dá 138 linhas de código e teste: `bin/forge-check` 53, `test_volta_por_delta` 49, `test_qa_lote_l10` 32 e o mapa 4. O total segue abaixo do teto de 150 da M14.

## Parecer
Aprovado, e na revalidação sobre f25db72 também. O diff fica dentro do limite da Q14 e cada C-n tem teste que mata mutante. Nenhum T-n aparece no código, e a M14 é atendida. Os três achados são recomendações e não devolvem a entrega.

## Revalidação (pareceres da branch: 1d50bea e 083a959)
Revisado: 460659b, o merge da lote-l09 que trouxe 1d50bea e 083a959. Os merges 88a83b3 e 460659b não têm resolução manual (o `--remerge-diff` sai vazio), e o patch do E14 não muda. Veredito: **aprovado**, sem achado novo.

Delta lido: 1d50bea e 083a959 do L08, nos arquivos `bin/forge-check` (+13 -2), `tests/test_forge.py` (+40 -5) e `tests/mutantes/lote-l08-pareceres-da-branch.json`.

Numa branch de trabalho, o `cmd_pr` agora conta só os pareceres cujo `branch:` é igual à branch. Se não houver nenhum, reprova com `sem parecer da branch` (falha fechada). A branch vem da ref ou, quando a ref é um sha, de `branch_do_sha`. A promoção, a biblioteca chamada sem branch (catraca do CI) e o sha ambíguo continuam lendo o parecer mais recente do pedido, como antes. Isso aperta a regra e não afrouxa nenhum portão.

O efeito no `hooks/parecer.py:419`, que usa o mesmo `cmd_pr`, também aperta: `gh pr create` e `gh pr ready` passam a exigir o parecer da própria branch.

Sonda de bypass: um parecer de outro item com `branch:` forjado para a branch de trabalho, e `commit:` na base. Resultado: rc 1, `commit: desatualizado: src/x.txt mudou depois do parecer`. O `branch:` só escolhe qual parecer é lido; a validade continua sendo a do `commit_vale`. Um parecer forjado não aprova nada que o mais recente do pedido já não aprovasse antes, então não há bypass.

Testes e mutante, num clone isolado em 083a959:
- `python3 -I -m unittest discover -s tests -p test_forge.py -k ConferenciaPresaAoHead`: rc=0 (11).
- `-k test_pr_`: rc=0 (32).
- `-p test_promover_homolog.py`: rc=0 (36).
- `bin/forge-mutante tests/mutantes/lote-l08-pareceres-da-branch.json`: rc=0, M53, M54 e M55 mortos.

Enquanto esta revalidação rodava, entrou o teste do QA 5ac531f (`tests/test_qa_lote_l08.py` +38 -1, classe `QaPareceresDaBranch`). Li o teste inteiro. Ele cobre três casos: o parecer próprio aprovado com o alheio desatualizado ou reprovado, a falta do parecer próprio com o alheio aprovado e a falta só do QA. Nenhum achado. `python3 -I -m unittest discover -s tests -p test_qa_lote_l08.py` deu rc=0 (24 testes). Ele chegou aqui pelo merge 83a28d7, sem resolução manual (o `--remerge-diff` sai vazio). O `commit:` passa a 83a28d7, o último commit de teste (E16).
