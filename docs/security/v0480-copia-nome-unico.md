---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-copia-nome-unico
commit: 950115403000c469798f92046bce95713ddfb5b3
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-23
---
# Review de segurança: v0478 (E111.3, CLONE-NOME-UNICO no forge-copia)

Delta lido: `900bfdfe..95011540` (`bin/forge-copia`, `tests/test_forge_copia_nome.py`, `tests/mutantes/v0480-copia-nome-unico.json`, `tests/mutantes/v0475-copia-pasta.json`, `tests/pesos-d4.json`, `changelog.d/v0480-copia-nome-unico.md`).

## Gatilhos
Gatilhos: controle do Forge (caminho de escrita das cópias na pasta liberada do sandbox), execução de git sobre pasta de terceiros.

## Conferência (CLONE-NOME-UNICO)
- **Caminho:** o nome sugerido sai de `--branch`, já validado por `git check-ref-format --branch` (`bin/forge-copia:263`) antes de `destino_dentro`; `/` vira `-` (`bin/forge-copia:84`), então o nome não tem separador e fica em `dirname(real)`, que já passou pelo `commonpath` da pasta liberada (`bin/forge-copia:110`). `--papel` só casa `[a-z0-9][a-z0-9-]*` com `re.fullmatch` (`bin/forge-copia:265`; recusa `../x`, `a/b`, `-qa` e `qa\n`). `..`, `@{-1}` e componente com `-` não escapam (sondas abaixo); o caminho sugerido é absoluto, nunca lido como opção.
- **Link:** o nome sugerido pode ser um link para pasta vazia fora da pasta liberada (A1), mas quem o usa é recusado por `destino_dentro` (`realpath` + `commonpath`, `bin/forge-copia:107-111`) e nada é escrito fora: falha fechado.
- **Caractere de controle:** a ref git recusa controle (< 0x20, DEL); controle bidirecional Unicode passa na branch e aparece na sugestão (sonda S3), mas só como texto de mensagem, sem efeito de caminho: sem achado.
- **Recusa falha fechado:** o destino ocupado sai com 2 antes de medir disco, criar `.gitignore` ou rodar git de escrita (`bin/forge-copia:267-269`); `tomado` só roda `git branch --show-current` dentro da própria cópia (`.git` presente) com `core.fsmonitor=` vazio e `--no-optional-locks` (`bin/forge-copia:95-96`), sem pager (saída capturada). Erro de leitura de pasta irmã em `nome_unico` levanta exceção e encerra sem criar nada (não pude provar o caso como root; sem achado).

## Achados
- A1 (recomendado) bin/forge-copia:79 · `ocupado` segue link: um link com o nome sugerido apontando para pasta vazia fora da pasta liberada é dado como livre e sugerido (S1); o uso é recusado depois, mas a sugestão deveria pular link: tratar `os.path.islink` como ocupado.

## Sondas

## Detalhe dos achados
**A1.** Evidência: `bin/forge-copia:79` (`ocupado`) e `:86` (laço de `nome_unico`). Sonda S1: com `c1` ocupado e `~/.forge-contrib/b-qa` como link para uma pasta vazia fora, `forge-copia clone c1 --branch melhoria/b --papel qa` sugere `.../b-qa` (rc 2); usar a sugestão dá `recusado: o destino fica fora de ...` (rc 2) e a pasta de fora fica vazia. Caminho de ataque: quem já escreve na pasta liberada planta o link; o agente segue a sugestão e só perde uma rodada. Severidade: baixa (sem escrita fora; falha fechado). Correção mínima: `return os.path.islink(caminho) or (os.path.lexists(caminho) and (not os.path.isdir(caminho) or bool(os.listdir(caminho))))` e um teste com o link. Esforço: P. Dono: autor da branch (E111.1).

Outras sondas (sem achado, entrada · obtido): `--branch melhoria/-rf` · sugere `<pasta>/-rf`, absoluto, rc 2; `--branch melhoria/a/../../x` · `nome de branch inválido`, rc 2; `--branch @{-1}` · `nome de branch inválido`, rc 2; `--papel $'qa\n'` · `papel inválido`, rc 2.

Teste novo rodado: `python3 -m unittest tests.test_forge_copia_nome` · 8 testes, OK. Suíte inteira: não rodada (brief: sem suíte local); sem PR aberto, CI ainda não conferido: o portão de merge segue dependendo do CI verde.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática e sondas locais em pasta temporária; varredor de segredos, SAST e auditor de dependências ausentes no PATH (lacuna; o delta não traz dependência nem segredo, conferido à mão).
