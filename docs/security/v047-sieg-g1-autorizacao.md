---
tipo: revisao-seguranca
contrato: 1
pedido: v0474
branch: melhoria/v047-sieg-g1-autorizacao
commit: 7d8ff8f51af8e12b1b8aed4f12b2bc9f3f78a07e
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-17
---
# Review de segurança: v047 ADR 0018, G1.0 e G1.1 (E1.34 do v0474, head 7d8ff8f5)

Gatilhos: autorização, controle do Forge (`bin/forge-check`, leitura das concessões). Volta por delta do parecer aprovado do head 2f150f4d (a rodada anterior fica no git).

## Resumo
- Delta lido (`forge-check parecer delta`, 2f150f4d..7d8ff8f5, sem o que veio da develop): junção da develop (#630 e #632). No domínio só `bin/forge-testes`, que juntou sem conflito (`git show --remerge-diff 7d8ff8f5 -- bin/` vazio): `test_estado_ilegivel` entra em `FORGE_CHECK` (:107), em `REAPROVEITAM_O_LOTE` (:117) e no mapa de `hooks/` (:173), ao lado do `test_autorizacao` desta branch (:112), que segue lá. Fora do domínio, conferido: o único conflito, `tests/test_testes_tocados.py:77`, resolvido para 90 (89 da develop mais `test_autorizacao`).
- Efeito na segurança: o mapa só amplia o que roda; não afrouxa portão. `bin/forge_autorizacao.py` e `bin/forge-check` sem diff em 2f150f4d..7d8ff8f5; `hooks/agentes.py`, `hooks/meta.py` e `hooks/pesado.py` vêm da develop (#630, #628) sem mudança da branch. A conclusão do 2f150f4d vale; nenhum achado novo; A9 a A14 seguem como estavam.
- Rodado no 7d8ff8f5: `python3 -m unittest tests.test_autorizacao tests.test_estado_ilegivel` (17 OK).
- CI do PR 629 no 7d8ff8f5: suíte 3.12 e 3.14 (partes 1 a 5), teto de pulados e bateria (passos, verificações longas, 3.14) verdes; `bateria (pareceres)` e `catraca` vermelhos à espera dos pareceres deste head (portão do merge, dono: tech-lead).

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
Nenhum risco aceito. Suíte: CI do PR 629 no 7d8ff8f5, suíte verde nas duas versões do Python. Lacuna: `gitleaks`, `osv-scanner`, `semgrep`, `zizmor` e `actionlint` fora do PATH.
