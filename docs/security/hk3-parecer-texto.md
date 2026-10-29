---
tipo: revisao-seguranca
contrato: 1
pedido: hk3-parecer-texto
branch: melhoria/hk3-parecer-texto
commit: 7b2a225fb476be9c09c3b1a2b41792b7fcaec6ad
parecer: reprovado
revisor: forge:security-engineer
data: 2026-10-29
---
# Review de segurança: hk3-parecer-texto (HK3-PARECER, PR B, E2)

Diff revisado: `d14a7133eb608f3b02298931e76ddc8ccfe55c20...7b2a225fb476be9c09c3b1a2b41792b7fcaec6ad` (`hooks/parecer.py` +55 -12, `docs/hooks.md`, fragmento de changelog e o corpus `tests/hooks/parecer/texto-*`). Requisito: o modelo de ameaças (`~/.forge-contrib/docs/security/hk3-parecer-ameacas.md`, E2) e as DECISÕES TÉCNICAS de 2026-10-29 12:06 e 12:34: o heredoc só fica isento quando a chamada inteira é de `cat` (`sed -n <números>p <arquivo>` conta como `cat`), e nenhuma forma que executa merge, pull ou gh pr passa.

Método: sondas locais e passivas contra o hook de `7b2a225` e contra o da base `d14a713` (mesmo corpo de fixture, cwd na integração, `git merge melhoria/x` sem parecer), 187 comandos em seis lotes (terminador e delimitador do heredoc, `sh -c`, `eval`, `merge-base`, `sed -n`, lançadores); o que liberou foi conferido contra o bash real (com `echo` no lugar do merge). Nada foi executado fora do bash local; nenhuma varredura externa.

## Gatilhos
`R-SEGURANCA`: controle do Forge (`hooks/parecer.py`, o portão `R-REVIEW`/`R-QA` na entrada da integração). Não toca pipeline, contêiner nem IaC, não mexe em segredo e não usa rede.

## Achados
- A1 (bloqueante) hooks/parecer.py:587 · a isenção do cat libera heredoc cujo terminador o hook calcula diferente do bash (`<<$'EOF'`, `<<$"EOF"`, `<<$'E\x4fF'`, `<<EOF\` com nova linha e `EOF`, `<<\` com nova linha, `<<-EOF` com `\`): o git merge da linha seguinte roda e o hook libera (rc=0)
- A2 (recomendado) hooks/parecer.py:193 · `env`, `nice`, `timeout` e `xargs` antes de `git merge`/`git pull` liberam (rc=0), igual na base `d14a713`, ao contrário do que docs/hooks.md:93 diz de lançadores seguidos; fora do delta, cartão próprio
- A3 (recomendado) hooks/parecer.py:41 · `SED_LE` sem âncora de palavra: `xsed -n 1p f` ou `/x/sed -n 1p f` viram `xcat f` no texto lido; sem contorno achado (não casa com `SO_CAT`), mas o regex deve exigir início de palavra
- A4 (recomendado) tests/hooks/parecer/texto-barra-heredoc-lido-e-ls.json:1 · o corpus de barrados não tem os delimitadores fora da forma `<<'FIM'` do A1; cada forma do A1 vira fixture barrada e mutante (qa-engineer)

## Detalhe dos achados
**A1 (bloqueante, alta).** Evidência: `hooks/parecer.py:44` (`SO_CAT`) e `:587` (`and not SO_CAT.fullmatch(comando)`), onde `comando` é a linha depois de `tirar_heredocs`. A isenção pula a rede D (`fora_da_gramatica_com_heredoc`), que na base recusava qualquer heredoc fora da forma `<<'FIM'` justamente porque o hook não prova onde o bash termina o corpo. Com `cat` na chamada, o hook leva tudo depois do `<<` por corpo; o bash termina o corpo no terminador que ele calcula e executa o resto. Caminho de ataque: um agente (ou texto injetado num brief, issue ou saída de ferramenta que o agente copia) emite uma chamada de cat com o delimitador `$'EOF'`; o portão de parecer não vê o merge de integração e a integração recebe código sem review nem QA, que é o que o controle existe para impedir. Provas, todas rc=0 em `7b2a225`, rc=2 na base, e conferidas no bash real (executam a linha depois do terminador):
- `cat <<$'EOF'` + `EOF` + `git merge melhoria/x` (o bash toma `$'EOF'` como delimitador `EOF`); o mesmo com `<<$"EOF"` e `<<$'E\x4fF'`;
- `cat <<EOF\` (barra invertida e nova linha) + `EOF` + `EOFEOF` + `git merge melhoria/x` (a continuação junta `<<EOFEOF`);
- `cat <<\` (barra invertida e nova linha) + `EOF` + `EOF` + `git merge melhoria/x` (junta `<<EOF`);
- `cat <<-EOF` + `\` + `<tab>EOF` + `git merge melhoria/x` (a continuação no corpo forma `<tab>EOF`, que o `<<-` aceita).
Já certos, sem achado: `<<'EOF'x`, `EOF ` com espaço, ` EOF` com espaço, `EOF` com `\r`, `<<-` com espaços, `$(`/crase no corpo sem aspas (recusam), `\$(` e crase escapada (inofensivos). Classe: `terminador-do-heredoc-diferente-do-bash` (mesma família da AR-7, `pasta-do-git-diferente-do-bash`: o hook calcula a coisa de um jeito e o bash de outro). Correção mínima: a isenção do `cat` só vale quando todo `<<` de `original` é `<<` ou `<<-` seguido de `'PALAVRA'`, `"PALAVRA"` ou `PALAVRA` (`[A-Za-z_][A-Za-z0-9_]*`) e depois só espaço, redirecionamento simples ou fim da linha, e quando nenhuma linha de comando (fora dos corpos) tem `\` nem `$`; qualquer outro delimitador volta à rede D, como na base. Esforço P. Dono: `tech-lead`. Dimensão nova da matriz de heredoc: forma do delimitador × continuação de linha × `<<-`.

**Revisado e sem achado.** (1) `merge-base`: o `MERGE = merge(?!-base\b)` só tira o subcomando `merge-base`; `git merge-base a b && git merge x`, `git merge -base x`, `merge-base-x` e a ofuscação `merge\-base` seguem como na base e o merge real continua visto. (2) `sh -c` inofensivo: as 60 formas sondadas de executar merge dentro do texto (`&`, `|`, `;`, `&&`, `||`, `if`/`while`/`do`, `{ }`, `( )`, `$X`, prefixo de atribuição, `>f`, funções `sleep () ( … )` e `sleep () while …`, `\git`, `"git"`, `$'…'` aninhado, aspas sem par, `$(`, crase, `<(`, `>(`, aqui-string, argumentos depois do script, segundo `-c`, `eval` antes ou depois, pipe para `sh`) seguem recusadas; `g\it` passa igual na base (ofuscação, fora do escopo registrado). `sh -c 'sleep 1' sh -c 'git merge …'` passa e é correto: o segundo `-c` é argumento do `sleep`. (3) `sed -n`: só vira `cat` com números e arquivos de caracteres literais e terminador logo depois; `-i`, `e`, `w`, opção depois do arquivo, metacaractere e `-e` não viram. (4) Corpos sem aspas com `$(` ou crase, também por continuação (`$` + `\` + nova linha + `(`), recusam. (5) `heredoc gravado` + programa (M3) segue barrado, e `bash`/`sh` recebendo o corpo também.

PA-7 (`docs/engineering/achados-recorrentes.md`): conferidas as classes por item: `lista negativa em trava` (AR-3) não se aplica (a lista do `sh -c` é positiva); `python sem -I` (AR-5) não se aplica (sem python novo no caminho); `pasta-do-git-diferente-do-bash` (AR-7) se repete no A1, na forma do terminador do heredoc; `mascara-do-shell-esconde-codigo` (AR-6) coincide com a ofuscação já registrada. A linha AR do A1 fica com o `tech-lead` (review), que a grava; cito a classe aqui.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: só `python3` local, o bash do sistema e o corpus do próprio hook; `gitleaks`, `osv-scanner`, `semgrep`, `zizmor` e `trivy` não rodaram (sem segredo, dependência, workflow nem imagem no delta; lacuna registrada). A suíte do item (`tests.test_hooks_parecer_pasta`) não foi rodada por mim: a carga da máquina ficou acima do teto na maior parte do tempo e o parecer não depende dela, só das sondas.
