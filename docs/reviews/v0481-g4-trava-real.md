---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-g4-trava-real
commit: 356362e3307f6773ff7088db38f004d22874ba73
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0481 (E7.5, G4 em fatias, classe T, revalidação por delta)

Escopo: revalidação do parecer reprovado no 883429dd (E7.3) pela volta E7.4. Delta lido: `forge-check parecer delta docs/reviews/v0481-g4-trava-real.md`, intervalo 883429dd..356362e3, no domínio só `docs/propostas/g4-fatias.md` (14 linhas trocadas); o outro arquivo do intervalo é o parecer anterior. Só documentação: sem código, sem guarda, sem mutante. O que o parecer anterior conferiu fora do delta (as 30 linhas do hook, os 19 cartões, os comandos do dono D1 a D10) segue valendo.

## O que foi conferido no delta
- **A1 (fechado):** a F5 tira o `--mirror` (`3117`) e diz por quê (sem destino literal, envia todas as refs); a F6 afrouxa só o `--force` de branch (`3115`), mantém o `--mirror` barrado com o motivo (cria tag `v*`, apaga `melhoria/*` de outro papel) e pede os testes de recusa de `git push --mirror <remoto>`, `git push -f origin v9.9.9` e `git push --force --tags`; D2 e a seção 5 citam o `--mirror`. Lido em `hooks/conformidade.py` do 8d7914bc: `git_tags_no_envio` (`3100`) barra a tag no envio independente do `--force` e não olha o `--mirror`, o que confirma que o `--mirror` precisa da própria recusa.
- **A2 (fechado):** a F7 fecha do CONFORMIDADE-COPIA-RECURSIVA-GIT só a troca do `.git/config` e do `core.hooksPath` e deixa aberta, com o caminho de fechamento (`.git/forge` no `denyWrite` pelo dono ou lacuna aceita), a gravação de `.git/forge/` fora de `run` pelo `cp -r`.
- **A3 (fechado):** 112 chamadas com ID literal. Refeito no 8d7914bc: `grep -c 'barrar('` = 138; com `"R-` literal = 112 (64, 19, 11, 9, 6, 3); 2 definições (linhas 1545 e 4174) e 24 chamadas com ID de variável. Confere com o texto.
- **A4 (fechado):** o comando novo da seção 2, rodado na pasta do Forge, dá `2518`, sha256 `1e864a97…916a`, `788` chamadas e `99` recusas, com a mesma quebra por forma (soma 99; 12,6%; leitura 9+6+3 = 18). A F1 define a recusa falsa pelo campo `alvo` nulo e a com efeito pelo `alvo` preenchido.

## Parecer
Aprovado no 356362e3. Os dois bloqueantes viraram texto certo (o `--mirror` segue barrado com teste de recusa; o cartão da cópia recursiva fecha só na parte que o sandbox já cobre) e os dois recomendados foram atendidos na mesma volta, com a linha de base agora reprodutível pelo sha256. Nenhum achado novo no delta.
