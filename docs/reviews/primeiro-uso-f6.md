---
tipo: review
contrato: 1
pedido: primeiro-uso-f6
branch: melhoria/primeiro-uso-f6
commit: ea227ed
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-14
---
# Parecer de autor: primeiro uso F6 (`forge sugerir`)

Autor e revisor são o mesmo papel aqui: este parecer é de autor e não substitui a review independente do PR.

## O que foi conferido
- **Anonimização** (`bin/forge-sugerir`): tokens (prefixos conhecidos, JWT, hex longo, `chave=valor`), e-mails, endereços de repositório (os do próprio Forge ficam), caminhos absolutos (Unix, `~`, Windows), nome do projeto (`.forge/novo-projeto.json`, remoto `origin`, pasta) e da pessoa (dono, `USER`, pasta pessoal, nome do git). É heurística: a pessoa vê o texto final antes de qualquer envio, e essa é a garantia real.
- **Nada sai sem "s":** recusa, fim de entrada, sem terminal e chamado de dentro do Claude guardam na fila (texto já anonimizado, modo 600); `--fila` recusa dentro do Claude e sem terminal. Falha do `gh` (rede) guarda e sai com 1. Sem rótulo, sem edição, só `gh issue create -R` (repositório trocável por `FORGE_SUGERIR_REPO`, para testes).
- **Hook e regra:** `gh issue create` já passava; ficou travado por fixture. Apertou: `gh issue create --label|-l` no Forge, de sessão de projeto, é barrado (rótulo é da sessão do Forge). `R-CONTRIB` diz que issue nova é permitida. Confere com a catraca: o único afrouxamento aparente (`gh issue create` explícito) não muda o comportamento, e a mudança no hook é restrição.
- **Testes:** 14 em `tests/test_sugerir.py` (12 falhavam sem a mudança) com `gh` falso e pty, e 3 fixtures de hook (2 vermelhas antes). Suíte completa 473 OK; `validar-plugin.sh` ok; `shellcheck bin/forge` limpo (`forge-sugerir` é Python).

## Riscos e pendências
- Altera `hooks/conformidade.py`: o PR precisa do rótulo `afrouxa-regra` do dono.
- O texto vai por issue pela conta da pessoa (P1 = A); o envio por bot e `Forge-contrib` fica para depois.
- A sugestão é pública se o repositório do Forge for público; o aviso diz que aparece com o nome de usuário.
- O PR é empilhado: depende de #111, #110, #103 e #102.
