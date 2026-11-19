---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-sandbox-controle
commit: 1aaea973c977ffa0111ca0482ac3e4b353863649
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-19
---
# Review de segurança: v0479-sandbox-controle

Revalidação (E29.9) no head 1aaea973, por delta: `forge-check parecer delta` de 03448b3d..1aaea973. Lido no domínio: `hooks/_comum.py` (`ler_trava`, e `gravar_json` fora do diff, `:2561-2564`), `hooks/agentes.py` (`ler_estado`, `pesado_livre`), `hooks/pesado.py`, `hooks/doutor.py` (`preparar_controle`), `bin/forge-init`, `bin/forge-pesado`, `bin/forge_sempre_atual.py`, `bin/forge-testes`, `templates/projeto/.claude/settings.json`, `docs/hooks.md:129`, as fixtures `tests/hooks/{agentes,pesado}/` do diff, as duas skills. Fora do domínio, lidos só para conferir A3 e A4: `tests/test_sandbox_controle.py:120-160`, `:270-300` e `docs/devops/v0479-sandbox-controle.md:5-61`. A rodada anterior está no git (parecer de 03448b3d).

## Gatilhos
Gatilhos: configuração do sandbox do Bash (controle de escrita), estado dos hooks de R-TETO (registro de agentes, trava pesada), teste de controle.

## Resumo
- **A1 fechado.** `pesado.fila` saiu da lista; o hook `pesado` grava `null` ao soltar (`hooks/pesado.py:387`); `forge-init` e o `SessionStart` do `doutor` criam `agentes.json` e `pesado.json` só quando faltam (`os.path.lexists`, sem seguir link); o arquivo de 0 byte vale como sem registro (`hooks/agentes.py:392`, depois das checagens de link, tipo e tamanho) e como sem trava (`hooks/_comum.py:2502`). JSON quebrado segue ilegível. `.forge/config.json` vem do modelo (`templates/projeto/.forge/config.json`).
- **Zerar o arquivo para soltar a trava:** não abre caminho novo. Dentro do sandbox o arquivo é `--ro-bind`: abrir com truncamento, `truncate`, `unlink` e `rename` sobre ele dão EROFS/EBUSY (sondas da 1ª rodada). O 0 byte só nasce quando o caminho falta, e faltar só é alcançável pelos caminhos fora da lista: a pasta mãe (A2) e o temporário vizinho (A5). Nos dois o agente já grava o conteúdo que quiser (`null`, `{"agentes": []}`), então tratar 0 byte como vazio não lhe soma poder. A tolerância afrouxa o HOOK-ESTADO-ILEGIVEL-LIBERA só para o 0 byte; o gravador é atômico (temporário e `os.replace`), então 0 byte por gravação interrompida não é caminho realista. `ler_trava` aceita espaço em branco como vazio e `ler_estado` exige 0 byte; nenhum dos dois o runtime produz, sem efeito.
- **Não negar a pasta mãe:** o motivo procede: `.forge/run/` tem arquivos gravados pelo Bash do time (`docs/devops/v0479-sandbox-controle.md:14`, `:61`) e `.git/forge` guarda `pr/`. Limite proporcional (ator interno, contorno deliberado por interpretador), registrado; o fecho é o cartão da identidade da pasta. No Forge o patch nega `.forge/` e `.git/forge/run` inteiros: o A2 só alcança `.git/forge` (rename) e o A5 não se aplica.
- **A3 fechado:** o teste soma `>`, `sort -o`, `git init` e `mv` por cima (`tests/test_sandbox_controle.py:296-298`) e o `ControleVazio` monta o vazio 0444 como o runtime. **A4 fechado:** a tabela e `docs/hooks.md:129` descrevem `.forge` como pasta na cópia do dono.
- Testes rodados no head: `tests.test_sandbox_controle` (14, OK, 2 pulados: bubblewrap aninhado negado aqui) e as 5 fixtures do delta e vizinha (`agentes/estado-vazio-0byte-libera`, `agentes/estado-ilegivel-texto-bloqueia`, `pesado/{falha,permissao-negada,pos-uso}-solta-trava`) pelo executor do `tests/test_hooks.py`, OK; o `test_hooks` inteiro passou de 500 s aqui e foi cortado. Sem execução de CI nem PR no head (`gh run list --commit` vazio): a recusa dentro do bubblewrap só tem prova no CI do PR, obrigatório para o merge.

## Achados
- A2 (recomendado) templates/projeto/.claude/settings.json:39 · Estado: registrado como limite (docs/hooks.md:129, devops:61); o ataque não entrou no teste do CI. Falta citar `.forge` como pasta mãe de `.forge/config.json` no modelo, não só `.forge/run`.
- A5 (recomendado) hooks/_comum.py:2562 · Em pasta gravável pelo Bash (modelo: .forge/run), o agente planta `pesado.json.<pid>.tmp` como link; gravar_json escreve nele e o os.replace põe o link no lugar (S1); ler_trava o segue e o agente controla a trava. Mesma família do A2, mesmo cartão.

## Sondas
- S1 · `python3 -I sonda.py` com `hooks/` do head: link `pesado.json.<pid>.tmp` -> arquivo do agente, `gravar_json(pesado.json, {"pid":1,"desde":1})`, o agente grava `null` no alvo · espera: pesado.json regular com a trava · obtido: `link: True -> .../alvo` e `ler_trava: None`

## Detalhe dos achados
**A2.** Correção mínima que falta: em `docs/hooks.md:129` e `docs/devops/v0479-sandbox-controle.md:61`, `.forge` (modelo) ao lado de `.forge/run` e `.git/forge`; o teste do rename fica no cartão. Severidade média, esforço P. Dono: tech-lead.

**A5.** Evidência: `hooks/_comum.py:2561-2564` cria o temporário com `write_text` (segue link, sem `O_EXCL`) na pasta do alvo; no modelo essa pasta é gravável pelo Bash. Caminho: subagente, com processo em segundo plano no seu namespace, planta links `pesado.json.<pid>.tmp` (o pid do hook não é conhecido: cobrir a faixa ou correr com inotify) para um arquivo fora da lista; na próxima tomada da trava o hook troca `pesado.json` pelo link e o processo escreve `null` no alvo. Em `agentes.json` o link só recusa (`O_NOFOLLOW` em `ler_estado`): falha fechada. S1 prova a mecânica fora do sandbox. Severidade média (ator interno, ruidoso, mesmo ganho do A2). Correção mínima: no `gravar_json`, abrir o temporário com `os.open(tmp, O_WRONLY|O_CREAT|O_EXCL|O_NOFOLLOW, 0o600)` e falhar se existir; o fecho completo (corrida de escrita no temporário) é o cartão do A2: pasta de controle sem nada gravado pelo Bash, conferida por identidade. Esforço P. Dono: tech-lead.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Suíte inteira: não rodada (brief); sem CI no head. Ferramentas: varredor de segredos e linters de workflow fora do PATH (lacuna; o diff não toca workflow nem segredo); bubblewrap aninhado negado (lacuna para sondar A2 e A5 dentro do sandbox).
