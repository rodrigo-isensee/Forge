---
tipo: revisao-seguranca
contrato: 1
pedido: v048
branch: melhoria/v0481-ambiente-claude-path
commit: 75f2e456414d0cb3e8e6e32c3afd1752798db61d
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-28
---
# Review de segurança: v0481-ambiente-claude-path (PR #965, volta 1, E13.24)

Revalidação por delta no head 75f2e456. A 1ª rodada (df4b2bf9, E13.9) fica no git; aqui vão só o delta lido e o estado dos achados.

## Gatilhos
Gatilhos: script de preparo da estação executado como root (scripts/preparar-estacao.sh), configuração do container com código baixado e executado no início (postStartCommand do .devcontainer).

## Achados

## Sondas

## Detalhe dos achados
**Delta lido** (`forge-check parecer delta`, df4b2bf9..75f2e456): no domínio, só `scripts/preparar-estacao.sh`, uma linha nova de comentário `# shellcheck disable=SC2016` com o motivo, logo acima do `grep` da linha 198 (antiga 197). Não muda comportamento: o padrão do `grep`, o `return` e o `printf` que grava no `.bashrc` ficam iguais. Fora do domínio, os três pareceres da 1ª rodada (docs/).

**Achados anteriores:**
- A1 (bloqueante, SC2016 em scripts/preparar-estacao.sh:197): resolvido. `shellcheck scripts/preparar-estacao.sh` no 75f2e456 sai com rc=0, sem aviso.

**Este commit:** regrava o parecer de segurança. A versão da 1ª rodada citava por extenso, como exemplo de linha recusada, uma pasta de outro usuário sob a raiz das pastas pessoais. Isso derrubou a "bateria (passos)" do run 46166972749 (verificar-contribuicao.sh: caminho pessoal em docs/security/v0481-ambiente-claude-path.md:28). A conclusão sobre o PATH não muda: o padrão novo aceita um subconjunto estrito do antigo.

**CI:** no run 46166972749 (head 75f2e456), "bateria (passos)" falhou só pelo texto do parecer, e "bateria (pareceres)" e "bateria" falharam em cascata. Por isso as verificações longas e a suíte em 5 partes foram puladas. Este parecer não afirma CI verde: a suíte inteira e o shellcheck do CI ficam para o run do head com este commit. Local, depois desta regravação: `scripts/verificar-contribuicao.sh origin/develop` passa.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Ferramentas: shellcheck (presente). Lacunas: gitleaks, zizmor e actionlint ausentes no PATH (não instalados, R-CUSTO). Nenhum workflow mudou no delta.
