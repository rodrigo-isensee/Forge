---
tipo: revisao-seguranca
contrato: 1
pedido: v046
branch: melhoria/v046-mutacao-bench
commit: 203e3554785746c600bd590fddb807d930eaa7a2
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-12
---
# Review de segurança: v046 (E7.15, melhoria/v046-mutacao-bench, revalidação por delta)

Delta revisado: `135b20d2..203e3554` (volta E7.13: texto de `agents/qa-engineer.md`, `agents/tech-lead.md` e `skills/qa-testing/SKILL.md` enxugado para caber nos orçamentos; `apoio` renomeado para `apoio_mudado` em `bin/forge-mutante:829-835`; `de` do M5, M16 e M17). Rodada anterior: E7.11 (`135b20d2`, aprovado), cujo delta foi `e452582f..135b20d2`. `forge-check parecer delta`: no domínio `bin/forge-mutante`, `agents/qa-engineer.md`, `agents/tech-lead.md` e `skills/qa-testing/SKILL.md`; specs, `tests/test_forge_mutante.py` e o fragmento do changelog lidos como apoio. Nada em `.github/` nem em `.githooks/`. Rodadas anteriores: E7.3 (`60bba369`, reprovado pelo A1), E7.7 (`e452582f`, aprovado com A2 e A4 recomendados) e E7.11 (`135b20d2`, aprovado com A5 recomendado).

## Gatilhos
Controle do Forge (`R-SEGURANCA`): `bin/forge-mutante --base` decide quais mutantes rodam na revalidação do QA (portão `R-QA`).

## Achados
- A1 (recomendado) bin/forge-mutante:800 · resolvido em e452582f (spec, arquivo e módulo do teste); sem regressão no delta.
- A2 (recomendado) skills/qa-testing/SKILL.md:96 · resolvido em 135b20d2 e mantido no enxugamento de 203e3554: SKILL:96, agents/qa-engineer.md:20 e agents/tech-lead.md:25 citam a --base <head aprovado> da volta, a linha base= e placar e bench só por versão (tech-lead.md:41).
- A3 (recomendado) bin/forge-changelog:222 · resolvido em e452582f (shlex.quote na tag); fora do delta.
- A4 (recomendado) bin/forge-mutante:810 · resolvido em 135b20d2 para helper, conftest, fixture de dado e pasta nova em tests/: a S2 da E7.7 refeita sai `apoio de teste no diff`, M1 sobrevive, rc 1 (S1 a S3).
- A5 (recomendado) bin/forge-mutante:812 · helper dentro de tests/test_*.py importado por outro teste (padrão da suíte: 66 arquivos importam de 22 test_*.py) fica fora do apoio; esvaziado, M1 sai fora do diff e a dirigida sai 0 (S5). Idem com tests/mutantes/*.py (S6).

## Sondas
- S1 · tests/apoio.py importado por tests/test_lib.py trocado por `return None`, outro.py mudado; `forge-mutante spec --base <base>` · espera: apoio no diff, M1 sobrevive, rc 1 · obtido: `apoio de teste no diff: tests/apoio.py`, `M1 · sobreviveu`, rc 1
- S2 · o mesmo com tests/conftest.py · espera: M1 roda e sobrevive · obtido: `apoio de teste no diff: tests/conftest.py`, `M1 · sobreviveu`, rc 1
- S3 · o mesmo com pasta nova tests/novo/apoio.py e com o dado tests/fixtures/d.json lido pelo helper · espera: M1 roda · obtido: as duas saem `apoio de teste no diff`, `M1 · sobreviveu`, rc 1
- S4 · `python3 -m unittest tests.test_forge_mutante.MutacaoDirigida` em 135b20d2 · espera: OK · obtido: `Ran 8 tests`, OK
- S5 · helper em tests/test_comum.py importado por tests/test_lib.py trocado por `return None`, outro.py mudado (M2 com teste que o mata) · espera: M1 roda e sobrevive · obtido: `fora do diff: M1 · lib.py`, `M2 · morreu`, rc 0
- S6 · o mesmo com o helper em tests/mutantes/apoio.py · espera: M1 roda · obtido: `fora do diff: M1 · lib.py`, rc 0
- S7 · `python3 -m unittest tests.test_orcamento_instrucao tests.test_metricas_texto tests.test_forge_mutante.MutacaoDirigida` em 203e3554 · espera: OK · obtido: `Ran 18 tests`, OK

## Detalhe dos achados
**Delta E7.15** (`135b20d2..203e3554`) · Nenhuma regra de segurança nem citação de ID saiu: os IDs `R-*` de `agents/qa-engineer.md`, `agents/tech-lead.md` e `skills/qa-testing/SKILL.md` são os mesmos antes e depois (comparação por arquivo); da skill sai só a etiqueta `BENCH-POR-RELEASE` (e `M-5`), que segue em `agents/tech-lead.md:41`. Ficam no texto: um mutante por linha de guarda mudada e a falta dele como achado do QA (`qa-engineer.md:20`, SKILL:93-94), sobrevivente bloqueia (SKILL:97), prazo, erro de carga e processo que cai como "sem veredito" (SKILL:96), `--processos` dentro da trava (`R-TETO`), nenhum hook, pre-push nem CI chamando a `--cobertura` (SKILL:95). O enxugamento tirou da skill a frase "a 1.ª rodada é a spec inteira" e "contra o head aprovado" ao lado de `base=`; as duas seguem no `--help` (`bin/forge-mutante:21-23`), e o texto ainda amarra a `--base` ao head aprovado e só à volta, então não vira achado. Em `bin/forge-mutante` o delta é só o nome: `apoio_mudado` deixa de sombrear o módulo global `apoio` (`:92`) dentro de `dirigir`, sem mudar ramo; os `de` de M5, M16 e M17 aparecem uma vez cada no arquivo (AR-12).

**A2** (resolvido) · `skills/qa-testing/SKILL.md:97`, `agents/qa-engineer.md:20`, `agents/tech-lead.md:26` e `:42`. A ligação `--base` = head já aprovado, com a conferência da linha `base=`, está onde o QA a lê; a decisão do dono de 2026-11-12 11:06 (placar e bench uma vez por versão, dirigida sem aumentar o CI do PR) está citada nos três textos. Nenhum hook, pre-push nem workflow chama a mutação no delta.

**A4** (resolvido no que pedia) · `bin/forge-mutante:806-812` (`apoio_de_teste`) e `:829-835`. A correção mínima da E7.7 foi aplicada como pedida: arquivo de `tests/` fora de `test_*.py` e de `tests/mutantes/` põe todos os mutantes no diff, com a linha `apoio de teste no diff: <arquivos>` na saída que o QA cola. A sonda S2 da E7.7 virou `tests/test_forge_mutante.py:1294`, e `:1310` guarda o contrário (teste e spec de outro mutante não põem todos). M16 a M20 em `tests/mutantes/v046-mutacao-bench-3.json` e o `de` atualizado do M5 batem com o texto de `135b20d2`, cada `de` uma vez só no arquivo (AR-12 conferido). Renomear ou apagar o helper aparece nos dois nomes por causa do `--no-renames`.

**A5** · evidência: `bin/forge-mutante:812` exclui do apoio todo `test_*.py`, e `:811` toda a pasta `tests/mutantes/`; o `--help` (`:19-21`) diz "helper importado ... põe todos no diff", o que não vale para helper que mora num `test_*.py`. Na suíte do Forge esse é o padrão comum: 66 arquivos de `tests/` importam de 22 módulos `test_*.py` (por exemplo `tests/test_acao_da_reprovacao.py:10` importa de `test_voltas`; `tests/apoio_volta_unica.py:23-24`, de `test_forge` e `test_hooks`). Caminho de ataque: o autor, entre o head aprovado e a revalidação, esvazia uma asserção numa função de um `test_*.py` usada pelo teste que mata um mutante cujo arquivo não muda, e mexe em outro arquivo da spec; a dirigida sai 0 (S5). É a classe do AR-3 (lista negativa em trava): a exclusão de `test_*.py` serve ao legítimo (mudar o teste de outro mutante não deve rodar tudo), mas cobre também o helper. Por que não bloqueia: o motivo que manteve o A4 recomendado na E7.7 continua (o `test_*.py` mudado aparece no delta que review, segurança e QA leem na mesma volta), a 1.ª rodada do QA é a spec inteira e a mutação não roda no CI do PR. Severidade: baixa. Correção mínima: em `apoio_de_teste`, tratar como apoio o `tests/test_*.py` mudado que outro arquivo de `tests/` importa no `rev` (`import <stem>`, `from <stem> import`, `from tests.<stem> import`, `from tests import <stem>`), e restringir a exclusão de `tests/mutantes/` a `*.json`; ajustar a frase do `--help` (`:19-21`, AR-9); um teste em `MutacaoDirigida` por caminho (S5 e S6) e um mutante por guarda nova na spec. Esforço: P. Dono: `tech-lead`. Pode ir para a versão seguinte, como o delta já prevê.

Conferência PA-7 (`docs/engineering/achados-recorrentes.md`): AR-3 é a classe do A5 (inalterado no delta E7.15, segue recomendado para a versão seguinte); AR-5 e AR-7 não se aplicam (nenhum `python` nem `git` novo no delta); AR-9 conferido no `--help` (`:19-23`, sem mudança); AR-12 conferido (M5, M16 e M17 em 203e3554).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Testes dos arquivos tocados rodados em `203e3554` numa worktree destacada: `tests.test_orcamento_instrucao`, `tests.test_metricas_texto` e `tests.test_forge_mutante.MutacaoDirigida`, 18 testes, OK (S7); na E7.11, `MutacaoDirigida` em `135b20d2`, 8 testes, OK; sondas S1 a S6 rodadas com a fixture de `MutacaoDirigida` numa worktree destacada, sem escrita na worktree do autor. O tempo do `test_forge_mutante` (75 s antes, 70 s depois) e a mutação fora do CI do PR são medida do QA; o delta não toca `.github/` nem `.githooks/`. Ferramentas ausentes no PATH (lacuna, não instaladas): gitleaks, semgrep, zizmor, actionlint; o delta não toca workflow nem traz segredo à leitura.
