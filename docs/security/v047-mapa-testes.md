---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-mapa-testes
commit: 477dbefe80ed35a590dc2f689eea32cd39177fcd
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-14
---
# Review de segurança: v047 (mapa de testes, E1.253)

Intervalo `origin/develop` (c5c3a449) `..477dbefe`: `bin/forge-testes` (`quem_importa`, `IMPORTAVEL`, `APOIO_NA_COMPLETA`, `VARRE_TESTS`), `tests/test_testes_tocados.py` (classe `QuemImporta`), duas specs de mutantes e o fragmento do changelog. Parecer aprovado, com duas recomendações.

## Gatilhos
`R-SEGURANCA`: a entrega mexe na escolha de testes do envio local, vizinha dos controles do Forge (`R-VERIFY`, M8). Não há analisador de entrada não confiável nem hook novo: a entrada de `quem_importa` é o texto dos próprios módulos de `tests/`, escrito por quem já tem escrita na branch.

## Achados
- A1 (recomendado) bin/forge-testes:232 · APOIO_NA_COMPLETA deixa tests/guarda_git.py ir ao dirigido, mas bin/forge-check:1138 (CODIGO_EM_TESTS) o lista como código de portão junto da catraca e da neutralidade; alinhar as duas listas numa fonte só ou acrescentá-lo aqui
- A2 (recomendado) bin/forge-testes:229 · o desenho do adendo 2 (fora do repo) registrou tests/apoio_*.py sem regra pela decisão 7 do dono; a leitura literal se mantém (módulo de teste no diff segue na completa), mas a mudança vira essa leitura: citar no PR e avisar o dono pelo Jarvis (R-DECISAO)

## Sondas

## Detalhe dos achados
**Ponto pedido pelo brief (opção C da M8, decisão 7 do dono).** A decisão M8 do dono (2026-10-24) diz que o envio de `melhoria/*` roda só os testes afetados, que caminho sem regra cai na suíte completa e que a bateria completa segue no CI de todo PR para `develop`, `homolog` e `main`. A opção C acrescenta que todo **módulo de teste** no diff roda a suíte inteira. A decisão 7 do estudo-custo-suite (2026-11-07 21:21, "Não, por ora") recusou a F3: levar módulo de teste no diff ao dirigido. Conferido no head:
- módulo de teste no diff segue na completa: `IMPORTAVEL` exclui `test_` (`bin/forge-testes:231`), e `planejar(["tests/test_hooks.py"])` devolve `("completo", ["tests/test_hooks.py sem mapa"])`;
- o próprio script já trata os apoios da raiz de `tests/` como produção, e não como teste (`bin/forge-testes:82`, no `--vermelho`), e `TESTE_DO_DIFF` (`bin/forge-testes:84`) não os inclui;
- o efeito é só local: o envio leve não roda teste (`.githooks/pre-push:402`), o `afetados` é opt-in (`.githooks/pre-push:584`), e `scripts/conferir-reversao.py` usa o plano como aviso, não como portão (docstring, linha 14). Nenhum workflow do CI chama o `forge-testes` para escolher testes; a suíte inteira no CI do PR continua obrigatória para o merge.

Do lado da segurança, não há caminho de ataque: quem enfraquece um apoio para escapar de teste local ainda passa pela suíte inteira no CI, e nenhum portão usa o plano dirigido. O que muda é governança, e por isso o A2 não bloqueia. O texto do desenho do adendo 2 (seção 3) diz que mapear apoio "afrouxa a opção C da M8" e que "isso é do dono". A leitura do código (apoio é produção; a opção C fala de módulo de teste) sustenta a entrega, mas contraria o registro. O teste que guardava essa leitura (`test_promover_e_apoio_seguem_na_completa`, com `tests/apoio_volta_unica.py`) foi trocado por `test_promover_e_portoes_de_tests_seguem_na_completa` (`tests/test_testes_tocados.py:165`). Correção mínima: o PR cita o argumento da E1.253 e esta leitura, e o Jarvis registra a mudança ao dono, sem pergunta nova se ele já a tiver como técnica. Esforço P. Dono: `tech-lead` (PR) e Jarvis (registro).

**A1.** Evidência: `bin/forge-testes:232` lista só `tests/catraca.py` e `tests/neutralidade.py`; `bin/forge-check:1138` define `CODIGO_EM_TESTS = (tests/catraca.py, tests/neutralidade.py, tests/guarda_git.py)` como "código do portão que mora em tests/". O `guarda_git` protege o `.git/config` comum do clone real contra mudança durante os testes (identidade e configuração; ver a docstring dele). Sondado: `planejar(["tests/guarda_git.py"])` dá dirigido com 48 módulos, entre eles `test_guarda_git` e `test_suite_paralela`, que o exercitam. Por isso não é defeito provado: um enfraquecimento dele cai no teste dele mesmo, e o CI roda tudo. Caminho de ataque: nenhum realista além do que o CI já cobre. Severidade: baixa (consistência entre duas listas do mesmo conceito). Correção mínima: acrescentar `tests/guarda_git.py` a `APOIO_NA_COMPLETA` ou derivar as duas de uma fonte só. A lista completa a cobrir é: `tests/catraca.py`, `tests/neutralidade.py` e `tests/guarda_git.py`. Esforço P. Dono: `tech-lead`.

**Outras dimensões conferidas, sem achado.**
- Hooks: `quem_importa` só acrescenta módulos ao plano dos hooks. Comparando base e head para todo `hooks/*.py`, o plano só cresce (`_comum`, `agentes`, `pesado`), e nenhum hook passa de completo para dirigido.
- Apoios: os 12 apoios da raiz (`ambiente_git`, `apoio_conferida`, `apoio_forge_check_rapido`, `apoio_jarvis`, `apoio_regra_id`, `apoio_sandbox`, `apoio_versao_defasada`, `apoio_volta_unica`, `gh_falso`, `guarda_git`, `modelo_git`, `sem_claude_ancestral`) passam de completo para dirigido. O `ambiente_git` alcança os módulos de `tests/evals/`, que é pacote.
- Terminação e custo: o ciclo entre apoios termina (há o conjunto `vistos` e um teste em processo à parte com prazo). As expressões regulares não têm retrocesso catastrófico, e os nomes passam por escape. O `fnmatch` recebe padrões vindos de arquivos versionados.
- Leitura: `textos_dos_testes` exclui link simbólico; o dicionário `apoios` lê `tests/*.py` sem a mesma exclusão, mas só afeta o plano local (informativo).
- Detecção por texto: um apoio carregado por nome montado em tempo de execução escapa do plano local. É a mesma limitação aceita para o resto do mapa, e o CI a cobre.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Rodado no clone, no head 477dbefe: `tests/test_testes_tocados.py` inteiro, 157 testes OK (1 pulado pelo sandbox: /proc de outro namespace); planos de base e de head comparados para cada `hooks/*.py` e cada apoio da raiz de `tests/`. A suíte inteira roda no CI do PR, que ainda não existe ("sem PR" no brief); o merge depende dela. Ferramentas da skill (varredura de segredos, SAST, auditoria de workflow) não rodadas: a entrega não toca segredo, dependência nem workflow.
