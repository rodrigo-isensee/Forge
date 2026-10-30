---
tipo: review
contrato: 1
pedido: worktree-orfas
branch: melhoria/worktree-orfas
commit: 398791ade119ef41e35c5b7d5b279190122a656e
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-30
---
# Code review: a lista do prune vai só ao log do forge-fechar (WORKTREE-ORFAS, F1)

Escopo: pedido WORKTREE-ORFAS-REV, E1.1 (`R-REVIEW`). Rodada 1. Li o diff inteiro, `git diff 31257c14c8d245d66e7806edb7cd65e22b3aeb04...398791ade119ef41e35c5b7d5b279190122a656e`: são 4 commits, de `13a8c35` a `398791a`, em 5 arquivos. O QA (E3.1) roda em paralelo, em `docs/qa/`, e não o refaço. O pedido não tem parecer de segurança: a decisão técnica de 2026-10-29 23:29 registra que não há gatilho, porque é só saída de terminal do script de fechamento.

## Achados
- A1 (recomendado) bin/forge-fechar:415 · com saída vazia do prune, o here-string entrega uma linha vazia e o log ganha um registro `[prune] ` sem texto; sugestão: `[ -z "$prune_saida" ] ||` antes do laço
- A2 (recomendado) tests/test_fechar_orfao.py:99 · o teste passa só `LANG` e herda `LC_ALL` do ambiente; com `LC_ALL=C` no executor, o falso já escreve `Removing` e o mutante M4 sobrevive (classe AR-4, teste herda o ambiente do CI); sugestão: passar também `LC_ALL="pt_BR.UTF-8"`

## Parecer
**Aprovado** no head `398791a`. A entrega faz o que o E1 e o E2 pedem: a lista do `git worktree prune -v` deixa de ir para a tela, e a linha `limpeza: …` continua sendo a última do passo 7. Os dois achados são recomendações e não devolvem a entrega.

- **A1:** o problema é só cosmético no log. A contagem não muda, porque `grep -c` sobre o texto vazio dá 0, e a tela também não muda.
- **A2:** nos executores do GitHub o `LC_ALL` vem vazio, então hoje o M4 morre. É a classe AR-4 (`teste herda o ambiente do CI`). Pela decisão técnica de 2026-10-29 15:28 (T1-CONF-ESCOPO-REV), nesta rodada fica só a citação da classe, sem linha AR nova nem contagem nova.

## Conferência por item do Entregar
- **Passo 7, comportamento da limpeza:**
  - A ordem não mudou: worktree, depois a branch local e por último a remota.
  - A conferência do sha (`sha_confere` antes do `worktree remove`) e o "nunca força" ficam intactos.
  - O prune continua rodando só quando o `worktree remove` falha e o diretório já não existe (`[ ! -d "$arvore" ]`, `bin/forge-fechar:412`).
  - O `prune_rc` não entra no `arv_st` nem na `pendencia`. O estado continua vindo do `git worktree list --porcelain`, como antes com o `|| true`, então os códigos de saída são os mesmos.
  - Os testes do registro órfão confirmam isso: o `prune_nega` sai com código 3 e mantém a branch pendente.
- **Linha `limpeza:` como última do passo:** o teste novo exige que, depois de `limpeza: remota=ok worktree=ok branch=ok`, venham só `Entrega p1 fechada em develop.` e `fim: código 0`. A linha `registro: prune tirou 301 …` aparece antes dela.
- **Contagem com LC_ALL=C:** o prune roda como `LC_ALL=C git worktree prune -v 2>&1` (`:414`), e a contagem é `grep -c '^Removing '` (`:416`). O falso de `git` traduz para `Removendo` fora do `LC_ALL=C` e o teste roda com `LANG=pt_BR.UTF-8`, então a guarda é provada (ressalva no A2). O falso confere o argumento exato `worktree prune` (checklist 12).
- **Aviso só quando o prune falha:** `[ "$prune_rc" = 0 ] || echo "aviso: …" >&2` (`:417`), conforme a DECISÃO TÉCNICA de 2026-10-30 00:15. No sucesso, a tela mostra só a contagem. O teste do `prune_nega` exige o aviso com `código 1` e exige que o `cannot prune` não apareça na tela.
- **`gravar_linha`:** é a extração da escrita no log que o `registrar` já fazia, com a mesma máscara (`mascarar`), o mesmo `flock` e o mesmo formato de data. O `registrar` passa a chamá-la sem mudar o comportamento. O `$log` está sempre definido antes do passo 7 (`:193`).
- **`docs/fechamento-integrador.md:46`:** o texto bate com o código: `LC_ALL=C`, a marca `[prune]`, a lista fora da tela, a mensagem da contagem e o aviso com o código e o caminho do log. O cabeçalho do script (`:32`) também foi atualizado. Não sobrou outro texto que diga que a lista do prune vai para a tela (procurei `prune -v` nos `.md`; os pareceres antigos descrevem o comportamento da época deles).
- **Teste novo, vermelho antes do verde:** troquei o `bin/forge-fechar` da base `31257c1` na worktree de review e rodei `test_prune_com_centenas_de_orfas_conta_na_tela_e_a_lista_fica_so_no_log`. Deu FAIL (`'orfa-' unexpectedly found`), e o arquivo foi restaurado em seguida. Com o head, `python3 -m unittest tests.test_fechar_orfao` dá `Ran 17 tests … OK`. O `shellcheck bin/forge-fechar` sai com rc 0.
- **Spec de mutantes:** `tests/mutantes/worktree-orfas.json` tem 5 mutantes (M1 a M5), um por guarda nova, cada um com o teste que o mata. Quem roda a mutação é o QA, e eu não a refiz.
- **Teto M14:** pelo `git diff --numstat --no-renames 31257c1...398791a`, contam `bin/forge-fechar` (22+10) e `tests/test_fechar_orfao.py` (24+0), num total de 56 linhas, abaixo de 150. A spec, o fragmento e o `.md` ficam fora da conta. O diff não toca `hooks/` nem caminho de `PROTEGIDOS`. A entrega traz um comportamento só.
- **Fragmento:** `changelog.d/worktree-orfas.md` está em `### Corrigido`, e a entrega não edita o `CHANGELOG.md`.
- **Regras:** `R-NEUTRO` sem termo de projeto e `R-CUSTO` sem nada pago. Nenhuma regra com ID e nenhum item de `invariantes` foi tocado.
- **Commits:** são 4 em Conventional Commits, em português. O E1 saiu em dois commits (`13a8c35` com o código e `398791a` com a documentação), e a divisão foi aceita pela DECISÃO TÉCNICA de 2026-10-30 00:15, porque juntá-los pediria `--force` (`R-VERIFY`).
- **`docs/engineering/praticas.md`:** o repositório do Forge não tem esse arquivo, então não há regra "decidida por" a citar. As ferramentas que valem para o diff são o `shellcheck` e a suíte do item, citadas acima.
