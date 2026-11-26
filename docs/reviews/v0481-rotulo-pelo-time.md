---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-rotulo-pelo-time
commit: ab5871d1dedead9ff0021f4063b629794f6f9f00
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-26
---
# Review: v0481 (E24.2, #918, 1.ª rodada completa: FORGE-ROTULO-PELO-TIME, 1.º PR)

Diff lido: `3c833f3f..ab5871d1` (merge-base com a `develop` = Base-sha), 10 arquivos, +266/-21. Código: `bin/forge_autorizacao.py` (+40 linhas de código líquidas, dentro do H1, um comportamento). Clone de revisão: `/root/.forge-contrib/wt/v0481-rotulo-pelo-time-rev`, no head `ab5871d1`.

## CI e ferramentas (citadas, não refeitas)
- ci: ab5871d1dedead9ff0021f4063b629794f6f9f00 verde
- `gh pr checks 918` no head `ab5871d1`: suíte 3.12 e 3.14 (5/5 cada), `bateria (passos)`, `bateria (python 3.14)`, `bateria (verificações longas)`, `instalação`, `teto de pulados`, `árvore já provada na develop` e `catraca` verdes. Vermelhos que não contam: `bateria (pareceres)` (log: "R-REVIEW: PR toca bin/forge_autorizacao.py ... sem parecer aprovado de review") e `bateria` (log: "pareceres: failure", o agregado do anterior); os dois esperam este parecer.
- Testes do diff: `python3 -m unittest tests.test_autorizacao tests.test_autorizacao_gravar` · 63 testes, OK.
- `bin/forge-mutante --processos 1` nas duas specs novas: M1 a M10 morreram (M10 morre por erro: com o `isinstance` trocado, o manifesto `[]` levanta `AttributeError`, que é o defeito que a guarda evita).
- Specs antigas editadas (`v0481-autorizacoes-fixas*.json`, trecho `de` ajustado ao `SEM_PRAZO`): `--ids M3,M8,M9,M19,M21` morreram.
- `--cobertura --base 3c833f3f`: toda guarda mudada coberta (242, 243, 245, 283, 284, 369, 473, 483; 123 e 151 pelos M1/M2); `--conferir --base 3c833f3f`: trechos no lugar.

## Leitura (checklist da skill, só o que o diff alcança)
1. Escopo: ato `rotulo-pelo-time` sem prazo, termo `homologacao`, alvo `fixo` e validade `fixa`; `inativa` fora do Forge (`.forge/versao` ou `origin` diferente do `repository` do plugin que lê); `ler --ato rotulo-pelo-time` dá rc 0/1; nenhum hook nem a catraca consome o ato (conferido: `SO_NO_FORGE` só é lido em `estado`, `SEM_PRAZO` só em `limite`, `problemas`, `leitura` e `executar`). Bate com o brief e com E24 do pedido; R3 (lista da `main`) fica para o 2.º PR, como a emenda diz.
2. ADR: Emenda ROTULO-PELO-TIME na ADR 0018 traz contexto com a ordem do dono, "Afrouxa?", "Por que o existente não basta", critério de reversão e tabela de leituras com medida (R-DECISAO). O que afrouxa e a solidez do limite são da segurança (E24.4), citada, não refeita.
3. Legibilidade: `SEM_PRAZO` reúne `FIXOS` e `SO_NO_FORGE` e troca as quatro leituras antigas sem mudar o comportamento dos fixos (teste `os outros fixos não mudam`). `fora_do_forge` lê o manifesto ao lado do módulo, não o da raiz (falha fechada: manifesto ausente, inválido, não objeto ou sem `repository` dá `inativa`).
4. Testes: `RotuloPeloTime` cobre ativo com o `origin` do Forge (maiúsculas e `.git`), outro `origin`, projeto com o `origin` do Forge, manifesto sem repositório e o `ler --ato`; o gravar cobre a frase que nasce ativa e as duas palavras juntas pendentes. O auxiliar `no_repositorio` limpa `GIT_*`, `FORGE_*` e `PYTHON*` e põe teto do git.
5. Commits: três commits `feat`/`fix`/`test` em português, com o pedido e a etapa; fragmento `changelog.d/v0481-rotulo-pelo-time.md` presente.

## Achados
- A1 (recomendado) bin/forge_autorizacao.py:232 · `slug` corta até o último `github.com[/:]` de qualquer host: `https://notgithub.com/rodrigo-isensee/Forge.git` e `https://x.invalid/github.com/...` dão o slug do Forge (sonda executada). Ancorar o host no início da URL e testar um host parecido.
- A2 (recomendado) bin/forge_autorizacao.py:469 · `cmd_corte` agora serve a todo ato sem prazo (`ato="corte-diario"` por omissão); o nome engana quem lê o `executar`. Renomear para `cmd_ler_sem_prazo` num item de faxina.

## Parecer
Aprovado no head `ab5871d1`. O diff faz o que o 1.º PR do E24 pede, nem mais: o ato novo nasce, só fica ativo no repositório do Forge e ninguém o consome ainda. A1 não bloqueia: além do `.forge/versao` que todo projeto tem, o `origin` é configuração local de quem já controla o clone, então o limite é de configuração, não de fronteira; o host parecido só tira o custo de quebrar o envio do projeto. Fica como cartão depois do merge, salvo se a segurança (E24.4) o julgar com gatilho. A2 é nome. Integração: o #917 (E25.1) também mexe em `bin/forge_autorizacao.py`; quem entrar depois resolve na hora do merge e, se o patch mudar, o `forge-check pr` aponta a revalidação.
