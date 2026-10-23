---
tipo: review
contrato: 1
pedido: impl-n-tpl-a
branch: melhoria/impl-n-tpl-a2
commit: 84c53e9afc27f5aa1ec76cdb8a7c3e884e9623c5
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-22
---
# Review: impl-n-tpl-a

Etapa E1.2 (`R-REVIEW`), feita por uma instância revisora que não é a autora (D-ETAPAS-INST = A). Diff lido: `a3dbe22..84c53e9`, 11 arquivos em 4 commits. A branch foi refeita, então este é um review novo da branch inteira desde o Base-sha, e não um delta do parecer reprovado da `melhoria/impl-n-tpl-a` (23099a4). Base do desenho: `docs/propostas/discovery-0.29.0/n-tpl.md` (lote N-TPL-a, §2 e §4) e o modelo de ameaças `docs/security/ameacas/n-tpl.md`. O parecer de segurança (E1.3) é do `security-engineer`, que roda em paralelo, e não é refeito aqui.

## Achados

## Parecer
**Aprovado.** O A1 do review anterior foi resolvido: cada item se reverte sozinho no HEAD, e os testes da M9 ficam num arquivo próprio. O conteúdo é o mesmo que já tinha sido revisado, e cada teste novo fica vermelho sem a mudança.

### A1 do review anterior: resolvido
- Commits: 6319d21 (NOME-PEDIDO-NEUTRO), 20a3127 (F8), 77d1856 (M9) e 84c53e9 (fragmento `changelog.d/impl-n-tpl-a2.md`, cujo nome bate com a branch). A ordem é a do desenho, com um commit por item (P3 = B).
- Sonda numa cópia em `$TMPDIR`, no HEAD 84c53e9, com `git revert --no-commit` de cada commit sozinho: os 4 revertem sem conflito. Depois de cada revert, os módulos de teste que sobram (`test_clareza`, `test_modelos_projeto`, `test_dependabot_modelo`) passam, e `Neutralidade*` e os invariantes de `test_forge` também ficam verdes.
- Os testes da M9 agora estão em `tests/test_dependabot_modelo.py`, criado pelo 77d1856. O `tests/test_modelos_projeto.py` só é tocado pela F8. Fora o fragmento, o único arquivo que mais de um commit toca é o `tests/config.json`, e só com acréscimo de chave ou linha, como o §4 permite.

### Conteúdo igual ao da branch antiga
- `git show --format=` de f23c3c1 e de 6319d21 dá o mesmo resultado; o mesmo vale para aa9279e e 20a3127.
- 9c7a716 e 77d1856: `skills/ci-cd/SKILL.md`, `stacks/node-react/pronto.md` e `templates/projeto/.github/dependabot.yml` são iguais byte a byte. Os testes (`DEPENDABOT`, `grupos` e `TestModeloDependabot`) são iguais linha a linha. Mudou só o lugar onde ficam: saíram do fim de `test_modelos_projeto.py` e foram para o arquivo novo, que traz os próprios imports e `ler`.

### Testes: vermelhos sem a mudança
Para esta sonda, tirei só os arquivos de conteúdo de cada item e mantive os testes:
- NOME-PEDIDO-NEUTRO (com o `_modelo.md` da base): `test_modelo_de_pedido_pede_nome_neutro_no_forge` falha, e `test_trechos_obrigatorios` também falha pelo invariante novo.
- F8 (sem os dois roteiros): 1 falha e 5 erros em `test_modelos_projeto`.
- M9 (sem o modelo, sem o bloco da stack e sem as frases da skill): 2 falhas e 3 erros em `test_dependabot_modelo`.

Também fiz três mutações pontuais:
- trocar o check `bateria` por `bateria-x` no roteiro do Forge faz falhar o `test_checks_citados_existem_nos_workflows`;
- pôr `major` no grupo de rotina do modelo faz falhar o `test_modelo_dependabot`;
- trocar `Active` por `Evaluate` no roteiro do modelo faz o `RegrasInviolaveis` falhar.

Rodei o `forge-init` num diretório vazio, com a cópia: ele cria `.github/dependabot.yml` e `docs/engineering/protecao-de-branch.md`, e nenhum `{{` sobra (AB-14). `test_cria_estrutura_completa` e `Neutralidade*` ficam verdes no HEAD.

### Checklist (itens de leitura)
O Forge não tem `docs/engineering/praticas.md`. O checklist abaixo é o da skill `engineering-practices`, e as checagens de ferramenta são as da suíte. O autor relatou o pre-push com 1384 testes OK em 84c53e9, e o pre-push deste parecer roda a suíte de novo.
1. Escopo: estão os 3 itens do N-TPL-a, mais o fragmento. A Q2 = A foi respeitada: só texto, nada em `.github/rulesets/`. Nada do N-TPL-b entrou.
2. Regras e ADRs:
   - `R-NEUTRO`: o ecossistema de pacotes aparece só em `stacks/node-react/pronto.md`; o modelo traz só a entrada `github-actions`, como pede o controle M9 (a). O roteiro neutro não cita catraca nem bateria, como pede F8 (i), e há teste para isso.
   - `R-CONFORMIDADE` e `R-CUSTO`: os textos dizem que o dono configura, que nenhum agente escreve na API nem recebe token, e que o repositório privado no plano gratuito fica sem esta camada.
   - Controles cumpridos: F8 (a) a (g), M9 (c) a (f) e NOME-PEDIDO-NEUTRO (a) a (c). As decisões D3a, D5 e D1 aparecem no modelo e no bloco da stack.
3. Legibilidade: os passos são curtos, um por linha, e os testes são diretos.
4. Entradas e erros: não se aplica, porque a entrega é texto e modelo.
5. Segurança: nada novo a encaminhar ao E1.3.
6. Performance: os testes novos rodam em milissegundos.
7. Testes: cobertos acima.
8. Acessibilidade: não se aplica.
9. Commits: Conventional Commits em português, um por item, cada corpo diz o porquê, sem `--amend` nem `--force`.
10. Critério de reversão: está no desenho (§2.1, medir os renomeios por neutralidade em 2 releases). Não há mecanismo novo.
11. Testes de ausência: `assertNotIn` e `assertNotRegex` procuram termos que hoje não estão no texto, como deve ser. Os testes que percorrem pastas afirmam um mínimo (`len(pronto) >= 1`, `len(citados) >= 2`).

### Recomendações (não bloqueiam)
- `tests/test_modelos_projeto.py:1`: a docstring ainda cita a M9 (modelo de dependabot.yml), mas o arquivo agora só tem a F8. Ajustar a docstring num próximo toque no arquivo.
- `tests/test_clareza.py:59`: há três linhas em branco antes de `TestNomeDoPedidoNeutro`, quando o padrão é duas. É só cosmético.
- O `--forcar` do `forge-init` sobrescreve um `dependabot.yml` que já existe (controle M9 (g) e AB-15). O desenho deixou isso fora do lote. Fica para a segurança (E1.3) confirmar se vira cartão.
