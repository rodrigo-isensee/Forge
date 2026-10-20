---
tipo: revisao-seguranca
contrato: 1
pedido: dv-5
branch: melhoria/dv-5
commit: 90014ae265c00c8129b9af1d1d465f4e828bd03f
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-20
---
# Review de segurança: dv-5

Escopo: `git diff 87dbbad67f931b2f004ea4c94f82a970f4f0180d 90014ae265c00c8129b9af1d1d465f4e828bd03f` (trava de release em `forge-check sobreposicao --ref`, frase na Fila de integração da R-FLUXO, invariante novo, testes `TravaDeRelease`, fragmento `changelog.d/dv-5.md`).

## Gatilhos
Controles do Forge (R-SEGURANCA): `docs/regras/R-FLUXO.md` e `tests/config.json` no diff; `bin/forge-check` é o conferente da fila de integração.

## Achados

## Detalhe dos achados
Verificações pedidas, com resultado:

- **Só restringe.** `bin/forge-check:3108` soma a trava depois de `cmd_sobreposicao`, cuja saída não muda; o rc só pode subir (`rc or ...`). Sem `--ref` o caminho antigo fica idêntico (o `and a.ref` curto-circuita, e `movimento` nunca lê `a.ref`). Na R-FLUXO (`docs/regras/R-FLUXO.md:16`) a frase só acrescenta uma espera; a frase final de que nenhum check nem parecer é dispensado continua. O invariante novo em `tests/config.json` só acrescenta proteção. Nenhum check, parecer ou hook é dispensado.
- **Erro de leitura.** `versao_do_plugin` (`bin/forge-check:1105`) trata ref ausente, JSON inválido, JSON que não é objeto, `version` ausente, não texto ou fora de `X.Y.Z` (TypeError, KeyError, ValueError cobertos; conferido em repositório descartável com `[1]` no plugin.json: aviso e rc 0). O erro não é silencioso: sai a linha `aviso: ... trava de release não conferida`; e não bloqueia sem prova (rc 0), como o pedido E1 manda. Timeout do git sobe como exceção (rc diferente de 0, ruidoso), não como verde.
- **`--ref` não burla por nome parecido.** `bin/forge-check:1130` tira no máximo `refs/heads/` e depois `origin/` e compara por igualdade exata com `melhoria/release-<versão da develop>`. Conferido em repositório descartável: `melhoria/outra`, `melhoria/release-0.24.0 ` (espaço), `melhoria/release-0.24.0/x`, `Melhoria/release-0.24.0`, `melhoria/release-0.23.0` e `refs/remotes/origin/melhoria/release-0.24.0` saem com rc 1 (o último é falso positivo, do lado restritivo); `melhoria/release-0.24.0`, `refs/heads/...` e `origin/...` passam. O valor de `--ref` nunca vai ao git (só comparação de texto): sem injeção de argumento.
- **Sem rede (R-CUSTO).** Só `git show <ref>:.claude-plugin/plugin.json` sobre refs locais, pelo `git()` único (`bin/forge-check:321`, sem variáveis GIT_* herdadas e com timeout); nenhum fetch, nenhuma biblioteca de rede.

Recomendações (não bloqueantes; severidade baixa ou informativa; a trava é contra engano do integrador, não fronteira contra adversário, e o PR continua passando por todos os checks e pareceres):

- R1 (baixa) `bin/forge-check:1123` · as refs `origin/develop` e `origin/homolog` são resolvidas por nome curto; uma branch local chamada `origin/develop` tem precedência sobre `refs/remotes/origin/develop` (o aviso de ambiguidade do git fica no stderr capturado). Conferido: com essa branch local na versão da homolog, a trava fica em rc 0 sem aviso. Caminho: só por engano ou por quem já escreve no repositório do integrador, que poderia também não rodar o passo. Correção mínima: ler `refs/remotes/origin/develop` e `refs/remotes/origin/homolog`. Esforço P. Dono: tech-lead.
- R2 (baixa) `docs/regras/R-FLUXO.md:16` · a trava lê refs locais: `origin/develop` desatualizada (antes do commit que sobe a versão) dá falso negativo, deixa passar. O risco já está no histórico do pedido; a frase da regra não diz para fazer `git fetch` antes. Correção mínima: na mesma frase, depois de `git fetch`. Esforço P. Dono: tech-lead.
- R3 (informativa) `bin/forge-check:1130` · a trava confia no nome declarado em `--ref` (não resolve a ref nem confere o conteúdo); quem cria uma branch `melhoria/release-<versão>` passa. Aceitável pelo propósito (ordem da fila, não autorização); a conferência na máquina para a promoção é a DV-4, fora deste pedido. Nenhuma ação agora.
- R4 (informativa) o passo depende de o integrador rodá-lo (a R-FLUXO o manda; nenhum hook ou CI o exige no merge na develop). Fora do escopo da DV-5; candidato a pedido futuro se a fila mostrar esquecimento.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Revisão manual do diff mais execução local de `bin/forge-check` em repositório git descartável no `$TMPDIR` (sem rede). `gitleaks`, `osv-scanner`, `semgrep`, `zizmor` e `actionlint` não estão no PATH (lacuna; o diff não toca dependência, workflow nem segredo). A suíte completa não foi rodada por esta revisão (fica com o QA; a entrega registra 941 OK).
