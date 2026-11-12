---
tipo: revisao-seguranca
contrato: 1
pedido: v046
branch: melhoria/v046-mutacao-bench
commit: e452582f9186c8b70a2a935d9c0e12e84ec6e48b
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-12
---
# Review de segurança: v046 (E7.7, melhoria/v046-mutacao-bench, revalidação por delta)

Delta revisado: `60bba369..e452582f` (`forge-check parecer delta`: no domínio só `bin/forge-mutante` e `bin/forge-changelog`; specs, testes e fragmento do changelog lidos como apoio). Nada em `.github/` nem em `.githooks/`. A rodada anterior (E7.3, `60bba369`) foi reprovada pelo A1.

## Gatilhos
Controle do Forge (`R-SEGURANCA`): `bin/forge-mutante` produz a prova de mutação que o QA cola no parecer (portão `R-QA`); `bin/forge-changelog release` roda na promoção de versão.

## Achados
- A1 (bloqueante) bin/forge-mutante:800 · resolvido em e452582f: no_diff põe o mutante no diff quando mudou a spec que o declara, o arquivo dele ou o módulo de um dos seus testes; S1 refeita (teste esvaziado) roda o mutante e sai 1; os mutantes M11 a M15 guardam a condição.
- A2 (recomendado) bin/forge-mutante:17 · parcial: o --help liga a --base ao head já aprovado pelo QA e manda conferir a linha base=; skills/qa-testing/SKILL.md e agents/qa-engineer.md ainda não citam a --base da dirigida. Levar as mesmas duas frases ao SKILL do QA.
- A3 (recomendado) bin/forge-changelog:222 · resolvido em e452582f: shlex.quote na tag; a tag v9$(id) sai citada entre aspas simples no comando impresso (test_tag_com_metacaractere_sai_citada_no_comando, verde).
- A4 (recomendado) bin/forge-mutante:802 · helper importado pelo teste (tests/apoio_*.py, tests/ambiente_git.py) esvaziado entre base e rev deixa o mutante fora do diff e a dirigida sai 0 (S2); o limite está escrito no --help. Pôr todos os mutantes no diff quando mudar arquivo de tests/ que não seja test_*.py.

## Sondas
- S1 · fixture de MutacaoDirigida: teste do M1 enfraquecido e outro.py mudado; `forge-mutante SPEC --base <base>` · espera: M1 roda e sobrevive, rc 1 · obtido: `M1 · sobreviveu`, rc 1 (test_teste_enfraquecido_entre_base_e_rev_roda_o_mutante_e_sobrevive, verde)
- S2 · repo em $TMPDIR: helper tests/apoio.py usado pelo teste que mata M1 (lib.py) trocado por `return None`, e outro.py (M2) mudado; `forge-mutante spec.json --base <base>` · espera: M1 roda e sobrevive · obtido: `fora do diff: M1 · lib.py`, rc 0 (sem --base: M1 sobrevive, rc 1)
- S3 · `python3 -c "import shlex;print(shlex.quote('v9\$(id)'))"` e test_tag_com_metacaractere_sai_citada_no_comando · espera: `'v9$(id)'` · obtido: `'v9$(id)'`, teste verde

## Detalhe dos achados
**A1** (resolvido) · `bin/forge-mutante:797-802` (`no_diff`) e `:821` (`spec_mudou`). Cobre os três caminhos da correção mínima da E7.3: o `arquivo`, a spec versionada (comparada pelo caminho relativo à raiz depois do `chdir` para o toplevel) e cada módulo possível do id pontuado (`modulos_do_teste` gera todos os prefixos, então `tests.test_lib.T.test_borda` inclui `tests/test_lib.py`). Spec fora do repositório (cópia em `$TMPDIR`, outra worktree) não conta como mudada; o `--help` diz "spec versionada no repositório" e o QA roda a spec da worktree do head, então não é caminho de ataque realista. Diff com `--no-renames`: renomear o teste aparece como apagado e criado, e os dois nomes entram em `mudados`.

**A2** (recomendado, parcial) · `bin/forge-mutante:17-22`: a 1.ª rodada do QA é a spec inteira; `--base` só na revalidação, com SHA = head já aprovado, e o parecer confere a linha `base=`. Isso responde à pergunta do brief: a ligação está descrita e é verificável pela saída. Falta levá-la a `skills/qa-testing/SKILL.md:92` (bloco de mutação) e a `agents/qa-engineer.md:20` (que só cita a `--base` da `--cobertura`), onde o QA a lê sem abrir o `--help`. Severidade: baixa. Esforço: P. Dono: `tech-lead`.

**A3** (resolvido) · `bin/forge-changelog:222`. O marcador `<tag da release anterior>` continua sem citação, de propósito: é texto para a pessoa substituir, não valor vindo do repositório.

**A4** · evidência: `bin/forge-mutante:802` (só o módulo do teste entra, não o que ele importa) e o próprio `--help` (`Helper importado pelo teste não conta`). Caminho de ataque: o autor (agente), entre o head aprovado e a revalidação, esvazia uma asserção dentro de um helper (`tests/apoio_*.py`, `tests/ambiente_git.py`, comuns na suíte do Forge) usado pelo teste que mata um mutante cujo arquivo não muda mais, e mexe em outro arquivo da spec para a rodada não sair 2; a dirigida sai 0 (S2). Por que não bloqueia: o limite está escrito na ferramenta; o helper mudado aparece no delta que review, segurança e QA leem na mesma volta (o `forge-check parecer delta` o lista); e a correção mínima da E7.3, que este parecer revalida, pedia a spec e o módulo do teste, não a cadeia de importação, que não tem fim (o próprio arquivo mutado importa outros módulos). Severidade: baixa. Correção mínima proporcional: em `dirigir`, se `mudados` tiver algum arquivo sob `tests/` que não seja `tests/test_*.py` nem `tests/mutantes/*.json`, todos os mutantes da spec entram (a rodada fica igual à 1.ª, sem custo no CI do PR, porque a mutação não roda no PR); com teste em `MutacaoDirigida` e mutante na spec. Esforço: P. Dono: `tech-lead`.

Pergunta do brief "helper importado pelo teste não conta: é aceitável?": sim, como limite documentado desta entrega, com o A4 recomendado; calar o limite não seria aceitável, e ele não está calado.

Conferência PA-7 (`docs/engineering/achados-recorrentes.md`): AR-5 e AR-7 não se aplicam ao delta (nenhum `python` novo em caminho que decide; o `git` roda no `cwd` que o próprio `main` fixou no toplevel); AR-12 (spec desatualizada) conferido: M11 a M15 e os ajustes em `v046-mutacao-bench.json` batem com o texto de `e452582f`.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Testes dos arquivos tocados rodados em `e452582f`: `MutacaoDirigida` e `ReleaseAvisaMedidasDaVersao`, 11 testes, OK. Ferramentas ausentes no PATH (lacuna, não instaladas): gitleaks, semgrep, zizmor, actionlint; o delta não toca workflow nem traz segredo à leitura.
