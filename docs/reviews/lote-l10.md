---
tipo: review
contrato: 1
pedido: versao-034
branch: melhoria/lote-l10
commit: 8f22ad36940371ce59a4819a3a976b4d3e4bb0d4
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-06
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

## Revalidação (spec de mutantes, 988505e)
Delta lido: 988505e, só `tests/mutantes/lote-l08-e7b.json` (+13 -2). O `bin/forge-check` não mudou. Chega aqui pelo merge edd8b6b, sem resolução manual (o `--remerge-diff` sai vazio). Veredito: **aprovado**.

- **M36 equivalente: confere.** O `conferencia_do_head` só é chamado pelo `pr_da_cli` (bin/forge-check:667 e :681). Nos dois caminhos, antes da chamada, o `pr_da_cli` já faz `branch = branch or branch_da_ref(...) or branch_do_sha(...)` com a mesma ref. O `or branch_do_sha` do `conferencia_do_head` (bin/forge-check:757) só roda quando esse resultado é None, e aí repete a mesma busca com as mesmas entradas, que volta None. Tirar o `or branch_do_sha` não muda nada que a linha de comando produza. O motivo escrito na spec está correto. Ficam guardadas as duas buscas reais: com `--base`, pelo M55 (lote-l08-pareceres-da-branch.json); sem `--base`, pelo M56.
- **M56:** guarda a busca da branch pelo sha no `pr_da_cli` sem `--base` (:666), com `ForgeCheck.test_pr_parecer_da_branch_da_ref_vale_sobre_o_de_outra_branch`.
- **Recomendação, sem achado no bloco:** o fallback redundante de :757 pode sair do código numa próxima mudança de `bin/forge-check`, e o M36 junto. Código que nenhum mutante consegue matar é candidato a remoção.

`bin/forge-mutante tests/mutantes/lote-l08-e7b.json`, numa worktree limpa em 988505e: rc=0. M36 equivalente; M37, M50, M51, M52 e M56 mortos.

## Revalidação 0.34 (head 8f22ad3, pedido versao-034, E4)
O L10 é o E4 da versao-034, e por isso o `pedido:` passa a `versao-034` e o `commit:` passa a 8f22ad3. Delta lido: `edd8b6b..8f22ad3`, pela primeira parente. O código e os testes de `bin/forge-check`, `tests/` e `agents/` foram lidos (o `agents/` não muda). Veredito: **aprovado**, sem achado novo.

O que cada commit trouxe:
- 9e2b7be e 944681a: só os pareceres de segurança e de review do L10 (spec 988505e), já lidos.
- 82d1aca e a45fe18: junções da lote-l09 (TEMPO-B1 e a correção das regressões do L08). O `--remerge-diff` sai vazio, sem resolução manual.
- 0e47e06: junção da develop (30b4453, L09 integrado pelo PR #450). Ela traz `pr_da_cli(..., conferir=True)` e o escopo da merge-integracao com `conferir=False` (bin/forge-check:657, :668, :682 e :1396), o lançador `tests/sem_claude_ancestral.py` (TESTES-SEM-CLAUDE-ANCESTRAL, só de teste, sem interruptor em produção), `tests/apoio_conferida.py` com `sem_manutencao`, os testes novos em `test_conf_escopo`, `test_atualizar`, `test_sugerir` e `test_estado_da_branch` e a spec `tests/mutantes/lote-l08-escopo.json`. Esse código tem pareceres próprios na develop. O `--remerge-diff` mostra quatro conflitos de código e teste, todos resolvidos sem perder nenhum dos lados: `bin/forge-testes` mantém `test_qa_lote_l10` (L10); `test_testes_tocados` mantém a contagem 41 (L10); `tests/mutantes/lote-l08-e7.json` M29 e M30 usam o `de:` da develop, que é o texto atual do código; e `test_volta_por_delta` mantém os testes do E14 e a linha `entrega conferida` que a develop pôs em `test_conferencia_reprova_anterior_bloco_e_achado`. Nos pareceres em `docs/` os conflitos ficaram com os dois lados.
- 8f22ad3: move as linhas de `changelog.d/lote-l08.md` para `changelog.d/lote-l10.md`. As cinco linhas são idênticas, só mudam os títulos das seções. O motivo foi o `test_changelog.FragmentoTemONomeDaBranch`.

O E14 continua inteiro. Entre edd8b6b e 8f22ad3, `ETAPA_ABERTA`, `etapas_novas_da_volta`, `fora_do_escopo_da_volta` e as chamadas em `gerar_volta` e `conferir_volta` (bin/forge-check:1844 a :2044) não mudam, e `tests/test_volta_por_delta.py` e `tests/test_qa_lote_l10.py` fora do conflito resolvido também não. O que veio do L09 e da develop mexe em `pr_da_cli` e no escopo da integração, que o E14 não toca. Não há conflito de comportamento entre os dois.

M14: o delta próprio do L10 não muda (138 linhas, A1). O que entrou pelas junções é código já integrado na develop e fica fora da conta do PR do L10 contra `origin/develop`.

Comandos, na worktree em 8f22ad3:
- `python3 -I -m unittest discover -s tests -p test_volta_por_delta.py`: 68, OK. `-p test_qa_lote_l10.py`: 1, OK. `-p test_conf_escopo.py`: 11, OK. `-p test_testes_tocados.py`: 86, OK.
- `bin/forge-mutante tests/mutantes/lote-l10.json`, num clone isolado em 8f22ad3: rev=8f22ad369403, M1 a M13 morreram, rc=0. `bin/forge-mutante tests/mutantes/lote-l08-escopo.json`: M60 e M61 morreram, rc=0.
- Suíte inteira: não foi rodada aqui (D-5). Cito a do push de 8f22ad3 (/tmp/push-l10.log, 2619 testes, OK, Histórico do pedido às 02:21).
