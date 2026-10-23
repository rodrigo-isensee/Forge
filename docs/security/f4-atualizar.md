---
tipo: revisao-seguranca
contrato: 1
pedido: F4-ATUALIZAR
branch: melhoria/f4-atualizar
commit: 4d86f26c7ff6266ff989476b75f2e2a1a3d691c3
parecer: reprovado
revisor: forge:security-engineer
data: 2026-10-23
---
# Review de segurança: F4-ATUALIZAR (revalidação por delta)

Escopo: delta `044e986..4d86f26` (commits `1f2731b` testes e `4d86f26` correção) sobre o parecer anterior (`commit: 671c625`, reprovado por A1). `forge-check delta --parecer` lista `bin/forge-atualizar` (linhas 54-124, 208-272), `README.md:77` e `tests/test_atualizar.py:422-502`; tudo relido, mais o `main` do `forge-atualizar` (tratamento de exceção, linha 279). Revisão estática e sondas locais em repositórios descartáveis (`HOME` em `$TMPDIR/security-engineer-f4`), sem rede externa.

## Gatilhos
Controle do Forge (`R-SEGURANCA`): `.forge/versao`, que só o dono altera, pelo terminal (`R-CONFORMIDADE`); e a `main` local, que é do usuário (`R-MAIN`).

## Achados
- A4 (bloqueante) bin/forge-atualizar:117 · fv.versao_de devolve None para .forge/versao fora de X.Y.Z (ex.: "0.4") e a comparação None > tupla levanta TypeError antes da pergunta: o comando morre no meio da mesclagem, com MERGE_HEAD e marcadores de conflito gravados em .forge/versao sem resposta do dono (sonda S9). Comparar só quando as duas versões forem válidas (senão, avisar que não deu para comparar) e um teste do caso
- A1 resolvido (S7, S7b, S7c: nada a fazer na main, numa branch qualquer e na develop local atrasada, nenhum commit novo)
- A2 resolvido (S2: mostra as duas versões e avisa que s rebaixa; resposta n deixa tudo como estava)
- A3 resolvido (docstring bin/forge-atualizar:8-9, README.md:77 e a lista de arquivos trazidos, S5)

## Detalhe dos achados
**A4. Versão malformada derruba o comando no meio da mesclagem (classe: conformidade, `R-CONFORMIDADE`, integridade de `.forge/versao`; regressão aberta pela correção de A2).** Evidência: `bin/forge-atualizar:117` faz `fv.versao_de(da_develop) > fv.versao_de(nossa)`; `bin/forge_versoes.py:30-32` devolve `None` quando o texto não casa `v?X.Y.Z`. O `main` só captura `EOFError` e `KeyboardInterrupt` (linha 279), então o `TypeError` sobe, o `merge --abort` da linha seguinte não roda, nem o doutor, nem o `oferecer_voltar`. Caminho: a `develop` do projeto traz um `.forge/versao` fora do formato (pré-release, valor truncado, linha extra que o `strip` não limpa); o dono roda `forge atualizar` e o conflito só em `.forge/versao` chega à linha 117. Sonda S9 (`.forge/versao` = `0.4` na develop, resposta n): `TypeError: '>' not supported between instances of 'NoneType' and 'tuple'`, `git status` = `UU .forge/versao`, `MERGE_HEAD` presente e o arquivo com `<<<<<<< HEAD|0.3.0|=======|0.4|>>>>>>>`. Antes da volta, o mesmo caso chegava à pergunta e a resposta n desfazia tudo (S3 do parecer anterior). Sem atacante: a `develop` entra por PR e o dono pode rodar `git merge --abort`. Mas o arquivo que só o dono altera fica alterado pela ferramenta sem a resposta dele, e a promessa "outro conflito é desfeito" quebra. Severidade: baixa (integridade local, sem exploração), bloqueante por ser controle do Forge e regressão desta volta. Correção mínima: `a, b = fv.versao_de(da_develop), fv.versao_de(nossa)`; `if a and b and a > b:` avisa; se `a` for `None`, imprimir que a versão da develop não está no formato X.Y.Z e seguir para a pergunta (padrão N). Teste: conflito com `.forge/versao` da develop = `0.4`, resposta n, termina com HEAD igual, árvore limpa e sem `MERGE_HEAD`. Esforço: P. Dono: devops-engineer (código), qa-engineer (teste).

**A1 a A3 do parecer anterior, com a sonda rodada de novo.**
- A1: `integrar_develop` sai com True sem mesclar quando a branch atual não é `forge/upgrade-<nova>` (linha 101). S7 (na `main` local já na 0.3.0, develop do remoto avançou): `True`, `main_mudou=nao`, último commit `main ja na 0.3.0`, árvore limpa, sem `MERGE_HEAD`. S7b (branch `feature/x`): `mudou=nao`. S7c (na `develop` local com commit próprio, atrás do remoto): `mudou=nao`. A saída final (linhas 266-270) diz "nenhuma branch criada e nada mesclado" nesse caso. Resolvido.
- A2: `versoes_do_conflito` lê `:3:` (develop) e `:2:` (branch do upgrade) e o aviso aparece quando a da develop é maior. S2 (develop 0.4.0, nova 0.3.0, resposta n): as duas versões e o aviso na tela, `versao=0.3.0 head_igual=sim status=[] merge_head=nao`. Resolvido (o caso malformado é o A4).
- A3: docstring e README passam a dizer "merge LOCAL só na branch do upgrade"; `trazidos` lista os arquivos e destaca `.forge/`, `.claude/` e hooks. S5: lista `.claude/settings.json` e `.githooks/pre-push` com o aviso. Os nomes vêm de `git diff --name-only`, que escapa caracteres de controle. Resolvido.

**Novo caminho para mexer em `.forge/versao` sem o dono?** Fora o A4, não. A pergunta continua atrás dos portões do `main` (`recusar_dentro_do_claude` e `tem_terminal`): S1, `yes s | forge-atualizar` e `CLAUDECODE=1 forge-atualizar` saem com 2. A guarda da linha 101 só reduz onde a mesclagem acontece. `adiantar_develop_local` continua só avançando (confere `--is-ancestor` nos dois sentidos, `update-ref` com valor antigo, `--ff-only`); S8, develop local divergente: aviso na tela e `develop_local_intacta=sim`. S4 (conflito em `a.txt` e `.forge/versao`): desfeito, `head_igual=sim status=[] merge_head=nao`. Informativo: se o dono já estiver numa `forge/upgrade-<nova>` de uma rodada anterior e o `forge-upgrade` disser "nada a fazer", a mesclagem acontece nessa branch, que é do próprio upgrade. Sem achado.

**Sonda rodada** (`reval2.sh` no scratchpad da sessão, repositórios bare locais): S1 saída 2 e 2; S7, S7b e S7c sem commit novo; S2 com aviso e estado intacto; S4 desfeito; S5 lista com destaque; S8 develop intacta; S9 `TypeError` e conflito deixado (A4). `python3 -m unittest tests.test_atualizar`: 71 testes, OK (nenhum cobre a versão malformada).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: revisão manual, `forge-check delta`, sondas com git e python3 locais. Lacuna: `gitleaks`, `semgrep`, `zizmor`, `actionlint` e `osv-scanner` não estão no PATH. O delta não mexe em workflow nem em dependência; nenhum segredo à vista no diff.
