# Teto fora do git (desenho)

Pedido v0478, etapa E159.1 (cartão TETO-FORA-DO-GIT). Só desenho: nenhum hook, script, teste, CI nem modelo de projeto foi alterado. Público: o dono e o time. Revisão: 2026-12-24. Base lida: develop 789fc141.

Origem: a pergunta de 2026-11-18 22:50 (A3, "onde fica o teto travado pelo sandbox") e a decisão do dono de 2026-11-19 08:28, opção (b): "o teto vai para um arquivo fora do controle de versão". O que muda: o teto, o ritmo, o piso de memória e a lista de pesados saem do `.forge/config.json`, que o projeto versiona, para um arquivo que o git não acompanha e o sandbox nega ao Bash, no Forge e no modelo de projeto. A guarda nova no hook `conformidade` fica para depois do PR #837, que mexe no mesmo arquivo. Custo zero (`R-CUSTO`). Regra do dono de 21/11 (item 3): cada fatia diz se é trava e qual sai.

## 1. O que existe hoje

| Quem | Evidência | Chaves |
|---|---|---|
| hook `agentes` (classe `Hook`) | `hooks/_comum.py:2647-2680` (une o projeto ao modelo `templates/projeto/.forge/config.json`) | `teto_agentes`, `teto_maximo`, `pesados`, `expiracao_horas`, `piso_memoria_gb`, `hooks_desligados` |
| hook `agentes` | `hooks/agentes.py:121-127` (piso), `:184-190` (ritmo), `:195-213` (teto), `:267-272` (peso); `:164-171` lê da raiz da sessão só no clone do Forge (A1 da v0478) | `piso_memoria_gb`, `ritmo`, `teto_*`, `peso` |
| hook `pesado` | `hooks/pesado.py:4` pela `Hook.config()` | `pesados` |
| `forge-check` | `bin/forge-check:490-503` (teto), `:4745-4746` (expiração), `:4760-4771` (piso) | idem |
| suíte em 2 partes | `scripts/suite-partes.py:259` | `piso_memoria_gb` |
| quem grava | `bin/forge-ritmo:40-54` (`ritmo`); `bin/forge-init:191-200` (`pesados` da stack) | `ritmo`, `pesados` |
| guarda do hook | `hooks/conformidade.py:3808-3812` e `:3912-3919` (só o config da raiz da sessão); `hooks/conformidade.json:37` | o arquivo inteiro |
| sandbox, modelo | `templates/projeto/.claude/settings.json:38-43`: `denyWrite` com `.forge/config.json` | o arquivo inteiro |
| sandbox, Forge | `.claude/settings.json:23-27`: `denyWrite` com `.forge/`; `.gitignore:20` ignora `/.forge` | a pasta inteira |
| ficam no `.forge/config.json` | `hooks/_comum.py:2513-2524` (`caminhos_extra`), `hooks/meta.py:234-236` (`idioma_do_dono`), `templates/projeto/.githooks/pre-push:318-335` (`registros`), `bin/forge-contador:61-72` (`teto_versao`), `bin/forge-copia:43` (o arquivo marca o projeto) | não mudam |

No Forge o arquivo já está fora do git (`.gitignore:20`) e coberto pelo `denyWrite` de `.forge/`. O problema está no **projeto**: lá o `.forge/config.json` é versionado (ADR 0005, item 1) e negado ao Bash. Por isso um `git pull`, `merge` ou `checkout` que mude o arquivo falha dentro do sandbox na cópia principal (`docs/engineering/v0479-sandbox-controle.md`, "Consequências").

## 2. O risco real

- **R1, merge que para no meio.** A `develop` do projeto traz um `.forge/config.json` novo (por exemplo, uma chave `registros` que o time acrescentou), e o Jarvis faz `git merge` na cópia principal: o git não consegue gravar o arquivo, e o merge fica pela metade, com a árvore suja. Severidade média: nada se perde, mas o fluxo para até o dono rodar o merge fora do sandbox.
- **R2, trava larga demais.** Negar o arquivo inteiro trava junto o que é do time (`caminhos_extra`, `registros`, `idioma_do_dono`), e uma mudança comum de projeto passa a depender do dono.
- **R3, teto que viaja no git.** Um teto versionado vai junto em todo clone e toda cópia do projeto, mas o teto é da máquina de cada um.

## 3. O desenho

Arquivo novo: **`.forge/limites.json`**, na cópia principal do projeto e do Forge. Um objeto JSON com as chaves que saem do `.forge/config.json`: `teto_agentes`, `teto_maximo`, `ritmo`, `piso_memoria_gb` e `pesados`. Com a recomendação da D2, também `peso` e `expiracao_horas`.

- **Fora do git:** no projeto, o `forge-init` e a migração acrescentam `.forge/limites.json` ao `.git/info/exclude` (o mesmo caminho do `--sem-versionar`, `bin/forge-init:224-245`) e ao `.gitignore`. No Forge, o `/.forge` do `.gitignore` já cobre.
- **Negado ao Bash:** no `denyWrite` do modelo, `.forge/config.json` sai e entra `.forge/limites.json`. No Forge, nada muda: `.forge/` já cobre.
- **Lido da raiz da sessão:** o leitor único passa a ser uma função `limites(hook)` em `hooks/_comum.py`. Ela lê `raiz_declarada()/.forge/limites.json` no projeto e no Forge, e o arquivo de uma cópia não vale, como o A1 da v0478 já faz no clone do Forge (`hooks/agentes.py:164-171`). `forge-check`, `suite-partes.py` e `forge-ritmo` importam essa função, sem um terceiro leitor.
- **Arquivo vazio vale como ausente:** o runtime do sandbox cria vazio e 0444 todo caminho negado que falta (sondado na v0479). Por isso, arquivo ausente, de 0 byte ou `{}` leva aos padrões do modelo (teto adaptativo, ritmo `equilibrado`, piso de 2 GB, pesados da reserva). JSON quebrado ou que não é objeto recusa o disparo, como hoje (`CONFIG_ILEGIVEL`, `hooks/agentes.py:1162`).
- **Criado antes do primeiro Bash:** o `preparar_controle` do hook `doutor` (`hooks/doutor.py:338-344`) cria `limites.json` com `{}` se ele falta, e o `forge-init` o cria com os `pesados` da stack.
- **Quem grava:** o `forge ritmo` grava em `limites.json`, por arquivo temporário e `rename` (o 0444 do vazio não impede, porque a pasta segue gravável fora do sandbox). Ele continua sendo do dono, no terminal, como hoje (`skills/novo-projeto/SKILL.md:27`).
- **Chave velha no `.forge/config.json`:** depois da migração, ela não vale mais. O `doutor` avisa uma vez por dia ("`teto_agentes` em .forge/config.json não vale; está em .forge/limites.json"). Não há queda para o arquivo velho: se houvesse, o versionado voltaria a mandar no teto.

### Fatias (nesta ordem, cada uma num PR)

**C1, leitor e arquivo novo (não é trava nova).** `limites(hook)` em `_comum`; `Hook.config`, `agentes`, `pesado`, `forge-check`, `suite-partes` e `forge-ritmo` passam a usá-la; `doutor` e `forge-init` criam o arquivo. Dono: `devops-engineer`. Até 150 linhas de código (H1). Se passar, separe o `forge-ritmo` e o `forge-init` numa C1b.
- Pronto quando: (a) `teto_agentes: 2` em `limites.json` limita o hook a 2, e o mesmo valor só no `config.json` não limita mais; (b) `limites.json` de 0 byte e 0444 leva ao teto adaptativo e não ao `CONFIG_ILEGIVEL`; (c) JSON quebrado recusa o disparo; (d) o `limites.json` de uma cópia (clone ou worktree) é ignorado; (e) `forge ritmo economico` grava em `limites.json` 0444 vazio e o hook lê 1; (f) o `forge-check fila` mostra o mesmo teto do hook; (g) as fixtures de `tests/hooks/agentes/` que gravam `config.json` passam a gravar `limites.json`.

**C2, migração e modelo (troca de trava: uma sai, outra entra).** É a migração `migrations/<versão>/migrar` com `LEIA.md` (ADR 0005), mais o `denyWrite` do modelo (`.forge/config.json` sai, `.forge/limites.json` entra), o `.gitignore` do projeto e o texto de `R-TETO.md:14`, ADR 0003 (item 6), ADR 0001 (linha 21) e `docs/hooks.md`. Sai a trava do sandbox sobre o `config.json`; entra a trava sobre o `limites.json`. Dono: `devops-engineer` (modelo e migração) e `software-architect` (emenda das ADRs).
- Pronto quando: (a) num projeto da versão anterior, a migração move as 5 (ou 7) chaves para `limites.json`, apaga-as do `config.json` e não toca nas outras; (b) rodada duas vezes, a segunda não muda nada; (c) com `config.json` ilegível, avisa e não toca em nada; (d) `limites.json` já existente e não vazio não é sobrescrito, e a migração diz quais chaves ficaram no `config.json` para o dono decidir; (e) `test_sandbox_controle` confere o novo `denyWrite`; (f) `git merge` que muda o `config.json` passa no sandbox (prova do R1, no CI, como hoje).

**C3, guarda do hook (depois do #837; aperta, sem trava que sai).** `CONFIG_DA_RAIZ` (`hooks/conformidade.py:3809`) e `ESTADO_NO_TEXTO` (`:3812`) passam a cobrir também `.forge/limites.json`. Entra uma linha nova em `hooks/conformidade.json` ao lado da `:37`. A recusa do `config.json` da raiz fica ou sai conforme a D3. Dono: `devops-engineer`; o parecer de segurança diz se aperta ou é neutro.
- Pronto quando: (a) `Write`, `Edit`, `sed -i`, `mv` por cima e `python3 -c` sobre `.forge/limites.json` da raiz são recusados para todo papel; (b) o `limites.json` de outra pasta segue livre; (c) ler (`cat`) segue livre; (d) mutante declarado por guarda nova.

## 4. Migração dos projetos

1. O dono atualiza o plugin, e o `forge-upgrade` roda a migração da C2 no projeto. A migração roda no terminal do dono, fora do sandbox. Dentro de uma sessão ela falharia, porque o `denyWrite` velho ainda nega o `.forge/config.json` de onde as chaves saem. O `forge-upgrade` detecta o sandbox e imprime o comando para o dono em vez de tentar.
2. A migração imprime o que moveu, chave por chave, e o diff do `config.json` fica para commit do time (`chore(forge): limites fora do git`).
3. O `forge-upgrade --ligar-sandbox` une o `denyWrite` novo ao do projeto. Até o dono reabrir a sessão, vale o velho.
4. Projeto que não migrar segue funcionando até a versão da C1: depois dela, as chaves do `config.json` deixam de valer e o `doutor` avisa a cada dia, com o comando da migração.

## 5. Reversão

- **Critério:** em 14 dias depois da C2 na `main`, reverter se (a) um projeto ficar com teto diferente do que o dono gravou (relato do dono ou `forge-check fila` divergente do arquivo), ou (b) o `doutor` não criar o arquivo antes do primeiro Bash e aparecer `CONFIG_ILEGIVEL` no `erros.log` de um projeto.
- **Como:** revert dos PRs na ordem C3, C2, C1. Uma migração de volta (`migrar --voltar`) devolve as chaves ao `config.json` e apaga o `limites.json`, e o `denyWrite` do modelo volta à lista da v0479.
- **Como medir:** (1) `git merge` de mudança no `config.json` dentro do sandbox, que hoje falha (R1) e passa depois da C2; (2) o teto que o `forge-check fila` mostra é igual ao do hook com o `limites.json` vazio, fixo e econômico (C1, f); (3) zero `CONFIG_ILEGIVEL` no `erros.log` em 14 dias.

## 6. Decisões do dono (`R-DECISAO`)

- **D1, nome e lugar do arquivo.** a) `.forge/limites.json` na cópia principal, ao lado do `config.json`; b) `~/.forge/projetos/<chave>/limites.json`, fora da pasta do projeto. **Recomendo a**: o dono acha o arquivo onde já procura, o `git clean -fdx` não o alcança (o arquivo está ignorado, e o `denyWrite` impede apagar), e (b) obriga a uma chave estável por projeto, que hoje só existe na máquina (`_maquina.identidade`).
- **D2, quais chaves saem.** a) só as 5 do pedido (teto, teto máximo, ritmo, piso, pesados); b) as 5 mais `peso` e `expiracao_horas`. **Recomendo b**: as duas também afrouxam o teto (peso maior toma a vaga dos outros projetos; expiração maior ou menor muda a conta dos agentes vigentes), e deixá-las no versionado mantém o R3. `teto_versao` (`bin/forge-contador:61`) é regra de versão do time e fica no `config.json`.
- **D3, a guarda do `config.json` depois da C3.** a) a recusa do hook ao `config.json` da raiz fica, e só o sandbox deixa de negar; b) a recusa sai e o arquivo passa a ser do time como qualquer outro. **Recomendo a**: `registros` roda comando no `pre-push` (`templates/projeto/.githooks/pre-push:318-335`) e `hooks_desligados` desliga hook (`hooks/_comum.py:2800-2804`), e os dois seguem sendo controle. A recusa do hook barra o agente e não barra o `git merge` (o git não passa pelo hook), e o R1 se resolve do mesmo jeito.
- **D4, o pesado da stack.** a) `pesados` sai para o `limites.json`, como pede o pedido; b) a lista da stack fica versionada, e só o acréscimo local vai ao `limites.json`. **Recomendo a**, pelo pedido e por ser mais simples (uma fonte só). O custo: o pesado novo do time não chega por git aos outros clones; chega pela stack (`stacks/<nome>/pesados.json`) numa versão do Forge.

## 7. Casos de abuso (para o `qa-engineer`, quando cada fatia for aberta)

- C1: `limites.json` de uma worktree ou cópia com `teto_agentes: 99` · disparo → hook `agentes` · vale o da raiz da sessão.
- C1: `limites.json` como link simbólico para um arquivo gravável · disparo → hook · recusa como ilegível (o link não é seguido).
- C1: `limites.json` de 0 byte depois de apagado e recriado pelo runtime · disparo → hook · padrões, sem recusa.
- C2: `config.json` do merge que traz `teto_agentes: 99` · merge → hook · a chave não vale, e o `doutor` avisa.
- C3: `d=.forge; python3 -c "open('$d/limites.json','w')"` · Bash → conformidade · recusa (o nome no texto da linha, `ESTADO_NO_TEXTO`).
- Limite herdado (A2 da v0479): renomear a pasta mãe `.forge` escapa da trava por arquivo; continua no cartão do inode guardado em `~/.forge/maquina`.

## 8. Fora do corte

`hooks_desligados`, `caminhos_extra`, `registros` e `idioma_do_dono` ficam no `config.json` versionado (são do time, não da máquina). Se `hooks_desligados` deve ir ao arquivo local, é um cartão próprio. A fila da máquina e o registro de agentes não mudam (`~/.forge/maquina`, `.forge/run/`). A prova no sandbox real (decisão do dono de 08:28, "a, com cartão para provar no sandbox real") é outro cartão.
