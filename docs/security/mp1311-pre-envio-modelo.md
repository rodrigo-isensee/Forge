---
tipo: revisao-seguranca
contrato: 1
pedido: melhorias-de-projeto-1311
branch: melhoria/mp1311-pre-envio-modelo
commit: 2b5fbd83fb4776c16dd6668448b0accb9d0a9657
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-14
---
# Review de segurança: melhorias-de-projeto-1311 (pré-envio no modelo, E1.34; revalidação E1.57)

Revalidação E1.57 por delta 27c40107..2b5fbd83 (`forge-check parecer delta`): `so_docs` do `templates/projeto/.githooks/pre-push` passa a pular o pronto rápido também com `changelog.d/**` e com arquivo igual ao da `origin/develop` (junção; DECISÃO DO DONO 13/11 17:31); `pre-push.local` com laço seguro para lista vazia sob `set -u`; texto da migração 0.47.1 e dos `pronto.md`; seção de veredito do vermelho da stack node-react (texto de processo, sem execução). Sem bloqueante: o pulo só afeta lint e tipos locais, a bateria completa segue no CI do projeto, e toda dúvida (ref ausente, arquivo apagado, `.github/`, tag, remoção) cai em rodar tudo.

Head 27c40107, diff contra a base c5aa70e1: migração 0.47.1 (passo pre-envio), `forge-upgrade` com vários passos por versão, `forge-init`, modelo `pre-push.local` e modelo de PR, arquivos de pronto das stacks.

## Gatilhos
Hook de git que executa comando no envio (`pre-push.local`) e migração que grava arquivo executável no projeto: gatilho de controle e de execução de código. Sem segredo, dado pessoal, rede ou dependência nova.

## Achados
- A2 (recomendado) templates/projeto/.githooks/pre-push:80 · `origin/develop` sem nome completo: uma tag ou branch local `origin/develop` sombreia a ref remota e faz código novo parecer junção, pulando o pronto rápido; use `refs/remotes/origin/develop` (S1).
- A1 (recomendado) bin/forge-init:69 · `escapar` cobre `/`, `&` e `|`, não `\` nem quebra de linha; hoje sem efeito, porque o texto vem do arquivo de pronto da stack, que é do Forge.

## Sondas
- S1 · repo descartável, `y` mudou depois de `refs/remotes/origin/develop`; `git tag origin/develop HEAD`; `git rev-parse -q --verify origin/develop:y` · espera: blob da ref remota (61780798) · obtido: blob do HEAD (f2ad6c76), a tag venceu

## Detalhe dos achados
Verificado sem achado bloqueante:
- Stack lida do `CLAUDE.md` do projeto (migrar-pre-envio:23-30) é validada por `[a-z0-9-]+` e por existência do arquivo (linha 36) antes de virar caminho: sonda com `../../x` imprimiu aviso e não criou `.githooks/pre-push.local`.
- Valores gravados no `pre-push.local` vêm só de `stacks/<stack>/pronto.md` (conteúdo do Forge, não do projeto nem de entrada externa); substituição por `str.replace` na migração, sem shell. O teste PreEnvioDoModelo trava aspas simples no comando (tests/test_forge.py:1287).
- Não sobrescreve nem segue arquivo existente (`exists()` ou `is_symlink()`, migrar-pre-envio:56,61); idempotente (segunda rodada rc=0, sem criar).
- `.git/info/exclude`: caminho vem de `git rev-parse --git-path`; só acrescenta os arquivos criados.
- `forge-upgrade`: `migracoes_pendentes` restringe a `migrar` e `migrar-*` dentro de `migrations/` do próprio plugin; rótulo e LEIA derivados do nome do arquivo, sem entrada do projeto; execução sem shell (lista de argumentos).
- `pre-push.local` executa `bash -c "$rapido"` com comando do próprio repositório do projeto, mesma fronteira de confiança do `.githooks/pre-push` existente; falha fecha (exit 1) e orienta; ausência de código da stack pula com aviso, não abre brecha de bypass além do que o dono já controla.
- Modelo de PR é só texto.

Esforço de A1: P; dono: devops-engineer (ou dono do `forge-init`).

Revalidação E1.57 (delta 27c40107..2b5fbd83), verificado sem bloqueante:
- Junção (pre-push:79-81): compara o blob de `origin/develop:<f>` com o de `<sha local>:<f>`; ref ou arquivo ausente em qualquer lado vira `recusa=1` (roda tudo); arquivo apagado no envio roda tudo. O caminho depois de `:` é literal (sonda com `x^{}` resolveu o mesmo blob dos dois lados, sem descascar); lista lida com `-z`, sem quebra por espaço ou nova linha.
- Caminho de abuso de A2: só quem já escreve no repositório local (o próprio autor ou agente) cria a tag; o ganho é pular lint e tipos locais, que o CI refaz e que são portão do merge. Por isso recomendado, não bloqueante. `git update-ref refs/remotes/origin/develop` continua possível mesmo com o nome completo; o nome completo fecha o sombreamento acidental e o atalho mais curto. Mudança só de modo (bit executável) com o mesmo blob também passa como igual; irrelevante para lint.
- `changelog.d/**` na lista de texto: fragmentos de changelog, sem execução.
- `pre-push.local:11`: `${arquivos[@]+"${arquivos[@]}"}` evita o erro de variável não definida com detecção vazia no bash antigo; sem mudança de fronteira.
- `stacks/node-react/pronto.md` (veredito do vermelho): texto de processo; o `git stash push/pop` é local, sem segredo nem rede. Coerência do passo (stash com a árvore limpa) é do review e do QA, não de segurança.

Esforço de A2: P; dono: tech-lead (autor da E1.37).

## Riscos aceitos e ferramentas
Nenhum risco aceito. E1.57: `tests.test_prepush_so_docs` (62, OK, 9 pulados pelo sandbox) e `tests.test_forge.PreEnvioDoModelo` (18 OK) no head 2b5fbd83; CI do PR 555 no mesmo head com as partes da suíte verdes, só `bateria (pareceres)` vermelha pelos pareceres a revalidar. Ferramentas: leitura estática e sondas locais; testes rodados: `tests.test_adotar` (24 OK) e `tests.test_forge.PreEnvioDoModelo` (14 OK). Suíte inteira: CI do PR (não há PR aberto; não conferido). Lacuna: nenhuma ferramenta de varredura invocada, nenhuma é necessária para este diff.
