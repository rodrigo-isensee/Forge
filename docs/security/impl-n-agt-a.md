---
tipo: revisao-seguranca
contrato: 1
pedido: impl-n-agt-a
branch: melhoria/impl-n-agt-a
commit: 5d13ce61a746311ec6e50e2fe64410b6e8435bb2
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-22
---
# Review de segurança: impl-n-agt-a

Escopo: `git diff 38c58247fdae5482ed441db4dd21bff4d55471d7 5d13ce61a746311ec6e50e2fe64410b6e8435bb2` (AGT-1 e AGT-2), contra as §3.1, §3.2 e §4 do modelo `docs/security/ameacas/n-agt.md` (em `~/.forge-contrib`).

## Gatilhos
Controles do Forge (hook `agentes`, guardas `R-TETO` e `R-BRIEF`) e estado local dos hooks (`<comum>/forge/run/`). Sem segredo, rede, dependência nova nem workflow.

## Achados

## Detalhe dos achados
Nenhum bloqueante. Conferência dos controles do modelo:

- **C1 (AGT-1, A1/A2).** `hooks/agentes.py:190-201` fixa `hook._run` em `<comum>/forge/run/` antes do `mkdir(mode=0o700)` (`:197`) e grava `.gitignore` com `*`; a docstring (`:10-12`) e `docs/hooks.md` dizem que no Forge a pasta não tem guarda de escrita e que `hooks_desligados` não vale no clone (`hooks/_comum.py:737-748`, ramo `clone_do_forge` volta antes de ler `hooks_desligados`). A2 e A7 ficam como risco residual registrado pelo autor, como o modelo prevê; nada piora frente à base, onde o hook nem rodava no clone.
- **C3.** O `erros.log` do clone vai para a mesma pasta (o `_run` fixado é usado por `registrar_erro`, `hooks/_comum.py:838`); coberto por `test_erro_interno_no_clone_deixa_linha_no_erros_log`.
- **A15.** `executar("agentes", principal)` segue sem `critico` (`hooks/agentes.py:353`), então `FORGE_GUARDA_ABERTA=1` não chega ao teto; `test_guarda_aberta_nao_abre_o_teto` dá código 2 `R-TETO`.
- **C4 (A4/A5).** `ler_brief` (`hooks/agentes.py:232-246`): `realpath` com o arquivo estritamente sob `docs/briefs/` da raiz da sessão ou de `~/.forge-contrib`; `lstat` exige arquivo regular; abre com `O_NONBLOCK|O_NOFOLLOW` e confere de novo por `fstat` (uma troca por FIFO entre o `lstat` e o `open` não bloqueia: a abertura não bloqueante volta na hora e o `fstat` recusa); lê no máximo 256 KiB + 1. Qualquer erro bloqueia só aquela mensagem. O hook só compara o hash e não ecoa conteúdo.
- **C5 (T8).** Cabeçalho = linhas antes da primeira `<<<BRIEF` (`:253-256`); exatamente uma `Arquivo:` e uma `Brief-sha256:`; o corpo e os blocos seguintes não contam. Separadores de linha exóticos só podem fazer o hook ver linhas a mais no cabeçalho, o que bloqueia (falha para o lado fechado).
- **`forge-check fila`.** `agentes_vigentes` usa `agentes.arquivo_de_estado(raiz)`; `diretorio_comum` exige o `.git` no topo e `e_clone_do_forge` o manifesto na raiz, e o `fila` já exige `KANBAN.md` na raiz. Fora do topo o arquivo não se acha e a conta dá 0: é só leitura informativa; quem barra é o hook.
- **Testes.** Rodei em cópia própria os três módulos da entrega: 46 OK no HEAD; com `hooks/agentes.py` e `bin/forge-check` da base, 27 dos 30 novos falham (vermelho antes do verde), incluindo T1, T10, T15, CA-3 e o de A15.

Recomendações (não bloqueiam; dono `tech-lead`, esforço P):
- R1 (baixa). `mkdir(mode=0o700, exist_ok=True)` (`hooks/agentes.py:197`) não corrige uma `run/` que já exista com permissão mais aberta, e `<comum>/forge/` nasce com a umask. Um `chmod 0o700` depois do `mkdir` fecha isso. Caminho de ataque fraco: só outro usuário local leria a contagem de agentes.
- R2 (baixa, classe A2). No clone, `hook.config()` ainda lê `<raiz>/.forge/config.json` (`hooks/_comum.py:757`). Numa worktree do Forge onde `.forge/` é pasta (é o caso desta worktree), quem escreve sem guarda pode subir `teto_agentes`; e um `.forge/versao` tornaria a worktree projeto, onde `hooks_desligados` volta a valer. É o mesmo risco residual de escrita sem guarda nas sessões do Forge (A2), já registrado; vale ler a config só do modelo no clone, ou levar ao C2.
- R3. O C2 (o `vigia` acusar escrita direta no `agentes.json`) não entrou; o modelo o marcou como recomendado e fora do lote se não coubesse. Fica para o lote b, com o CA-2.

## Riscos aceitos e ferramentas
Nenhum risco aceito novo. Risco residual já registrado no modelo e na docstring: A2/A7 (estado do clone sem guarda de escrita nas sessões do Forge), dependente do C2 e do C6.
Ferramentas: leitura do diff e do código, sondas e suíte em cópia própria em `$TMPDIR`. Ausentes no PATH (lacuna, não instaladas): gitleaks, semgrep, osv-scanner, zizmor, actionlint, trivy. A entrega não traz dependência, workflow nem imagem, então só o gitleaks faria diferença; o diff foi lido por inteiro e não traz credencial.
