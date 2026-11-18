---
tipo: review
contrato: 1
pedido: v0477
branch: melhoria/v0477-textos-processo
commit: 447a4c8da0973a8fd04121d8a32032948e0a8570
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-18
---
# Review: v0477 (E2.2, branch melhoria/v0477-textos-processo)

Primeira rodada, head 447a4c8d sobre a base 038249c5. Diff: 4 arquivos, 6 inserções e 3 remoções, só texto `.md` e fragmento de changelog (0 linhas de código no teto H1). Classe C (`forge-check classe`: agente e skill; gatilho de segurança por `docs/regras/R-LIMITES.md`).

## Achados
- A1 (recomendado) docs/regras/R-LIMITES.md:44 · tirar "também" está fora do escopo E2 (H8, G6) e não aparece no commit nem no fragmento; cite no corpo do PR: regra com ID, mudança neutra, só para o núcleo caber no teto (develop vermelha por 1)

## Sondas

## Parecer
**Aprovado.**

- **H8** (`agents/tech-lead.md:21`): a seção "Caminho curto para o pequeno (H8)" já está na develop em `skills/engineering-practices/tamanho-por-item.md:20` (#644); o item põe o ponteiro no papel. O comando de contagem saiu da linha do agente e continua no arquivo apontado (`tamanho-por-item.md:10`); `test_teto_do_h1_no_tech_lead_e_na_skill` aceita as duas formas.
- **SIEG-G6** (`skills/trabalho-em-paralelo/ritmo-e-corte.md:16`, ponteiro em `agents/tech-lead.md:39`): uma linha, sem conflito com o lote por arquivo nem com a junção da diretriz 26; cita `R-FLUXO` pelo ID.
- **R-LIMITES.md:44, regra com ID (pergunta do brief): neutra.** A frase anterior já proíbe, sem condição, tudo o que custe dinheiro sem autorização expressa do dono; a segunda só nomeia um caso. Com ou sem "também", ela não restringe o alcance (não lê como "só vale para melhoria vinda de projeto", porque a primeira é universal) nem o amplia. As invariantes de `tests/config.json` para R-LIMITES ("sem autorização expressa do usuário", "Nada no Forge (CI, testes, scripts, fluxo) consome API paga") seguem presentes. Não pede `afrouxa-regra`. Atende a G6 deste mesmo item: a branch fica verde sozinha mesmo com a develop vermelha; se `melhoria/v0476-nucleo-teto` entrar antes, a palavra pode voltar em item próprio, sem pressa.
- Medida conferida, sem rerrodar a suíte (roda no CI do PR): `tests.test_jarvis_nucleo` no head 43 OK; na `origin/develop` (038249c5) falha `test_jarvis_e_regras_cabem_na_metade_da_base` com "37512 not less than or equal to 37511" (o 1 caractere do brief). `tests.test_metricas_texto` OK; `python3 -I tests/catraca.py --base origin/develop` rc=0 (sem guarda no diff, nenhum mutante devido).
- Commit único, Conventional Commits em português, mensagem clara; fragmento `changelog.d/v0477-textos-processo.md` em português (decisão do dono de 18/11).
