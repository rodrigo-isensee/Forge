---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0478-devops-lote
commit: d50b9cd0783da93d77709cdba273c1f45ce053b2
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-18
---
# Review de segurança: v0478 (E6.4, lote de devops)

Diff revisado: `4182a6b9..d50b9cd0` (scripts/preparar-estacao.sh, tests/test_ferramentas_portoes.py, bin/forge-testes, tests/pesos-d4.json, agents/devops-engineer.md, skills/ci-cd/SKILL.md, skills/cyber-security/SKILL.md, changelog.d/v0478-devops-lote.md).

## Gatilhos
Gatilhos: dependência nova (o modo `--ferramentas` e o preparo completo baixam e executam binários e pacotes de terceiros na estação do dono).

## Achados
- A1 (recomendado) scripts/preparar-estacao.sh:84 · a soma esperada vem da mesma release do binário: protege contra download corrompido, não contra release trocada; fixar no script o sha256 de cada artefato ao lado da versão (linha 75)
- A2 (recomendado) scripts/preparar-estacao.sh:104 · os dois pacotes do índice da linguagem entram sem versão fixada (pega a última publicada), contra o "sem latest" da skill ci-cd; fixar a versão de cada um, como as dos binários
- A3 (recomendado) scripts/preparar-estacao.sh:87 · falha do `tar` numa lista `&&` dentro do bloco não dispara `set -e`: a linha seguinte grava "instalou" sem binário instalado; envolver em `if tar ... && install ...; then fez; else falta; fi`

## Sondas

## Detalhe dos achados
**A1** (baixa; esforço P; dono: devops-engineer). Evidência: scripts/preparar-estacao.sh:75 fixa só a versão; :83-85 baixa o artefato e o arquivo de somas do mesmo endereço de release e compara. Caminho de ataque: quem controla a conta do mantenedor (ou troca os ativos de uma release mutável) substitui binário e soma juntos; a estação do dono executa o binário com o acesso dele (token do `gh`, chaves). O comentário em :72-73 já declara "integridade, não autenticidade", então não é defeito, é endurecimento: com a soma fixada no script, a troca posterior da release vira `falta:` em vez de instalação. Os três artefatos a fixar: actionlint 1.7.12 (linux amd64, tar.gz), gitleaks 8.30.1 (linux x64, tar.gz), osv-scanner v2.7.1 (linux amd64, binário).

**A2** (baixa; esforço P; dono: devops-engineer). Evidência: scripts/preparar-estacao.sh:104 instala `zizmor` e `semgrep` sem versão. Caminho: uma versão maliciosa publicada no índice (incidente já visto no ecossistema) entra na próxima estação preparada. Correção mínima: `nome==versão` nas duas chamadas de :113-114, com o bump pelo mesmo fluxo de revisão das versões dos binários.

**A3** (informativa para segurança, defeito de relato; esforço P; dono: devops-engineer, review do tech-lead). Evidência: :87 `tar ... && install ...` seguido de `fez "instalou ..."` em :89. Repro local da semântica: `bash -c 'set -e; f(){ if true; then false && true; echo "seguiu: instalou"; fi; }; f'` imprime `seguiu: instalou`. Só ocorre com o hash conferido e o membro ausente do tar (formato da release mudou); não abre caminho de ataque, mas o dono lê "fez:" sem a ferramenta do portão.

Verificado sem achado:
- Falha fechada: soma vazia ou diferente não instala (:85, :91); o teste `test_soma_errada_nao_instala` cobre e passou (6 testes, rc 0).
- Casamento da soma por nome exato (`$2 == a` ou `*a`, :84), sem prefixo nem expressão; um nome parecido não serve de soma.
- Extração só do membro nomeado, num `mktemp -d` próprio (:82, :87); `install -m 755` para `~/.local/bin`, sem root; `rm -rf` do temporário ao fim (:96).
- Endereços todos `https://github.com/<dono>/<repo>/releases/download/<versão fixada>` (:107-112); sem credencial, sem custo (`R-CUSTO`).
- O modo `--container` (postStart, sem o dono) sai em :452-455, antes de `garantir_ferramentas` (:446 é o `--ferramentas`, :591 o preparo completo; `test_modo_container_nao_baixa_ferramenta`); o pacote do gerenciador do sistema só entra por `sudo` com o dono presente (:101).
- `--simular` não grava nada (`test_simular_lista_as_tres_ferramentas_de_binario_e_nada_e_gravado`).
- Ferramenta já no PATH não é rebaixada (:79); arquitetura fora de x86_64 vira `falta:` (:109).
- Textos de agentes e skills: mudança de redação e a regra "quem instala é o script, ferramenta ausente é achado"; o item "ensaio de roteiro em alvo não provado descartável" entra como ameaça fixa no STRIDE da skill. Sem afrouxamento de regra com ID.

Recomendação informativa (sem achado): `curl` com `--proto '=https'` impede que um redirecionamento rebaixe o protocolo; hoje a soma cobre o binário, mas não o arquivo de somas.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: nenhuma das da skill (gitleaks, osv-scanner, semgrep, zizmor, actionlint, shellcheck) está no PATH desta estação, lacuna registrada; revisão por leitura, o teste novo `tests/test_ferramentas_portoes.py` rodado localmente (OK) e a sonda de shell de A3. Suíte inteira: só no CI do PR (não rodada aqui, conforme o brief).
