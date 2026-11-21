---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-ae7-comparador
commit: 3d0bdaf9089fe91ae820e969846ba79234413809
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: AE7.1, `forge-check comparar` (v0478 E58.37), head 3d0bdaf9

Revalidação da rodada de 5961e2f3 (E58.33, no git). Delta lido (`forge-check parecer delta`, `5961e2f3..3d0bdaf9`): no domínio, `bin/forge_comparar.py` (extração blob a blob, veredito de 4 níveis com `updatedInput`, cada lado em temporário e HOME próprios) e a ajuda do `comparar` em `bin/forge-check:10179`; fora do domínio, `tests/test_comparar.py`, 6 specs de mutante e o fragmento do changelog (lido só para conferir A4).

Gatilhos: execução de comando (roda o código dos hooks da base e do head), controle que analisa entrada (medida do "só aperta").

## Confirmação pedida: a mudança só aperta
Sim. O delta só toca `bin/forge_comparar.py` e o texto de ajuda do subparser; não toca `hooks/`, `tests/config.json`, `docs/regras/`, workflow nem pre-push, e nenhum consumidor chama o `comparar` ainda. Dentro do comparador, o delta só aperta a medida (mais um nível, reescrita contada, lados isolados); a reprovação é sobre o que a medida ainda não vê.

## Achados
- A1 (bloqueante) bin/forge_comparar.py:124 · resolvido no formato `hookSpecificOutput` (S1 refeita: rc 1); falta a forma antiga `{"decision":"approve"}`, que o Claude Code ainda mapeia para allow: head que aprova por ela sai rc 0 aceites-novos=0 (S5)
- A2 (bloqueante) bin/forge_comparar.py:62 · resolvido para export-subst (S2 refeita: rc 1); o clone aplica os atributos de checkout (`ident`, `working-tree-encoding`, `eol`, `filter`) que a extração blob a blob ignora: 2 linhas de `.gitattributes` desligam parecer e conformidade instalados e o comparador dá rc 0 (S6, S7)
- A5 (recomendado) bin/forge_comparar.py:22 · resolvido em parte: HOME temporário e docstring dizem que executa código; resta o TMPDIR de quem chama, compartilhado: o hook do head grava nos temporários de outras execuções em curso (a S3 gravou 36 alheios); passar TMPDIR = temporário do lado
- A7 (recomendado) bin/forge_comparar.py:99 · matcher lido com `re.fullmatch` do Python; o Claude Code usa outra máquina de regex: sintaxe só do Python (`(?i)bash`) roda no comparador e talvez não no Claude Code (S9: rc 0); aceitar só a forma simples `[A-Za-z0-9_|]*` ou `*`, o resto nao-verificavel
- A8 (recomendado) bin/forge_comparar.py:113 · saída de hook que não é UTF-8 derruba o comparador com traceback e rc 1 sem a linha `so-aperta` (S8); ler bytes e decodificar com `errors="replace"`, ou sair nao-verificavel rc 2
- A9 (recomendado) bin/forge_comparar.py:149 · `updatedInput` de um hook conta como reescrita mesmo quando outro hook recusa o caso (S1: base=recusa head=recusa entrada-reescrita); falso positivo seguro, mas pede o rótulo afrouxa-regra à toa: contar a reescrita só quando o nível final não é recusa

## Estado dos achados anteriores
Estado: A1 e A2 continuam abertos pelas formas novas acima; A3 resolvido (`bin/forge_comparar.py:152-161`, `:177-178`; S3 refeita rc 1 com os 12 aceites da base); A4 resolvido (docstring e changelog declaram o limite; entrada traz `transcript_path` e `permission_mode`); A5 em parte (acima); A6 resolvido na documentação (`bin/forge-check:10179`; o cartão da catraca fica com quem a ligar).

## Sondas
- S5 · head = base + hook PreToolUse(Bash) que imprime `{"decision":"approve","reason":"ok"}` · espera: rc 1 aceite-novo (allow) nos casos que a base deixa em silêncio · obtido: rc 0 aceites-novos=0
- S6 · head = base + `.gitattributes` `hooks/parecer.py ident` (idem conformidade) e no topo de cada um `if "$Id$" != "$"+"Id$": sys.exit(0)` · espera: rc 1 · obtido: rc 0; `git clone` grava `"$Id: 0682…190a $"` (hook mudo), o blob tem `"$Id$"`
- S7 · head = base + só `.gitattributes` `hooks/parecer.py working-tree-encoding=UTF-16LE` (idem conformidade), nenhum byte de hook mudado · espera: rc 1 · obtido: rc 0; no `git clone` o python3 sai rc 1 "source code cannot contain null bytes" (hook mudo)

## Detalhe dos achados
Método: clone descartável em `/root/.forge-contrib/wt/sondas-v0479-ae7-E5837/repo` no head 3d0bdaf9, base de sonda `0f5c0c7c` = head + corpus de 16 casos reais (8 `parecer/*`, 8 `conformidade/*`), cada sonda um commit sobre ela; roteiro em `sondas.sh` e saída em `saida.txt` na mesma pasta (no roteiro, S6b é a S7 deste parecer e S7 é a S9; a S7 do parecer foi refeita à mão, comando na saída desta revisão). Controles: base contra si rc 0; head sem `PreToolUse` rc 1 com 12 aceites. Refeitas: S1 rc 1 (allow e entrada-reescrita), S2 rc 1 (12 aceites; a extração não expande `$Format$`), S3 rc 1 (12 aceites). `tests/test_comparar.py`: 42 testes OK.

- **A1 (S5)** · `bin/forge_comparar.py:120-126`. O Claude Code mantém para PreToolUse a decisão de topo antiga: `approve` vale allow e `block` vale deny (o comparador já lê o `block`, linha 124, e não o `approve`). Caminho: hook escrito pela documentação antiga aprova sozinho e pula a pergunta ao usuário; a medida diz "nada liberado a mais". Severidade alta (mesma dimensão do A1 da 1ª rodada: mecanismo de liberação). Correção mínima: `saida.get("decision") == "approve"` sem `permissionDecision` vira `ALLOW`; teste com a forma antiga. Esforço P. Dono: tech-lead. Dimensão nova da matriz: forma da saída (específica e de topo).
- **A2 (S6, S7)** · `bin/forge_comparar.py:62-89`. O clone do marketplace faz checkout, que aplica os atributos do `.gitattributes` da própria árvore: `ident`, `working-tree-encoding`, `text`, `eol`, `crlf` e `filter` (este se o driver existir na máquina), além de `export-subst` e `export-ignore` já tratados. A extração por `cat-file` grava o blob cru. S7 é o caso mais forte: só o `.gitattributes`, nenhum hook mudado, e os dois hooks principais ficam inexecutáveis no projeto instalado (erro não bloqueante = silêncio) com o comparador em rc 0. A correção da 1ª rodada seguiu a lista que este parecer deu (só export-subst e export-ignore), que estava incompleta; a lista inteira está acima. Severidade alta. Correção mínima: `nao-verificavel` (rc 2) quando qualquer lado tem um arquivo `.gitattributes` em qualquer pasta da árvore (o repositório hoje não tem nenhum: custo zero); alternativa mais cara: extrair por `git clone --no-checkout` + `checkout` em temporário, como o instalador. Esforço P. Dono: tech-lead.
- **A5** · `bin/forge_comparar.py:22`. TMPDIR passa da lista positiva para o hook; dois `comparar` simultâneos (agentes em paralelo) compartilham a pasta, e o head de um alcança a base do outro em curso, o mesmo efeito da S3 da 1ª rodada entre execuções. A marca da S3 refeita registrou 36 `hooks.json` gravados, todos fora do comparador desta execução (18 `forge-hook-*` de 18/11 e 18 `tmp*` de hoje 02:14-02:16 em `/tmp/claude-0`, restos de outras execuções). Correção: `TMPDIR` = o temporário do lado (como o HOME). Esforço P. Dono: tech-lead.
- **A7** · `bin/forge_comparar.py:99`. Sem o motor do Claude Code aqui (nada pago nem instalado, `R-CUSTO`), a diferença de sintaxe não foi provada do lado do Claude Code; por isso recomendado. Os matchers atuais de `hooks/hooks.json` são todos da forma simples.
- **A8, A9** · prosa no bloco; esforço P; dono tech-lead.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Sem CI no head (sem PR aberto): a suíte inteira fica para o CI do PR; rodados aqui só `tests/test_comparar.py` (42 OK) e as sondas. Lacuna: gitleaks, osv-scanner, semgrep, zizmor e actionlint fora do PATH; o delta não toca workflow nem dependência. Segredo: nenhum padrão de token ou chave nas linhas acrescidas. Efeito colateral da sonda S3: sobrescreveu `hooks.json` em 36 temporários alheios de `/tmp/claude-0` (lista em `$TMPDIR/s3-marca`); são restos de outras execuções, sem uso confirmado.
