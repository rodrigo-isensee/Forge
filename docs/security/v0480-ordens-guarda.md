---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-ordens-guarda
commit: 9e460e4f1aa51ef214386390351faf9ebc749deb
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-23
---
# Review de segurança: v0478 (E123.27, guarda do arquivo de ordens, PR #811)

Corte 1 do hook de ordens (E123.25): só a guarda, tirada da `melhoria/v0480-ordens-hook` sobre a develop fc488261. Lido o diff inteiro `fc488261..9e460e4f` (41 arquivos).

Gatilhos: hook de controle (`hooks/conformidade.py`, `hooks/conformidade.json`), política de escrita de arquivo de controle do Jarvis, `bin/forge-init` (ignorados do git do projeto).

## Origem do código
- `hooks/conformidade.py`, `hooks/conformidade.json`, `bin/forge-init`, `tests/test_forge.py`, `tests/mutantes/v0479-conformidade-trilha-7.json` e as 31 fixtures `tests/hooks/conformidade/ordens-*.json`: `git diff 35211762 9e460e4f` vazio. É o código aprovado pela segurança na `melhoria/v0480-ordens-hook` (E123.3, E123.8, E123.12, E123.16 e E123.21, este no head 35211762); A1 a A4 daquelas rodadas seguem resolvidos aqui: A1 em `hooks/conformidade.py:3825` e `hooks/conformidade.json:67`, A2 em `hooks/conformidade.py:1612` e `:1637-1645`, A3 em `bin/forge-init:222`, A4 em `hooks/conformidade.py:3822` e `hooks/conformidade.json:66`.
- A develop andou de 5cff9f6a (base da ordens-hook) a fc488261 só em documentação: nenhum dos arquivos acima mudou nela.
- `tests/test_hooks.py`: a classe `GuardaDasOrdens` (`:3741`) traz os quatro testes da guarda da classe antiga `OrdensEmVigor`; saem só os testes do hook `ordens` (corte 2). Sai também `test_so_o_jarvis_escreve_o_arquivo_de_ordens` (dono `["jarvis"]` das duas entradas). Sondei: com `qa-engineer` posto no `quem` de cada entrada, os testes da guarda passam (X1, X2 sobrevivem). Não vira achado: a catraca do CI (`tests/catraca.py:495`, `mudancas_da_politica`) recusa, depois do merge, toda mudança de entrada já existente em `hooks/conformidade.json`. Neste PR, o `quem` das duas entradas foi lido: `["jarvis"]`.

## Só aperta, por escrito
O item **só aperta**. Nada nele libera o que antes era recusado:
- `hooks/conformidade.json:66-67`: duas entradas novas com dono. No laço de `Guarda.caminho_barrado` (`hooks/conformidade.py:1603-1624`), entrada que casa só recusa ou segue (`continue`); nunca libera nem interrompe a leitura das outras. Entrada a mais só acrescenta recusa.
- `hooks/conformidade.py:1611-1612`: um `or` a mais em `achou`, só para `.forge/ordens/`: casa mais caminhos, logo recusa mais.
- `hooks/conformidade.py:3825,3828,3831`: `ordens` em `CAMINHOS_DO_CONTROLE`, `CONTROLE_NO_TEXTO` e `PEDIDO_OU_BRIEF`. Os três são lidos só em `GuardaDaProva` (`:3889-3893`, `recusa_do_estado` `:3954`, `controle_no_texto` `:3971`), e lá o casamento só leva a `barrar`. O jarvis fica fora (`controle` None). Mais texto casado dá mais recusa (falso positivo possível em linha que cita `forge-contrib` e `ordens` e que o hook não modela; é o custo já aceito para `pedidos` e `briefs`).
- `hooks/conformidade.py:3602-3612` (`entrada_valida`): equivalente na decisão, como provado na rodada E123.21 (S1: 1419864 casos, 0 divergências); o código é o mesmo.
- `bin/forge-init:222`: `.forge/ordens/` vai para os ignorados. Tira do git só o arquivo que o hook do corte 2 vai ler, para que um commit de branch não chegue à cópia do Jarvis. Não afrouxa nenhuma regra.
- Neste corte o arquivo protegido ainda não tem leitor (o hook `ordens` vem no corte 2). A guarda chega antes do leitor: não abre nenhum caminho novo.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum.
Ferramentas: leitura do diff; `git diff 35211762 9e460e4f` nos arquivos da guarda. No head: `python3 -m unittest tests.test_hooks.GuardaDasOrdens tests.test_hooks.Hooks.test_politica_de_conformidade_malformada_bloqueia tests.test_hooks.Hooks.test_fixtures_do_controle_so_jarvis tests.test_forge.ForgeInit.test_o_arquivo_de_ordens_fica_fora_do_git` deu 7 testes OK. `forge-mutante tests/mutantes/v0480-ordens-guarda.json tests/mutantes/v0480-ordens-guarda-2.json` deu 16 de 16 mortos (M15, M16, M22 a M26, M28, M30 a M37; o M26 morre por erro do teste declarado, que passa sem o mutante). A sonda X1/X2 (spec em `$TMPDIR`, fora do repositório) está descrita acima. A suíte inteira não rodou (o brief pede sem suíte local); vale o CI do PR #811, pendente na hora deste parecer e obrigatório para o merge.
