---
tipo: revisao-seguranca
contrato: 1
pedido: impl-n-tpl-a
branch: melhoria/impl-n-tpl-a2
commit: 84c53e9afc27f5aa1ec76cdb8a7c3e884e9623c5
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-22
---
# Review de segurança: impl-n-tpl-a

Escopo: `git diff a3dbe22 84c53e9` na branch refeita `melhoria/impl-n-tpl-a2` (4 commits, 11 arquivos, +331 -1): o modelo de pedido, os dois passos a passos da proteção de branch, o modelo `templates/projeto/.github/dependabot.yml`, o bloco do ecossistema em `stacks/<stack>/pronto.md`, a skill `ci-cd`, os invariantes novos em `tests/config.json`, os testes novos e o fragmento do changelog. Nenhum workflow, hook, script de `bin/` nem a catraca mudam. Conferido contra o desenho (`docs/propostas/discovery-0.29.0/n-tpl.md`) e o modelo de ameaças (`docs/security/ameacas/n-tpl.md`, itens 2, 3 e 4, e o T-1).

Este parecer substitui o da branch antiga (`melhoria/impl-n-tpl-a`, commit 23099a4), que fica só de registro. Comparação direta: `git diff 23099a4 84c53e9` restrito aos arquivos da entrega mostra o texto dos modelos, dos passos a passos, da stack, da skill, de `tests/config.json` e de `tests/test_clareza.py` **idêntico**; a única mudança é a mudança de lugar dos testes da M9, de `tests/test_modelos_projeto.py` para o arquivo próprio `tests/test_dependabot_modelo.py`, sem nenhuma asserção perdida nem alterada, e o fragmento renomeado para `changelog.d/impl-n-tpl-a2.md`.

## Gatilhos
- Controles do Forge: `tests/config.json` (só acréscimo de invariantes: 1 na chave do modelo de pedido e 3 em cada passo a passo; nenhum removido nem afrouxado).
- CI/CD e dependência: o modelo de `dependabot.yml` e o bloco da stack. São arquivos de modelo, que o `forge-check` não detecta pelo diff (T-1); o lote leva parecer de qualquer forma, pelo gatilho de controle do Forge.

## Achados

## Detalhe dos achados
Não há achado bloqueante. O que o brief pediu conferir:

- **Passo a passo da F8** (`docs/protecao-de-branch.md`, `templates/projeto/docs/engineering/protecao-de-branch.md`): enforcement **Active** com o aviso do modo Evaluate (passo 2), lista de desvio vazia, sem administrador, dono nem bot (3), bloqueio de deleção e de force push (5, 6), PR obrigatório sem aprovação humana obrigatória (7, controle 2(g)), branch atualizada (8) e fonte do check fixada em GitHub Actions, com o motivo do status gravado por token (9). Os checks do Forge `bateria` e `catraca` (`docs/protecao-de-branch.md:23-24`) são os `name:` dos jobs dos dois workflows, que rodam em todo PR sem filtro de caminho. O modelo de projeto não cita catraca nem bateria e manda o `devops-engineer` listar os jobs. Conferência só de leitura (`gh api .../rules/branches/<b>`); os dois textos dizem que nenhum agente chama API de escrita nem recebe token. O aviso de custo do repositório privado no plano gratuito está em "Antes de começar", com subir de plano como decisão do dono (`R-CUSTO`). Controles 2(a) a 2(g) e 2(i) cobertos; AB-12 coberto por `tests/test_modelos_projeto.py`.
- **M9, sem rede, sem custo, sem afrouxar** (`templates/projeto/.github/dependabot.yml:14-32`): neutro, só a entrada das ações do CI, com comentário que manda copiar o bloco da stack (`:2-3`, controle 3(a)). `target-branch: develop`, `open-pull-requests-limit: 5`, `cooldown` de 7 dias, grupo de rotina só minor e patch e grupo `maiores` à parte. Não há auto-merge, `registries`, `insecure-external-code-execution`, `ignore` nem `@dependabot` (3(d), 3(e)); os comentários dizem que a configuração só vale na branch padrão e que o alerta de segurança abre contra ela (3(f)). O bloco da stack (`stacks/<stack>/pronto.md:52-79`) traz `cooldown` 1/1/7, grupos em minor e patch, `maiores` e `ignore: []`, sem credencial. O robô é recurso gratuito do GitHub; nada no lote chama rede nem serviço cobrado. A skill `ci-cd` (`skills/ci-cd/SKILL.md:57-60`) repete que o robô não tem isenção de parecer (`R-SEGURANCA`). AB-16 coberto por `tests/test_dependabot_modelo.py`.
- **Neutralidade e marcador** (3(a), 3(b); AB-14, AB-17): sonda numa cópia de 84c53e9 em `$TMPDIR` (`git archive`): `forge-init` num diretório novo criou `.github/dependabot.yml` e `docs/engineering/protecao-de-branch.md`, sem nenhum `{{` sobrando em arquivo criado. `NeutralidadeDoNucleo`, `tests.test_modelos_projeto`, `tests.test_dependabot_modelo` e `tests.test_clareza`: 21 testes OK. Nenhuma exceção nova em `neutralidade_nucleo`.
- **Nome neutro do pedido** (`templates/projeto/docs/pedidos/_modelo.md:5`): forma do ID (minúsculas, dígitos, hífen), sem segredo nem dado de pessoa em qualquer projeto, sem nome de stack nem de projeto só no Forge (`R-NEUTRO`), e a correção de um vermelho de neutralidade é renomear, nunca exceção nem pasta ignorada (controles 4(a) a 4(c); AB-18). Invariante novo em `tests/config.json`; os de antes continuam.
- **Commits que se revertem sozinhos** (P3 = B, o achado do review da branch antiga): num clone em `$TMPDIR`, `git revert --no-commit` de cada um dos 4 commits sobre 84c53e9 aplicou sem conflito.
- **T-1** (continua): o padrão de pipeline do `forge-check` (`bin/forge-check:128`) não pega `templates/projeto/.github/`. Neste lote não há fuga, porque `tests/config.json` dispara o gatilho de controle do Forge; o cartão GATILHO-MODELO continua valendo.

Recomendações (não bloqueiam; as mesmas do parecer da branch antiga, porque o texto é idêntico):
- **R1. Desvio do `main-do-dono` em repositório pessoal.** Baixa. `docs/protecao-de-branch.md:33` e `templates/projeto/docs/engineering/protecao-de-branch.md:30` mandam pôr "só o dono" no desvio; em conta pessoal a lista de desvio tende a aceitar o papel de administrador, não um usuário. Se o bot tiver esse papel, também passa pelo "Restrict updates" (com os checks do `portoes` ainda exigidos). Correção mínima: uma frase "o bot tem papel de escrita, nunca de administrador". Esforço P. Dono: tech-lead.
- **R2. A conferência não confere a fonte do check nem a regra `update` da `main`.** Baixa. `docs/protecao-de-branch.md:41` e `templates/projeto/docs/engineering/protecao-de-branch.md:38`: citar que cada check de `required_status_checks` vem com `integration_id` preenchido e que a `main` mostra a regra `update`. Esforço P. Dono: tech-lead.
- **R3. Testes do texto frouxos em dois pontos.** Informativa. `tests/test_modelos_projeto.py:43` junta `name:` de passos e de jobs; `:53` não barra uma linha "Bypass list: Repository admin". Esforço P. Dono: tech-lead ou qa-engineer.
- **R4. `--forcar` sobrescreve o `dependabot.yml` do projeto** (3(g), AB-15). `bin/forge-init:74-78` sobrescreve sem aviso. Exige ação explícita e se desfaz pelo git; proposta de cartão. Esforço P. Dono: tech-lead.

## Riscos aceitos e ferramentas
- Riscos aceitos: nenhum novo. Ficam os do desenho: o YAML só é validado de fato na primeira execução do robô num projeto, e o `zizmor` do CI não varre o modelo (fora de `.github/workflows`).
- Ferramentas usadas, só locais: `git diff`, `git archive` e clone local em `$TMPDIR`, `forge-init` da cópia, `git revert --no-commit` por commit, os padrões de gatilho do `forge-check` lidos da cópia e os testes focados.
- Lacuna: `gitleaks`, `osv-scanner`, `semgrep`, `zizmor`, `actionlint`, `trivy` e `shellcheck` fora do PATH; nada instalado. Busca de padrões de segredo no diff por `grep`: nada. Sem rede: o comportamento do GitHub vem da documentação pública; a prova é a conferência do dono.
