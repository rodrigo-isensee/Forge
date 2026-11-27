---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-hook-raiz-forge
commit: baffa052cf425f0bc0eaed636e681c52b299b372
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-26
---
# Review de segurança: v0481 (E37.2, #930, 1ª rodada completa)

Gatilhos: hook de bloqueio (`hooks/conformidade.py`), R-CONFORMIDADE, R-VERIFY (pre-push da raiz), o que roda fora do sandbox (postStart do container como root).

## Resumo
- Lido: `git diff 6edd59d2..baffa052` inteiro (`hooks/conformidade.py`, 19 fixtures `raiz-forge-*`, `tests/test_hooks.py`, `tests/mutantes/v0481-hook-raiz-forge.json`, `docs/hooks.md:69`, o fragmento do changelog). Também li o caminho de chamada (`prova_fora_de_projeto`, `GuardaDaProva.barrar`, `checar_texto`) e a detecção da sessão (`hooks/_comum.py:67-80`).
- **O que aperta:** `EM_VIGOR_NA_RAIZ` (`hooks/conformidade.py:4171`) e `na_raiz_em_vigor` (`:4302`, `:4310`). A recusa vale na raiz da sessão e na cópia principal, e a pasta corrente, `wt/*` incluída, não abre exceção. Write, Edit, MultiEdit, redirecionamento, `cp`, `mv`, `rm -rf`, `sed -i`, `ln`, `install`, `touch`, `chmod`, `dd`, `rsync`, `tar -C`, `tee`, `perl -i`, `awk -i`, `bash -c`, `git checkout|restore -- <caminho>`, `git -C <raiz>` vindo de `wt/`, `..` no caminho e o link já plantado recusam como no projeto. O teste novo `test_fixtures_da_raiz_do_forge` passa local (1 teste, OK), e os mutantes RF1 a RF4 guardam as quatro condições.
- **O que não fecha:** a promessa "como num projeto" falha em três formas triviais, e cada uma desliga o controle inteiro:
  - o texto de interpretador (A1);
  - o alvo opaco (A2);
  - o manifesto da raiz, que desliga a própria detecção da sessão (A3).
- **CI do head `baffa052`** (run 45928648861 e a catraca em 45928648787) está vermelho:
  - por defeito: A7 (`tests/test_hooks.py:913`) e A8 (`tests/test_indice_fixtures.py:157`);
  - por processo, sem defeito: `catraca` (R-CONFORMIDADE em `hooks/conformidade.py`, falta o rótulo `afrouxa-regra` do dono depois do último push) e `bateria (pareceres)` (R-REVIEW, falta parecer). A `bateria (python 3.14)` é só o agregador.
- ci: baffa052cf425f0bc0eaed636e681c52b299b372 vermelho

## Achados
- A1 (bloqueante) hooks/conformidade.py:2178 · checar_texto barra o texto de interpretador sem alvo; na sessão do Forge na_raiz_em_vigor(None) é falso e `python3 -c`, `node -e` e o heredoc do interpretador gravam .githooks/pre-push e devcontainer.json da raiz (S1-S4); no projeto recusam
- A2 (bloqueante) hooks/conformidade.py:4302 · alvo opaco (`F=.githooks/pre-push; printf x > $F`, S5) passa na raiz da sessão do Forge (no projeto recusa); a linha sem leitura ou com erro interno que cita a entrada também (:4565 só olha ESTADO_NO_TEXTO); docs/hooks.md:69 o aceita sem decisão do dono
- A3 (bloqueante) hooks/_comum.py:72 · explorável: S6 · Write em .claude-plugin/plugin.json da raiz (nome diferente de forge) passa; na chamada seguinte a raiz deixa de ser clone do Forge e a recusa nova e as travas da sessão somem (2º passo: fixture raiz-forge-outro-repo-libera, rc 0)
- A4 (recomendado) hooks/conformidade.py:4171 · na raiz, `git switch|checkout <branch>`, `stash pop`, `apply`, `checkout-index -f` e `patch` trazem o .githooks/pre-push de uma branch enviada pelo agente (sondas S3, S4, S7, S8, S38 do arquivo, rc 0, também no projeto); cartão com decisão do dono
- A5 (recomendado) hooks/conformidade.py:4171 · `.devcontainer.json` na raiz e `.devcontainer/<pasta>/devcontainer.json` seguem livres (rc 0, também no projeto); o editor os oferece ao abrir o container, e o postStart deles roda como root; proteger a pasta .devcontainer/ e o .devcontainer.json
- A6 (recomendado) hooks/conformidade.py:2178 · `printf x > $(echo .githooks)/pre-push` passa no projeto e na raiz do Forge (rc 0 nos dois): o destino por substituição com resto literal não chega ao barrar; cartão para a Guarda base
- A7 (bloqueante) tests/test_hooks.py:913 · CI vermelho: fixture estadoclone-rm-git-bloqueia espera o motivo .git/forge/ e recebe o do .git (na_raiz_em_vigor casa .git porque .git/hooks/ fica sob ele); a recusa continua, só a mensagem mudou; acerte o esperado ou a ordem
- A8 (bloqueante) tests/test_indice_fixtures.py:157 · CI vermelho: docs/hooks-fixtures.md desatualizado (falta o prefixo raiz-*); rode scripts/indice-fixtures.py e versione o índice

## Sondas
- S1 · Bash `python3 -c "open('.githooks/pre-push','w').write('x')"`, cwd na raiz da sessão (clone do Forge), papel devops-engineer · espera: rc 2 (arquivo em vigor .githooks/), como no projeto · obtido: rc 0
- S2 · Bash `node -e "require('fs').writeFileSync('.githooks/pre-push','x')"`, cwd na raiz da sessão do Forge · espera: rc 2 · obtido: rc 0 (no projeto, rc 2)
- S3 · Bash `python3 -c "open('.devcontainer/devcontainer.json','w').write('x')"`, cwd na raiz da sessão do Forge · espera: rc 2 (arquivo em vigor .devcontainer/devcontainer.json) · obtido: rc 0
- S4 · Bash `python3 -c "open('<raiz>/.githooks/pre-push','w').write('x')"` com cwd em ~/.forge-contrib/wt/x · espera: rc 2 (a pasta corrente não abre exceção) · obtido: rc 0
- S5 · Bash `F=.githooks/pre-push; printf x > $F`, cwd na raiz da sessão do Forge · espera: rc 2, como no projeto (`$F` com ação crítica) · obtido: rc 0
- S6 · Write `<raiz>/.claude-plugin/plugin.json` com `{}`, raiz da sessão no clone do Forge · espera: rc 2 (o manifesto decide se as travas valem) · obtido: rc 0

## Detalhe dos achados
Ameaça: um agente sob injeção de instrução, dentro do sandbox, grava na raiz um arquivo que roda fora dele. O pre-push roda no próximo `git push` do dono no terminal. O postStart roda como root no próximo início do container e lê o login do gh. Com isso o agente ganha execução fora do sandbox, com as credenciais do dono. Severidade das três formas: **alta**. Cada uma é uma chamada só, sem nada além do que o agente já tem.

Como as sondas rodaram: `/root/.forge-contrib/wt/_sec125-v0481-sonda.py <cópia> forge|projeto [ids]` monta a fixture `raiz-forge-s0-write-githooks-bloqueia` e troca só a entrada. Ela usa o `Fixture`/`rodar` de `tests/test_hooks.py` e roda o hook do head revisado. O modo `projeto` dá a comparação "como num projeto". Foram 49 entradas. As que recusam nos dois modos estão no Resumo.

- **A1:** `checar_texto` (`hooks/conformidade.py:2161-2178`) resolve o caminho (`self.resolver(c, raiz)`), mas chama `self.barrar(*achado)` sem `alvo=`. Correção mínima: `self.barrar(*achado, alvo=<o caminho resolvido>)`. Com isso o texto de interpretador cai em `na_raiz_em_vigor` como o redirecionamento. Fixtures que faltam: `python3 -c`, `node -e`, `python3 - <<'EOF'` e o caminho absoluto vindo de `wt/`, para `.githooks/`, `.git/hooks/` e `devcontainer.json`. Esforço P. Dono: tech-lead.
- **A2:** `GuardaDaProva.barrar` só recusa por `na_raiz_em_vigor` quando o alvo é um `Path` resolvido. A recusa do alvo opaco (variável, `${…}`, construção não modelada) chega com `alvo=None` e é descartada. O padrão já existe para o estado dos hooks: `recusa_do_estado` com `ESTADO_NO_TEXTO` (`:4300`) e o recurso da linha sem leitura em `:4565`.
  - Correção mínima: um `EM_VIGOR_NO_TEXTO` (`\.githooks`, `\.git/hooks`, `devcontainer`, e `\.claude-plugin` com A3).
  - Com ele, a recusa sem alvo resolvido numa linha que o cita barra, e o recurso de `prova_fora_de_projeto` (`:4565`) também barra a linha sem leitura ou com erro interno que o cita.
  - Corrigir a frase "O alvo opaco ... segue como antes" em `docs/hooks.md:69`.
  - O que fica livre, sem citar o nome na linha (`$(printf '\x2e…')`), é o limite já registrado da ADR 0009, seção 6.
  - Esforço P. Dono: tech-lead.
- **A3:** `tem_manifesto_do_forge` (`hooks/_comum.py:67-74`) lê o `.claude-plugin/plugin.json` da raiz a cada chamada. A docstring diz que ele "serve para PROTEGER mais, nunca para dar poder". Mas o mesmo arquivo, gravável pelo agente na raiz, decide se a proteção existe: apagá-lo ou renomear o `name` desliga a sessão do Forge (`hooks/conformidade.py:4678`). A chamada seguinte cai no "não age" da fixture `raiz-forge-outro-repo-libera`. Isso vale também para as travas da v0478 E51.1 (push na main, `--no-verify`, `--force`), que já existiam antes deste item. Daí `explorável: S6`, fora do delta.
  - Correção mínima: incluir `.claude-plugin/` em `EM_VIGOR_NA_RAIZ`, para recusar Write, Edit e escrita ou remoção pelo Bash na pasta do manifesto da raiz e da cópia principal. A versão sobe pela cópia de `wt/`, por branch e PR.
  - Fixtures: Write, `sed -i` e `rm -rf .claude-plugin` na raiz recusam; na cópia de `wt/`, liberam.
  - Esforço P. Dono: tech-lead.
- **A4:** a promessa "Write, Edit e Bash" não cobre o git trocando a árvore da raiz. O caminho é este:
  1. o agente envia, pela cópia de `wt/` (fluxo legítimo), uma `melhoria/*` com `.githooks/pre-push` alterado;
  2. ele roda `git switch` ou `git checkout <branch>` na raiz;
  3. o próximo push do dono roda o script novo.

  No projeto é igual, então a paridade se mantém. Fechar isso muda o fluxo da raiz e é decisão do dono (R-DECISAO). Correção proposta: na sessão do Forge, com o alvo na raiz ou na cópia principal, recusar `switch`, `checkout <ref>`, `reset --hard`, `merge`, `pull`, `stash pop|apply`, `apply`, `am`, `cherry-pick`, `rebase`, `checkout-index`, `read-tree -u` e `patch` quando `git diff --quiet HEAD <ref> -- .githooks .devcontainer .claude-plugin` acusa diferença. A alternativa é a raiz só andar por `--ff-only` de `main`, `develop` e `homolog` do remoto. Cartão (G1.2). Esforço M. Dono: tech-lead.
- **A5:** severidade baixa. O editor pergunta qual configuração usar quando há mais de uma, e a reconstrução usa a que já estava gravada, então depende de o dono escolher a errada. Correção mínima em `hooks/conformidade.json` e `EM_VIGOR_NA_RAIZ`: `.devcontainer/` inteira e `.devcontainer.json` (hoje só `.devcontainer/devcontainer.json`). A fixture `raiz-forge-vizinho-devcontainer-libera` passa a esperar rc 2 ou sai. Esforço P. Dono: tech-lead.
- **A6:** é falha da Guarda base, anterior ao item: a recusa não chega a ser chamada, então A2 não a cobre. Cartão (G1.2). Esforço M. Dono: tech-lead.
- **A7 e A8:** são defeitos do CI, não de segurança. Em A7 a recusa de `rm -rf .git` continua, e qualquer das duas mensagens serve à segurança. Vão à volta única E37.5. Dono: tech-lead.

Riscos que ficam fora, sem achado: `scripts/` da raiz não roda sozinho fora do sandbox. O postStart (`.devcontainer/devcontainer.json`) clona a main do remoto, e os atalhos `jarvis` e `jarvis-forge` executam do cache do plugin ou da cópia vigente. A exceção é `jarvis-forge --dev` (`--plugin-dir .`), já documentado como "sem a proteção da cópia vigente". `.git/config`, `.vscode` e os arquivos de shell da raiz são protegidos pelo sandbox (ADR 0009).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Varreduras de segredos, SAST e workflows: não se aplicam a este delta (um hook e fixtures, sem dependência nem workflow). A suíte inteira foi lida do CI do head. Local, com `flock /root/.forge-contrib/trava-teste-b.lock`: `tests.test_hooks.Hooks.test_fixtures_da_raiz_do_forge` OK e as sondas acima.
