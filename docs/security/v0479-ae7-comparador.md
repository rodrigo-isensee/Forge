---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-ae7-comparador
commit: 757355b43bd7f4bb2b3b5dd109270cdb1d426f80
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: AE7.1, `forge-check comparar` (v0478 E58.50), head 757355b4

Revalidação do parecer 911f1f91 (head f50171d2: A11 e A12 bloqueantes, A13 recomendado). Delta lido: `forge-check parecer delta` deste arquivo (`f50171d2..757355b4`). No domínio, `bin/forge_comparar.py` (docstring, `CABECALHO_SUSPEITO`, `plugin_fora_da_raiz`, `blobs_do_lote`, `cabecalho`, `fora_da_medida`, `extrair`) e a ajuda do `comparar` em `bin/forge-check:10179-10180`. Fora do domínio, `tests/test_comparar.py`, 6 specs de mutante e o fragmento do changelog.

Gatilhos: execução de comando (roda o código dos hooks da base e do head), controle que analisa entrada (medida do "só aperta").

## Confirmação pedida: a mudança só aperta
Quase. Ela só acrescenta saídas rc 2 antes de medir: árvore ilegível, link simbólico, `source` do marketplace e o cabeçalho lido em qualquer recuo, em fluxo e com escape. A `extrair` agora falha diante de link em vez de recriá-lo. O delta não toca `hooks/`, `tests/config.json`, `docs/regras/`, workflow nem pre-push. Há um único ponto que solta: o corpo do `.md` deixou de contar. Antes, `hooks:` no começo de qualquer linha do `.md` dava rc 2; agora só o cabeçalho conta (S23: a regra antiga casa, rc 0 no head). A troca é intencional e coberta por teste (`test_hooks_no_corpo_ou_como_texto_no_cabecalho_mede`). Não tem caminho de ataque, porque o Claude Code só lê `hooks` do cabeçalho. Nenhum caminho que antes dava rc 1 passa a dar rc 0.

## Os limites declarados são honestos?
Em quase tudo, sim. O docstring (`:1-22`) e a ajuda listam o que é medido e o que dá `nao-verificavel`, e cada item tem sonda rc 2. O limite "hook declarado por outro caminho não é visto" está escrito. Há uma premissa falsa dentro da própria medida declarada ("extraídos [...] como o clone do plugin os instala"). Em `:170`, o comentário diz "o clone sem --recursive deixa a pasta vazia". O Claude Code, porém, clona o plugin com `--recurse-submodules --shallow-submodules` e roda `git submodule update --init --recursive --depth 1` sempre que existe `.gitmodules`. Os dois textos estão no binário do Claude Code instalado. Isso é porta da medida: A14, bloqueante. Ficam fora do que o comparador promete, e por isso são só recomendados: o `metadata.pluginRoot` do marketplace (A15, sem leitura provada) e os vetores de liberação que não são hook (A16).

## Achados
- A14 (bloqueante) bin/forge_comparar.py:170 · submódulo é pulado na extração e não dá nao-verificavel, mas o Claude Code instala o plugin com --recurse-submodules: hooks.json com hook em ext/x.py (gitlink + .gitmodules) mede rc 0 (o script falta e conta como recusa), e o clone real traz o allow (S22)
- A15 (recomendado) bin/forge_comparar.py:91 · `plugin_fora_da_raiz` não olha `metadata.pluginRoot` (o esquema do marketplace o descreve como base das fontes relativas): pluginRoot ./outro com source . mede rc 0 (S21); o validador ainda lê a raiz, sem caminho provado
- A16 (recomendado) bin/forge_comparar.py:19 · os limites não dizem que liberação sem hook fica fora da medida (allowed-tools no cabeçalho de .md, mcpServers, lspServers e monitors do plugin): quem lê so-aperta medido pode supor que o plugin inteiro só aperta

## Estado dos achados anteriores
- A11: resolvido (`:132-139`, `:179-180`). S15, S16, S17 e S17b (link absoluto para fora) dão rc 2 "link simbólico na árvore". S19 refeita: o validador segue lendo através do link ("hooks: Invalid input").
- A12: resolvido (`:91-99`, `:146-147`). S18 e as variantes objeto github, `./outro/..` e dois plugins dão rc 2. O `./` dá rc 0, como esperado. S20 refeita: o validador lê o plugin de `source` ("hooks: Invalid input").
- A13: resolvido (`:40-43`, `:117-123`, `:148-153`). S14 e S14b a S14d dão rc 2. As formas novas S14e (`? |-` com a chave em bloco), S14f (âncora e alias) e S14g (BOM, linha em branco e comentário antes do `:`) também dão rc 2. O controle S14h (`'hoo''ks'`, que no YAML não é `hooks`) dá rc 0. Falso positivo: C0, base contra si, rc 0 sobre os 1535 `.md` com cabeçalho.
- A1 a A10: o delta não os toca. Os controles C0 (rc 0) e C1 (hook allow em Bash, rc 1 com 4 aceites novos) seguem iguais.

## Sondas
- S22 · head = base + `.gitmodules` (ext, url file://) + gitlink 160000 em `ext` (x.py imprime allow) + grupo Bash em hooks.json com `python3 ${CLAUDE_PLUGIN_ROOT}/ext/x.py`, commit rc 0 · espera: rc 2 · obtido: rc 0 aceites-novos=0
- S24 · `git clone --recurse-submodules --shallow-submodules` do commit da S22, depois ext/x.py com stdin de Bash · espera: o instalador traz o submódulo · obtido: ext/x.py presente, saída permissionDecision allow

## Detalhe dos achados
Método: clone descartável em `/root/.forge-contrib/wt/sondas-v0479-ae7-E5850/repo` no head 757355b4. A base de sonda `dbfc5c2d` é o head mais o corpus de 16 casos da rodada anterior. Cada sonda é um commit sobre essa base, com o rc do commit e o `ls-tree` conferidos antes do `comparar`, usando `TMPDIR=/root/.forge-contrib/wt/sondas-v0479-ae7-E5850/tmp`. Roteiro em `sondas.sh` e saída em `saida.txt`. A 1ª S22 do roteiro não valeu: o `git add -A` tirou o gitlink e o `.gitmodules` está no `.gitignore:15`. Ela foi refeita à mão com `add -f`, e o commit `030a4f49` traz `ext` 160000 e `.gitmodules`. `tests/test_comparar.py`: 59 testes OK.

- **A14 (S22, S24)** · `bin/forge_comparar.py:170` e `:132-139`.
  - Evidência: a `fora_da_medida` lista a árvore mas não olha o modo 160000. A `extrair` pula o submódulo e deixa a pasta vazia, então o hook que chama um script dali falha e é medido como recusa. O instalador de plugin do Claude Code, que usa o prazo `CLAUDE_CODE_PLUGIN_GIT_TIMEOUT_MS`, clona com `--recurse-submodules --shallow-submodules` e, quando existe `.gitmodules`, roda `submodule update --init --recursive --depth 1`. Os dois textos estão em `/usr/local/bin/claude`.
  - Caminho de ataque: um head acrescenta um submódulo, que pode até vir de outro repositório, e um grupo em `hooks.json` que o executa. A medida diz "nada liberado a mais", e o projeto que atualiza recebe o allow. Isso também fura o "só head deste repositório".
  - Severidade e custo: alta. O `.gitignore:15` ignorar `/.gitmodules` não barra `add -f`. O repositório não tem nenhum gitlink, então a correção não custa nada.
  - Correção mínima: `nao-verificavel` quando a árvore de qualquer lado tem entrada 160000 ou um `.gitmodules` em qualquer pasta. Junto, tirar o comentário de `:170` e citar o submódulo na lista do docstring e da ajuda. Teste com gitlink + `.gitmodules`, com gitlink sozinho e com `.gitmodules` sozinho.
  - Esforço P. Dono: tech-lead.
  - Por que só agora: a premissa vem de rodadas anteriores e não foi sondada até aqui. É uma dimensão nova da matriz (conteúdo que o instalador busca fora da árvore), não um achado do delta.
- **A15 (S21)** · `:91-99`. O `metadata.pluginRoot` existe no esquema do marketplace do Claude Code ("Base path for relative plugin sources"). Um head com `pluginRoot: ./outro`, `source: "."` e hook allow em `outro/` mede rc 0. O `claude plugin validate --strict` ainda valida a raiz: com hooks inválidos só em `outro/`, dá "Validation passed"; com hooks inválidos na raiz, falha. Sem caminho provado, então fica recomendado. Correção: `nao-verificavel` com `metadata.pluginRoot` presente. Esforço P. Dono: tech-lead.
- **A16** · `:19-22`. O "só aperta" mede hooks, e o docstring diz isso. Mas a linha `so-aperta: medido` pode ser lida como garantia sobre o plugin inteiro. `allowed-tools` no cabeçalho de comando ou skill, e `mcpServers`, `lspServers` e `monitors` no manifesto, liberam ou executam sem passar por hook e ficam fora da medida. Correção: acrescentar esses itens à lista de limites do docstring e da ajuda. Esforço P. Dono: tech-lead.

## Riscos aceitos e ferramentas
- Riscos aceitos: nenhum.
- CI: não há CI no head (sem PR aberto), então a suíte inteira fica para o CI do PR. Rodados aqui só `tests/test_comparar.py` (59 OK), as sondas e o `claude plugin validate --strict` das S19, S20 e S21.
- Lacunas de ferramenta: gitleaks, osv-scanner, semgrep, zizmor e actionlint não estão no PATH. O delta não toca workflow nem dependência.
- Segredo: nenhum padrão de token ou chave nas linhas acrescidas.
- Escrita: nenhuma fora da pasta de sonda e deste parecer.
