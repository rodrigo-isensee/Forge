---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-hook-raiz-forge
commit: 10c1b834b6fb062bfb2f9b7d9020dbbcbe828abf
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-27
---
# Review de segurança: v0481 (E37.7, #930, volta 1, por delta)

Gatilhos: hook de bloqueio (`hooks/conformidade.py`), R-CONFORMIDADE, R-VERIFY (pre-push da raiz), o que roda fora do sandbox (postStart do container como root), o manifesto que decide as travas da sessão.

## Resumo
- Delta lido (`forge-check parecer delta`, `baffa052..10c1b834`): no domínio, `hooks/conformidade.py` (`EM_VIGOR_NA_RAIZ`, `MOTIVO_EM_VIGOR`, `EM_VIGOR_NO_TEXTO`, `caminho_barrado`, `checar_texto`, `destino_opaco`, `barrar` e o recurso de `prova_fora_de_projeto`), `docs/hooks.md:69`, as 33 fixtures `raiz-forge-*` e `estadoclone-rm-git-bloqueia` e `tests/test_hooks.py`. Fora do domínio: o índice das fixtures, os mutantes e o fragmento do changelog.
- Estado dos achados da 1ª rodada:
  - A1: resolvido. S1 a S4 dão rc 2, e a sonda N5 (heredoc do interpretador no manifesto) também.
  - A2: parcial. S5 e o valor calculado passam a recusar (N7, N8, N10, N11). A variável com resto passa: A9.
  - A3: resolvido. S6 dá rc 2, e o tech-lead com a raiz em `melhoria/*` também recusa (T1 a T4).
  - A4: cartão. O limite está registrado em `docs/hooks.md:69` (cartão G4).
  - A5: resolvido (S3, N9).
  - A6: cartão. O limite está registrado em `docs/hooks.md:69`.
  - A7 e A8: resolvidos. A suíte está verde no CI do head.
- Efeito colateral em `wt/`: o texto de interpretador que escreve e cita uma entrada recusa também na cópia (L1, L9). **Aceitável:**
  - é a mesma recusa do projeto (L1 e L9 dão rc 2 nos dois modos);
  - Write, Edit, `sed -i` (L5) e o destino por variável (L4) seguem livres na cópia;
  - o heredoc de `git commit -m` (L2) e o de um arquivo de documentação (L3) que citam `.githooks` também seguem livres.
- Legítimos na raiz, todos com rc 0: a leitura por interpretador (L6), o `cat` da entrada para `$TMPDIR` (L7) e o `grep` para `$TMPDIR` (L8).
- ci: 10c1b834b6fb062bfb2f9b7d9020dbbcbe828abf vermelho
  - A suíte (3.12 e 3.14, partes 1 a 5), a instalação, os passos e as verificações longas estão verdes (run 45938234240).
  - `bateria (pareceres)` e `catraca` (run 45938234292) estão vermelhas por processo: falta parecer e falta o rótulo `afrouxa-regra`. `bateria` é o agregador.

## Achados
- A9 (bloqueante) hooks/conformidade.py:4347 · explorável: S7 · destino_opaco só calcula o destino sem resto; `D=.githooks; printf x > $D/pre-push` (S7) e `D=.claude-plugin; printf '{}' > $D/plugin.json` (S8) passam na raiz do Forge (rc 0; no projeto, rc 2), contra docs/hooks.md:69
- A10 (recomendado) hooks/conformidade.py:130 · ESCRITA_NO_TEXTO não vê `open(…,'r+')` com `print(file=)` (N1) nem `subprocess` (N4): gravam .githooks/pre-push na raiz e no projeto (rc 0); o controle de fato é o sandbox negar a escrita nessas entradas da raiz, como já nega .git/hooks
- A11 (recomendado) hooks/conformidade.py:4301 · checar_texto do clone só casa a entrada literal; `os.path.join('.git','hooks',…)` (N2) e `'.git/' + 'hooks/…'` (N3) passam na raiz do Forge (no projeto, rc 2 pelo `.git`); hoje o sandbox nega .git/hooks, então sem caminho realista

## Sondas
- S7 · Bash `D=.githooks; printf x > $D/pre-push`, cwd na raiz da sessão (clone do Forge), papel devops-engineer · espera: rc 2, como no projeto (`$D` com ação crítica) · obtido: rc 0
- S8 · Bash `D=.claude-plugin; printf '{}' > $D/plugin.json`, cwd na raiz da sessão do Forge, papel tech-lead, raiz em melhoria/z · espera: rc 2 (o manifesto decide as travas) · obtido: rc 0

## Detalhe dos achados
Como as sondas rodaram: `/root/.forge-contrib/wt/_sec130-v0481-sonda.py <cópia> forge|projeto` (36 entradas) e `_sec130-v0481-sonda-tl.py` (5 entradas, papel tech-lead). As duas montam a fixture `raiz-forge-s0-write-githooks-bloqueia` e rodam o hook do head revisado. No arquivo, S7 é a entrada N6 e S8 é a T5.

- **A9 (alta):** a ameaça é a da 1ª rodada. Um agente sob injeção grava o pre-push ou o manifesto da raiz numa chamada só. Com o pre-push, ganha execução fora do sandbox no próximo push do dono. Com o manifesto, desliga a detecção da sessão do Forge e todas as travas dela.
  - A causa: `GuardaDaProva.destino_opaco` (`hooks/conformidade.py:4347`) retorna quando o destino não é "sem resto". A Guarda base cobre esse caso só para o `.git` (`resto_colado`, por isso `D=.git; printf x > $D/hooks/pre-commit` recusa).
  - Correção mínima: no clone, com o destino opaco com resto, recusar quando um texto preciso do valor (`textos_do_valor(caminho)[0]`) casa `EM_VIGOR_NO_TEXTO`. Isso mantém livre a linha `printf x > $TMPDIR/y; cat .githooks/pre-push` (fixture `raiz-forge-variavel-com-resto-cita-githooks-libera`).
  - Fixtures que faltam: S7 e S8 na raiz (rc 2), e as duas na cópia de `wt/` (rc 0).
  - Esforço P. Dono: tech-lead.
- **A10 (média):** é lacuna da Guarda base, anterior ao item e igual no projeto. A família "como o interpretador grava" é aberta: `open` com `r+` e `print(file=)`, `subprocess`, `os.link`, um script em `$TMPDIR` rodado depois. Fechá-la caso a caso não termina, e a ADR 0009 (seção 6) já a registra como limite do hook.
  - Correção proposta, decisão do dono (R-DECISAO): negar no sandbox a escrita em `.githooks/`, `.devcontainer/`, `.devcontainer.json` e `.claude-plugin/` da raiz, como o sandbox desta sessão já nega `.git/hooks` (conferido com `test -w`: `.git/hooks` protegido; `.githooks`, `.devcontainer` e `.claude-plugin` graváveis).
  - Até lá, o hook pode somar ao `ESCRITA_NO_TEXTO` o modo `r+`/`x` e o `print(... file=`.
  - Cartão (G1.2), corrigido antes do merge ou levado ao dono. Esforço P (sandbox) ou M (regex). Dono: devops-engineer (configuração do sandbox), tech-lead (regex).
- **A11 (baixa):** a paridade com o projeto falha no texto de interpretador que monta `.git/hooks` por partes. Hoje não há caminho realista, porque o sandbox nega a escrita em `.git/hooks`. Correção mínima em `checar_texto` do clone (`:4300`): tratar a citação de `.git` como nome inteiro como `.git/hooks/` da raiz, como o projeto faz pelo `.git`. Esforço P. Dono: tech-lead.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Varreduras de segredos, SAST e workflows não se aplicam (um hook e fixtures, sem dependência nem workflow). A suíte inteira foi lida do CI do head. Local, com `flock /root/.forge-contrib/trava-teste-b.lock`: `tests.test_hooks.Hooks.test_fixtures_da_raiz_do_forge` OK (10,6 s) e as sondas acima.
