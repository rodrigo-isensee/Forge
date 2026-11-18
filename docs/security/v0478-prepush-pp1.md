---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0478-prepush-pp1
commit: 6c84adb4ea7cda8e9b95de6d2857201afedc2f7e
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-18
---
# Review de segurança: v0478 (patch PP1 do envio local, E14.4)

Primeira rodada no head 6c84adb4, base 4182a6b9. Lido inteiro: `docs/devops/pp1-pre-push.patch` (o controle, que o dono aplica à mão em `.githooks/pre-push`), `docs/devops/pp1-aplicar.md`, a linha nova do `bin/forge-testes`, o fragmento do changelog e o `tests/test_pre_push_patch.py`. Não há modelo de ameaças `docs/security/ameacas/pre-push.md`; o parecer usa o modelo do próprio hook (trava em `$TMPDIR`, entrada de outro processo, árvore da própria branch).

Gatilhos: controle do envio local (`.githooks/pre-push`, via patch), leitura de arquivo compartilhado entre processos (trava), execução de Python da árvore no hook.

## Conferido

- **PRE-PUSH-TEXTO-TRAVA-FD** (patch:13). O `head` lê `/proc/self/fd/9`, que no Linux reabre o inode já aberto e conferido por `trava_confere` (o `-O /proc/self/fd/9` do hook em vigor), e não o caminho. Trocar o caminho por um link depois da conferência não desvia a leitura. O descritor 9 é herdado pelo `$(...)` e pelo `head` nos três pontos de chamada (`--status`, `mostrar_fila`, `avisar_trava_velha`). Aberto só para escrita (`9>>`), o arquivo é reaberto para leitura pelo dono, sem ganho de permissão. Sem o descritor (ou sem `/proc`), o texto sai vazio: falha fechada, sem erro. A saída continua presa a 200 bytes e a `[:print:]` em `LC_ALL=C`, então nenhum escape chega ao terminal. Sonda própria: com a trava apagada e trocada por um link para outro arquivo, o descritor leu o original e o caminho leu o desviado; sem o descritor, a saída ficou vazia. Teste: `test_le_o_arquivo_do_descritor_e_nao_o_do_caminho` e `test_sem_descritor_o_texto_sai_vazio_e_sem_erro`.
- **FILA-INTERVALO-ZERO** (patch:155-156). O `case` recusa tudo que não é dígito antes do `$((10#$intervalo))`, então a avaliação aritmética de uma variável de ambiente não abre injeção (a forma `a[$(cmd)]` não chega a ela). Sonda: `$(id)` foi recusado no `case`; `0`, `00` e `18446744073709551616` (que dá a volta para 0) foram recusados; `99999999999999999999` é aceito como positivo, o que é inofensivo.
- **PREPUSH-LEVE-COBERTURA-CATRACA** (patch:24-45, 91-110) e **PREPUSH-INDICE-E-PULOS** (patch:49-71, 114-145). Rodam com `python3 -I`, sem `shell=True`, e os nomes de arquivo vão por argv depois do `-c`, onde não viram opção. `catraca.ler` chama `git show <ref>:<caminho>` por lista e sem as variáveis `GIT_*`; o `ast.parse` não executa o teste contado. Toda saída repassada ao terminal passa pelo mesmo `tr -d` de controles do hook em vigor. O código executado é o da árvore da própria branch (`tests/catraca.py`, `bin/forge-check`, `bin/forge-mutante`, `scripts/indice-fixtures.py`). É a mesma fronteira que o hook já cruza com `tests/neutralidade.py`, `scripts/verificar-contribuicao.sh` e a suíte, e a mesma árvore que quem envia já executa. Não há fronteira nova.
- **Falha da ferramenta** (saída 2) vira aviso no envio leve, e o CI confere com a catraca da base. A branch pode neutralizar a checagem local mexendo na própria `tests/catraca.py`, mas isso não contorna o portão: é o desenho do ENVIO-LEVE, igual às checagens baratas que já existem.
- **Patch.** O `git apply --check` passa limpo no head. O `git apply --stat` mostra que ele toca só `.githooks/pre-push` (116 linhas a mais, 3 a menos), e o blob de origem `f944360` é o do hook na develop. O `tests/test_pre_push_patch.py` rodou isolado: 18 testes OK em 32 s.

A suíte inteira fica para o CI do PR. Esta etapa não abre PR, e o brief pede o parecer sem suíte local.

## Achados

- A1 (recomendado) docs/devops/pp1-aplicar.md:19 · o roteiro aplica o patch da árvore, não o do commit revisado, e o conferir mostra só o diff do hook; aplique `git show 6c84adb4:docs/devops/pp1-pre-push.patch` e rode `git apply --stat` (todos os arquivos) antes, para um patch mudado depois do parecer não entrar sem revisão.
- A2 (recomendado) docs/devops/pp1-pre-push.patch:91 · a guarda confere `[ -f bin/forge-check ]` sem `[ ! -L bin/forge-check ]`, ao contrário das outras; `catraca.forge_check()` resolve o link e executa o alvo. A fronteira é a mesma, mas iguale a guarda (acrescente `[ ! -L bin/forge-check ]`).

## Sondas

## Detalhe dos achados

**A1.** Evidência: `docs/devops/pp1-aplicar.md:19-20`. Caminho: o dono aplica à mão, num controle travado para os agentes, o arquivo `docs/devops/pp1-pre-push.patch` que estiver na branch naquele momento. Um commit posterior ao parecer, de um agente ou de um merge, pode mudar o patch, por exemplo para tocar outro arquivo protegido. O `git diff --stat -- .githooks/pre-push` não mostra o que caiu fora do hook. Hoje o patch toca só o hook (conferido acima), então não há defeito; o risco é o da janela entre o parecer e a aplicação. Severidade: baixa. Correção mínima: no roteiro, usar `git show 6c84adb4ea7cda8e9b95de6d2857201afedc2f7e:docs/devops/pp1-pre-push.patch > "$TMPDIR/pp1.patch"`, rodar `git apply --stat` e `git apply --check` nesse arquivo e depois `git apply` dele; ou trocar o conferir por `git status --short`. Esforço: P. Dono: devops-engineer.

**A2.** Evidência: patch:91, contra `tests/catraca.py:1653-1659`, onde `forge_check` faz `Path(__file__).resolve()` e `exec_module` de `bin/forge-check`. Caminho: um `bin/forge-check` versionado como link aponta para um arquivo fora do repositório e é executado no envio. Quem pode fazer isso é o autor da branch, que já executa a própria árvore, então não há ganho de privilégio. É coerência com `[ ! -L ]` nas guardas vizinhas (`bin/forge-mutante`, `tests/catraca.py`). Severidade: baixa. Correção mínima: acrescentar `[ ! -L bin/forge-check ]` à condição da patch:91. Esforço: P. Dono: devops-engineer.

## Riscos aceitos e ferramentas

Nenhum risco aceito. Ferramentas: leitura estática, `git apply --check/--stat`, sonda local do descritor e do intervalo, e o `tests.test_pre_push_patch` isolado. Não estavam no PATH (lacuna): `gitleaks`, `shellcheck`, `semgrep`. O shellcheck do hook roda no CI quando o patch for aplicado.
