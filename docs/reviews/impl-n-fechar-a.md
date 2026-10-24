---
tipo: review
contrato: 1
pedido: impl-n-fechar-a
branch: melhoria/impl-n-fechar-a2
commit: bf0606059c9b082900fae957b7e4ab52e0324163
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-22
---
# Review: impl-n-fechar-a (lote N-FECHAR-a refeito, A1 a A6)

Escopo: `git diff a3dbe22..bf06060` (`bin/forge-fechar`, `docs/fechamento-integrador.md`, seis arquivos novos `tests/test_fechar_*.py` e `changelog.d/impl-n-fechar-a2.md`), contra o §2 do desenho `docs/propostas/discovery-0.29.0/n-fechar.md` e o adendo `docs/security/ameacas/n-fechar.md`. Rodada nova numa branch refeita: o review anterior (86cf4f5, branch `melhoria/impl-n-fechar-a`) serve de referência, mas a entrega foi lida inteira, sem `forge-check delta`. Sondas numa cópia própria em `$TMPDIR/tl5-revert`; o HEAD da worktree compartilhada não foi trocado.

## Achados

## Parecer
**Aprovado.** Os seis itens seguem o desenho e os controles do adendo, cada commit se reverte sozinho no HEAD com os testes que sobram verdes (P3 = B), e o A1 do review anterior está resolvido.

### Conferido
- **Reversão por commit (P3 = B), sonda feita à mão.** Sobre o HEAD `bf06060`, `git revert --no-commit` de cada commit, sozinho, numa cópia limpa: os 7 revertem sem conflito (dd09940, 32c1c2f, 8543a6e, 7a2fad5, f791d46, f893326 e bf06060). Depois de cada reversão rodei todos os `tests/test_fechar*.py` que sobraram, e todos passaram: dd09940, 107 testes OK; 32c1c2f, 109 OK; 8543a6e, 105 OK; 7a2fad5, 107 OK; f791d46, 102 OK; f893326, 110 OK. Nenhum item depende de função ou variável criada por outro.
- **O teste de cada item fica vermelho sem a mudança dele.** Sonda: o HEAD com só o `bin/forge-fechar` do item revertido, rodando o arquivo de teste do item. A3 (`test_fechar_faixas`): 5 de 5 falham. A1 (`test_fechar_orfao`): 3 de 3. A2 (`test_fechar_config`): 6 de 7 (o sétimo é o guarda "sem aviso, sem campo"). A4 (`test_fechar_sinal`): 4 falhas e 1 erro em 5. A5 (`test_fechar_base_andou`): 8 de 10 (os outros dois são os guardas "base já no head" e "head já mesclado"). A6 (`test_fechar_sha_arvore`): 1 de 2 (o outro é o guarda do caminho feliz).
- **Suíte do fechamento no HEAD:** 112 testes OK (78,8 s), o mesmo número do lote antigo. O `tests/test_fechar.py` não mudou, então nenhuma asserção existente saiu (`R-VERIFY`). Os arquivos novos importam o módulo `test_fechar` e não a classe, o que evita rodar a classe duas vezes. Cada um embrulha o `git` falso no próprio `setUp` (`prune_nega`, `ls_develop_falha`, `diff_falha`), sem tocar no atalho comum.
- **A1 do review anterior: resolvido.** `docs/fechamento-integrador.md:25-29`, na seção "Espera longa e corte por sinal", traz: `--espera` até 540 em primeiro plano; acima disso, `run_in_background` com leitura da linha `log:` e do `fim:`; a proibição do `pkill -f`, com a parada pelo pid; e log sem `fim:` ou com 143, 130, 129 ou 1 tratado como não sucesso (conferir o PR e rodar `--limpar`). Isso entrou no commit do A4 (7a2fad5), como pedia a volta.
- **A3 (dd09940):** a função `faixa` confere o tamanho antes do valor e compara em base 10. As faixas são pausa de 1 a 30, intervalo de 5 a 120 e `--espera` de 0 a 7200. O piso 0 só vale com `FORGE_FECHAR_TESTE=1` e o teto vale sempre. Tudo roda antes do passo 1 e do log (C-A3-1 a C-A3-4).
- **A1 (32c1c2f):** o caminho da worktree é lido inteiro (`substr($0,10)`) nas duas leituras. O `prune -v` grava a lista no log. Registro órfão com o `prune` negado imprime `git worktree prune`, e não o `remove`, e deixa a branch pendente. Os comandos impressos passam por `printf '%q'`, inclusive a linha final com `--limpar` (C-A1-1 a C-A1-4).
- **A2 (8543a6e):** o stderr do `branch -D` é guardado e impresso. A decisão vem do estado do config, comparando o nome exato da seção em texto fixo, e "o resto não tem ponto" afasta o falso positivo de `a` com `a.b`. Qualquer código diferente de 0 e de 1 vira `config=pendente`, e o campo `config=` fica no fim da linha. O teste usa o `config.lock` como diretório (C-A2-1 a C-A2-4).
- **A4 (7a2fad5):** `trap 'exit 143|130|129'` vem depois do `trap fim EXIT`. O `trap ''` está no `registrar` e no `fim`. O `dormir` usa `sleep &` com `wait`, e o `fim` mata o `sleep` que sobra. Os testes medem 143 no pid e no grupo, 130 e 129, e o `fim:` sai em menos de 10 s com um intervalo de 30 s em curso (C-A4-1, C-A4-2 e C-A4-4).
- **A5 (f791d46), passo 2b:** só roda com `ja_mesclado=0`. Toda falha de leitura para: `ls-remote`, resposta vazia, `rev-parse`, `--is-ancestor` com código diferente de 1, `merge-base --all`, `diff` e `sort`/`comm`. Os dois lados usam `--no-renames -z`, e a interseção sai de `sort -zu` e `comm -z -12`. O script não faz fetch, e o `--dry-run` imprime o passo sem ler o servidor (C-A5-1 a C-A5-5).
- **A6 (f893326) contra o adendo, sobre o desvio relatado.** O adendo pede conferir o sha da branch local antes de remover a worktree e deixá-la pendente se não conferir. O commit faz isso: lê `sha_local` no topo de `limpar_entrega` e acrescenta um `elif` antes do `git worktree remove`. O desvio em relação ao e8ec48e antigo é só de ordem: lá a conferência do sha vinha antes do caso "você está na worktree", e aqui vem depois dele. A mudança é necessária para o commit não tocar a linha que o A1 muda, que é o que permite a reversão isolada. Nos dois casos a worktree não é removida, então o controle do adendo está cumprido. A diferença é só o texto do aviso quando os dois casos ocorrem juntos (ver a primeira recomendação).
- **Commits:** um por item, na ordem do §2 (A3, A1, A2, A4, A5), mais o A6 e um commit só para o fragmento. Conventional Commits em português. O fragmento tem o nome da branch, sem renomeação (`bin/forge-changelog`), e o `CHANGELOG.md` não foi tocado.
- **Regras:** sem `--force`, sem `--no-verify` e sem aplicar rótulo (`R-VERIFY`, `R-CONTRIB`); nada com custo (`R-CUSTO`); nada específico de projeto (`R-NEUTRO`).
- **Segurança:** o parecer próprio do `security-engineer` está na mesma branch (504b03e) e não foi refeito aqui (`R-SEGURANCA`).
- **Ferramentas:** o Forge não tem `docs/engineering/praticas.md`, e o `bin/forge-fechar` não está na lista do shellcheck do CI (não há shellcheck nesta máquina). Não há regra de ferramenta para citar.

### Recomendações (não bloqueiam)
- `bin/forge-fechar:251`: quando quem roda está na worktree **e** a branch tem commit não mesclado, o aviso manda "saia dela e rode: `git worktree remove` ... `&& git branch -D` ...", sem dizer que há commit novo. É o texto da base, e o script não remove nada. Mesmo assim, vale citar o commit não mesclado nesse aviso ou trocar a ordem dentro de um commit futuro. Vai para o N-FECHAR-b.
- `bin/forge-fechar:287` e `:314`: `cfg_campo` só é declarado `local` dentro de um ramo, e a linha 314 o lê também nos outros ramos. Se houver uma variável de mesmo nome no ambiente, ela entra na linha `limpeza:`. Declará-lo no `local` do topo da função fecha isso. É o mesmo padrão da R1 de segurança (`tmp2b` e `dorme_pid` sem início no topo), que já foi para o N-FECHAR-b.
- `docs/fechamento-integrador.md:23` × `:32`: a frase "a rodada seguinte (mesmo comando) ... termina a limpeza" só vale enquanto a branch local e a remota existem. Se o corte cair no meio da limpeza, vale o `--limpar`, como dizem a linha 29 e a seção do `--limpar`. Uma oração a mais na linha 23 remove a ambiguidade.
- Do review anterior, continuam valendo: o critério de reversão do A5 (desenho §6) na seção "Reversão" do documento; o `diff_falha` derruba os dois lados do diff, então um mutante que troca só o `|| die` de um lado sobrevive; e, no A6, a linha "pendente, rode:" sugere o comando que o script recusou. Esse último fica como cartão para o `security-engineer`.
