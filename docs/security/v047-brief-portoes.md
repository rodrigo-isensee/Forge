---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-brief-portoes
commit: c8861f242153ed9fa5ef4a97dc5acb83b9ac9619
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-14
---
# Review de segurança: v047 (desenho do BRIEF-NAO-SEGURA-VAGAS, revalidação)

Revalidação por delta (etapa E1.241) da volta E1.228 do desenho. Intervalo `cc0cf876..c8861f24`: só `docs/propostas/brief-portoes-por-ferramenta.md` (e o parecer anterior). O `forge-check parecer delta` diz "nenhum arquivo do domínio mudou" (a proposta é documentação), mas o pedido é de revalidação do desenho de controles do Forge (hook `conformidade`, hook `agentes`, `bin/forge-check`), então a releitura foi da seção 3 (3.2, 3.3, 3.4), da 4, da 8 (T4, T7, T8), da 9 e da 10, conferida contra o código da `develop` no mesmo clone (`hooks/conformidade.py`, `hooks/agentes.py`).

## Gatilhos
`R-SEGURANCA`: o desenho cria um subcomando que grava no pedido e em `docs/briefs/`, muda as guardas do hook `conformidade` e do hook `agentes` (Z10) e, na parte 0 da seção 10, corrige uma fronteira do hook que já está aberta na `develop`. Classe C quando implementado. Sem código nesta entrega: o parecer é de desenho e não há suíte a rodar.

## Achados
- A7 (bloqueante) docs/propostas/brief-portoes-por-ferramenta.md:97 · Parte 0: o critério novo do opaco cobre só brief e entrega --pedido; pausa, recado e as demais escritas pelo opaco ($(...), crase, "$f") e pelo interpretador com script opaco seguem livres ao autor. O opaco deve passar pelo predicado inteiro do forge_check_grava.

## Sondas
- S6 · `$(command -v forge-check) pausa`, papel de autor de stack, hook conformidade em c8861f24 · espera: rc 2 (a forma direta dá rc 2) · obtido: rc 0
- S7 · `$(command -v forge-check) recado --para . oi`, papel de autor de stack · espera: rc 2 (a forma direta dá rc 2) · obtido: rc 0
- S8 · `python3 -I "$(command -v forge-check)" pausa`, papel de autor de stack · espera: rc 2 · obtido: rc 0
- S9 · `f=$(command -v forge-check); "$f" pausa` e a crase `` `command -v forge-check` recado --para . oi ``, papel de autor de stack · espera: rc 2 · obtido: rc 0 nas duas

## Detalhe dos achados

**Estado dos achados da rodada anterior (parecer em `cc0cf876`).**
- A1 (bloqueante): resolvido na seção 3.4. Toda ação do `brief` grava salvo a lista fechada de leitura (`fila`, `mensagem`, conferência de arquivo, `portoes --so-mostrar`); a ação é procurada em todas as palavras livres (fecha a forma `brief --pedido fila portoes`, sonda S4 do desenho); `--so-mostrar` só pela abreviação que o argparse aceita, sem `=valor` e antes de `--`; `entrega --portoes` grava sempre; destinos em `docs/pedidos/` e `docs/briefs/` pela política do papel; `BRIEF_ACOES` com teste cruzado contra o hook e contra o `_option_string_actions` do argparse; entra no mesmo PR do subcomando (parte 3). Aceito.
- A2: resolvido na 3.3 (id e linha sob o mesmo `flock`, expressão fechada com o par papel e tipo da tabela e a branch validada e escapada, todas as etapas antes do primeiro brief, chave natural para não duplicar). T4 agora depende de A1, que está resolvido.
- A3: resolvido na seção 4 (`head_enviado` como fonte única no gerador e no `selar` de brief gerado; nada do `gh` nos bytes reproduzidos; falha fechada).
- A4: resolvido na seção 3 (uma constante, o hook `agentes` lê `fc.ETAPAS_DE_PARECER` do módulo que `de_escrita` já recebe, `hooks/agentes.py:593`; portão de devops grava só `docs/devops/<pedido>.md`).
- A5: resolvido na seção 3 (`ls-remote` de agora igual a `origin/B` e ao local; sem rede recusa) e em T7.
- A6: resolvido na 3.2 (F igual aos ids do pedido menos o `Cobre:`; buraco do pedido não reprova; faixa que contém o `Cobre:` reprova).

**A7 (média, bloqueante; parte 0 da seção 10 e o item "Programa opaco e interpretador" da 3.4).** Evidência: `args_do_forge_check` (`hooks/conformidade.py:97-108`) só devolve os argumentos do programa opaco (`$`/crase no nome) quando a linha tem `anotar --tipo` ou `--gravar`, e no ramo do interpretador só acha o script se uma palavra tem o nome literal `forge-check` (`:101-103`); fora disso o `forge_check_grava` (`:1590`) não roda. As sondas S6 a S9 mostram, no papel de autor, `pausa` (grava `.forge/pausa.json`, que o hook reserva à sessão principal, X1) e `recado` (caixa de recados da sessão principal, S8) passando pelo opaco, pela crase, pela variável e pelo interpretador, enquanto a forma direta é recusada. Também passam `brief selar` (S2 do desenho) e `entrega --pedido` pelo opaco. O desenho propõe trocar o critério do opaco por "o mesmo predicado da escrita (`brief` com ação de escrita, `entrega --pedido` ou `--portoes`)" (linha 97), e a parte 0 (linha 176) e os mutantes (linha 168) repetem só esses dois; implementado assim, `pausa`, `recado`, `pedido` sem `--ler`, `rodar`, `meta`, `medida`, `anotar` e `transcricao anonimizar` continuam abertos pelo opaco. Caminho de ataque: um agente de autor (sessão de subagente com a política de caminhos do papel) roda `$(command -v forge-check) pausa` e pausa a fábrica, ou `$(command -v forge-check) recado ...` e põe texto na caixa da sessão principal, que o Jarvis lê como recado entre sessões; as duas fronteiras existem justamente para tirar isso dos papéis de autor. Correção mínima no desenho (texto da 3.4, da parte 0 e dos mutantes): o programa opaco (nome com `$` ou crase) e o interpretador cujo primeiro argumento posicional é opaco devolvem sempre os argumentos ao `forge_check_grava` (falha fechada: quem decide é a política de destinos inteira, que só age quando o subcomando é de escrita), em vez de uma lista à parte; cobrindo, no corpus da parte 0, `brief selar`, `entrega --pedido`, `pausa`, `recado`, `pedido` (sem `--ler`), `rodar`, `meta`, `medida`, `anotar`, `brief --gravar` e `transcricao anonimizar`, cada um nas formas `$(command -v forge-check)`, `"$(which forge-check)"`, crase, `f=$(...); "$f"` e `python3 [-I] "$(command -v forge-check)"`, e o corpus de legítimos com as leituras pelo opaco (`brief fila`, `entrega` sem `--pedido`, `pausa --retomar`, `recado --confirmar`, `pedido --ler`) passando. Mutante: "opaco passa pela política inteira" no lugar dos dois da linha 168. Esforço P. Dono: `tech-lead` (autor do desenho; o hook vai com o corpus do `conformidade`).

**Sem achado novo** em 3.2, 3.3, 3.4 (fora o item do opaco), 4, T1 a T8 e na ordem dos PRs da seção 10 (a regra do hook entra no mesmo PR do subcomando, partes 3 e 4).

Revalidação: a volta precisa só corrigir o texto do critério do opaco (3.4, parte 0 e mutantes da parte 0), conforme A7; a releitura vai pelo `forge-check parecer delta` deste parecer.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática do desenho e do código da `develop` no clone, e as sondas S6 a S9 sobre o hook `conformidade` em subprocesso com ambiente limpo, num repositório temporário (só leitura, nada gravado no clone). Sem varredura de segredo nem de dependência: a entrega é só texto, sem dependência nova.
