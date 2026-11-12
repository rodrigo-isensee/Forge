---
tipo: revisao-seguranca
contrato: 1
pedido: v046
branch: melhoria/v046-mutacao-bench
commit: 60bba369d14f778d47f085e4f68c59707c44388f
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-12
---
# Review de segurança: v046 (E7.3, melhoria/v046-mutacao-bench)

Diff revisado: `8b5a44d5..60bba369` (bin/forge-mutante, bin/forge-changelog, specs e testes). Nada em `.github/` nem em `.githooks/` (conferido: diff vazio nessas pastas).

## Gatilhos
Controle do Forge (`R-SEGURANCA`): `bin/forge-mutante` produz a prova de mutação que o QA cola no parecer (portão `R-QA`); `bin/forge-changelog release` roda na promoção de versão.

## Achados
- A1 (bloqueante) bin/forge-mutante:805 · --base escolhe o mutante só pelo `arquivo` mutado; mudança nos módulos de `testes` ou na própria spec não o põe no diff. Teste esvaziado entre rodadas deixa o mutante fora do diff, sem rodar, e a revalidação sai 0 (S1). Incluir o mutante se a spec ou um módulo de `testes` mudou.
- A2 (recomendado) bin/forge-mutante:19 · nada liga a --base ao head já aprovado pelo QA nem diz que a 1.ª rodada do portão é a spec inteira; qa-testing e qa-engineer não citam a --base. Escrever no SKILL do QA: dirigida só na revalidação, base = head já aprovado, e conferir a linha base= no parecer.
- A3 (recomendado) bin/forge-changelog:223 · o nome da tag entra cru num comando impresso para copiar; nome de ref aceita `$(`, `;` e `|` (git check-ref-format aceita refs/tags/v9$(id)). Citar com shlex.quote. Baixa: exige criar tag no repositório do Forge.

## Sondas
- S1 · clone de 60bba369; commit com `# comentario` em bin/forge-mutante e `return` no início de test_fora_do_forge_nao_avisa; dirigir(specs v046-mutacao-bench*.json, base=60bba369, rev=HEAD) · espera: M9 roda (o teste que o mata mudou) · obtido: fora do diff: M9 · bin/forge-changelog; rodam M1..M8

## Detalhe dos achados
**A1** · evidência: `bin/forge-mutante:805` (`if m["arquivo"] not in mudados`) e o filtro da linha seguinte; o uso na revalidação está prescrito em `bin/forge-mutante:19`. Caminho de ataque: o autor (agente), entre a 1.ª rodada e a revalidação, enfraquece o teste listado em `testes` de um mutante cujo arquivo-alvo não muda mais (ou edita o `para` da spec), e mexe em outro arquivo da spec para a rodada não sair 2; o QA roda `--base <head revisado>` como o próprio texto da ferramenta indica; o mutante cujo teste foi esvaziado sai `fora do diff`, os demais morrem, saída 0, e o sobrevivente fica escondido no portão. Severidade: média (esvazia a prova de mutação de um controle do Forge sem nenhum erro). Correção mínima: em `dirigir`, um mutante entra quando qualquer destes caminhos está em `mudados`: o `arquivo` dele; o arquivo da spec que o declara; o arquivo de cada módulo de `testes` (o id pontuado `tests.x.Classe.metodo` vira `tests/x.py`). Com teste novo em `MutacaoDirigida` para os dois casos (só o teste mudou; só a spec mudou), e mutante na spec cobrindo a condição nova. Esforço: P. Dono: `tech-lead` (autor da E7.1).

**A2** · evidência: `bin/forge-mutante:19`; `skills/qa-testing/SKILL.md:92-96` e `agents/qa-engineer.md:20` sem menção à `--base`. Caminho: com qualquer SHA posterior à última mudança de um arquivo, os mutantes dele saem do diff; a linha `base=… mb=… rev=…` mostra a base, mas ninguém é instruído a conferi-la. Severidade: baixa (a saída lista cada `fora do diff`). Correção mínima: no SKILL do QA, a 1.ª rodada é a spec inteira; `--base` só na revalidação, com a base igual ao head que o QA já aprovou, e quem lê o parecer confere a linha `base=`. Esforço: P. Dono: `tech-lead`.

**A3** · evidência: `bin/forge-changelog:223`. Caminho: alguém com permissão de criar tag no repositório do Forge cria `v9$(…)`; o `git describe --match 'v[0-9]*'` a devolve e o tech-lead cola o comando impresso no shell. Severidade: baixa. Correção mínima: `shlex.quote(anterior)` na linha impressa. Esforço: P. Dono: `tech-lead`.

Perguntas do brief: (1) o `--base` esvazia a prova num portão? Em parte: base sem ancestral, ilegível ou sem mutante no diff sai 2 (testes `MutacaoDirigida` verdes), mas o recorte ignora testes e spec (A1). (2) Injeção ou caminho fora do repositório? Não: a `--base` passa por `resolver` (`rev-parse --verify --end-of-options <ref>^{commit}`), e `merge-base` e `diff` recebem só SHAs, com `--` e `--literal-pathspecs`; `arquivo` só é comparado como texto, sem abrir caminho; o `git describe` tem argumentos fixos e `cwd` na raiz, e a saída só é impressa (A3 é o único resíduo). O aviso do release não muda o código de saída.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Testes dos arquivos tocados rodados: `MutacaoDirigida` e `ReleaseAvisaMedidasDaVersao`, 7 testes, OK. Ferramentas ausentes no PATH (lacuna, não instaladas): gitleaks, semgrep, zizmor, actionlint; o diff não toca workflow nem traz segredo à leitura.
