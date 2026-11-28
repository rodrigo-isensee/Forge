---
tipo: revisao-seguranca
contrato: 1
pedido: v0474
branch: melhoria/v0474-h2-texto
commit: 5a590bf3e8465df0b7a283fefe871ef504b50ad4
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-17
---
# Review de segurança: v0474-h2-texto

Gatilhos: tests/config.json (invariantes novas), texto do Jarvis e do tech-lead (H2, autor até o merge), trecho movido da skill briefs-e-conferencia para arquivo auxiliar.

## Achados
- A1 (recomendado) skills/briefs-e-conferencia/autor-ate-o-merge.md:7 · a retomada por SendMessage não reserva a branch no hook agentes (hooks/agentes.py:991, só recusa id com lápide); dizer que a retomada do autor também é uma delegação de escrita (Z10, R-TETO): só depois do SubagentStop dele e sem outra escrita aberta na branch.

## Sondas

## Detalhe
- Base ba968580, head 5a590bf3; 6 arquivos, só texto, JSON e fragmento de changelog; nada em `hooks/`, `bin/`, `.github/`, `.githooks/` nem permissão (`git diff --stat ba968580 HEAD -- hooks bin .githooks .github` vazio).
- Invariantes: comparação por script entre base e head de `invariantes`, `invariantes_motivo` e `invariantes_motivo_trecho`. Nenhum arquivo, trecho ou motivo saiu nem mudou; 509 trechos na base, 522 no head (13 novos, todos com `regra` e `porque`). O trecho que saiu de `skills/briefs-e-conferencia/SKILL.md:24` (o comando `forge-check brief gerar --volta ... --parecer` e "Recomendação não entra") não era invariante próprio; agora está em `autor-ate-o-merge.md:9` e ganhou invariante no arquivo novo. O invariante `forge-check brief gerar` da SKILL segue casando na linha 11.
- R-TETO (Z10, uma delegação de escrita por branch): `skills/briefs-e-conferencia/SKILL.md:14` intacta, e o hook não muda nesta branch. O aviso descrito em `autor-ate-o-merge.md:13` só aparece quando o autor não está ativo (linha 14), isto é, quando o Z10 já libera a branch; não abre segunda escrita simultânea, e "O disparo segue" vale só para o aviso, não para a recusa do Z10. A1 é a lacuna anterior que o H2 torna o caminho principal: resposta pré-existente do hook, sem ataque externo (o risco é dois agentes do próprio time escreverem a mesma branch), por isso recomendado. Dono: tech-lead (texto nesta branch ou na parte de ferramenta). Esforço P.
- R-REVIEW (portões no mesmo head): "no mesmo head" e "numa passada, em paralelo" seguem em `agents/jarvis.md:29-30`; `autor-ate-o-merge.md:9` exige os três portões no mesmo head num brief único e manda o que chega depois para a volta seguinte, o que não junta pareceres de heads diferentes. Quem deu o parecer continua revalidando por `forge-check parecer delta` (linha 10). Aperta, não afrouxa.
- Decisão: H2 está no recibo da 0.47.4 (DECISÃO DO DONO 2026-11-17 10:16 no pedido v0474).
- Prova: `python3 -m unittest tests.test_forge.RegrasInviolaveis tests.test_forge.Neutralidade tests.test_forge.NeutralidadeDoNucleo tests.test_forge.RegrasComId tests.test_forge.Orcamento tests.test_jarvis_nucleo` verde no head 5a590bf3 (57 testes). A suíte inteira roda no CI do PR de integração; a branch ainda não tem PR nem CI.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Sem credencial no diff; a ferramenta de varredura de segredos não está no PATH, lacuna registrada.
