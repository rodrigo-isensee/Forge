---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-ae4-ordens
commit: 768ddb9017fda505bfe54164e1b962eaffecc943
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: v0479-ae4-ordens (AE4.1, revalidação E58.107)

Volta por delta. Rodada anterior: o parecer que aprovou df0cf4d9 (fica no git). Delta lido por `forge-check parecer delta`: `df0cf4d9..768ddb90`, sem o que veio da develop; no domínio, `agents/jarvis.md` e `bin/forge-check`.
- Merge da develop (7cf7d1e4, pais 9a66c9a4 e a6baf239): o diff próprio da branch contra a develop em `bin/forge-check`, `bin/forge-testes`, `agents/jarvis.md` e `hooks/` é linha a linha igual ao de df0cf4d9 contra a base anterior c9d69234 (`git diff -U0`, linhas `+`/`-`: zero diferenças). Sem resolução à mão; o código da develop (inclusive `hooks/conformidade.py`) veio pelos PRs dela e não é relido aqui.
- `bin/forge-check:5085,5094,5097,5099`: as quatro recusas do `--cartao` passam o alvo por `sem_controle` (saída lida por modelo). Hoje o alvo já chega validado por `APONTADOR` no `cmd_anotar`; é defesa em profundidade.
- `bin/forge-check:7588-7589,5118,7946`: `APONTADOR` e `CARTAO_DA_ORDEM` viram texto compilado no uso (`re.fullmatch`/`re.search`); o padrão é o mesmo de antes, e o `fullmatch` sobre a alternância sem grupo cobre a cadeia inteira nos dois ramos, como antes.
- `bin/forge-check:7567`: `DECISAO_DO_REGISTRO` volta ao `re.compile` direto, com padrão idêntico ao de `registro_da_frase(FRASE_DO_DONO)`.
- `agents/jarvis.md:12-16`: texto encurtado (`ordem: --cartao`) e a linguagem fácil em item próprio; a regra da ordem segue no `forge-check anotar`, que é quem a impõe.

## Gatilhos
Gatilhos: controle do Forge (guarda de gravação do registro do dono no `bin/forge-check`), mudança no `bin/forge-check` sujeita à catraca `afrouxa-regra`.

## Estado dos achados anteriores
- A1, A2, A3, A4 (rodadas anteriores): corrigidos, sem mudança no delta.

## Só aperta? (confirmação escrita para a catraca)
Confirmação: só aperta. A guarda do `cmd_anotar` aceita e recusa exatamente o mesmo conjunto (padrão de `APONTADOR` inalterado, só compilado no uso); `CARTAO_DA_ORDEM` e `DECISAO_DO_REGISTRO` têm padrão idêntico ao aprovado; as quatro recusas ganham `sem_controle`, o que só retira caractere de controle da saída; o merge da develop não altera o diff próprio da branch; o resto é texto do Jarvis sem mudança de regra.

## Detalhe
- Sonda de equivalência no head (módulo carregado de `bin/forge-check`): `re.fullmatch(APONTADOR, x)` e `re.compile(APONTADOR).fullmatch(x)` dão o mesmo resultado em `AE4-1`, `E58`, `E58.107`, `E58.1a` (aceitos) e `AE4-1\n`, `E5 `, `x|E5`, `AE4-1|E5`, `ae4-1`, `E5.1.2` (recusados); `DECISAO_DO_REGISTRO.pattern == registro_da_frase(FRASE_DO_DONO).pattern` é `True`; `sem_controle("E9\x1b[2J\nproximo: falso x")` sai numa linha só.
- `python3 -m unittest tests.test_ordens tests.test_decisoes`: 29 testes, OK.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Suíte: sem PR nem CI no head (o brief pede sem suíte local); rodei só os testes das ordens e das decisões. Ferramentas: `forge-check parecer delta`, `git diff`, leitura estática e a sonda acima.
