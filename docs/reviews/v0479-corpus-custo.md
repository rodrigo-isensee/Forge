---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-corpus-custo
commit: 41db435f92eeadb4d16f641857538e77a1ca9657
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0479-corpus-custo

Code review do conserto do teste de custo do corpus da volta única (v0478 E41.1) no head b953cd45, base develop ef186de8 (v0478 E41.2). O diff troca a medida de CPU do `test_corpus_nos_dois_hooks` por um contador de trabalho (`sitecustomize` com auditoria: execuções do hook, subprocessos abertos e `time.sleep` do código do hook) e declara 12 mutantes.

## Achados
- A3 (recomendado) tests/apoio_volta_unica.py:78 · Segue da rodada anterior: `trabalhadores_do_limite_de_cpu`, `limite_de_cpu_do_corpus` e `limite_de_cpu_do_corpus_sob_carga` continuam sem uso fora do `test_medida_cpu.py`. É código morto.
- A5 (recomendado) tests/apoio_volta_unica.py:190 · O teto exato (ruído 0) foi medido só no Python 3.12.3 com git 2.43. Não há run de CI na branch. Se o 3.12 do CI, com outro git, contar diferente, o check fica vermelho. Meça no primeiro CI do PR e, se divergir, ponha a medida do CI.
- A6 (recomendado) tests/apoio_volta_unica.py:228 · Com o TMPDIR dentro de um repositório git (sonda S3), o lote deu 4637 subprocessos e 5890395 passos e reprovou. O acerto cobre a profundidade, mas não um tmp dentro de um work tree. Documente isso na mensagem do teste ou acerte o teto para esse caso.

## Sondas
- S1 · forge-mutante com spec ad hoc, hooks/_comum.py:2872 `hook = Hook(nome)` seguido de `sum(range(20000000))`, teste test_corpus_nos_dois_hooks · espera: morreu (regressão de CPU do hook reprova) · obtido: S1 · sobreviveu · hooks/_comum.py:2872
- S2 · python3 -I: excessos_de_trabalho({'execucoes':557,'subprocessos':4631+557,'sono':0.0},557) · espera: excesso (um git a mais por decisão, +12%) · obtido: []
- S3 · test_corpus_nos_dois_hooks em 41db435f com TMPDIR=/root/.forge-contrib/tmp/e416t (realpath dentro do repositório /workspaces/.forge-contrib) · espera: verde (o tmp só muda a profundidade) · obtido: FAIL, subprocessos 4637 > 4631, interpretador 5890395 > teto

## Provas conferidas
- Mutantes: 12 declarados (`tests/mutantes/v0478-corpus-custo.json` M1 a M8 e `-2.json` M9 a M12), um por guarda mudada. O log do autor (`tmp/e411/mutantes.log`, `forge-mutante` em rev b953cd45, base ef186de8) dá os 12 como mortos, com rc=0. O M1 (o driver roda o caso duas vezes) e o M2 (o hook dorme) são regressões reais e morrem. O M2 é válido: `time` é importado em `hooks/_comum.py:23`, então não morre por NameError.
- 10 rodadas sob carga: `tmp/e411/dez.log` registra 10 verdes, com carga de 1 min entre 4,4 e 39 em 12 núcleos. Cada rodada deu 557 execuções, 4631 subprocessos (4632 na 9.ª) e sono 0. A CPU informativa ficou entre 139,8 e 145,1 s.
- Causa: o comentário do commit registra 125,5 s livre contra 142,1 s sob carga (o mesmo lote) e os 127 a 185 s do CI. Os logs repro-carga, repro-cache e repro-2cpu confirmam a subida sob carga, mas nenhum passou de 180 s.
- Teste novo: rodei `ContadorDeTrabalhoDoCorpus` (6 testes, OK em 0,13 s). A suíte inteira não foi rodada (fica para o CI). O módulo verde do autor está em `tmp/e411/modulo.log` (22 testes OK).

## Parecer
Na rodada b953cd45, reprovado (na revalidação abaixo, aprovado). A medida deixa de depender da máquina, como o dono pediu, e os mutantes cobrem as guardas. Mas o novo portão não pega a classe de regressão que o antigo pegava: CPU gasta dentro do processo do hook (A1, sonda S1). E o teto que sobrou é folgado o bastante para deixar passar um git a mais por decisão (A2, sonda S2).

Para corrigir o A1, uma medida de trabalho do interpretador que não dependa da máquina. Por exemplo: chamadas de função contadas com `sys.setprofile` ou `sys.monitoring` (Python 3.12+) no mesmo `sitecustomize`, com teto da medida mais o ruído. Ou uma contagem de passos do parser do hook. Regex catastrófico dentro do motor `re` em C escapa à contagem de chamadas; nesse caso, explique no PR qual teste o cobre (o P3 de `test_hooks_volta_propriedades`, de 3 s por chamada, não pega 200 ms).

Para corrigir o A2, troque o teto por execução por um teto do lote próximo da medida, ou por um teto por execução de 8,4. O teste de borda continua no teto.

Os achados A3 e A4 não bloqueiam.

## Revalidação no head 41db435f (v0478 E41.6)
Li o delta de `forge-check parecer delta docs/reviews/v0479-corpus-custo.md`, de b953cd45 a 41db435f. No domínio: `tests/apoio_volta_unica.py`, `tests/test_hooks_volta_corpus.py`, as specs `tests/mutantes/v0478-corpus-custo{,-2,-3,-4,-5}.json`, `tests/provas/v0479-corpus-custo.md` e o fragmento do changelog. Antes do commit, a branch avançou até ace39a6b, mas só com o parecer de segurança, que está fora do domínio.

- **A1 resolvido.** O `sitecustomize` agora conta, por `sys.monitoring`, só no código do repositório: as chamadas, os inícios de função e os saltos para trás. Ele só liga com `FORGE_TESTE_TRABALHO_CODIGO`, e em produção não há nem o arquivo nem a variável. A sonda S1 virou o mutante M23 e morre. Pela prova, o lote deu 5861227 contra o teto de 5860121. O M25 (um laço de 1000 voltas por decisão) também morre. O limite está declarado no comentário e no changelog: o trabalho de dentro de uma chamada C que já existia (o `re` catastrófico) não é contado.
- **A2 resolvido.** O teto agora é a medida mais o ruído: 4631 + 0 subprocessos e 5860121 + 0 passos. A sonda S2 virou o M24 e morre (5188 > 4631). O `test_um_acima_do_teto_reprova` cobre a medida mais 1.
- **A4 resolvido.** As 10 rodadas sob carga, as sondas e os mutantes estão no commit (`tests/provas/v0479-corpus-custo.md`). O `HOME` vazio do contador tirou os briefs de `~/.forge-contrib`, que eram a fonte de 4631 a 4633.
- **Mutantes.** O log do autor dá M1 a M29 mortos, com cobertura `--base ef186de8` rc=0. São um mutante por guarda mudada; o M27 morre por erro do teste declarado, o que vale como morto.
- **Teste novo rodado:** `ContadorDeTrabalhoDoCorpus`, 12 testes, OK. Rodei também `test_corpus_nos_dois_hooks` no head, em quatro ambientes:
  - meu ambiente, com 334 variáveis e TMPDIR `/tmp/claude-0`: OK em 41,9 s;
  - `env -i`, com 19 variáveis que o hook viu e o mesmo tmp: OK;
  - TMPDIR `/tmp/claude-0/e416/b`, com 4 níveis: OK;
  - TMPDIR dentro de um repositório git: FAIL (S3, A6).

  O acerto por variável e por nível bate exato, também com 215 variáveis a menos. A suíte inteira fica para o CI.

### Risco declarado: 3.12 contra 3.14 e a versão do git
- **Passos no 3.14: o desenho cobre.** `excessos_de_trabalho` pula os passos fora do Python da medida (`tests/apoio_volta_unica.py:249`), com teste (`test_passos_do_interpretador_valem_so_no_python_da_medida`) e mutante (M19). No 3.14 o teto de passos não vale, e isso não é falha.
- **Subprocessos no 3.14: o teto exato vale nas duas versões.** Pela leitura, a contagem não muda. Cada lançamento gera um evento `subprocess.Popen`. O evento extra `os.posix_spawn`, que o 3.13+ passou a usar com `close_fds=True`, exige `os.path.dirname(executable)` (`/usr/lib/python3.12/subprocess.py:1826`). Os lançamentos do corpus usam nome nu: `git` em `bin/forge-check:588`, `gh` e `bash`. O único com caminho absoluto (`sys.executable` em `bin/forge-check:5012`) não é alcançado, porque as execuções contadas (557) batem com as declaradas e um filho Python seria contado. Isso não foi provado em execução: a tentativa de rodar com um 3.14 local foi negada pela permissão da sessão.
- **3.12 com outro git: o desenho não cobre (A5).** A medida não tem chave pela versão do git nem pelo patch do Python: o CI instala o 3.12 mais novo, e o autor mediu no 3.12.3. A sonda S3 mostra que a contagem segue a resposta do git ao ambiente: um tmp dentro de um work tree gera 6 subprocessos a mais. Um git que responde diferente (código de saída, saída de `config --get`, `ls-files`) desloca a contagem da mesma forma, e com ruído 0 qualquer passo reprova. Ainda não há defeito provado no CI, porque não existe run. Por isso o achado é recomendado, e o CI obrigatório do PR é o portão. Se ele divergir, a correção volta ao autor com a medida do CI. Pôr a versão do git na chave da medida, como já se faz com o Python, desligaria a checagem no CI, que é onde ela importa.

### Parecer na revalidação
Aprovado no head 41db435f. Os bloqueantes A1 e A2 estão resolvidos, com sonda virada mutante que morre. A3, A5 e A6 não bloqueiam.
