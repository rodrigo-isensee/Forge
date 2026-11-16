---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-parecer-seguranca-curto
commit: 02fe845d9896048bc0a4b504ac9bac0b3a9c7018
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-16
---
# Review de segurança: v047 (parecer de segurança curto, E2.276; portão E2.279)

Escopo: parecer completo (não havia parecer anterior) do diff `5e74c70e..02fe845d`, lido inteiro: `agents/security-engineer.md`, `docs/security/_modelo.md`, `templates/projeto/docs/security/_modelo.md`, `tests/test_achado_teto_doc.py` e o fragmento `changelog.d/v047-parecer-seguranca-curto.md`. A pergunta: encurtar o parecer (mitigação pelo ID, gatilhos em uma linha, volta sem recópia) tira evidência do portão de segurança? Não: a mitigação citada pelo ID continua com `arquivo:linha` e teste, a volta registra o delta lido e o estado de cada achado anterior, e a releitura do que o delta toca em controle do Forge segue exigida (`R-REVIEW`, `R-SEGURANCA`).

## Gatilhos
Gatilhos: processo do portão de segurança (agente `security-engineer` com invariantes em `tests/config.json`, modelo do parecer e a cópia do template); não toca `hooks/`, `bin/`, `.github/`, `docs/regras/`, `tests/catraca.py`, `tests/config.json`, dependência, segredo nem dado pessoal.

## Achados
- A1 (recomendado) bin/forge-check:3039 · O esqueleto do parecer novo ainda escreve em `## Gatilhos` a marca "os gatilhos da R-SEGURANCA que a entrega toca", não a forma `Gatilhos: ...` do modelo novo; alinhar a marca evita que o autor siga o formato antigo. Dono: tech-lead (fora deste item, que não toca bin/).

## Sondas

## Detalhe dos achados
A1: consistência, sem caminho de ataque; o `forge-check docs` não confere o conteúdo da seção, então o parecer gerado pelo esqueleto continua válido. Fica como recomendação para um lote que já toque `bin/forge-check` (arquivo protegido, `R-CONFORMIDADE`).

Demais pontos, sem achado:
- Nenhum trecho de `invariantes` some: os 13 itens de `agents/security-engineer.md` em `tests/config.json` continuam presentes (conferido por expressão contra o arquivo no head); a única linha removida dos modelos é a frase de instrução de `## Gatilhos`, substituída pela forma de uma linha.
- Os dois modelos seguem iguais byte a byte (teste novo `test_os_dois_modelos_seguem_iguais`).
- A regra nova não afrouxa o bloqueio: `bloqueante` continua exigindo evidência, e o requisito de `## Sondas` (PAR-P1) e de `critério mudou:` não muda.
- Neutralidade (`R-NEUTRO`): o exemplo `M1.1` é genérico; nenhum nome de projeto ou stack entra.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do diff inteiro; conferência dos invariantes de `tests/config.json` contra os três arquivos tocados. Testes do item, na raiz do clone no head: `tests.test_achado_teto_doc` (4 testes, OK) e, por tocarem o formato do parecer, `tests.test_parecer_conteudo` e `tests.test_reval_delta` (25 testes, OK, 70 s). A suíte inteira fica para o CI do PR. Sem varredura de segredos nem de dependências: o diff não toca nenhuma das duas.
