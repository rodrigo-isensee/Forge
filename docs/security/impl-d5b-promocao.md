---
tipo: revisao-seguranca
contrato: 1
pedido: impl-d5b-promocao
branch: melhoria/impl-d5b-promocao
commit: ffa8b00957735dd90ac7e318379a6a084766063d
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-22
---
# Review de segurança: impl-d5b-promocao

Escopo: o diff `c092f1b..ffa8b00` (o script `scripts/promover-homolog.py`, o teste `tests/test_promover_homolog.py`, a classe `GuiaDaPromocao` em `tests/test_forge.py`, os guias `docs/promocao-integrador.md` e `docs/fechamento-integrador.md` e o fragmento `changelog.d/impl-d5b-promocao.md`). Revisão estática e passiva.

## Gatilhos
Fluxo de branches e portões (`R-FLUXO`, `R-MAIN`, `R-CONTRIB`): o script usa a credencial do `gh` de quem o roda para abrir PR na `homolog` e lê checks e rótulos que decidem se a promoção está pronta. Não toca workflow, ruleset, hook nem caminho da lista `PROTEGIDOS` da catraca.

## Achados

## Detalhe dos achados
Conferido, sem achado bloqueante:
- Não mescla, não aplica rótulo, não usa `--force` nem `--no-verify`: o merge só é impresso (`scripts/promover-homolog.py:213`, `:263`), com `--match-head-commit <sha>`, que faz o merge falhar se a `develop` andou depois da conferência (protege contra TOCTOU).
- A `main` é recusada no par de refs (`:91-94`, lista fechada `develop`/`homolog`) e no PR aberto com base diferente da `homolog` (`:170-172`) (`R-MAIN`).
- Todas as chamadas externas usam lista de argumentos, sem shell (`:47`, `:155`, `:227`); a versão e o corpo vindos da ref entram como argumento, sem injeção de comando.
- Catraca vermelha nunca passa: sai com 3 e só avisa do rótulo do dono (`:248-256`); check em estado desconhecido para (`:244-246`); falha de leitura do `gh` para, não vira verde (`:239-241`). Falha segura.
- O `gh` substituto (`FORGE_GH`) só vale com `FORGE_PROMOVER_TESTE=1` e avisa quando ignorado (`:142-147`); quem controla o ambiente já controla a máquina, sem fronteira nova.
- `--dry-run` não chama `gh` nem `git fetch` (`:202-221`); o teste prova que refs e árvore não mudam (25 testes de `tests.test_promover_homolog` verdes numa cópia em `$TMPDIR`).
- Sem segredo, sem dependência nova (só biblioteca padrão), sem custo (`R-CUSTO`).

Recomendações (não bloqueantes):
- R1 (baixa) `scripts/promover-homolog.py:165-173`: `gh pr list --head develop` também devolve PR de fork cuja branch se chama `develop`, e o script reusa o primeiro da lista e lê os checks dele. Caminho: com o repositório público, alguém de fora abre PR de fork `develop` → `homolog` (no evento `pull_request` o workflow roda na versão do PR e pode passar sempre); o script poderia mostrar verde lendo o PR errado. Hoje não há caminho realista: o repositório é privado e sem colaborador externo (ADR 0008), o comando de merge resolve a branch do próprio repositório com `--match-head-commit`, e com o repositório público valem os rulesets com checks obrigatórios e a aprovação de workflow de fork. Correção mínima: pedir `headRepositoryOwner` (ou `isCrossRepository`) no `--json` e ignorar ou recusar PR de outro repositório; teste com o `gh` falso. Esforço P. Dono: `tech-lead`. Vale fazer antes do gatilho de tornar o repositório público.
- R2 (informativa) `scripts/promover-homolog.py:104-107`: só pareceres adicionados ou alterados entram (`--diff-filter=AM`); um parecer reprovado apagado na leva não é visto. É auxiliar: o portão continua no `forge-check pr` de cada entrega e nos checks do PR; registrar no guia que o script não substitui esses portões já está implícito em "sem tirar nenhum portão".

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do diff e execução dos testes do script numa cópia. Lacunas: `gitleaks`, `semgrep`, `osv-scanner`, `zizmor` e `actionlint` não estão no PATH (não instalados, `R-CUSTO`); o diff não traz credencial nem workflow. A conferência de reversão por commit (`revert-sozinho.sh`) não rodou neste ambiente (negada pela permissão da sessão); não é item de segurança e fica com o review e o QA.
