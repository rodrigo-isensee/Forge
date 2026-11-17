---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-sieg-g1-autorizacao
commit: 580b6c34c8cc46ae8270cc42017427d82f64b784
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-17
---
# Review de segurança: v047 ADR 0018, G1.0 e G1.1 (E2.667, head 580b6c34)

Gatilhos: autorização, controle do Forge (`bin/forge-check`, leitura das concessões). Volta por delta do parecer aprovado do head f42850b5 (a rodada anterior fica no git).

## Resumo
- Delta lido (`forge-check parecer delta`, f42850b5..580b6c34): no domínio, `bin/forge-check` (subcomando `autorizacao ler`, sem guarda de versão), `bin/forge_autorizacao.py` (novo, 190 linhas, lido inteiro) e a ADR 0018; fora do domínio, lidos para conferir os casos de abuso, `tests/test_autorizacao.py` e os mutantes.
- G1.0: a ADR passa a `aceita`, com D1, D2 e D4 decididas pelo dono e D3 como ação dele; confere com o registro das decisões (linhas 47 a 53). Campo `Pedido` e fechamento `F-<Pedido>` (itens 1, 2 e 7): **aval da segurança dado**. O `F-` vale pela presença e só aperta (`bin/forge_autorizacao.py:154` só leva a `vencida`); `F-` forjado só encurta, sem caminho que amplie. Resolve o A10.
- G1.1, falha fechada: link, não comum, FIFO (`O_NONBLOCK`), fora de UTF-8, cabeçalho repetido ou nome fora da forma viram erro e nenhuma concessão fica `ativa` (`:44-80`, `:167`); campo ausente, `Sha256`, `Gravado-por` (sha256 do `forge-check` carregado, `bin/forge-check` em `executar`), ato, alvos, `Pedido`, `Autoriza` e validade ilegível dão `adulterada` (`:111-128`). `Fuso` vazio ou com `..` cai em validade ilegível (sondas S5, S6 abaixo). Saída passa por `sem_controle`.
- Caso de abuso `inativa` (o único do Critério de parada que vale para a leitura): vencida em UTC com o `Fuso` batendo (`:104-107`), teto de 48 h ou 7 dias (`:98-108`), retirada, usada (`U-`), adulterada, de outro `forge-check` e fechamento do pedido (`:148-155`): cobertos e provados por `tests.test_autorizacao` (8 testes, rodados aqui: OK). Os demais casos (fala-forjada, recorte-ou-ressalva, numero-solto, forma-opaca, escrita-direta, escopo-largo, uso-duplo, rotulo-sem-autorizacao, ci-sem-declaracao) são do G1.2 em diante.
- Aprovado: só leitura, nada barra; os três achados novos são coerência do leitor que só pesa quando o G1.3 passar a barrar, e todos exigem escrita direta na pasta, que a G1.2 protege (Consequências, linha 69).

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
Nenhum risco aceito. Suíte: não rodada (brief: sem suíte local); a branch não tem PR nem execução de CI (`gh run list` vazio), então o CI do PR segue como portão do merge. Rodado: `python3 -m unittest tests.test_autorizacao` (8 OK). Lacuna: `gitleaks`, `osv-scanner`, `semgrep`, `zizmor` e `actionlint` fora do PATH.
