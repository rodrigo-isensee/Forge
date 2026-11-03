# 0015 - Porta de entrada do onboarding: terminal e Jarvis, sem hook fora de projeto

Estado: proposta. Data: 2026-11-02. Destrava: o PR da fase E do lote-unico-032 (L44 a L48), que traz o atalho `forge`, o prompt de primeiro uso, `forge adotar` e a skill `adotar-projeto`; vira `vigente` nesse PR.
Propósito: decidir por onde quem acabou de instalar o Forge chega aos dois caminhos (projeto novo e projeto existente) sem mudar o contrato dos hooks. Público: quem mantém o Forge e quem desenha a entrada de novos usuários. Revisão: 2026-12-02.

## Contexto
Fatos lidos em `docs/onboarding-1/arquitetura.md` (seção 0), conferidos por leitura de código:
1. O plugin não roda nada na instalação; "o primeiro contato" só pode ser a primeira sessão ou o primeiro comando no terminal.
2. Fora de projeto os hooks são inertes por contrato (ADR 0003, item 3; `raiz_do_projeto` só devolve raiz com `.forge/versao`).
3. O `SessionStart` não fala com a pessoa: o texto vira contexto do modelo (ADR 0003, item 1); um aviso só sairia no `Stop`, depois da primeira resposta.
4. Numa pasta sem `.forge/versao` quem abre não é o Jarvis: o atalho `jarvis` roda `claude --continue` sem `--agent`; o texto do Jarvis sobre o primeiro uso nunca é lido ali.
5. O `forge` provavelmente não está no PATH do terminal (a referência de plugins põe `bin/` no PATH só da ferramenta Bash); o `scripts/instalar-atalho.sh` instala só `jarvis` e `jarvis-forge`. A conferência numa estação limpa (`command -v forge`) é do QA da fase E.

## Decisão
Entrada pelo terminal e pelo texto do Jarvis, sem hook novo (alternativa A do desenho do ONBOARDING-1):
1. **`forge` sem argumento** mostra boas-vindas curtas (o que é, os dois caminhos, a lista de subcomandos); `-h` segue mostrando só a lista.
2. **`forge` no PATH do terminal:** o `instalar-atalho.sh` instala também um `forge` em `~/.local/bin`, que acha o `bin/forge` do plugin instalado.
3. **`jarvis` em pasta sem `.forge/versao`:** em repositório git que não é o clone do Forge, abre `claude --agent forge:jarvis` com o prompt de primeiro uso; fora de repositório, oferece só `forge novo-projeto`. Nunca no clone do Forge.
4. **`forge adotar`** (leitura do projeto, branches que faltam, estado, retomada) termina abrindo o Jarvis com o prompt da skill `adotar-projeto`; o `forge-init` não troca um `core.hooksPath` alheio.
5. **Texto do Jarvis** fica como rede de segurança para quem abre `claude --agent forge:jarvis` à mão.
6. **Não toca `hooks/`** nem o contrato "hooks só agem em projeto com `.forge/versao`".

## Alternativas
| Opção | Prós | Contras |
|---|---|---|
| B. Hook de início de sessão fora de projeto | Alcança quem abre `claude` direto | Quebra a ADR 0003 (inertes fora de projeto); dispara em todo repositório aberto; o aviso só sai no `Stop`; o agente continua sendo o padrão; toca `hooks/hooks.json` e `hooks/_comum.py` |
| `settings.json` na raiz do plugin com `agent: forge:jarvis` | Sem script | O Jarvis viraria o agente principal em toda pasta com o plugin ativo, inclusive nas sessões do próprio Forge |

## Consequências
- Mais fácil: zero token em pasta que a pessoa não quer adotar; nenhuma superfície nova de hook; a adoção reusa o `forge-init` e as skills existentes.
- Mais difícil: quem instala e abre `claude` direto, sem digitar `forge` nem `jarvis`, não vê a oferta até ler o README; mais um subcomando (`forge adotar`) e uma skill a manter.
- `forge adotar` toca credenciais do `gh`, `core.hooksPath` e branch remota: o parecer de segurança da fase E o cobre.

## Por que o existente não basta
Existe a oferta do `novo-projeto` no texto do Jarvis (`agents/jarvis.md`, "Primeiro uso") e o `forge novo-projeto`. Pela leitura de código (fato 4), o texto não é lido em pasta sem `.forge/versao`, e `forge` não chega ao PATH do terminal (fato 5). Não há `bin/forge-adotar` nem skill de adoção para repositório existente. Evidência de execução: a conferência de `command -v forge` fica para o QA da fase E (sem ela, o fato 5 é por leitura).

## Critério de reversão
Reabrir a alternativa B (só `systemMessage`, no `Stop`, uma vez por pasta) se o teste do tutorial com uma pessoa nova, ou duas sugestões vindas de projetos (`forge sugerir`), mostrarem alguém que instalou, abriu `claude` direto e não achou os caminhos.

## Leituras
| Data | Medida | Veredito (manter, ajustar, reverter) |
|---|---|---|
| 2026-12-02 | sugestões de projeto e testes de tutorial que citam "não achei por onde começar" | pendente |
