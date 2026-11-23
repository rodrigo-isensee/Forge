---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-ordens-hook
commit: 8e84ef3b57fa6fe7cee56e7b640dfecaba1a8271
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-23
---
# Review: v0478 (E123.11, 2ª volta do hook ordens)

Revalidação pelo delta (H3, `R-REVIEW`): `forge-check parecer delta docs/reviews/v0480-ordens-hook.md`, intervalo `cf679683..8e84ef3b`, sem o que veio da `develop` (a base avançou de `f483671` para `8773be3`). Lidos só os arquivos de código e teste do domínio, nos commits `27c90696`, `21c23d2a` e `78fb63b9`. Parecer anterior: aprovado em `cf679683` (`f343d229`). A volta responde aos achados da segurança E123.8; o mérito de segurança é do `security-engineer`. Aqui confiro só correção, consistência e teste.

## Delta lido
- A1 (pasta própria): `NO_FORGE` vai para `docs/ordens/ordens-em-vigor.md` (`hooks/ordens.py:21`). A entrada do mapa de donos passa a ser a pasta `~/.forge-contrib/docs/ordens/` (`hooks/conformidade.json:67`), e `CAMINHOS_DO_CONTROLE`, `CONTROLE_NO_TEXTO` e `PEDIDO_OU_BRIEF` ganham `ordens` (`hooks/conformidade.py:3820-3827`). As fixtures S1 a S3 bloqueiam, e `ordens-dev-cat-libera` deixa a leitura passar.
- A2 (cópia principal): o `achou` aceita a forma relativa à cópia principal só para as entradas de `PELA_COPIA_PRINCIPAL` (`hooks/conformidade.py:1611-1612`). `relativos_a_copia_principal` usa o mesmo cálculo de `fontes` no `ordens` (`diretorio_comum`, `.git` nomeado, `relativo_ao_pai`). Com o `.git` que não se resolve ou num repositório nu, devolve lista vazia. As fixtures S4 bloqueiam 5 formas, e a do jarvis passa.
- A3: `.forge/ordens-em-vigor.md` entra nos `ignorados` do `bin/forge-init:222`. O teste `test_o_arquivo_de_ordens_fica_fora_do_git` confere o efeito pelo `git check-ignore`.
- ADR 0003 (itens 1 e 6) e o fragmento `changelog.d/v0480-ordens-hook.md` batem com o código. A única citação de `docs/kanban/ordens-em-vigor.md` que sobra está no contexto histórico da ADR (linha 82), e isso está correto.
- Nenhum teste foi afrouxado. O mínimo de fixtures `ORDENS-SO-JARVIS` sobe de 8 para 20, e há 20 na pasta. As fixtures alteradas mudam só o caminho de `kanban` para `ordens`. O `refactor` `78fb63b9` tira o cache por entrada e não muda o comportamento.
- Mutantes: M21 a M26 e M28 cobrem cada linha de guarda mudada. M27 não existe porque saiu com o cache do `78fb63b9` e não deixou guarda sem mutante. M15, M16 e M19 foram reescritos para o caminho novo.
- O `ordens` no texto não aumenta o bloqueio indevido. Sondas de leitura com dev na sessão do Forge saíram com código 0: commit com `fix(ordens): $(...)` na cópia de `wt/`, `$d` apontado para a cópia de `wt/` e a pasta `docs/coordenadas`. O `$d` para `docs/pedidosx` sai com código 2, o mesmo da base com `pedidos`, então a classe não é nova.

## Provas
- `python3 -s -E -m unittest tests.test_hooks.OrdensEmVigor tests.test_forge.ForgeInit.test_o_arquivo_de_ordens_fica_fora_do_git` (`env -i`): `Ran 24 tests in 9.330s OK`.
- `bin/forge-mutante tests/mutantes/v0480-ordens-hook-4.json`: M21, M22, M23, M24, M25 e M28 `morreu`. M26 `morreu · (erro)`, porque o `git check-ignore` levanta exceção sob o mutante, e é esse o desenho do teste.
- Suíte inteira: fica no CI do PR e não foi rodada de novo.

## Parecer
Aprovado. Os três achados da segurança E123.8 foram tratados no delta, cada um com teste de comportamento e mutante. Nenhum teste foi afrouxado, e a documentação acompanha o código.
