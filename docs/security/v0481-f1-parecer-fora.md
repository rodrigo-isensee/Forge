---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-f1-parecer-fora
commit: e26310c229a8fae6bcbc2168d9a2db3d16875f2a
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-26
---
# Review de segurança: v0481 (E29.3, #925, F1 corte 1: leitura do parecer no status)

## Gatilhos
Gatilhos: controle de portão (leitura do parecer que decide o merge), integração com a API do GitHub pelo token da sessão, código em `PROTEGIDOS` (`bin/forge_pareceres.py`).

## Achados
- A1 (bloqueante) bin/forge_pareceres.py:139 · CI do head vermelho (run 45915860351: suíte partes 2/5 e 4/5 nas duas versões); segurança não aprova sem a suíte verde. A correção é a do review A1 e A2 (M27 com `de` único, índice regerado), sem mudança de segurança; reenvie e eu revalido por delta.
- A2 (recomendado) bin/forge_pareceres.py:141 · `in contas` (141 e 120) aceita substring e até login vazio se `contas` vier como str (sondas S1 e S2 do detalhe): o filtro do M1.1 deixa de ser lista positiva exata. `ler` recusa `contas` que não seja set/frozenset de str não vazias (Recusa), com teste.
- A3 (recomendado) bin/forge_pareceres.py:117 · resposta malformada do `gh` solta KeyError, AttributeError ou TypeError em vez de Recusa (117 `pr["number"]`, 120 `user` não objeto, 141 `creator` não objeto; sondas S3 a S5): fecha, mas fora do M19.1. Converta como o `publicar` (linha 170) e teste os três.

## Sondas

## Detalhe dos achados
**O que o corte faz, pela lente do G2** (`docs/security/ameacas/g2-parecer-status.md`): `ler` e `conferir` cobrem M1.1 e M1.2 (filtro de conta antes do mais novo, 141; `test_c1_status_do_bot_ignorado`, `test_c2_bot_mais_novo_nao_esconde_failure_da_conta`), M2.1 (igualdade exata do contexto, 141; `test_c3_contexto_parecido`), M5.1 (sha256 do corpo normalizado, 122; `test_c6_comentario_editado`, `test_c6_comentario_apagado`), M5.2 (autor do comentário na lista, 120; `test_c7_comentario_de_outra_conta`), M6.1 (`target_url` só por `fullmatch`, dono/repo do `origin`, PR do head, `html_url` igual e nunca seguido, 117 a 120; `test_c8_target_url_fora_do_formato` confere que nenhuma chamada sai antes da recusa; `test_comentario_de_outro_pr_pelo_mesmo_id`), M7.1 (descrição inteira por `fullmatch`, 115; `test_c9_descricao_fora_da_forma`), M8.1 (commit, branch, pedido, tipo e veredito do frontmatter iguais ao head e ao estado, 124 a 127; `test_c10_*`) e M19.1 nas páginas (`--paginate --slurp`, forma conferida, 135 a 137; `test_c17_*`). O id do comentário e o número do PR só entram no caminho da API como dígitos do regex, e a busca vai ao repositório do `origin` com `--hostname` explícito: `GH_REPO` e `GH_HOST` não desviam a leitura. Status mais novo inválido da conta mascara o válido mais velho e vira (None, motivo): falha fechada. Comentário apagado derruba a leitura inteira por Recusa: negação de serviço já aceita no T5.

**Quem pode forjar.** (1) O bot do workflow (T1): fora da lista, ignorado (C1, C2). (2) Outra conta com acesso (ator 5): fora da lista, ignorada no status e no comentário (C7, `test_c19_conta_fora_da_lista_ignorada`). (3) A mesma conta pelo Bash (T4, `gh api` direto com corpo cujo sha256 bate): passa por `ler` hoje; é a lacuna [B] do T4, fechada só por M4.1 e M4.2 (cortes 8 e 3 do plano do PR). Sem chamador, não é achado deste corte, mas o corte 9 não pode entrar antes deles. (4) Conta de outro papel: com uma conta só, `conferir` não amarra o `creator` do status ao autor do comentário nem ao papel do contexto; neutro hoje (uma conta), a rever quando houver conta por papel.

**A2.** Evidência: `bin/forge_pareceres.py:141` e `:120`, `login in contas`. Caminho: o corte 7 (M1.4) lê a lista de um arquivo da base; um valor escalar no lugar da lista (por exemplo `"contas": "conta-dos-agentes"`) chega a `ler` como str, e qualquer login que seja trecho dele (`conta`, `agentes`, ou o vazio) passa no filtro do status e do comentário. Sondas (`python3 -I /root/.forge-contrib/v0481-sec118-sonda.py <cópia>`, sem rede): S1 · contas `"conta"`, autor `cont` · espera: fora · obtido: aprovado; S2 · contas `"conta"`, autor `""` · espera: fora · obtido: aprovado. Severidade: média latente (sem chamador hoje). Correção mínima: no começo de `ler`, `if not isinstance(contas, (set, frozenset)) or not all(isinstance(x, str) and x for x in contas): raise Recusa(...)`, e um teste com str e com conjunto vazio de nomes. Esforço P. Dono: autor do F1 (E29.1).

**A3.** Evidência: `:117` (`pr["number"]`), `:120` (`(c.get("user") or {}).get` com `user` str), `:141` (`(s.get("creator") or {}).get` com `creator` str; com `contas` str e `user` nulo, TypeError). Sondas: S3 · comentário com `user: "conta"` · espera: Recusa · obtido: AttributeError; S4 · PR sem `number` · espera: Recusa · obtido: KeyError; S5 · contas str, `user: null` · espera: Recusa · obtido: TypeError. Caminho: resposta da API fora do contrato (mudança do servidor, `gh` trocado no PATH); o efeito é exceção não prevista no chamador do corte 9, que hoje fecharia por queda, não por Recusa com motivo. Severidade: baixa. Correção mínima: em `ler`, envolver o laço e `conferir` em `except (KeyError, TypeError, AttributeError, ValueError) as e: raise Recusa(...) from None`, como o `publicar`; testes dos três formatos. Esforço P. Dono: autor do F1.

**O que aperta, o neutro e o que afrouxa.**
- Aperta: nada muda no comportamento de hoje; `ler`, `conferir` e `frontmatter` não têm chamador (`grep` em `bin/`, `hooks/` e `scripts/`: só os testes). Quando o corte 9 as ligar, a leitura é mais estrita que o arquivo na branch: conta, sha256, URL presa ao PR e frontmatter preso ao head.
- Neutro: `publicar` e `agregado` sem mudança (o `{owner}/{repo}` deles é o corte 2); nenhum workflow, permissão de token, dependência ou segredo novo; varredura manual do diff sem segredo.
- Afrouxa: nada neste corte. Para não afrouxar depois: o corte 9 só entra com M1.4 (corte 7), M4.1 (corte 8), M4.2 (corte 3) e M10.1 (cortes 5 e 6); a herança (M11.1, M12.1) não tem forma em `DESCRICAO` e hoje é recusada (fecha), e precisa de corte próprio antes de alguém depender dela.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Testes afetados rodados no head (com a trava de teste): `python3 -m unittest tests.test_forge_pareceres`, 65 testes, OK. CI: run 45915860351, vermelho em 2/5 e 4/5 (A1); `bateria (pareceres)` espera os pareceres. Ferramentas ausentes no ambiente (lacuna registrada, nada instalado): varredor de segredos, SAST, auditoria de dependências e linters de workflow; o diff não toca dependência nem workflow.
