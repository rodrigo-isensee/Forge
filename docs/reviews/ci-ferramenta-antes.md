---
tipo: review
contrato: 1
pedido: ci-ferramenta-antes
branch: melhoria/ci-ferramenta-antes
commit: 07bfbe856be86649836f0bdce50cb83874a6e2c5
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-21
---
# Review: CI, a ferramenta e as checagens baratas antes dos testes

Escopo: `10c838f...07bfbe8`, 3 commits, 3 arquivos (`.github/workflows/ci.yml` +35 -32, `tests/test_ci_local.py` +23, fragmento `changelog.d/ci-ferramenta-antes.md`). Quem revisa não é o autor (D-ETAPAS-INST).

Veredito: **aprovado**, sem bloqueantes; duas recomendações abaixo.

## Ferramentas
- O Forge não tem `docs/engineering/praticas.md`; não há regra "ferramenta" com comando a citar. actionlint e zizmor sem PATH nesta estação: a prova deles é a própria bateria do PR (que agora os roda depois dos testes), a cargo do QA. Pendência registrada, não revisão manual.
- Suíte `tests.test_ci_local` rodada em cópias por `git archive`: em `19cb145` (só o teste) 1 falha, `AssertionError: 10 not less than 4 : Claude Code CLI`; em `10c838f` 49 OK; em `07bfbe8` 50 OK. Vermelho antes do verde comprovado.

## O que foi conferido
- E1, decisão D3 = A: o passo do Claude Code CLI (com `claude --version`) e o `validate --strict` vêm logo depois do setup do Node; changelog, release, degrau, segredo e parecer vêm antes de `Testes do Forge`. Os testes são o mesmo comando, sem `||`, laço nem `continue-on-error`, e com o mesmo `if` (`!cancelled()` + gate): continuam obrigatórios; nada afrouxado.
- Nova tentativa: confinada à instalação (uma só, `sleep 5`); a segunda falha encerra o passo pelo `bash -e` padrão do runner, e `claude --version` falho também. Não mascara falha determinística: ela falha duas vezes.
- Mudança de ordem de shellcheck, actionlint/zizmor e e2e (aviso do conferente): a posição deles em relação aos testes não mudou (já vinham depois); o bloco "testes + linters" desceu inteiro e o e2e foi junto para o fim. Como todos os passos usam `!cancelled()`, nenhum deixa de rodar por falha anterior. Efeito só de ordem no log, fora do pedido literal mas neutro.
- Dependências entre passos: o e2e usa o `claude` instalado antes; o `GITHUB_PATH` do actionlint/zizmor vale para os passos seguintes; o setup do Python segue antes de qualquer `python3` pesado. Job `rapida` intocado.
- Teste novo: `pos()` exige ocorrência única de cada nome (desempacotamento de um item), então renomear um passo quebra o teste em vez de passar calado. Os trechos procurados existem no `ci.yml` de `07bfbe8`.
- R-CUSTO: nenhum serviço pago; R-NEUTRO: sem termo de projeto. Fragmento em `changelog.d/` presente.
- Commits: Conventional Commits em português, vermelho, verde e fragmento separados.

## Recomendações (não bloqueiam)
- `.github/workflows/ci.yml:95`: a nova tentativa roda em qualquer falha do `npm install`, e a mensagem afirma "(rede)" sem conferir. A decisão D3 fala em nova tentativa por falha de rede; o risco que ela guarda (mascarar falha) não ocorre, mas a mensagem induz a erro. Sugestão numa próxima entrega: "instalação falhou; uma segunda tentativa (falha de rede é a causa esperada)" ou só repetir quando o log do npm trouxer `ECONNRESET|ETIMEDOUT|EAI_AGAIN|ENOTFOUND`.
- `changelog.d/ci-ferramenta-antes.md:2`: "o vermelho barato aparecer em segundos" vale para o log do passo; a conclusão do check `bateria` ainda espera o job inteiro, porque os passos seguintes rodam com `!cancelled()`. Precisar o texto na release, se o integrador quiser.
- shellcheck e actionlint/zizmor também são baratos (segundos) e poderiam vir antes dos testes; fica como candidato de outra melhoria, já que o pedido não os listou.

## Riscos e observações
- O passo de instalação não pôde ser exercitado aqui (npm não roda nesta estação); depende da bateria do PR.
- `.github/` é controle: parecer de segurança (E1.3), de devops (E1.6) e o rótulo do dono seguem em outras instâncias; este review não os substitui.

## Achados
