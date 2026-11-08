---
tipo: revisao-seguranca
contrato: 1
pedido: versao-043
branch: melhoria/uniao-043
commit: c14db03f9b41c1b4b9952a0a289bbf6de333e4cf
parecer: aprovado
data: 2026-11-08
revisor: forge:security-engineer
---

# Segurança do delta da junção da 0.43 (melhoria/uniao-043)

Brief `versao-043-security-engineer-12` (sha256 9b4e1db5…ac82). Base: `origin/develop` em f84153b3934f1c7b1af8db29024bcb81bd022409. Head: c14db03f9b41c1b4b9952a0a289bbf6de333e4cf, igual a `origin/melhoria/uniao-043` depois do `git fetch origin` e à "entrega conferida" de 13:32 no Histórico. Referências: `docs/security/ameacas/versao-043.md`, `docs/security/ameacas/versao-075.md` e os pareceres por branch (`docs/security-v043/g1.md`, `g1-r2.md`, `g3.md`; `docs/security-v075/g1.md`, `g2.md`, `g2-r2.md`, `g3.md`).

## Gatilhos
O delta toca caminhos protegidos: `.githooks/pre-push` (E4-1 MAQ-A7, PP-1, PP-4a), `hooks/agentes.py` (B9 hash-brief, AG-1a) e `bin/forge-check` (E3, B-n do estudo). Não toca `.github/`, `hooks/hooks.json`, `hooks/quadro.py`, `hooks/conformidade.py`, `docs/regras/` nem `tests/config.json`.

## O que li e rodei (só local e passivo)
- O primeiro pai tem 21 commits: 20 merges e o commit 3d4787f (A1 do review g1). Os segundos pais são exatamente os shas das listas `versao-043-lista-2.txt` a `-6.txt`.
- Rodei `git show --remerge-diff` em cada merge. Só 5 têm resolução: bc37d49 (`bin/forge-check`, `tests/test_voltas.py`), d1b456e (`bin/forge-check`, o `import statistics`), 8b5100b (`bin/forge-check`, `erro_dos_atributos` e `cmd_movimento`), b507c48 (`tests/test_forge_mutante.py`) e d3f0c58 (`tests/test_pre_push_trava.py`). Todas mantêm os dois lados e só tiram marcadores (`<<<<<<<`, `=======`, `>>>>>>>`) ou acertam linhas em branco. Nenhuma linha de controle sai. Os outros 15 merges são a fusão automática pura (remerge-diff vazio).
- O Histórico (01:25) cita conflito também em `.githooks/pre-push`, `bin/forge-testes`, `tests/test_sobreposicao_quadro.py` e `tests/test_testes_tocados.py`. Nos commits, esses 4 arquivos não têm resolução nenhuma: o resultado é a fusão automática. É uma divergência de registro, não de árvore. Nenhum hook foi tocado por resolução manual.
- Fiz a cobertura por linha (script no scratchpad). Para cada uma das 20 pontas, toda linha que a branch acrescentou sobre o merge-base está no head, com a contagem. Nenhuma linha que ela tirou voltou, salvo `saida = []` e `return 0`, que outras partes acrescentam em funções novas. Comparei também função por função de `bin/forge-check`. As únicas funções mudadas por uma branch e diferentes no head são `main` e `executar` (o despacho dos subcomandos novos de várias partes) e `custo_do_movimento`. Esta última é a união exata da E3-1c (`chave_do_cartao`) e da E3-2a (`partition(MARCA_DE_ATRIBUTOS)`, um `--titulo` não fabrica custo).
- Árvore do head extraída por `git archive` no scratchpad. `bash -n` e `shellcheck` dão 0 avisos em `.githooks/pre-push` e `bin/forge-fechar`, igual à develop. Parse sem definição duplicada no nível do módulo em `bin/forge-check`, `forge-testes`, `forge-mutante`, `forge-changelog`, `forge-doutor`, `hooks/agentes.py` e `scripts/promover-homolog.py`. `python3 -I bin/forge-check --help` carrega o módulo. Busca de marcador de conflito: só os arquivos que já os têm na develop (forge-salvar, forge-desfazer e os testes deles; sem mudança no delta). Busca de padrão de segredo no diff: 0.
- Não rodei módulo de teste. A fila estava ocupada (`.githooks/pre-push --status` rc 0, suíte no pid 1623749 desde 14:37:21; load1 8,0). O envio da junção rodou os afetados com rc 0 (Histórico, 14:35). Para provar o C-7 e o C-8 depois da mudança de lugar das constantes, fiz uma sonda em processo (sem módulo de teste), em `## Sondas`.

## Resposta ao Objetivo
1. **Nenhuma resolução tirou nem enfraqueceu controle.**
   - E3. As constantes do C-4, C-7 e C-8 ficaram com uma definição só (`bin/forge-check:2948-2952`: `MARCA_DE_ATRIBUTOS`, `LEITOR_DA_MARCA`, `PEDIDO_DO_ATRIBUTO`, `RECUSA_DA_MARCA`, `TETOS_DO_MOVIMENTO`). Isso fecha o A2 do g1 e o A1 do review g1. `RECUSA_DA_MARCA` e `TETOS_DO_MOVIMENTO` só mudaram de lugar, com o mesmo texto. O C-1 a C-6, o C-10 (no `--gerar`) e o C-15 estão nas linhas das pontas aprovadas (cobertura por linha 0 faltas).
   - Estudo. O G-3 da AG-1a está de pé em `hooks/agentes.py`: a reserva é calculada depois do teto (`:358`, `:361`), e o erro grava lista vazia. O corte do A1 bloqueante do g2 (`MAIOR_TOKEN`, `:286`) está como no 3ee3672 aprovado no g2-r2. A recusa de vários cabeçalhos da B9 (`:211`, `:227`) convive com ela sem interação: o cálculo de branches pula o conferente.
   - O C-1 da PP-4a (`.githooks/pre-push:436-437`) e o `gravar_duracao` da PP-1 (`:404`) estão no hook integrado, sem mudança. A falha fechada do pre-push segue: a trava que não abre sai com 1 (`:291`), a espera esgotada barra (`:311`, `:319`) e o teste vermelho sai com 1 (`:421`).
   - O C-6 e o C-9 da B19a e o C-1 e o C-2 da conferir-ref (b8068da, no head pela fechar-relogio) também estão lá.
2. **Caminhos protegidos e hooks com falha fechada.** As resoluções não tocaram hook. `.githooks/pre-push` e `hooks/agentes.py` são a fusão automática de mudanças em regiões separadas:
   - no pre-push, `FORGE_ENTRADA` (E4-1), as linhas de relógio (PP-1) e a árvore enviada (PP-4a);
   - no agentes.py, a B9 em `mensagem_sem_forma` e a AG-1a em `lancar`.
   O `FORGE_ENTRADA` passa por `fullmatch` de `[a-z-]{1,20}` (`bin/forge-testes:261`, `:289`; `bin/forge-mutante:583`, `:611`), o cuidado do modelo de ameaças da E4. A variável não muda o que roda nem recusa. `hooks/hooks.json` e `hooks/quadro.py` estão iguais aos da develop.
3. **Condições de junção.**
   - A3 do g1 e do g1-r2: cumprida. A E3-2b (57eef1c) não é ancestral do head e nenhum commit da E3-3 entra, então o hook `quadro` e o R-WIP por coluna ficam. Isso segue as decisões do dono de 2026-11-08 02:29 e 07:44.
   - Os A1 e A5 do g3 (C-15 com cartão de ponte) continuam como condição da E3-3, fora desta junção.
   - O bloqueante A1 do g2 (AG-1a) fechou no g2-r2, e o sha mesclado é o aprovado (3ee3672).
   - Os outros shas mesclados batem com os pareceres por branch, ou são parte sem gatilho pelo modelo de ameaças. A B9 entrou em b1c5762, que só difere do 888c483 aprovado em `docs/hooks.md`. Sem gatilho: E2-1, E4-1, PY-1, FF-2, B1, B12, B15, UN-1, entre outras.

## Achados

## Sondas
- S1 · `erro_dos_atributos('ok · Atributos : responsavel=x', {})` na árvore do head · espera: recusa do C-7 · obtido: "o --motivo não leva `atributos:`; use --titulo, --pedido e --responsavel"
- S2 · `erro_dos_atributos('x'*501, {})` · espera: recusa do C-8 · obtido: "--motivo acima de 500 caracteres"
- S3 · `erro_dos_atributos('ok', {'pedido': 'a/b'})` e `{'pedido': 'versao-043'}` · espera: recusa e None · obtido: recusa "--pedido fora da forma" e None

## Riscos aceitos e ferramentas
Nenhum risco aceito novo. Os recomendados dos pareceres por branch continuam como estavam, porque a junção não tocou nessas linhas e eles não são condição desta junção:
- A4 e A5 do g1 (controle C1 nos atributos; `mkdir` de `.forge/run` seguindo link, hoje em `bin/forge-check:3038`);
- A1 e A2 do g2-r2;
- A1 do g3 (v075), que fica para a B20b.

Ferramentas: `shellcheck` usado. `gitleaks`, `semgrep`, `osv-scanner`, `zizmor`, `actionlint` e `bandit` não estão no PATH (lacuna; nada instalado, R-CUSTO). O delta não traz dependência nova nem workflow.

## uniao-043

sha revisado: c14db03f9b41c1b4b9952a0a289bbf6de333e4cf · delta origin/develop (f84153b3)..c14db03f, primeiro pai: 20 merges e o 3d4787f
veredito: aprovado
Sem bloqueante. As cinco resoluções são aditivas, o commit A1 só deduplica as constantes e move duas, os hooks vêm da fusão automática e a condição A3 está cumprida.
