---
tipo: revisao-seguranca
contrato: 1
pedido: conf-anexo-pareceres
branch: melhoria/conf-anexo-pareceres
commit: 135ee4ed8018078c88d059d18bd9a4aaf3d529d9
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-17
---
# Review de segurança: conf-anexo-pareceres

Diff revisado: `git diff f636d27c95bd1fdc9137baa830e0f53905863eaf...d574bf4c1c6fce19c655200c7d1d594f2e8246f0` (agents/conferente.md:71, tests/test_forge.py:233-242, changelog.d/conf-anexo-pareceres.md).

## Gatilhos
Controles do Forge (R-SEGURANCA): o conferente é uma camada de verificação de escopo. A pergunta é se, com `docs/security/` e `docs/devops/` como anexo implícito, o autor de uma entrega consegue esconder mudança indevida nessas pastas sem que algum portão a pegue.

## Achados
Por classe, com o cenário que a reproduz e o que a cobre. A mudança alinha o conferente ao `forge-check`, que já trata as quatro pastas de parecer como livres (`bin/forge-check:60`, `LIVRES`).

**C1. Parecer forjado de outro papel** (o autor grava `docs/security/<pedido>.md` ou `docs/devops/<pedido>.md` com `parecer: aprovado`) · coberto.
- Cenário: em entrega com gatilho, o `tech-lead` escreve o parecer de segurança no lugar do `security-engineer`. O conferente agora dá `escopo: ok (anexo)`.
- Cobertura: hook `conformidade` (escrita exclusiva: `hooks/conformidade.json:46` devops, `:48` seguranca; fixtures `tests/hooks/conformidade/parecer-seguranca-tech-lead-bloqueia.json`, `parecer-devops-tech-lead-bloqueia.json`, `parecer-por-bash-dev-bloqueia.json`) e `forge-check pr`, que confere o hash do parecer contra `autoria.jsonl` com o papel certo (`bin/forge-check:510-514`) e exige o parecer commitado (`:506-508`). Um arquivo forjado que escape do hook falha na autoria. Com symlink em `docs/security/`, também falha: o registro é pelo caminho.
- Severidade: informativa.

**C2. Aceite de risco forjado** (`docs/security/aceites/<pedido>.md`, que fica sob `docs/security/`) · coberto pelo hook, não pelo `forge-check pr` · baixa.
- Cenário: o parecer de segurança sai `riscos-aceitos`. Em vez de esperar o dono, o autor commita `docs/security/aceites/<pedido>.md` com `aceite: sim` e o `commit:` do parecer. Antes desta mudança, o conferente marcaria `escopo: fora` e reprovaria. Agora o arquivo entra como `escopo: ok (anexo)`, só por acréscimo.
- Cobertura: o hook `conformidade` não deixa nenhum agente gravar ali (`hooks/conformidade.json:47`, `quem: []`; fixtures `aceite-tech-lead-bloqueia.json` e `aceite-seguranca-bloqueia.json`). O `forge-check pr` confere só o conteúdo do aceite (`bin/forge-check:442-456`), não quem o gravou, e não há checagem no CI. A `main` continua sendo mesclada pelo dono (R-MAIN).
- Caminho de ataque: exige um agente autor que contorne o hook (por exemplo, trazer o arquivo de outro commit com uma operação do git que o hook não modela) e um parecer `riscos-aceitos` já emitido. Isso não é realista no fluxo atual. A camada que se perde só existia por acaso: a mesma regra reprovava também o aceite legítimo que o dono grava na branch.
- Correção mínima (opcional, decisão do dono): no item 2, `docs/security/` (salvo `docs/security/aceites/`, que gera a linha `escopo: aceite do usuário` sem reprovar). Assim o arquivo aparece para o Jarvis levar ao dono. Esforço P. Dono: `tech-lead`, num pedido próprio.

**C3. Alterar ou apagar parecer existente** (de outro pedido ou do mesmo) · coberto.
- Cenário: o autor troca `parecer: reprovado` por `aprovado` num parecer já commitado.
- Cobertura: a troca de linha aparece como remoção em `git diff --numstat --no-renames`, e o resultado é `escopo: anexo com remoção`, que reprova (agents/conferente.md:71). A autoria (C1) também falha, porque o hash muda.
- Acrescentar texto ao fim de um parecer não muda o frontmatter que o `forge-check` lê. Arquivos `_*.md` (`_modelo.md`) são ignorados por `documentos()` (`bin/forge-check:178`).
- Severidade: informativa.

**C4. Código ou configuração escondidos na pasta** · coberto.
- Nada no Forge executa ou carrega `docs/security/` nem `docs/devops/`: só o `forge-check` os lê, e só arquivos `.md` (`bin/forge-check:173,176`).
- Um arquivo que não é `.md` ali é inerte, e o review de código o vê no diff.
- Severidade: informativa.

**C5. Âncora na raiz** · lacuna anterior a esta mudança, ampliada · informativa.
- A lista não diz "na raiz do repositório". `templates/projeto/docs/security/_modelo.md` e `templates/projeto/docs/devops/_modelo.md` contêm o trecho `docs/security/` e `docs/devops/`, e um conferente que leia o caminho por substring poderia aceitá-los como anexo. Esses modelos vão para todos os projetos.
- O mesmo já valia para `docs/reviews/`, `docs/qa/` e `docs/kanban/` (há `templates/projeto/docs/reviews/_modelo.md`).
- Cobertura parcial: só por acréscimo, o teste `Neutralidade`, o review e o PR `homolog` → `main` mesclado pelo dono.
- Recomendação (P, `tech-lead`, num pedido próprio): "(caminhos a partir da raiz do repositório)" no item 2.

Comando para reproduzir a análise de escopo de qualquer classe: `git -C <worktree> diff --numstat --no-renames f636d27c95bd1fdc9137baa830e0f53905863eaf...<ref> -- docs/security docs/devops`. Teste que prende a lista: `python3 -m unittest tests.test_forge.Agentes.test_conferente_lista_de_anexos_implicitos -q` → OK.

## Riscos aceitos e ferramentas
Nenhum risco aceito. C2 e C5 são de severidade baixa ou informativa e ficam como recomendação, sem bloquear. Ferramentas: leitura estática e o teste focado acima. Faltam no PATH `gitleaks`, `zizmor`, `actionlint` e `semgrep`, que não se aplicam a esta mudança (nenhum workflow, segredo ou código executável no diff).

## Revalidação após o retrabalho 1
Diff revisado: `git diff 68a1490b8aaa75467aa06a9d78c358d508dd8437...135ee4ed8018078c88d059d18bd9a4aaf3d529d9` (agents/conferente.md:71, tests/test_forge.py:243-246, changelog.d/conf-anexo-pareceres.md; o resto do intervalo é o parecer de review, `docs/reviews/conf-anexo-pareceres.md`, anexo por acréscimo). Veredito sobre `135ee4e`: **aprovado**.

Cobertura declarada (VV-1): lido o diff inteiro do retrabalho, o item 2 "Escopo" de `agents/conferente.md` (linha 71), `hooks/conformidade.json:44-48` e `bin/forge-check:443-456,517`. Rodado: `python3 -m unittest tests.test_forge.Agentes.test_conferente_lista_de_anexos_implicitos -q` → OK. Não rodei a suíte inteira (R-TETO).

**C2 (aceite de risco forjado) · fecha.**
- `agents/conferente.md:71` agora diz que `docs/security/aceites/` fica fora da lista e que o aceite na entrega é `escopo: fora`: volta ao comportamento anterior a esta mudança, sem afrouxar.
- O teste prende a exceção (`tests/test_forge.py:245`) e que ela não entra na lista (`:246`).
- Cenário que reproduz: `git -C <worktree> show 135ee4e:agents/conferente.md | grep -c 'docs/security/aceites/'` → `1` (era `0` em `d574bf4`).
- O caminho excluído é o mesmo que o hook bloqueia para todo agente (`hooks/conformidade.json:47`) e que o `forge-check` lê como aceite (`bin/forge-check:446`).

**C5 (âncora na raiz) · fecha.**
- `agents/conferente.md:71`: "a lista vale a partir da raiz do repositório (`templates/projeto/docs/...` não é anexo)". O teste prende a frase (`tests/test_forge.py:244`).
- Cenário que reproduz: uma entrega que altere `templates/projeto/docs/security/_modelo.md` sem item no "Entregar" deve sair `escopo: fora`. Com o texto novo, a leitura por substring deixa de valer como anexo.

**Achados novos, por classe**
- **N1. Teste que prende o texto, não o lugar** · informativa. As duas frases novas são conferidas com `assertIn` no arquivo inteiro (`tests/test_forge.py:244-245`), e não no item 2. Se uma edição futura mover a frase para outro trecho de `agents/conferente.md`, o teste continua passando, mas a exceção deixa de valer para o escopo. Cenário: mover a frase do aceite para o modo de outro item e rodar o teste focado → OK. Cobertura: o trecho fica a poucos caracteres do `re.search` da lista, e o review vê o diff. Recomendação (P, `tech-lead`, sem bloquear): ampliar o `re.search` até o fim da frase do aceite. Não há caminho de ataque realista: o efeito depende de uma edição do próprio Forge, que passa pelo review e pelo dono.
- **N2. Aceite legítimo do dono na branch** · informativa, comportamento anterior mantido. Quando o dono grava o aceite na branch revisada, o conferente marca `escopo: fora`. Era assim antes deste pedido, e a DECISÃO TÉCNICA de 2026-10-17 deixa a linha própria para um cartão, se o dono quiser. Não é vulnerabilidade: o erro fica do lado seguro, porque reprova e leva o caso ao Jarvis.
- **Sem achado:** em outras subpastas de `docs/security/` e `docs/devops/` (`ameacas/`, pareceres). O hook só dá escrita a elas ao papel dono (`hooks/conformidade.json:46,48`). C1, C3 e C4 continuam como na rodada anterior.

Nenhum risco aceito. As ferramentas ausentes são as mesmas da rodada anterior, e nenhuma se aplica a este diff.
