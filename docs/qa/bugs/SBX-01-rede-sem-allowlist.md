# SBX-01 - Sandbox do Bash acessa qualquer host, a allowlist de rede não é aplicada
- Status: limite documentado (rodada 1 de correção; o QA revalida). `network.allowedDomains` no projeto só pré-libera; restringir a rede exige `sandbox.network.strictAllowlist: true`, que só vale em `~/.claude/settings.json` ou em configuração gerenciada. Não é defeito do arquivo do projeto; decisão de ligar é do dono (README, "Sandbox do Bash").
- Severidade: crítica (falha de segurança: a contenção de rede prometida no README não se sustenta)
- Responsável sugerido: dono do Forge (`.claude/settings.json` é protegido e a mudança é decisão do usuário, R-DECISAO); revisão pelo `tech-lead`
- Ambiente: branch `melhoria/sandbox-bash`, commit 4b9a502 (HEAD da sessão de teste), Linux/WSL2, Bash com sandbox ativo

## Passos para reproduzir
1. Na raiz do Forge, com o sandbox ativo: `curl -s -o /dev/null -w "%{http_code}\n" https://example.com`
2. Repetir com um host fora da lista: `curl -s -o /dev/null -w "%{http_code}\n" https://httpbin.org/get`

## Resultado esperado
Ambos bloqueados pelo sandbox. O README (seção "Sandbox do Bash", item Rede) diz: "só GitHub, npm e PyPI". `allowedDomains` em `.claude/settings.json` lista somente esses domínios.

## Resultado obtido
- `example.com`: HTTP 200 (IP remoto `::1`, corpo servido). Sem `<sandbox_violations>`.
- `httpbin.org/get`: HTTP 200.
- Só as APIs de `deniedDomains` (`api.anthropic.com`, `api.openai.com`) são negadas, com 403 e `deny network-outbound ... (host is on the deny list)`.
- Conclusão: a lista de negação funciona; a lista de permissão (`allowedDomains`) não é aplicada como barreira.

## Evidência
Saída literal dos dois `curl` acima: `http=200` para `example.com` e `http=200` para `httpbin.org`. Sandbox ativo confirmado pelo bloqueio de `~/sonda-sandbox` e `.git/config` (Read-only file system) na mesma sessão.
Impacto prático: o Bash consegue enviar código do projeto a qualquer destino, o que contraria a contenção de ADR 0009.
