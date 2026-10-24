---
tipo: review
contrato: 1
pedido: lote-leitura-hook
branch: melhoria/lote-leitura-hook
commit: 0e8776d7b330e57036c6d7684c205e888d058e55
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-24
---
# Review: lote-leitura-hook (revalidação 15, volta H pela opção B da rev14)

Pedido RET-LEITURA-HOOK-H-REV, E1.1. Sou revisor independente e não implementei esta volta (`R-REVIEW`). O parecer anterior (revalidação 14, `reprovado`, A1 bloqueante, A2 e A3 recomendados) está em `72a6b97`, sobre `6d5252d`.

**Delta lido.** O `forge-check delta --parecer docs/reviews/lote-leitura-hook.md` deu `6d5252d..0e8776d`. Os commits do autor são `73aa3c4` (E1 e E2), `f3ff1ef` e `0e8776d` (E3). O merge `fa3a35c` só traz a `develop` (`c96f622`, segundo pai): `git diff fa3a35c^2 fa3a35c` sobre `bin/`, `docs/fechamento-integrador.md`, `tests/test_changelog.py` e `tests/test_fechar*.py` sai vazio. Li inteiro:
- `hooks/_comum.py:1819-1926`: `LancadorDemais`, as duas exceções novas, `separar_lancadores`, `_ler_lancadores` e `_dividir`;
- `hooks/conformidade.py:27-34`, `841-873` (`segmento`) e `1698-1722` (`alvos_de_escrita`), e conferi que `rotulo_na_sessao_do_forge` (`1394`) segue no `except ValueError`;
- `tests/test_hooks.py:3251-3446` (as formas, os testes dos itens 1, 2, 4, 5 e 7 e as mutações), os 11 fixtures `lancador-texto-aberto-*`, `tests/mutantes/lote-leitura-hook.json`, `docs/hooks.md:95` e `changelog.d/lote-leitura-hook.md:15`.

Fica como "já lido" o que vem antes de `6d5252d` (revalidações 1 a 14) e o que o merge traz da `develop` (`bin/forge-changelog`, `bin/forge-fechar`, os pareceres e fragmentos de `changelog-json-link` e `lote-fechar-031`, `docs/fechamento-integrador.md` e os testes deles), revisados nos PRs #319 e #320.

**Critério.** A decisão "B" do dono de 2026-10-24 sobre a rev14 (opção B da proposta `lote-leitura-hook-caminho-rev14.md`, seção 2B, itens 1 a 7, os textos da seção 3.2 e os recomendados da seção 4), as decisões "A" da rev12 e da rev13, que seguem, a decisão "A" de 2026-10-22 (voltas por classe) e o piso da `develop`.

## Achados
- A1 (recomendado) hooks/conformidade.py:1713 · a regra do tee só vê a palavra tee solta: env -uS'"' -S'tee docs/reviews/x.md' dá [] (a develop dava o alvo, e os dois env gravam); sem efeito hoje, porque o PreToolUse recusa a linha e a autoria ausente falha fechado no forge-check pr
- A2 (recomendado) tests/mutantes/lote-leitura-hook.json:4 · o item 7 de B pede os 14 mutantes (M1 a M10 e B1 a B4) e a spec traz 8 pelo teto do forge-mutante; M4 a M8 e M10 caberiam numa segunda spec (cartão MUTANTE-TETO)
- A3 (recomendado) tests/test_hooks.py:3032 · o teto de 60 s das propriedades é tempo de relógio: com carga 12 em 8 núcleos (review, segurança e QA juntos, M6), a da rev13 deu 83,6 s e 74,2 s e falhou, e a nova (linha 3333) deu 56,0 s; medir a CPU do filho tira a instabilidade

## Parecer
**Aprovado.** A volta fecha o A1 da revalidação 14 pela opção B, como o dono decidiu, e cumpre os itens 1 a 6 do critério de fim de B; o 7 fica em parte, pelo limite da ferramenta (A2). Nenhum achado bloqueia. Os três recomendados não devolvem.

**Como a opção B ficou.** Os dois `shlex.split` de `_ler_lancadores` passam por `_dividir` (`_comum.py:1916`). Com `gasto > 0`, isto é, com uma palavra fora da tabela já vista, ele levanta `TextoAbertoComLeituras`, subclasse de `LancadorDemais`. Com `gasto == 0`, levanta `TextoDivididoAberto`, que é `ValueError` e não é `LancadorDemais`. O `gasto` sobe (linha 1895) antes do `_dividir` da leitura adiada (linha 1899), e assim `env -uS'"' cat .env` já cai na recusa. O `-S` certo (linha 1889) usa o mesmo `gasto`, e assim `env -iu -S\' cat .env` também recusa. O `segmento` (`conformidade.py:852`) pega a subclasse antes de `LancadorDemais` e recusa com `barrar`, o motivo da proposta e o `CONTORNO_DO_LANCADOR`. Só `TextoDivididoAberto` vai a `ilegivel`. Não há `except ValueError` genérico no `segmento`, e por isso o teto não é engolido: `env -iS'env -a -b -c ls'` recusa pelo teto (sonda abaixo e `test_texto_dividido_aberto_com_mais_de_uma_leitura_recusa`). No `rotulo_na_sessao_do_forge`, o achado cai no `except ValueError`, como a proposta manda. Em `alvos_de_escrita`, a subclasse vem antes do `except ValueError`, e o teto e a leitura única seguem sem alvo, como antes.

**Prova** (`$TMPDIR/tech-lead-lote-leitura-hook/h/sonda.py`: o `conformidade` sem o marcador, na cópia limpa de `0e8776d` e na `origin/develop` `f142001`, com o mesmo modelo de corpus):

| Texto (sem marcador) | develop | lote |
|---|---|---|
| `env -uS\' cat .env`, `env -uS'"' cat .env`, `env -uS\' rm -rf .git`, `env --spl='"' cat .env`, `env -vuS"'" cat .env` | 2 | 2 (texto que não fecha) |
| `env -iu X env -uS\' cat .env`, `env -iu -S\' cat .env`, `X=1 env -uS\' cat .env` | 2 | 2 |
| `env -aS'"' cat .env`, `env -aS'"' rm -rf .git`, `env -iS'"' cat .env` | 0 | 2 (endurecimento) |
| `env -uS\' cd /tmp/y; rm -rf .git`, `echo ok; env -uS\' true; cat .env` | 2 | 2 |
| `env -uS'"' make`, `env -uS\' echo ok` (FD18) | 0 | 2 (falso positivo registrado) |
| `sudo -x env -S'"' cat .env`, `nice -Z env -S'"' cat .env`, `env -a x -S'"' cat .env` | 0 | 2 (o lançador real falha ou não roda o `cat`) |
| `env -iS'env -a -b -c ls'` | 0 | 2 (pelo teto, não pelo texto aberto) |
| controle: `env -S'"' cat .env`, `env -u X -S'"' cat .env`, `env -i -S'"' cat .env` | 0 | 0 |
| `env -iu X cat .env`, `env -i cat .env` | 2 | 2 |

Nenhuma forma sai 0 no lote e 2 na `develop`. A varredura ampla com a `develop` como oráculo (item 3) é do QA.

**A1, explicação.** A regra do `tee` (`conformidade.py:1713`) segue a letra da seção 2B: cada palavra depois de uma palavra `tee`. Só que o `tee` também pode estar dentro do texto de um `-S` que fecha, ao lado do que não fecha. Em `env -uS'"' -S'tee docs/reviews/x.md'`, a função dá `[]` no lote e `['docs/reviews/x.md']` na `develop`. O `env` do uutils (`/usr/bin/env`) e o GNU (`gnuenv`) gravam o arquivo, conferido em `$TMPDIR`. Não há efeito hoje, por dois motivos. O `PreToolUse` recusa a linha (`TextoAbertoComLeituras`), e o `PostToolUse` não chega a rodar. E a autoria ausente falha fechado: o `forge-check pr` recusa o parecer sem registro do papel. A sugestão é juntar à regra as palavras do texto dividido que fecha. É recomendado.

**A2, explicação.** O item 7 de B pede os mutantes do QA (M1 a M10) e os quatro do item 5. O `forge-mutante` aceita até 8 por spec (`MAXIMO_DE_MUTANTES`, `bin/forge-mutante:43`). O autor declarou B1 a B4, M1, M2, M3 e M9 e escreveu o motivo no commit `f3ff1ef`. O QA da revalidação 14 matou M4 a M8 e M10 com os testes da suíte. Uma segunda spec (por exemplo, `lote-leitura-hook-2.json`) cumpriria o item ao pé da letra, sem mudar a ferramenta. O cartão MUTANTE-TETO está aberto. Como a ferramenta limita e esses mutantes já morreram, fica recomendado.

**A3, explicação.** A spec de B (item 1) pede "abaixo de 60 s, medido". Os testes medem o tempo de relógio do filho (`time.monotonic`). Rodei os 15 testes do lote sob a carga da rodada M6 (load average de 12 a 14, em 8 núcleos). `test_propriedade_sem_marcador_atras_de_lancador_com_opcao_fora_da_tabela`, da rev13 e fora do delta, falhou duas vezes: 83,6 s e 74,2 s para 18 040 formas. Na revalidação 14, com a máquina livre, ele passou. A propriedade nova levou 56,0 s para 49 559 formas, a 93% do teto. O comportamento está certo, e a falha é de carga. Com a M6, essa carga passa a ser o normal da rodada. A sugestão é medir a CPU do filho (`resource.getrusage(RUSAGE_CHILDREN)`), com o mesmo teto, ou levar a propriedade a um alvo lento. Não promovo a bloqueante: o critério pede 60 s medidos, e o teste faz o que o critério pede.

### Revalidação 14: o que fechou
| Achado | Estado | Evidência |
|---|---|---|
| A1 (texto dividido com aspa aberta numa leitura a mais derruba as outras) | fechou, pela opção B | a tabela acima; as 10 formas do item 2 e a variante `env -iu -S\' cat .env` dão 2, e o controle dá 0 |
| A2 (a propriedade amostra as palavras) | fechou na parte da volta | a dimensão nova roda a palavra de 1 caractere sem amostra (o teste afirma 61 × 6 × 4 formas); a amostra antiga vai ao cartão PROP-AMOSTRA, como a seção 4 manda |
| A3 (as exclusões da propriedade não estão escritas) | fechou | `docs/hooks.md:95` traz o texto da seção 3.2 com as duas exclusões |

### Critério de fim da opção B
| Item | Estado | Evidência |
|---|---|---|
| 1. Propriedade da dimensão | verde | `test_propriedade_leitura_a_mais_que_falha_nao_tira_recusa`: 49 559 formas em 56,0 s; cada grupo de 1 caractere de `[A-Za-z0-9]` sem amostra; os grupos de 2 com amostra (um em 3), que o "Tempo" de B permite; o `-S` certo depois de cada palavra de 1 caractere fora da tabela; os prefixos de `--split-string`; depois de `NOME=valor`, de `-i` e atrás de `env -iu X`; cada lançador; os corpos `make` e `echo ok` pelo motivo |
| 2. Fixtures `-bloqueia` | verde | os 11 fixtures `lancador-texto-aberto-*`, o do FD18 incluído; `TEXTO_ABERTO_RECUSA` e o controle no teste do item 2; o alvo do `tee` em `alvos_de_escrita` |
| 3. Varredura com a `develop` | do QA | a sonda acima não acha regressão |
| 4. Sonda viva | verde | `test_sonda_viva_do_texto_dividido_aberto`, com cada `env` da máquina |
| 5. Mutações | verdes | as quatro de B, cada uma numa cópia limpa (`test_mutacoes_do_texto_dividido_aberto_ficam_vermelhas`) |
| 6. Caminho com o marcador | verde | `test_propriedade_do_alfabeto_de_opcoes_do_lancador`, `test_mutacoes_do_lancador_ficam_vermelhas` e `test_propriedade_do_lancador_que_divide_texto_com_marcador` passaram; o corpus e o T9b, pelo pre-push da entrega (suíte completa) |
| 7. Spec de mutantes | em parte | 8 de 14 (A2) |
| Textos da seção 3.2 | literais | os três trechos e o FD17 aparecem uma vez cada, na ordem (FD17, FD18, `$'…'`), e a frase antiga das provas saiu (comparação por script) |
| Fragmento | certo | `changelog.d/lote-leitura-hook.md:15`, com o FD18 e o contorno |
| Commits | limpos | Conventional Commits em português, com a classe e o critério; o merge da `develop` sem reescrever |

### Fora do bloco
- **Testes que rodei**, na cópia limpa (`git archive 0e8776d`, em `$TMPDIR/tech-lead-lote-leitura-hook/h/lote`): os 5 testes novos e 10 testes da rev12 e da rev13 do lançador, com `Ran 15 tests in 438.603s`, `FAILED (failures=1)`. A única falha é o tempo do A3. Rodei de novo os dois testes de propriedade: o da rev13 falhou outra vez pelo tempo (74,2 s), e o novo passou. A suíte completa não rodou, porque o brief limita a execução aos testes do lote.
- **Teto M14:** não vale para o `lote-leitura-hook` (decisão M14).
- O Forge não tem `docs/engineering/praticas.md`, então não há regra de ferramenta nem de leitura a citar. O PA-7 (`docs/engineering/achados-recorrentes.md`) está sem linhas, e não há item a conferir.
- **Pendência do quadro, para o Jarvis:** a seção 4 da proposta manda o resto do A2 do review ao cartão PROP-AMOSTRA e o A2 da segurança ao ENV-S-OPCAO. Nenhum dos dois aparece em `docs/kanban/historico.md`, onde estão ENV-CD-FORGE e MUTANTE-TETO.
- **Segurança:** é do E2.1 e não foi refeita aqui. O A1 vai como nota ao `security-engineer`: hoje não tem gatilho, mas depende de o `PreToolUse` recusar a linha.
