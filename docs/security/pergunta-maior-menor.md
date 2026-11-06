---
tipo: revisao-seguranca
contrato: 1
pedido: versao-033
branch: melhoria/pergunta-maior-menor
commit: 88c82dd4d4c97f004e0d273ef70c142f443e5c18
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-04
---
# Review de segurança: versao-033 (PERGUNTA-MAIOR-MENOR)

Escopo: diff `b45e40a..88c82dd` (5 arquivos: `docs/regras/R-DECISAO.md`, `skills/modo-iniciante/SKILL.md`, `tests/config.json`, `tests/test_pergunta_maior_menor.py`, `changelog.d/pergunta-maior-menor.md`). Revisão estática, primeira rodada.

## Gatilhos
Controles do Forge (`R-SEGURANCA`): a branch altera o texto de uma regra (`docs/regras/R-DECISAO.md`) e a lista de invariantes em `tests/config.json`.

## Achados

## Detalhe dos achados
Sem achado bloqueante nem recomendado. O que foi conferido:

1. **Ordem ampla continua sem valer como confirmação.** O diff toca só a linha 11 de `docs/regras/R-DECISAO.md` (o formato da pergunta). O bloco "Complemento: \"tanto faz\" e ordem ampla" (`docs/regras/R-DECISAO.md:26-29`) está byte a byte igual à base: ordem ampla só cobre itens já `confirmado` ou `delegado`; custo, acesso, exceção a regra e ato irreversível seguem fora da delegação.
2. **Nenhuma invariante afrouxada ou removida.** `git diff b45e40a 88c82dd -- tests/config.json` não tem linha removida; só acrescenta a frase nova à lista de `docs/regras/R-DECISAO.md` (`tests/config.json:555`). A lista de `skills/modo-iniciante/SKILL.md` (`tests/config.json:187`) e a contagem mínima (`tests/config.json:662`) estão iguais; as frases cobradas ("Afrouxa o processo?", "custo de eficiência", "decidam vocês", a frase que nega a saída em custo, acesso, exceção e ato irreversível) continuam no texto. O JSON é válido.
3. **O texto novo não abre brecha para o Jarvis decidir pelo dono.** A mudança só acrescenta informação à pergunta (comparação do custo entre opções, em palavras); não muda quem decide, não cria atalho de delegação e mantém a recomendação separada das opções. Na skill (`skills/modo-iniciante/SKILL.md:35`, exemplo nas linhas 41-43), a opção sem número diz "não dá para dizer se é maior ou menor: não medido", o que preserva a proibição de inventar número. Observação informativa, sem caminho de ataque e de clareza (vai ao `tech-lead` se quiser): a regra em `docs/regras/R-DECISAO.md:11` lista "a mais barata", "a mais cara", "igual" e não cita o caso `não medido`, que só a skill trata.

Testes rodados no commit revisado (todos OK): `test_pergunta_maior_menor.py` (1), `test_comportamento.py` (6) e, por dúvida sobre o tamanho e o texto da linha alterada, `test_clareza.py` (7) e `test_textos_dono_f10.py` (3). Suíte inteira fica com o `qa-engineer` (D-5).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do diff, `git diff`, `python3 -I` (validação do JSON e testes). `gitleaks` não está no PATH (lacuna registrada; o diff é só texto e teste, sem credencial à vista na leitura).
