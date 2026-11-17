---
tipo: revisao-seguranca
contrato: 1
pedido: v0474
branch: melhoria/v047-sieg-g1-autorizacao
commit: 2f150f4dac973291017e18556b652ba65ee9748d
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-17
---
# Review de segurança: v047 ADR 0018, G1.0 e G1.1 (E1.22 do v0474, head 2f150f4d)

Gatilhos: autorização, controle do Forge (`bin/forge-check`, leitura das concessões). Volta por delta do parecer aprovado do head c890fbd6 (a rodada anterior fica no git).

## Resumo
- Delta lido (`forge-check parecer delta`, c890fbd6..2f150f4d): no domínio só `bin/forge-testes:112`, que põe `test_autorizacao` na tupla `FORGE_CHECK` (mapa de testes afetados; A5 do review E1.11). Fora do domínio, conferidos: a docstring de `tests/test_autorizacao.py:1` (só o caminho `bin/forge-check`) e a contagem 88→89 em `tests/test_testes_tocados.py:77`; o resto do diff são pareceres.
- Efeito na segurança: o mapa só amplia o que roda ao tocar `bin/forge-check`; não afrouxa portão nem muda a leitura das concessões. `bin/forge_autorizacao.py` e `bin/forge-check` não mudam no delta (último commit do leitor: 580b6c34): a conclusão do c890fbd6 vale. Nenhum achado novo; A9 a A14 seguem como estavam.
- Rodado no 2f150f4d: `python3 -m unittest tests.test_autorizacao` (8 OK) e `python3 -m unittest tests.test_testes_tocados` (162 OK, 1 pulado), o teste que deixou o CI vermelho no c890fbd6.
- CI do PR 629: sem execução no 2f150f4d; o PR está `CONFLICTING` com a develop (`mergeStateStatus: DIRTY`) e a última execução (1b5de74f) é anterior à correção. A suíte completa segue portão do merge, fora da segurança (dono: tech-lead, trazer a develop e ter o CI verde).

## Achados
- A9 (recomendado) docs/adr/0018-autorizacao-do-dono-gravada.md:25 · Aberto, vai ao G1.2 (gravar): com `Fuso` Etc/UTC a leitura aceita `ate:` de data escrita (sonda S7: `ativa`); a regra de tratar UTC ou sem região como não legível em data, hora e "esta noite" segue pendente.
- A10 (recomendado) docs/adr/0018-autorizacao-do-dono-gravada.md:15 · Resolvido no 580b6c34: campo `Pedido` na concessão e `F-<Pedido>` pela presença (itens 1, 2, 7; `bin/forge_autorizacao.py:122,154`), mostrado em `ler` (`:179`).
- A11 (recomendado) docs/adr/0018-autorizacao-do-dono-gravada.md:42 · Aberto: a lista matinal das ativas com vencimento (registro da D1, linha 48) ainda não está na G1.6 nem no item 12.
- A12 (recomendado) bin/forge_autorizacao.py:111 · `Id` do cabeçalho não é conferido contra o nome do arquivo (sonda S2: A-1 com `Id: A-9` fica `ativa`); retirada e confirmação casam pelo nome e a declaração (G1.4) pelo `Id`. Confira `Id == nome` antes do G1.3.
- A13 (recomendado) bin/forge_autorizacao.py:98 · O teto curto vem de lista dos termos curtos e qualquer outra `Origem-da-validade` ganha 7 dias (S3); `Hora-da-fala` futura é aceita (S4). Teto de 7 dias só para os termos do mapa escrito; fala depois de `agora` é ilegível.
- A14 (recomendado) bin/forge_autorizacao.py:67 · Só o último componente é conferido como link: `.forge` como link para outra pasta é lido e a concessão fica `ativa` (S8). Recuse link em `.forge` e em `autorizacoes` (ou abra por `dir_fd` sem seguir link) junto com a proteção do G1.2.

## Sondas

## Detalhe dos achados
Sondas desta rodada (nenhuma prova bloqueante; registro dos recomendados): script com `python3 -I` sobre `bin/forge_autorizacao.concessoes`, concessão base íntegra com `Gravado-por` igual ao da chamada e `agora` 2026-11-17 12:00 UTC. S1 base: `ativa`. S2 `Id: A-9` no arquivo `A-1`: `ativa`. S3 `Origem-da-validade: quando der` com `ate:` 6 dias adiante: `ativa`. S4 `Hora-da-fala` 2026-11-20 (futura): `ativa`. S5 `Fuso` vazio: `adulterada`. S6 `Fuso: ../../../etc/passwd`: `adulterada`. S7 `Fuso: Etc/UTC` com data escrita: `ativa`. S8 `.forge` como link para pasta com concessão íntegra: `ativa`.

**A12.** Caminho: quem consegue escrever na pasta (hoje sem proteção; depois da G1.2, só por falha dela) grava `A-1` com `Id: A-9`; `autorizacao retirar A-9` grava `Retira: A-9` e a `A-1` continua ativa para o hook do G1.3. Severidade baixa (exige escrita direta, que já forja tudo; aqui só confunde a retirada, que deve sempre funcionar). Correção: `campos["Id"] != nome` entra em `problemas` (precisa passar o nome). Esforço P. Dono: tech-lead.

**A13.** Caminho: concessão gravada com termo que o `gravar` deveria ter levado a `uso-unico` (defeito do G1.2 ou escrita direta) passa a valer 7 dias em vez de 48 h; a lista de termos curtos é lista negativa no lado que amplia (AR-3). Severidade baixa (o `Validade-utc` gravado ainda manda; o teto é defesa em profundidade). Correção: 7 dias só quando a `Origem-da-validade` normalizada é um dos termos escritos do mapa do item 6 (data e hora, dia da semana, "esta noite", "até o fim deste pedido"); o resto, 48 h. `instante(Hora-da-fala) > agora` vira validade ilegível. Esforço P. Dono: tech-lead (G1.1 ou G1.2, antes do G1.3).

**A14.** Caminho: a ADR (item 7) pede arquivo sem link; um `.forge` trocado por link desvia a leitura para pasta fora das três grafias protegidas na G1.2. Severidade baixa (trocar `.forge` exige escrita na raiz principal). Correção: `is_symlink()` também em `raiz/.forge`, ou abertura encadeada com `O_NOFOLLOW`; incluir `.forge` como link no teste `escrita-direta`. Esforço P. Dono: tech-lead (G1.2).

## Itens conferidos sem achado
- `SEM_GUARDA_DE_VERSAO` ganha `autorizacao` (`bin/forge-check`, linha 9245): o subcomando só lê e não confere repositório; o `Gravado-por` continua preso ao sha256 do `forge-check` carregado, então cópia defasada só deixa concessões `adulterada` (fecha).
- `raiz_principal` lê a pasta da cópia principal, como a ADR pede (item 1); clone sem `.git` comum cai na própria raiz.
- Retirada (`R-`) e uso (`U-`) não exigem integridade: só apertam. Confirmação (`C-`) exige `Sha256`, `Gravado-por`, `Confirma` igual ao nome e fala posterior (`:131-139`).
- PA-7: AR-1 e AR-2 com mutantes da leitura (`tests/mutantes/v047-sieg-g1-autorizacao*.json`, fora do domínio, só conferidos na lista).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Suíte: só no CI do PR (sem execução no 2f150f4d, PR em conflito com a develop), portão do merge. Lacuna: `gitleaks`, `osv-scanner`, `semgrep`, `zizmor` e `actionlint` fora do PATH.
