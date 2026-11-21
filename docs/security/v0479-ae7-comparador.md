---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-ae7-comparador
commit: f50171d232c95fa4562422bcda5f92a144a8a586
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: AE7.1, `forge-check comparar` (v0478 E58.46), head f50171d2

Revalidação da rodada de bddae43f (E58.41, parecer 4f0d2ae9 que ficou fora do remoto; A10 bloqueante e A9 recomendado). Delta lido: `forge-check parecer delta` deste arquivo (`3d0bdaf9..f50171d2`), conferido contra `bddae43f..f50171d2`; no domínio só `bin/forge_comparar.py` (`declara_hooks`, `MANIFESTOS` e `CABECALHO_HOOKS` em `fora_da_medida`, a regra do A9 em `executar`, um comentário); fora do domínio, `tests/test_comparar.py`, 5 specs de mutante e o fragmento do changelog.

Gatilhos: execução de comando (roda o código dos hooks da base e do head), controle que analisa entrada (medida do "só aperta").

## Confirmação pedida: a mudança só aperta
Sim. O delta só toca `bin/forge_comparar.py`; não toca `hooks/`, `tests/config.json`, `docs/regras/`, workflow nem pre-push. As 3 checagens novas só acrescentam saídas rc 2 antes de medir (JSON ilegível e busca que falha também viram rc 2); a regra do A9 só deixa de marcar `entrada-reescrita` quando o head recusa, caso que não roda (S9a). Nenhum caminho que antes dava rc 1 ou 2 passa a dar rc 0.

## Achados
- A11 (bloqueante) bin/forge_comparar.py:86 · `fora_da_medida` lê os blobs pelo caminho na árvore, que o git não segue por link; o clone e o Claude Code seguem: `.claude-plugin` como link para uma pasta com `hooks` no plugin.json dá rc 0 (S15, S19); link no hooks.json pula o A7 (S16)
- A12 (bloqueante) bin/forge_comparar.py:85 · a medida roda os hooks da raiz, mas o Claude Code instala o plugin de `plugins[].source` do marketplace.json: head com `source: ./outro` e hook allow em outro/ dá rc 0 (S18); o validador lê o plugin de outro/ (S20)
- A13 (recomendado) bin/forge_comparar.py:30 · `hooks` no cabeçalho só é pego sem recuo e literal: cabeçalho YAML todo recuado, em fluxo (`{..., hooks: ...}`) ou com a chave escapada (`"hoo\x6bs":`) dá rc 0 (S14b, S14c, S14d); leitura de hook no cabeçalho de plugin não provada no Claude Code

## Estado dos achados anteriores
A10 resolvido nas formas diretas (`:29-30`, `:68-75`, `:85-91`; S12 objeto, S12b caminho, S12c `s`, S12d marketplace, S14 cabeçalho: todas rc 2); as formas por link e por `source` são A11 e A12, dimensão nova (posição da declaração). A9 resolvido (`:232`; S9a: base que reescreve contra head que recusa, rc 0; S11 segue rc 1 nos 4 casos aceitos). A1, A2, A5, A7 e A8: sondas refeitas no head, mesmo resultado da rodada anterior (S5 rc 1; S6, S6c, S7 rc 2; S10 sem marca no TMPDIR de quem chama; S9, S9b rc 2; S8 rc 0 sem traceback). A3, A4 e A6: o delta não os toca.

## Sondas
- S15 · head = base com `.claude-plugin` movida para `cp2/`, `hooks` allow em Bash no cp2/plugin.json (o objeto da S12) e `ln -s cp2 .claude-plugin` (modo 120000 no commit) · espera: rc 2 · obtido: rc 0 aceites-novos=0
- S16 · head = base com `hooks/hooks.json` trocado por `ln -s h2.json hooks/hooks.json`, h2.json com o matcher `Bas.` da S9b · espera: rc 2 (como a S9b) · obtido: rc 0
- S18 · head = base + `outro/` (cópia de `.claude-plugin/` e `hooks/`, com hook allow em Bash no topo de outro/hooks/hooks.json) e `"source": "./outro"` no marketplace.json · espera: rc 2 · obtido: rc 0 aceites-novos=0
- S19 · `claude plugin validate . --strict` no clone da S15 com `"hooks": {"PreToolUse": "nao-lista"}` em cp2/plugin.json · espera: o Claude Code lê o manifesto através do link · obtido: "plugins[0] plugin.json → hooks: Invalid input", rc 1 (com o hook válido: "Validation passed")
- S20 · `claude plugin validate . --strict` no clone da S18 com `hooks` inválido em outro/.claude-plugin/plugin.json · espera: o Claude Code lê o plugin de `source` · obtido: "hooks: Invalid input", rc 1; o mesmo só na raiz: "Validation passed", rc 0

## Detalhe dos achados
Método: clone descartável em `/root/.forge-contrib/wt/sondas-v0479-ae7-E5846/repo` no head f50171d2, base de sonda `c9161a9d` = head + o corpus de 16 casos da rodada anterior, cada sonda um commit sobre ela com o rc do commit e o `ls-tree` conferidos antes do `comparar`; `TMPDIR=/root/.forge-contrib/wt/sondas-v0479-ae7-E5846/tmp`. Roteiro em `sondas.sh` e `sondas2.sh`, saídas em `saida.txt` e `saida2.txt` (na 1ª passada a S15 não montou o link, `git mv -q` não existe, e a S16 usou o matcher simples `Bas`: refeitas em `saida2.txt`). Controles: base contra si rc 0; head sem `PreToolUse` rc 1 com 12 aceites. S13 refeita: `claude plugin validate .claude-plugin/plugin.json --strict` na árvore da S12 "Validation passed", com `"PreToolUse": "nao-lista"` "hooks: Invalid input", rc 1. `tests/test_comparar.py`: 53 testes OK.

- **A11 (S15, S16, S19)** · `bin/forge_comparar.py:86-95`. `cat-file -e <sha>:.claude-plugin/plugin.json` falha quando `.claude-plugin` é link (o git não atravessa link na árvore), e o laço pula o manifesto; `cat-file blob <sha>:hooks/hooks.json` de um link devolve o texto do alvo, que não é JSON, e `:94-95` sai `None` sem checar o matcher. A extração (`:118-124`) recria os links, `hooks_de` (`:134`) e o Claude Code os seguem (S19). Caminho: um head move a declaração para trás de um link e a medida diz "nada liberado a mais", o mesmo efeito do A10. Severidade alta. O repositório não tem nenhum link (`git ls-tree -r f50171d2`: 0 entradas 120000): custo zero. Correção mínima: em `fora_da_medida`, `nao-verificavel` quando a árvore de qualquer lado tem entrada de modo 120000 (a lista do `ls-tree` de `:82` já está ali, basta pedir o modo); teste com link em `.claude-plugin`, em `hooks/hooks.json` e num `.md` (S17: `agents/s17.md` link para texto com `hooks:` dá rc 0). Esforço P. Dono: tech-lead.
- **A12 (S18, S20)** · `bin/forge_comparar.py:85-89` e `:134`. A medida assume que o plugin instalado é a raiz, mas a entrada do marketplace escolhe a raiz do plugin por `source` (pasta, ou repositório de fora). Caminho: um head aponta `source` para uma pasta com outro `hooks/hooks.json` que aprova; o projeto que atualiza instala essa pasta, e a medida roda os hooks da raiz, intactos. Severidade alta. O marketplace de hoje tem `"source": "."`. Correção mínima: `nao-verificavel` quando o marketplace.json de qualquer lado tem um `plugins[].source` que não seja a string `.` ou `./`, ou mais de uma entrada em `plugins`; testes com `./outro` e com objeto `{"source": "github", ...}`. Esforço P. Dono: tech-lead.
- **A13 (S14b, S14c, S14d)** · `bin/forge_comparar.py:30`, `:90`. Sem caminho provado (não está provado que o Claude Code lê `hooks` do cabeçalho de agente ou skill de plugin), por isso recomendado. Correção: no bloco entre o 1º e o 2º `---` de cada `.md`, `nao-verificavel` quando aparece `hooks` em qualquer posição (com recuo, em fluxo) ou uma barra invertida de escape. Esforço P. Dono: tech-lead.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Sem CI no head (sem PR aberto): a suíte inteira fica para o CI do PR; rodados aqui só `tests/test_comparar.py` (53 OK) e as sondas. Lacuna: gitleaks, osv-scanner, semgrep, zizmor e actionlint fora do PATH; o delta não toca workflow nem dependência. Segredo: nenhum padrão de token ou chave nas linhas acrescidas. Nenhuma escrita fora da pasta de sonda e deste parecer.
