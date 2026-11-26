---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-oraculo-hermetico
commit: 7b2c4cbde05813f9b68efa53cbf39631870b5cc9
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-26
---
# Review: v0481 (E27.6, testes herméticos do oráculo do sempre-atual, volta 1)

Revalidação por delta (H3, R-REVIEW) do 7b2c4cbd, volta 1 do autor (E27.5) sobre o parecer reprovado do 2affeefe (E27.2).

## Parecer

Aprovado. Os três achados da 1ª rodada (A1 bloqueante, A2 e A3 recomendados) estão resolvidos, e o delta não traz achado novo.

- ci: 7b2c4cbde05813f9b68efa53cbf39631870b5cc9 verde

Delta lido: `forge-check parecer delta` deu o intervalo `2affeefe..7b2c4cbd`, com o domínio em `tests/sem_claude_ancestral.py`, `tests/test_oraculo_sempre_atual.py` e `tests/test_sempre_atual.py` (+38 -6, commit 7b2c4cbd). Os commits de parecer do intervalo (c930e8a4 segurança, f4eded88 review) ficam fora do domínio. O restante da branch foi lido na 1ª rodada (2affeefe) e não mudou. Código de produção continua intocado (`bin/` sem diff contra a base 707fea56).

A1 (o `/proc` real sem cobertura) está resolvido pela sugestão (b). `ProcReal.test_proc_real_e_coerente_so_no_nosso_namespace_e_enxerga_um_claude_vivo` chama `fsa.proc_coerente()` e `fsa.processos_de_interesse()` sem dublê, com um `claude` vivo de verdade (link para o Python, cwd numa pasta temporária). A verdade vem à parte: `os.readlink("/proc/self") == str(os.getpid())`, lido no `/proc` literal e não na `PROC` de produção.
- No CI o namespace é o nosso. O oráculo da base já provava isso: rodava `adiado` sobre o `/proc` real e matava o mutante (S1 da 1ª rodada). Com o mutante `PROC = "/proc-nao-existe"`, `proc_coerente()` devolve False contra `nosso` True, e a asserção de `tests/test_sempre_atual.py:103` falha. O mutante morre no CI pelo ProcReal. Isso é dedução do código e do namespace do CI: não houve run do mutante no CI, porque um run pago não se gasta para isso (R-CUSTO).
- No sandbox do Bash (`/proc/self` → 10, pid 3) o teste toma o ramo da dúvida, sem skip. Rodei as sondas no meu clone. `PROC = "/proc-nao-existe"` passa no sandbox, o que é esperado: lá a produção também dá dúvida. `proc_coerente` trocado por `return True` falha (1 falha). Então o teste também não é vazio no sandbox.
- No CI do head, `tests.test_sempre_atual` rodou na `suíte (python 3.12, parte 5/5)`, com 1387 testes OK, e também nas partes do 3.14, todas verdes.
- A asserção de preparo de `vivo()` voltou em `tests/test_oraculo_sempre_atual.py:480`. Ela lê da árvore do teste o `comm`, o `cwd` e o processo vivo, e assim repõe a asserção que a 1ª rodada notou como a única removida.

A2 está resolvido: o "Limite conhecido" do oráculo e o cabeçalho do `test_sempre_atual` agora descrevem a árvore do teste e apontam o `ProcReal`. A3 está resolvido: a mensagem de uso cita `[--proc <pasta>]`, e `--proc` sem pasta ou sem script sai com a mensagem de uso, rc 1, sem IndexError (sondado: `sem_claude_ancestral.py --ate 1 --proc x` → uso, rc=1).

Testes afetados, no sandbox do Bash, no 7b2c4cbd: `python3 -m unittest tests.test_sempre_atual tests.test_oraculo_sempre_atual` → "Ran 202 tests in 339.990s OK". A suíte inteira ficou com o CI.

Guardas mudadas: só `if len(resto) < 3` do lançador de teste, que não é código de controle da classe C (sem mutante declarado, como na 1ª rodada). O ramo de falha foi sondado acima.

CI do PR #922 no 7b2c4cbd: todos os checks concluídos verdes (suíte 3.12 e 3.14 nas 5 partes, instalação, teto de pulados, bateria passos e verificações longas, catraca, árvore já provada), fora `bateria` e `bateria (pareceres)`, que esperam o parecer.
