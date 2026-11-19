---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0478-guardas-parecer
commit: 83a8ce1713df9e363bbd80f93a61ae8e87288579
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-19
---
# Review de segurança: v0478 (guardas do hook `parecer`, E3.46, "Só aperta?")

Volta por delta. A rodada anterior é a `f7354120` (E3.38, head `993b6bb3`), com a comparação inteira contra o hook da develop; ela fica no git e não é recopiada aqui.

Gatilhos: hook de controle (`hooks/parecer.py`, `hooks/_gh_api.py`) que guarda o portão de parecer de todos os projetos e do Forge.

## Delta lido
`forge-check parecer delta docs/security/v0478-guardas-parecer.md` (`993b6bb3..83a8ce17`, sem o que veio da develop):
- `hooks/` e `.githooks/`: sem mudança no intervalo (`git diff --stat 993b6bb3 83a8ce17 -- hooks/` vazio). O hook revisado na E3.38 é o mesmo deste head.
- `bin/forge-testes`: só listas de módulos de teste (`FORGE_CHECK`, `REAPROVEITAM_O_LOTE`, `MAPA`) e o `teste_do_indice`, que só acrescenta módulo ao plano dirigido. Contra a develop (`eca1d21b`), a branch muda 4 linhas, todas de lista. Não decide portão.
- `tests/test_hooks.py`: o `Fixture` ganha `config` e `config_bruta` (só monta o repositório de teste) e o critério de carga do `test_prazo_do_merge` (veio da develop). Não toca o hook.
- `docs/hooks.md:39` (D2): texto que registra a recusa do shell por expansão com a ação crítica no `-c`.
- Fora do domínio, lido por ser a razão do delta: `tests/fixtures/heredoc-volta-unica.json`, CN2 (`$(printf bash) -c '…'`) e VA2 (`"$BASH" -c '…'`) passam de `parecer: 0` para `parecer: 2`; `conformidade` e as outras fixtures não mudam (`git diff 650be460 83a8ce17`: 3 arquivos, 4 inserções, 3 remoções).

## Só aperta?
**Sim, reconfirmado neste head.** Nada além das três consultas de só leitura do `gh api` (afrouxamento 2, sondas 5 da E3.38) passou a ser aceito em relação à develop. Motivo: o hook não mudou desde `993b6bb3`, onde a comparação inteira deu zero entradas novas aceitas fora dessas três; e as duas únicas expectativas mudadas no delta vão de 0 para 2, ou seja, o corpus agora exige recusa onde antes aceitava. A correção é a certa: o bash roda o corpo do `-c`, então `gh pr merge` sem parecer por esse caminho deve recusar (D2, falha fechada). Nenhuma expectativa vai de 2 para 0.

## Achados
- A11 (recomendado) docs/hooks.md:41 · Limites declarados da D4 seguem abertos (nome por expansão na aritmética e valor avaliado como expressão), aceitos pelo critério da D7; o dono confirma pelo Jarvis. Sem mudança desde o parecer `460a8a00`.

## Estado dos achados anteriores
- A13, A12, A1 a A10: fechados; o delta não os toca.
- A11: aberto como recomendado, sem delta.

## Riscos aceitos e ferramentas
Nenhum risco aceito neste parecer. Nenhuma sonda nova: o delta não muda o hook. A suíte inteira roda no CI; o brief não cita CI deste head e o gh não está autenticado neste sandbox, então o verde do corpus com CN2 e VA2 em 2 fica com o CI do PR. Lacuna: `gitleaks` e `semgrep` não estão no PATH. O delta não traz segredo nem dependência.
