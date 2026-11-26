---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-recibo-contador
commit: bc9b1d1f89bfbe7157b93cecba53420292c303e8
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-26
---
# Review de segurança: v0481 (#921, ordens_teto), 1ª rodada completa (E20.17)

Escopo lido: `git diff 707fea56..bc9b1d1f` inteiro (19 arquivos): `hooks/ordens_teto.py`, `hooks/hooks.json`, a emenda da ADR 0003 item 3, `docs/hooks-fixtures.md`, `bin/forge-testes`, o corpus `tests/hooks/ordens_teto/`, `tests/test_hook_ordens_teto.py`, os mutantes e o fragmento do changelog; e, fora do diff, o que o hook importa (`hooks/ordens.py`: `fontes`, `ler_ordens`, `escapadas`, `no_teto`; `hooks/_comum.py`: `Hook.projeto`, `bloquear`, `executar`) e a guarda de escrita da pasta das ordens em `hooks/conformidade.py:4178-4188`.

## Gatilhos
Gatilhos: hook novo de controle no PreToolUse (Write, Edit, MultiEdit), emenda de ADR de hooks (ADR 0003 item 3), arquivo que vira contexto da sessão principal (ordens em vigor)

## Achados
- A1 (bloqueante) hooks/ordens_teto.py:76 · CI vermelho no head: o job catraca recusa por R-QA a guarda `__name__ == '__main__'` sem mutante declarado; o parecer só aprova com o CI do head todo verde. Declarar o mutante ou a isenção com motivo em tests/mutantes/v0481-recibo-contador*.json.
- A2 (recomendado) hooks/ordens_teto.py:37 · Edit (e o 1º item do MultiEdit) com old_string vazio em arquivo ausente ou vazio, que a ferramenta trata como criação com o new_string, passa sem contar (S1, S2: 40 linhas, saída 0). Contar o new_string como o texto final nesses dois casos.
- A3 (recomendado) hooks/ordens_teto.py:69 · com o arquivo já acima do teto (gravado fora do Write), o Edit que encurta mas não chega ao teto é recusado (S3: 20 para 19 linhas, saída 2). Não trava o dono, mas trava a correção passo a passo: deixar passar quando linhas e caracteres não crescem.
- A4 (recomendado) tests/test_hook_ordens_teto.py:30 · os testes só montam projeto; a fonte da sessão do Forge (~/.forge-contrib/docs/ordens/) não tem caso. A sonda S9 prova que funciona hoje; falta o teste que segura (recusa a 16 linhas, passa a 15, casa temporária).

## Sondas

## O que aperta, o neutro e o que afrouxa
- **Aperta:** recusa nova (saída 2, `R-CONFORMIDADE`) no Write, Edit e MultiEdit que deixaria o arquivo de ordens em vigor acima de 15 linhas ou 2000 caracteres, nas duas fontes do `ordens` (cópia principal do projeto e `~/.forge-contrib/docs/ordens/`), contado pelas mesmas funções do `ordens` (`escapadas`, `no_teto`; `hooks/ordens_teto.py:15,68-69`), então hook que lê e hook que recusa não divergem na conta (controle e Unicode inclusos). A emenda da ADR 0003 item 3 só acrescenta a frase da recusa na gravação; nenhum texto foi tirado.
- **Neutro:** o `ordens` não muda (só lê, o corte com aviso segue como rede, sai sempre 0); a guarda de quem grava a pasta (`hooks/conformidade.py:4179-4188`: só o Jarvis, subagente barrado também pelo texto) não muda; erro interno do novo hook libera e vai ao `erros.log` (`executar` sem `critico`), o que equivale a não ter o hook, sem abrir nada que antes estava fechado; a gravação pelo Bash fica fora, como já estava; a entrada nova do `hooks.json` usa os mesmos `-s -E` e o `timeout` de 10 s, sem mexer nas outras; o mapa do `bin/forge-testes` só acrescenta testes.
- **Afrouxa:** nada. Nenhuma regra, invariante, teste ou guarda sai ou fica mais fraca no diff; o vermelho do catraca é de mutante ausente (A1), não de regra que some.

## A recusa pode travar o dono de corrigir as próprias ordens?
Não. O hook só age nas ferramentas do agente (PreToolUse); o dono edita o arquivo no próprio editor sem passar por ele. Dentro da sessão, a saída fica aberta: com o arquivo já acima do teto, o Write de 15 linhas passa (S4) e o MultiEdit que tira o excesso de uma vez passa (S5); no Forge, o mesmo (S9b). Arquivo ausente, link para fora da base ou maior que 64 KiB fazem o Edit passar (a conta não se faz), nunca recusar. O único atrito é o A3: o encurtamento parcial de um arquivo já acima do teto é recusado, e o Jarvis precisa regravar inteiro. Hoje o arquivo do Forge está em 15 linhas e 1980 caracteres contados (no teto, com 20 de folga): a próxima ordem acrescentada recusa, e o Jarvis terá de juntar ordens antes de gravar, o que é o pedido do dono de 25/11 21:47 ("recusa ao passar do tamanho, em vez de cortar calado").

## Detalhe dos achados
**A1.** Evidência: `gh pr checks 921`, job catraca (run 45880744827) com a linha "R-QA: guarda de hooks/ordens_teto.py mudada sem mutante declarado ... hooks/ordens_teto.py:76". Não é falha de segurança, mas o portão exige CI todo verde no head; o vermelho de `bateria (pareceres)` é a falta dos próprios pareceres e não conta contra o autor. Correção mínima: declarar o mutante da guarda ou isentá-la com motivo, como o catraca indica. Esforço P. Dono: autor (tech-lead).

**A2.** Evidência: `trocar` devolve None quando `old_string` é vazio (`hooks/ordens_teto.py:37`), e `depois` devolve None quando o arquivo não se lê (`:48-51`); a ferramenta Edit cria o arquivo com o `new_string` quando `old_string` é vazio e o arquivo não existe (ou está vazio). Caminho: o Jarvis cria as ordens pela 1ª vez (ou regrava um arquivo vazio) por Edit com texto acima do teto; o hook cala e o `ordens` volta a cortar o fim (com o aviso, não calado). Sem ator hostil (só o Jarvis grava a pasta): severidade baixa, é furo do contrato que o PR declara. O teste `tests/test_hook_ordens_teto.py:101` deixa passar o vazio sobre arquivo não vazio, o que está certo (lá a ferramenta falha). Correção mínima: em `depois`, se a 1ª troca tem `old_string` vazio e o arquivo está ausente (`FileNotFoundError`, não o link para fora) ou vazio, o texto final é o `new_string` (e o resto das trocas do MultiEdit sobre ele); caso de teste com as duas formas. Esforço P. Dono: autor (tech-lead).

**A3.** Evidência: S3. Caminho: arquivo acima do teto por gravação fora do Write (o dono no editor, ou o Bash do Jarvis); o Jarvis tenta encurtar por Edit e é recusado até acertar o teto de uma vez. Severidade baixa (disponibilidade da correção, não da guarda). Correção mínima: em `principal`, antes de recusar, ler o texto atual (`ler_ordens`) e deixar passar quando o novo tem linhas e caracteres menores ou iguais aos atuais; a mensagem do aviso segue no `ordens`. Esforço P. Dono: autor (tech-lead).

**A4.** Evidência: `tests/test_hook_ordens_teto.py:26-35` monta só `.forge/versao` com git; nenhum caso usa a casa temporária com `~/.forge-contrib/docs/ordens/` e um clone com o manifesto do Forge, que é a fonte usada nas sessões do próprio Forge. S9a e S9b provam o comportamento de hoje, sem teste que o segure contra regressão em `fontes`. Esforço P. Dono: autor (tech-lead), com o qa-engineer.

Sondas executadas (nenhuma prova bloqueante; por isso o bloco `## Sondas` fica vazio). Roteiro em `$TMPDIR` da sessão, hook rodado como no `hooks.json` com ambiente limpo e casa temporária, sobre o head bc9b1d1f:
- S1 · Edit, arquivo ausente, old_string "", new_string 40 linhas · espera: 2 · obtido: 0 (A2)
- S2 · Edit, arquivo vazio, old_string "", new_string 40 linhas · espera: 2 · obtido: 0 (A2)
- S3 · arquivo com 20 linhas, Edit que tira a 20ª · espera (desejável): 0 · obtido: 2 (A3)
- S4 · arquivo com 20 linhas, Write de 15 · espera: 0 · obtido: 0
- S5 · arquivo com 20 linhas, MultiEdit que tira 5 · espera: 0 · obtido: 0
- S6a/S6b · na worktree: Write de 16 linhas no arquivo da worktree (não é fonte) · 0; no da cópia principal · 2
- S7 · Write de 16 linhas por link simbólico para o arquivo · espera: 2 · obtido: 2
- S8 · Write de 16 linhas por link duro para o arquivo · obtido: 0 (limite aceito, abaixo)
- S9a/S9b · clone do Forge, Write de 16 / 15 linhas em `~/.forge-contrib/docs/ordens/ordens-em-vigor.md` · 2 / 0
- S10 · nome com a caixa trocada · obtido: 0 (o sistema de arquivos daqui distingue caixa: é outro arquivo)

Limites sem achado (proporcionalidade): o link duro (S8) e a caixa trocada em sistema de arquivos que não distingue caixa escapam da comparação por `realpath` (`hooks/ordens_teto.py:27-29`); criar o link exige escrever na pasta das ordens pelo Bash, que o `conformidade` só dá ao Jarvis, e o Jarvis não ganha nada gravando por um nome torto. Se o autor quiser fechar de graça, comparar por `os.path.samefile` quando o arquivo existe resolve os dois.

Testes: `tests/test_hook_ordens_teto.py` rodado no clone revisado, 12 testes, OK. Suíte inteira: as 10 partes da suíte e as baterias de passos e verificações longas verdes no CI do head (run 45880744962); catraca vermelho (A1).

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Ferramentas: leitura estática, sondas locais do hook com ambiente limpo e o teste novo. Faltaram no ambiente (lacuna, nada instalado): gitleaks, semgrep, zizmor, actionlint e osv-scanner; o diff não traz segredo, dependência nem workflow, então a falta não muda o parecer.
