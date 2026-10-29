---
tipo: revisao-seguranca
contrato: 1
pedido: hk3-parecer-texto
branch: melhoria/hk3-parecer-texto
commit: cf6bf0adc637685b8f4773e5f9ea2f59c373cbf1
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-29
---
# Review de segurança: hk3-parecer-texto (HK3-PARECER, PR B, E2), revalidação da volta 1

Revalidação por delta (`7b2a225fb476be9c09c3b1a2b41792b7fcaec6ad..cf6bf0adc637685b8f4773e5f9ea2f59c373cbf1`) do parecer reprovado de `bef210359d71577e3f8ed9e33b30c094b764d264`. Requisito: o modelo de ameaças (`~/.forge-contrib/docs/security/hk3-parecer-ameacas.md`, E2) e as DECISÕES TÉCNICAS de 2026-10-29 12:06, 12:34 e 13:44: o heredoc só fica isento quando a chamada inteira é de `cat` (`sed -n <números>p <arquivo>` conta como `cat`) e nenhuma forma que executa merge, pull ou gh pr passa.

Método: sondas locais e passivas, 101 comandos em dois lotes, contra o hook de `cf6bf0a`, o de `7b2a225` e o da base `d14a713` (repositório descartável com a integração na `develop`, `git merge melhoria/x` sem parecer; nada executado, só o veredito do hook). O delta de `hooks/` é só `hooks/parecer.py` (+29 -8 em `7b2a225..cf6bf0a`); o merge da develop `f3f63f9` não muda `hooks/` (`git diff --stat d14a713 f3f63f9 -- hooks` vazio); o resto do delta (`bin/forge-check`, `agents/conferente.md`, pareceres de outros pedidos) veio da develop e não é controle deste PR.

## Gatilhos
`R-SEGURANCA`: controle do Forge (`hooks/parecer.py`, o portão `R-REVIEW`/`R-QA` na entrada da integração). Sem pipeline, contêiner, IaC, segredo nem rede.

## Achados
(nenhum bloqueante; nenhum recomendado novo)

## Revalidação dos achados anteriores
- **A1 (bloqueante, resolvido).** `heredocs_simples` (`hooks/parecer.py:97`) e a condição em `:610` devolvem à rede D todo heredoc fora de `<<`/`<<-` + `'P'`, `"P"` ou `P` (`\w`), com `\` ou `$` em linha de comando, `\` no fim de linha de corpo ou `<<` que a regex não consome. As seis formas do A1 (`<<$'EOF'`, `<<$"EOF"`, `<<$'E\x4fF'`, `<<EOF\`+nova linha, `<<\`+nova linha, `<<-EOF` com `\` no corpo) passaram de rc=0 em `7b2a225` para rc=2; também rc=2: `<<'EOF'x`, `<<EOF` com `\` no fim do corpo, segunda chamada com delimitador ofuscado depois de uma chamada simples, dois heredocs na mesma linha, `<<'EOF'` com `$'EOF'` no corpo. Corpos legítimos seguem isentos (`<<'EOF'`, `<<EOF`, `<<-EOF`; `EOF ` com espaço e `EOF\r` não terminam o corpo, como no bash). Nenhuma forma passa que não passasse em `7b2a225`: das 85 do lote 1, 8 mudaram de 0 para 2 e nenhuma de 2 para 0.
- **A2 (resolvido).** `docs/hooks.md` registra a limitação [B]: `env`, `nice`, `timeout` e `xargs` antes de `git merge`/`git pull` liberam como na base; texto enviado por pipe a um shell também.
- **A3 (resolvido).** `SED_LE` (`hooks/parecer.py:41`) ganhou a âncora `(?<![^\s;&|(])`: `xsed -n 1p f` e `/x/sed -n 1p f` não viram `cat`; a doc diz isso.
- **A4 (resolvido).** O corpus ganhou as fixtures barradas das formas do A1 (`texto-barra-heredoc-delimitador-ansi-c.json`, `-ansi-c-hex`, `-aspa-cifrao`, `-com-barra-e-quebra`, `-barra-no-lugar-do-delimitador`, `-menos-com-barra-no-corpo`, `-aqui-string`), duas de `sh -c` (`BASH_ENV=` e texto enviado a shell por pipe) e a legítima com `$` no corpo; mutantes em `tests/mutantes/hk3-parecer-texto-4.json`. Lacuna: não rodei a suíte nem os mutantes (só as sondas), e o parecer não depende deles.

Item 13:44 do `sh -c`: `e_shell_c_de_texto` recusa `BASH_ENV=` na linha e shell sem `-c` entre as palavras (`… | sh`, `dash`, `zsh`, `busybox sh`, `env sh`, `source /dev/stdin`); sondados e sem merge liberado. `echo git merge x | sh` segue rc=0, igual à base e ao registrado como limitação [B].

Observação fora do delta (sem achado, igual à base `d14a713`): `/usr/bin/git merge melhoria/x` passa em qualquer versão (o hook só reconhece `git` sem caminho); não é regressão deste PR, e quem quiser fechar abre cartão próprio com o `tech-lead`.

PA-7 (`docs/engineering/achados-recorrentes.md`), conferido por item: AR-3 (lista negativa) não se aplica, a isenção do `sh -c` é lista positiva; AR-5 (python sem -I) não se aplica, sem python novo no caminho; AR-6 (`mascara-do-shell-esconde-codigo`) coincide com a ofuscação registrada; AR-7 (`pasta-do-git-diferente-do-bash`) foi a classe do A1 e o conserto a cobre; AR-1, AR-2, AR-4, AR-8 e AR-9 não se aplicam. Linha AR é do `tech-lead`; nenhuma nova.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: `python3` local e o bash do sistema; `gitleaks`, `osv-scanner`, `semgrep`, `zizmor` e `trivy` não rodaram (sem segredo, dependência, workflow nem imagem no delta; lacuna registrada). Carga conferida em `/proc/loadavg` (abaixo de 7) antes de cada lote.
