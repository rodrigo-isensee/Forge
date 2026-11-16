---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-pr-hook-rapido
commit: 8eebc2a51576f5d9957653f4ad55bbdf7682f12b
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-15
---
# Review de segurança: v047 (E2.142, PR-HOOK-RAPIDO, E2.117)

Diff revisado: `bf475209..8eebc2a5`, parecer completo (não havia parecer anterior). Arquivos: `hooks/parecer.py` (o `gh pr ready` e o `gh pr merge` passam a usar o resultado gravado como atalho), `bin/forge-check` (`textos_da_arvore`, leitura em lote), `bin/forge-testes`, `docs/hooks.md`, o changelog, o teste e os mutantes.

## Gatilhos
Controle do Forge (hook `parecer`, `R-REVIEW`): a decisão do merge passa a confiar em estado local fora da árvore versionada (`<diretório comum do git>/forge/pr/<head>/`).

## Achados
- A1 (bloqueante) hooks/parecer.py:791 · Nos projetos, o gh pr merge passa a liberar pelo aprovado gravado, e o agente o grava com uma linha que carrega o forge-check do plugin e chama gravar_resultado_do_pr com lista vazia (a conformidade libera, S2): merge com review reprovado e sem CI de pareceres no projeto (S1, S3).
- A2 (recomendado) hooks/_comum.py:2757 · O comentário ainda diz "sem cache de veredito no merge: seria um arquivo que o agente escreve"; o código agora usa o resultado gravado no merge e no ready. Atualize o texto com o limite que vale.
- A3 (recomendado) changelog.d/v047-pr-hook-rapido.md:1 · Entrada em "Corrigido" sem dizer que o ready e o merge passam a confiar no arquivo local; o PR-HOOK-PRAZO declarou isso como afrouxamento (release-0.47.0). Declare igual no changelog e no PR.

## Sondas
- S1 · fixture pr-merge-com-pareceres.json (projeto) com o review em `parecer: reprovado`, hook parecer com `gh pr merge feature/x --squash`, sem resultado gravado · espera: rc 2 · obtido: rc 2 (R-REVIEW, o último parecer não é aprovado)
- S2 · mesma raiz, hook conformidade, papel tech-lead: `python3 -c "...SourceFileLoader('f','<plugin>/bin/forge-check')...;f.gravar_resultado_do_pr(pathlib.Path('.'),'p1','feature/x','develop',[])"` · espera: rc 2 · obtido: rc 0
- S3 · a linha da S2 executada na raiz, depois o hook parecer com `gh pr merge feature/x --squash` · espera: rc 2 · obtido: rc 0 (no clone do Forge, ready e merge também: rc 2 antes, rc 0 depois)

## Detalhe dos achados
**A1 · média · esforço P · dono: tech-lead (autor da E2.117).**
Evidência: `hooks/parecer.py:791` (o `merge_de_pr`, que roda também nos projetos) passa `gravado=ATALHO`; em `hooks/parecer.py:564-566`, o `aprovado` de `resultado_gravado_do_pr` retorna sem chamar o `cmd_pr`. O registro é um JSON em `<comum>/forge/pr/<head>/`. A única prova de origem é o campo `escritor`, o sha256 do `forge-check` do plugin (`bin/forge-check:1570-1573`). Qualquer processo que carregue o próprio `forge-check` do plugin grava esse campo certo.

Quem grava e como forjar: o `forge-check pr` grava o registro, mas `gravar_resultado_do_pr(raiz, pedido, ref, base, violacoes)` é uma função pública do módulo. Quem chama a função com `violacoes=[]` grava um `aprovado` do mesmo head e da mesma base, com o escritor válido. Nos projetos, a conformidade protege `.git/forge/` só quando o caminho aparece na linha (o `cat > .git/forge/pr/a.json` dá rc 2). Na S2, a linha não cita o caminho, porque quem o calcula é o próprio `forge-check`, e por isso passa. No clone do Forge, o tech-lead não tem lista de escrita, e até o `cat >` literal passa: na sonda local, a fixture do clone dá rc 0.

Caminho de ataque: um agente de projeto barrado no `gh pr merge` pelo parecer reprovado ou ausente roda a linha da S2 e repete o merge. O ganho é mesclar sem os pareceres. O modelo do projeto (`templates/projeto/`) não traz CI que confira os pareceres, então nos projetos o hook é o portão do merge. Antes desta entrega, o merge sempre refazia o `cmd_pr`. O parecer da PR-HOOK-PRAZO (`docs/security/v046-pr-hook-prazo.md`, A1 e A2) só aceitou confiar no arquivo para o `gh pr create` porque "o merge, o `gh pr ready` e o CI conferem sem cache e barram". Esta entrega tira esse controle compensatório do merge nos projetos. O dono decidiu, em 2026-11-14 08:16, que a autorização de afrouxar (diretriz 3) não vai aos projetos.

No clone do Forge, o ruleset (`bateria (pareceres)` e `catraca`, `docs/protecao-de-branch.md:22-25`) continua sendo o portão no servidor. Lá, o atalho só acelera, e o resíduo é informativo.

Correção mínima: fora do clone do Forge, o `ATALHO` usa só o `reprovado` (para recusar) e nunca o `aprovado` (para liberar). Em `verificar`, por exemplo: `if estado == "aprovado" and (gravado == EXIGE or e_clone_do_forge(raiz)): return`. Nos projetos, o `aprovado` gravado cai na conferência de hoje, que fica mais barata com o `textos_da_arvore`. O teste: a fixture de projeto com o review reprovado e o aprovado gravado por `gravar_resultado_do_pr(..., [])` no `gh pr merge` espera rc 2. A outra saída é o dono aceitar o risco (`riscos-aceitos`, pelo Jarvis, `R-DECISAO`).

**Respostas do brief.**
1. Quem grava: o `forge-check pr` (`bin/forge-check:1596-1615`), em `<comum>/forge/pr/<head>/<sha256(pedido, base)[:20]>.json`, pasta 0700.
2. Dá para forjar um aprovado do mesmo head? Sim. Nos projetos, pela S2 (a conformidade não vê o caminho). No clone do Forge, também por escrita direta. O `escritor` impede só o registro de outra versão do `forge-check`, não a forja.
3. O reprovado gravado recusa também nos projetos? Sim, no `gh pr merge`: `merge_de_pr` roda nos projetos com `ATALHO`, e `hooks/parecer.py:567-568` recusa com o motivo gravado. No `gh pr ready` não, porque `pronto_de_pr` retorna antes fora do clone do Forge (`hooks/parecer.py:616-617`; a S1 no ready do projeto dá rc 0, como antes). A recusa pelo reprovado é coerente: mesmo head, mesma base e mesmo `forge-check` dão o mesmo veredito do `cmd_pr`. As exceções são o registro de autoria e a lista de conferidos, lidos do disco; o resultado pode envelhecer, mas rodar `forge-check pr` de novo sobrescreve o registro. Isso não dá ganho a um atacante: um reprovado forjado só recusa.

**`textos_da_arvore` (bin/forge-check:339-365): sem achado.** O `ls-tree -z` não é recursivo e lê só blobs `.md`; subpasta e submódulo ficam fora. A resposta do `cat-file --batch` fora do pedido (objeto ausente, cabeçalho de 2 campos, saída truncada) devolve `{}`: nenhum parecer lido, e o `cmd_pr` reprova (falha fechada). O cache usa o id da árvore como chave, que fixa o conteúdo, então não envelhece. O link simbólico `.md` sai com o texto do alvo, como no `git show` de antes. O UTF-8 inválido levanta exceção, como antes; no hook, a linha crítica recusa.

**A2 e A3** são texto, sem caminho de ataque, e não devolvem. A2: o comentário de `hooks/_comum.py:2756-2759` contradiz o código e induz o próximo revisor a achar que o merge não tem cache. A3: mantém a regra de declarar o que tira controle (`R-DECISAO`, item d), como no PR-HOOK-PRAZO.

Conferido contra `docs/engineering/achados-recorrentes.md` (PA-7): AR-7 (escrita e leitura pelo mesmo `--git-common-dir`, ok). AR-1 e AR-12: os mutantes do item foram declarados em `tests/mutantes/v047-pr-hook-rapido.json`, mas não rodei o `forge-mutante`, que fica com o QA e o CI.

## Riscos aceitos e ferramentas
Nenhum risco aceito até agora. O A1 pode virar `riscos-aceitos` só com o aceite do dono (`docs/security/aceites/v047.md` com `commit:` igual a este).

Testes rodados no head 8eebc2a5: `python3 -m unittest tests.test_pr_hook_rapido` (10 testes, OK). As sondas S1 a S3 rodaram com o harness `tests/test_hooks.py` (`Fixture`, `rodar`) em raízes temporárias, contra os hooks e o `bin/forge-check` do head. O resto da suíte fica com o CI do PR, que não conferi: o `gh` não lê a configuração dentro do sandbox.

Ferramentas da skill fora do PATH (lacuna): gitleaks, semgrep, zizmor, actionlint, osv-scanner. Nenhuma delas é necessária a este diff.
