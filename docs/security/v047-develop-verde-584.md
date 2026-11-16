---
tipo: revisao-seguranca
contrato: 1
pedido: v047-develop-verde-584
branch: melhoria/v047-develop-verde-584
commit: 6105741af55f9eedc2c5873c34d10cd4d48948c9
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-16
---
# Review de segurança: v047-develop-verde-584

Parecer completo (primeira rodada) do diff `befbb464..6105741a` (E2.433): `agents/jarvis.md` (aspas na `description` do frontmatter e corte de 3 caracteres no corpo) e o fragmento `changelog.d/v047-develop-verde-584.md`.

## Gatilhos
Gatilhos: nenhum

## Achados
- A1 (recomendado) skills/ci-cd/SKILL.md:1 · fora do diff: tests.test_metricas_texto segue vermelho no head por estouro desta skill (caracteres 7579 > 6781, frase_media_x10 184 > 172, linhas_longas 29 > 27), vindo do #576; o conserto do jarvis.md sozinho não deixa a develop verde nesse teste.

## Sondas

## Detalhe dos achados
Leitura do diff: a `description` só ganhou aspas duplas; o valor lido é o mesmo texto (conferido com leitura do valor entre aspas: sem aspas nem barra invertida internas, 250 caracteres). `tools:` e `model:` não mudaram, então nenhuma permissão do agente principal cresceu. As duas trocas no corpo ("primeira pessoa, em português"; "regras 9-11") não mudam regra, portão nem ID citado. Nenhum caminho de `PROTEGIDOS` de `tests/catraca.py`, nenhum arquivo de `hooks/`, `docs/regras/`, `tests/config.json` nem `.github/` foi tocado.

A1: `python3 -m unittest tests.test_metricas_texto tests.test_jarvis_nucleo` no head 6105741a: 25 testes, 1 falha, só em `skills/ci-cd/SKILL.md`; `agents/jarvis.md` não aparece entre os estouros. O arquivo da skill não muda nesta branch (último commit dele: 22f1eaa8, #576). Sem caminho de ataque: severidade informativa. Correção mínima: reduzir o texto da skill até o teto em `tests/fixtures/metricas-texto.json` (subir o teto é afrouxar), num item próprio. Esforço P. Dono: `devops-engineer` (dono da skill de CI).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Revisão estática por leitura do diff e testes do item; sem varredura de segredos ou de dependências, porque o diff é só texto de agente e changelog. A suíte inteira roda no CI do PR.
