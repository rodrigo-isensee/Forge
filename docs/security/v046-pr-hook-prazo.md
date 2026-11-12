---
tipo: revisao-seguranca
contrato: 1
pedido: v046
branch: melhoria/pr-hook-prazo
commit: c6577dbb3253de42614764090553d740bc16181b
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-12
---
# Review de segurança: v046 (E20.4, revalidado na E20.22, PR-HOOK-PRAZO)

Diff revisado: `origin/develop...4ae51318` na E20.4; revalidação por delta `4ae51318..c6577dbb` (`forge-check parecer delta`: no domínio `bin/forge-check`, `hooks/_comum.py`, `hooks/parecer.py`; fora, changelog e testes, lidos). O `forge-check pr` grava o resultado por head em `<diretório comum do git>/forge/pr/<head>/` e o hook `parecer` passa a liberar o `gh pr create` lendo o aprovado do mesmo head, branch, base e escritor.

## Gatilhos
Controle do Forge (hook `parecer`, `R-REVIEW`) e estado lido por hook fora da árvore versionada.

## Achados
- A2 (recomendado) hooks/conformidade.py:951 · escrita com `$(git rev-parse --git-common-dir)/forge/pr/...` ou variável da linha (`d=.../.git; cp x $d/forge/...`) passa: o resto depois de `$(…)` é resolvido na raiz da cópia, não no diretório comum; já existia, e agora forja o aprovado que libera o PR

## Sondas
- S1 · hook conformidade, papel tech-lead, Bash `cat > "$(git rev-parse --git-common-dir)/forge/pr/a.json" < x` · espera: rc 2 (.git/forge/ protegido) · obtido: rc 0
- S2 · hook conformidade, papel tech-lead, Bash `d=/workspaces/Forge/.git; cp x $d/forge/pr/a.json` · espera: rc 2 · obtido: rc 0
- S3 · hook conformidade, papel tech-lead, Write em `<comum>/forge/pr/<head>/a.json` (caminho literal) · espera: rc 2 · obtido: rc 2 (R-CONFORMIDADE, marca de sessão)
- S4 · `resultado_gravado_do_pr` com registro aprovado sem `escritor`, com `escritor` de 64 zeros e com o sha256 do forge-check carregado · espera: ausente, ausente, aprovado · obtido: ausente, ausente, aprovado
- S5 · `podar_resultados` com irmãs SHA40 velha, link para pasta de fora, pasta com link para arquivo de fora, pasta não SHA40, ponta da develop e a gravada · espera: só a velha e a do link interno saem; alvos de fora intactos · obtido: igual
- S6 · `podar_resultados` com irmã SHA40 que contém subpasta · espera: para com aviso, nada apagado fora · obtido: "pr: aviso: resultados antigos não apagados (Is a directory)", pasta mantida

## Detalhe dos achados
**A1 (E20.4) resolvido no delta.** O registro grava `escritor`, o sha256 do próprio `forge-check` (bin/forge-check:1529-1532, gravado em :1562); a leitura descarta registro sem escritor ou com outro (bin/forge-check:1593-1594); o hook carrega o `forge-check` do PLUGIN (hooks/_comum.py:2420), então só o gravado pela cópia vigente libera. O de uma branch em obra ou de versão anterior vira `ausente`, que recusa (S4). Resíduo: o sha256 é público e um processo que escreve direto no `.git/forge/pr/` pode copiá-lo; esse caminho é o A2, não um achado novo.

**A2** (inalterado) · evidência hooks/conformidade.py:951 (`alvos_da_escrita` resolve o resto depois de `$(…)` na raiz da cópia) e hooks/conformidade.json (`.git/forge/` e `.git/`, quem: nenhum) · caminho de ataque: o agente grava o JSON aprovado (agora com o escritor copiado) com `$(git rev-parse --git-common-dir)/forge/pr/<head>/x.json` ou com uma variável definida na linha (S1, S2); o hook não reconhece o `.git/` e libera. A mesma forma alcança `.git/config` e `.git/hooks/`. Já existia antes desta branch; fora dela. Ganho: PR fora do rascunho sem os pareceres; o merge, o `gh pr ready` e o CI conferem sem cache e barram · severidade média para o hook de conformidade, baixa para esta entrega · correção mínima: com `$(…)` ou variável no caminho de escrita, somar como alvo o mesmo resto resolvido a partir do diretório comum do git (como `pastas_do_curinga` já faz) e conferir contra os protegidos `.git/forge/`, `.git/`, `.git/config`, `.git/hooks/`, `.git` · esforço P · dono tech-lead (cartão separado).

**Poda (bin/forge-check:1535-1549).** Só roda depois de gravar com sucesso (:1568-1571); sem a lista das pontas (`for-each-ref` falhou) não apaga nada; apaga só irmãs com nome SHA40 que não são a gravada nem ponta de `refs/heads` ou `refs/remotes`; pula link (`is_symlink`) e não segue link de arquivo (o `unlink` tira o link, não o alvo, S5); subpasta faz o `unlink` falhar e a poda parar com aviso (S6). Head de worktree destacada sem ref pode ter o resultado podado: vira `ausente`, falha fechada. Troca de pasta por link entre a conferência e o `iterdir` exige escrita no `.git/forge/pr/`, que já é o A2; informativo.

**Dica do prazo (hooks/parecer.py:563-564).** `contorno_do_prazo` só recebe "rode antes forge-check pr" quando o PR em criação não tem resultado gravado (`motivo` só vem de `resultado_gravado_do_pr`, com `gravado=True`); a saída do rascunho, o merge e o texto longo seguem com `CONTORNO_DO_TETO`. Só muda o texto da recusa; a recusa por prazo continua (hooks/_comum.py:2785).

**Changelog do rascunho.** Só documenta o que o código já faz nos projetos (sem dispensa do rascunho fora do clone do Forge, `pull_request` em hooks/parecer.py): endurece, não afrouxa.

Conferido contra docs/engineering/achados-recorrentes.md: AR-7 (escrita e leitura pelo mesmo `--git-common-dir`); AR-3 e AR-5 sem ocorrência no delta.

## Riscos aceitos e ferramentas
Sem risco aceito. Testes rodados no head c6577dbb: `python3 -m unittest tests.test_pr_hook_prazo` (17 testes, OK); o resto da suíte fica com o CI do PR. Sondas S1 a S3 da E20.4; S4 a S6 numa sonda local (`python3 -I`) contra o `bin/forge-check` do head, num repositório temporário. Ferramentas da skill fora do PATH (lacuna): gitleaks, semgrep, zizmor, actionlint, osv-scanner; nenhuma é necessária a este diff.
