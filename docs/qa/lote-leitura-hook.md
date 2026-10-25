---
tipo: qa
contrato: 1
pedido: lote-leitura-hook
branch: melhoria/lote-leitura-hook
commit: 0e8776d7b330e57036c6d7684c205e888d058e55
parecer: reprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-24
---
# QA: lote-leitura-hook (revalidação 15: opção B da rev14, texto dividido que não fecha aspas recusa com mais de uma leitura)

Pedido RET-LEITURA-HOOK-H-REV, E3.1, em paralelo com o review e a segurança (decisão ACELERA-RODADA "A", item 4). Sem especificação de UX: as obrigações são as decisões do dono em `RET-LEITURA-HOOK-H` (opção B da proposta `lote-leitura-hook-caminho-rev14`, itens 1 a 7 do critério de fim da seção 2.B, os textos da seção 3.2 e os recomendados da seção 4). O código testado é o de `0e8776d`; `hooks/` muda em `_comum.py` e `conformidade.py` (42 linhas) contra `6d5252d`. Tudo foi rodado em cópias por `git archive` em `$TMPDIR/qa-engineer-lote-leitura-hook/v15/` (`lote` = `0e8776d`, `base` = `ba57c0b`, a develop). O parecer anterior (revalidação 14) é de `6d5252d`.

## Achados
- A1 (bloqueante) tests/test_hooks.py:3422 · classe "regra do lote sem teste que a guarde" (requisito da seção 2.B da rev14, "toma como alvo cada palavra depois de um `tee` da parte"): os mutantes X5 (só a primeira palavra depois do `tee` é alvo) e X6 (a opção do `tee` entra como alvo) em `hooks/conformidade.py:1714` sobrevivem à suíte inteira, porque os testes do alvo (`tests/test_hooks.py:3358` e `:3422`) só usam um `tee` com um alvo e sem opção; o código está certo (sonda abaixo: `env -uS\' tee -a docs/qa/y.md z` dá os dois alvos, sem o `-a`), falta o teste e a linha na spec de mutantes; correção só de teste
- A2 (recomendado) tests/mutantes/lote-leitura-hook.json:1 · a spec do autor (B1 a B4, M1, M2, M3, M9: 8 de 8, no teto) não tem mutante para duas linhas de guarda do diff: o `except TextoDivididoAberto` (`hooks/conformidade.py:859`, mutante X3, "uma leitura só vira recusa") e o `gasto` do texto dividido adiado (`hooks/_comum.py:1899`, X1); os dois morrem (saída abaixo), então é só lista incompleta; trocar M1/M2 (mutantes das voltas anteriores, que os testes da volta também matam) por X1 e X3 cabe no teto
- A3 (recomendado) docs/hooks.md:95 · a promessa "ler a mais não esconde alvo" vale para o texto que não fecha e não para o teto: `env -a -b -c -d tee docs/qa/t.md` não dá alvo em `alvos_de_escrita` (o teste `tests/test_hooks.py:3248` fixa isso); só afeta a autoria, não a recusa (a linha recusa); registrar no texto ou dar o alvo como no `TextoAbertoComLeituras`

## Critério → teste → resultado
| Critério (RET-LEITURA-HOOK-H, seção 2.B da rev14) | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| 1. Propriedade "leitura a mais que falha não tira recusa": toda forma com palavra fora da tabela antes do texto que não fecha dá 2, qualquer que seja o corpo; `env -S<F> C` sem palavra fora da tabela fica como hoje | `test_propriedade_leitura_a_mais_que_falha_nao_tira_recusa` (49 559 formas, 28 s); varredura deste QA com a develop como oráculo (`varrer.py`) | fragmentos `'`, `"`, `'"`, `"'`, `x'`, `' y`; grupo de 1 e 2 letras; `-S` certo depois de palavra fora da tabela; outros lançadores; corpos `make` e `echo ok` | passou |
| 2. Fixtures `-bloqueia` (as formas do bug 3, `env -iu -S\' cat .env`, `-aS'"'`, `-iS'"'`; falso positivo FD18 `env -uS'"' make`; controle `env -S'"' cat .env` sai 0; alvo de `tee`) | `test_texto_dividido_aberto_com_mais_de_uma_leitura_recusa`, `Hooks.test_fixtures` (11 fixtures `lancador-texto-aberto-*`) | `gasto` 0 contra 1 ou mais; o controle de uma leitura só | passou |
| 3. Varredura com a develop como oráculo, 0 regressões, com e sem aspa aberta | `varrer.py` (2502 formas) e `varrer2.py` (49 888 formas), no mesmo processo, `decidir_na_guarda` de cada árvore | grupos com `u`, `C`, `i`, `v`, `a`, `f`, `0`, `Z`; `env -iu -S`, `env <w> -S`, `env -S'env -…S…'`, `sudo`, `nice` na frente | passou (0 e 0; endurecimentos 554 e 20 580) |
| 4. Sonda viva, sem rede: o `env` da máquina imprime o `.env` falso em `env -uS\' cat .env` e não roda nada em `env -S'"' cat .env` | `test_sonda_viva_do_texto_dividido_aberto` e sonda deste QA | rc e saída do `env` real (GNU 9.7 e uutils 0.8.0) | passou |
| 5. Mutações: achado a `ilegivel` (B1), só a falha do `-S` adiado (B2), recusar com `gasto == 0` (B3), sem a regra do `tee` (B4) | `test_mutacoes_do_texto_dividido_aberto_ficam_vermelhas` e `forge-mutante` deste QA | as quatro linhas de guarda | passou (B1 a B4 morreram) |
| 5a. Detalhes da regra do `tee` (várias palavras, opção do `tee`) | nenhum | mais de um alvo; opção que não é alvo | **falhou** (A1: X5 e X6 sobrevivem) |
| 6. O caminho com o marcador não muda | `test_corpus_nos_dois_hooks`, `Hooks.test_fixtures`, alfabeto com marcador (dentro de `tests.test_hooks`, 91 testes) | `CorpusHeredocVoltaUnica`, `parecer` e `conformidade` | passou |
| 7. Spec de mutantes `tests/mutantes/lote-leitura-hook.json` (A4 do QA da rev14) | `test_spec_de_mutantes_do_lote_e_valida` e `forge-mutante` | spec válida (1 a 8 mutantes, `de` aparece uma vez no arquivo) | passou (A2: lista incompleta nas linhas 859 e 1899) |
| Texto de `docs/hooks.md` (seção 3.2: texto da linha 95, as provas, FD17 e FD18) | conferência por `grep` (cada âncora aparece uma vez) | `critério mudou: RET-LEITURA-HOOK-CAMINHO-REV14` presente | passou |
| Recomendados da seção 4 (A3 do QA da rev14 em FD17 e FD18; A4 na spec) | conferência: FD17 (`env -Z echo cat .env`, `sudo -i echo cat .env`, `xargs -p`, `timeout -Z 5`) e FD18 no texto | contorno escrito | passou |

## Cenários e resultado real
- **Bug `lote-leitura-hook-3`, formas relatadas e variantes, ponta a ponta** (`python3 hooks/conformidade.py` com a entrada JSON do Claude Code, repositório temporário do `Fixture`, `HOME` limpo; `v15/sonda.py`, `f1.log`; rc develop / lote). Todas dão 2 no lote: `env -uS\' cat .env` (2/2), `env -uS\' rm -rf .git` (2/2), `env -uS'"' cat .env` (2/2), `env -vuS"'" cat .env` (2/2), `env --spl='"' cat .env` (2/2), `env -iu X env -uS\' cat .env` (2/2), `env -CS\' cat .env` (2/2), `env -iu X env -iu -S\' cat .env` (2/2), `sudo -Z env -uS\' cat .env` (2/2), `env -uS\' cd /tmp/y; rm -rf .git` (2/2). A variante que a rev14 chamou de a que escapa, `env -iu -S\' cat .env`, dá 2 (2/2). Passam de 0 para 2 (endurecimento): `env -aS'"' cat .env`, `env -aS'"' rm -rf .git`, `env -iS'"' cat .env`, `env X=1 -uS\' cat .env`, `env -iu X -S\' cat .env`, `env -Z -S"'" cat .env`, `nice -Z env -S\' cat .env`, `env -iu -S'env -a -b -c ls'` (o texto dividido com K+1 palavras: o teto não é engolido) e `env -iS'env -a -b -c ls' ls`. Controles: `env -S'"' cat .env`, `env -S\' cat .env`, `env -u X -S\' cat .env`, `env -S'"' -iu X cat .env` saem 0/0 (uma leitura só, o `env` falha ao dividir, como na develop); `env -u X cat .env`, `env -S'cat .env'`, `env -i cat .env`, `env cat .env`, `cat .env`: 2/2; `env -iu X ls` e `env -u X ls`: 0/0. Falso positivo registrado (FD18): `env -uS'"' make` e `env -uS\' ls` saem 2 (develop: 0), com o contorno `env -u X make`.
- **O bug `lote-leitura-hook-3` fecha?** Sim: as formas relatadas e as variantes da classe saem 2, e a varredura contra a develop tem 0 regressões. Bug fechado (estado atualizado no arquivo do bug); o bug `-2` (a classe maior) também.
- **Varreduras contra a develop** (mesmo processo, `decidir_na_guarda` de cada árvore, hooks de `ba57c0b` e de `0e8776d`). Com aspa aberta, `varrer.py` ampliada: grupos `-{"", u, C, iu, vu, iC, a, f, 0, Z, ui, uv, ivu, -, uC}S` com 9 fragmentos de aspa, `env -iu -{g}S…`, `env -{g} -S…`, `env -Z -S…`, `env -a -S …`, `env A=1 -iu -S…`, `sudo -Z env …`, `nice -Z env -S…`, `env -S'env -{g}S… C'`, dois corpos: 2502 formas, **0 regressões**, 554 endurecimentos; as 140 que o lote ainda libera são só `env [X=1|-|-0|--] -S<aspa aberta> C` e variantes com `--split-string`, `-0` ou o `-S` depois de `--` (uma leitura só, o `env` falha; a develop também liberava) e as de crase (`-S\``, que não é aspa, igual à develop). Sem aspa aberta, `varrer2.py` (12 lançadores, `-`+0x21..0x7E, pares e trios de letras, abreviações longas, encadeados): 49 888 formas, **0 regressões**, 20 580 endurecimentos, 0 rc fora de 0 e 2, 101 s.
- **Os dois hooks, com o marcador** (`f2.log`): `env -uS\' gh pr merge 5`, `env -iu -S\' gh pr merge 5`, `env -aS'"' gh pr merge 5` e `env -S'"' gh pr merge 5` saem 2 no `parecer` e no `conformidade` (develop: 0, como na volta G); o controle `env -u X gh pr merge 5` sai 0/0. `env -uS\' tee .forge/versao` sai 2/2 no `conformidade`.
- **Alvos de escrita** (`alvos_de_escrita`, módulo do lote): `env -aS'"' tee docs/reviews/x.md`, `env -iu -S\' tee docs/qa/x.md; echo ok`, `sudo -Z env -iS'"' tee docs/security/a.md` e `env -uS\' tee -a docs/qa/y.md z` dão os alvos (a opção `-a` fora); `env -S'"' tee docs/qa/x.md` e `env -a -b -c -d tee docs/qa/t.md` dão `[]` (uma leitura só, como na develop; e o teto, A3).
- **Sonda viva** (hooks desligados, `.env` falso `SEGREDO_FALSO=abc123` em pasta do `$TMPDIR`, `HOME` no `$TMPDIR`, sem rede; `v15/viva/`): uutils 0.8.0 (`/usr/bin/env`) imprime o `.env` em `-uS\' cat .env`, `-aS'"' cat .env` e `-iS'"' cat .env`, e falha ao dividir em `-S'"' cat .env` e em `-iu -S\' cat .env`; GNU 9.7 (`/usr/bin/gnuenv`) imprime o `.env` em `-uS\' cat .env`, `-iu -S\' cat .env` e `-aS'"' cat .env`, e falha ao dividir em `-S'"' cat .env` e `-iS'"' cat .env`. As formas que o lote recusa rodam de verdade em ao menos um `env`.
- **Vermelho antes do verde.** `forge-testes --vermelho 6d5252db2c3799d8114fb432647d4ae0dfcb5109` (a base da volta H), no HEAD limpo: `rc=2`, "test_hooks · sem veredito (prazo, sinal ou executor sem registro em B)"; contagem: `não prova (passa na base)=1877; prova (asserção)=16; pulado=1; sem veredito=1`; o módulo `test_hooks` (91 testes, 582 s de relógio no meu ambiente) não cabe no prazo do `forge-testes`, e a saída 2 não vale como vermelho. Forma manual (`hooks/_comum.py` e `hooks/conformidade.py` de `6d5252d` sobre os testes de `0e8776d`, `v15/verm/`, `verm1.log`): `Ran 5 tests in 170.612s`, `FAILED (failures=4)`. Caem na base `test_propriedade_leitura_a_mais_que_falha_nao_tira_recusa` (`AssertionError`), `test_texto_dividido_aberto_com_mais_de_uma_leitura_recusa` (`AssertionError: 0 != 2 : o conformidade libera "env -uS\\' cat .env"`), `test_mutacoes_do_texto_dividido_aberto_ficam_vermelhas` (`[0, 0, 0] != [2, 2, 0]`) e `test_spec_de_mutantes_do_lote_e_valida` (`0 != 1 : B1`); `test_sonda_viva_do_texto_dividido_aberto` passa na base (só prova o `env` da máquina, que não depende do hook).
- **`forge-mutante` sobre `tests/mutantes/lote-leitura-hook.json`** (spec do autor, cópia limpa, `rev=0e8776d7b330`):
```
forge-mutante: pedido=lote-leitura-hook rev=0e8776d7b330 spec=55a5496ca95f498d3b79d2283ce68fd313127927db8353e955e381aea2d54df2
B1 · morreu · hooks/conformidade.py:853
B2 · morreu · hooks/_comum.py:1889
B3 · morreu · hooks/_comum.py:1923
B4 · morreu · hooks/conformidade.py:1714
M1 · morreu · hooks/_comum.py:1896
M2 · morreu · hooks/_comum.py:1897
M3 · morreu · hooks/_comum.py:1893
M9 · morreu · hooks/conformidade.py:856
rc=0
```
  Conferência da lista contra o diff: as linhas de guarda mudadas são o `except TextoAbertoComLeituras` (B1), o `_dividir` do `-S` certo (B2), o `if gasto` (B3), o ramo do `tee` (B4), o `_dividir` do texto adiado (coberto só por M2, que tira a leitura inteira) e o `except TextoDivididoAberto` (sem mutante). Para as duas últimas somei a lista do QA (`v15/mutx.json`, testes do lote), com um mutante por linha e o `tee` em duas formas:
```
forge-mutante: pedido=lote-leitura-hook-h-qa rev=0e8776d7b330 spec=e26e1f00d5deddae8979b0fd802efc481d3da3b4b6a6b6acf4eb91b5cc2155d0
X1 · morreu · hooks/_comum.py:1899      (o texto dividido adiado usa gasto 0)
X2 · morreu · hooks/_comum.py:1923      (a fronteira `if gasto > 1`)
X3 · morreu · hooks/conformidade.py:859 (uma leitura só passa a recusar)
X4 · morreu · hooks/_comum.py:1924      (o achado vira `LancadorDemais` e some do alvo do `tee`)
X5 · sobreviveu · hooks/conformidade.py:1714 (só a primeira palavra depois do `tee`)
X6 · sobreviveu · hooks/conformidade.py:1714 (a opção do `tee` entra como alvo)
rc=1
```
  X5 e X6 sobrevivem com os testes do alvo de escrita, e a suíte inteira só tem estes (`grep alvos_de_escrita tests/`): A1.
- **Testes do lote, rodados por este QA** (cópia `v15/lote`, módulo inteiro como o brief manda; a suíte completa roda uma vez no pre-push, ACELERA-RODADA "A", item 1): `python3 -m unittest tests.test_hooks`: `Ran 91 tests in 581.990s`, `OK` (`[propriedade do texto aberto] 49559 formas em 28.0 s`, `[T] pior tempo de decisão: 0.42 s`). `scripts/validar-plugin.sh` sobre a branch: `Validation passed`.
- **PA-7** (`docs/engineering/achados-recorrentes.md`): sem linhas ("nenhum ainda"); nada a conferir.

## Riscos
- O único bloqueante é de teste, não de comportamento: o código da regra do `tee` está certo nas sondas; falta o teste com dois alvos e com opção, e a linha na spec. A correção é só de `tests/`, e não toca `hooks/`.
- A promessa de `docs/hooks.md:95` ("recusam se qualquer leitura recusa") e o texto da seção 3.2 fecham: a classe "lançador que divide texto" tem agora uma regra só (recusa com mais de uma leitura e texto que não fecha), com a construção como oráculo; 0 regressões em 52 390 formas contra a develop, nas duas famílias.
- `forge-testes --vermelho` não dá veredito para `tests.test_hooks` (prazo; o módulo leva cerca de 580 s sob a carga desta máquina): a prova do vermelho saiu pela forma manual. Se o prazo é do `forge-testes`, vale cartão (melhoria vista abaixo).
- O falso positivo FD18 (`env -uS'"' make`, `env -uS\' ls`) é o custo aceito pelo dono na opção B; ele está no texto, com contorno, e as sondas vivas mostram que o `env` real falha ou roda nas formas recusadas.
