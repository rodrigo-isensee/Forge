---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-pv-b3-pre-push
commit: 081067f06a28a5bea555e81f69e9cbb35d8c05b2
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: v0478 E57.41 (patch PR-VERDE B3 do pre-push)

Escopo: `docs/engineering/v0479-pv-b3-pre-push.patch` (35 linhas acrescentadas em `.githooks/pre-push`, blob base `f9443600`) e os comandos de aplicar e testar de `docs/engineering/v0479-pv-b3-pre-push.md`. O patch não foi aplicado na branch; foi aplicado só numa cópia descartável em `$TMPDIR` para as sondas.

## Gatilhos
Gatilhos: hook de envio (controle do Forge, arquivo protegido), execução de código da árvore no envio, variável de ambiente que decide o controle.

## Achados
- A1 (bloqueante) docs/engineering/v0479-pv-b3-pre-push.patch:23 · FORGE_REGISTROS_PRAZO vai cru ao timeout: com o valor --help (ou --version) o timeout imprime a ajuda, sai 0 e a conferência nunca roda; registro desatualizado passa sem --no-verify. Validar só dígitos (como FORGE_TRAVA_ESPERA) e recusar o resto.
- A2 (recomendado) docs/engineering/v0479-pv-b3-pre-push.md:32 · O comando de aplicar lê o patch da ponta móvel da branch, não do commit revisado 081067f0; fixe o sha revisado e confira com git apply --stat que só .githooks/pre-push muda antes do git apply.
- A3 (recomendado) docs/engineering/v0479-pv-b3-pre-push.md:25 · O texto diz que o patch não adiciona opção de pular; com A1 adiciona. Corrigir o texto junto com A1 e somar a sonda S1 ao roteiro de teste (caso 6: prazo não numérico recusa).

## Sondas
- S1 · cópia em $TMPDIR com o patch e um tests/test_sonda_sem_peso.py sem peso; FORGE_REGISTROS_PRAZO=--help .githooks/pre-push origin <bare vazio> < stdin · espera: rc 1, registro desatualizado · obtido: rc 0, checagens baratas ok, envio leve
- S2 · mesma cópia, sem FORGE_REGISTROS_PRAZO · espera: rc 1 · obtido: rc 1, registro desatualizado test_sonda_sem_peso sem peso, checagens baratas reprovadas (controle da S1)

## Detalhe dos achados
**Só aperta?** Sim, quanto ao que já existe: o patch só acrescenta linhas (`git apply --numstat`: 35/0), entra depois das checagens atuais em `checagens_baratas`, usa variáveis já declaradas `local` na função (`.githooks/pre-push:339`: `envio ponta ref saida rc`), só atribui `falhas=1` e nunca a zera, e roda antes da saída do envio leve (`.githooks/pre-push:397-404`). Ferramenta ausente ou link segue com aviso, como a regra D6 já aceita para as outras checagens. Nenhuma recusa atual é afrouxada. O defeito é que a recusa nova tem uma porta (A1).

**A1** · evidência: patch:23, `timeout "${FORGE_REGISTROS_PRAZO:-180}" python3 ...`; o coreutils trata `--help`/`--version` como opção, sai 0 sem executar o comando (S1). Caminho de ataque: agente com envio recusado por registro desatualizado exporta a variável e envia; não usa `--no-verify`, então a proibição de `R-VERIFY` não o pega à letra, e o envio passa. O CI ainda reprova (impacto limitado a burlar o portão local e gastar CI), mas o caso de abuso do próprio B3 é "nunca verde por defeito da conferência". Severidade: média. Correção mínima (dono `devops-engineer`, aplica o dono do Forge): antes do laço, `prazo="${FORGE_REGISTROS_PRAZO:-180}"; case "$prazo" in ''|*[!0-9]*) echo "pre-push: FORGE_REGISTROS_PRAZO deve ser um número de segundos inteiro (veio '${prazo}')." >&2; falhas=1 ;; esac`, rodar a conferência só com o prazo válido e chamar `timeout -- "$prazo" python3 ...` (o `--` também fecha a porta sozinho: valor iniciado por `-` vira erro 125, que recusa). Esforço P. Observação: `FORGE_REGISTROS_PRAZO=0` desliga o prazo (sem limite), mas a conferência roda; não é desvio.

**A2** · `git show origin/melhoria/v0479-pv-b3-pre-push:...patch` pega o que estiver na ponta no momento de aplicar; quem tiver escrita na branch troca o patch depois do parecer e o dono aplica o que ninguém revisou. Hoje o patch só toca `.githooks/pre-push`, e o `git add` explícito limita o commit, mas a árvore pode ficar com outras mudanças. Correção: `git show 081067f06a28a5bea555e81f69e9cbb35d8c05b2:docs/engineering/v0479-pv-b3-pre-push.patch` (ou o sha da revisão seguinte), `git apply --stat` antes e `"${TMPDIR:-/tmp}"` (fora do sandbox o `$TMPDIR` pode estar vazio e o arquivo iria para `/b3.patch`). Severidade baixa. Dono `devops-engineer`.

**Comando de testar (doc:41-48):** seguro. Roda o hook direto numa cópia em `$TMPDIR`, sem `git push`; no envio leve o hook sai antes de trava e fila (`.githooks/pre-push:401-404`), e o único acesso a rede é leitura (`ls-remote` do destino e o `git fetch` da `develop` feito pelo `forge-testes`). Ao reproduzir, use como `<url>` um repositório que não tenha a branch de prova (ex.: um bare vazio): com a própria cópia o hook responde "o remoto já tem o que seria enviado" e não confere nada.

**Outros pontos conferidos, sem achado:** saída do `forge-testes` filtrada de caracteres de controle antes de ir ao terminal (patch:28, :36); `env -u BASH_ENV -u ENV` e `python3 -I` (o apoio é carregado por caminho do arquivo, `bin/forge-testes:79`, e os dois arquivos são conferidos contra link); entrada fechada com `</dev/null`; ref só `refs/heads/?*`; o `--base origin/develop` vai ao `git fetch` com `--end-of-options` e ramo validado (`bin/forge-testes:117`, `:923`). A conferência só vale quando a ponta enviada é o HEAD (patch:20), a mesma regra aceita do changelog; enviar outro commit pula a conferência e o CI confere (D6). Executar `bin/forge-testes` da árvore não cruza fronteira: é o código de quem envia, como o próprio hook. `bash -n` do hook com o patch: ok.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: `git apply --check/--numstat`, `bash -n`, sondas no hook aplicado numa cópia descartável. Lacunas: `shellcheck` e `gitleaks` não estão no PATH desta estação (o CI roda a bateria). Suíte não rodada localmente (brief: sem suíte local); o parecer não substitui o CI do PR que aplicar o patch.
