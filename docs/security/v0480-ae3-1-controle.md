---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-ae3-1-controle
commit: 98882c4903c31dd2e074783dec70b31882046244
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-22
---
# Review de segurança: v0478 (E108.3, AE3.1 `bin/forge_controle.py`)

Primeira rodada, revisão completa. Base b0895f6c, head 98882c49. Desenho: `docs/propostas/v0479-melhorias-anti-erro.md` (AE3, linha da AE3.1 na tabela de cartões, D3 e D7).

Gatilhos: controle do Forge que roda git na pasta de controle e decide o que entra no commit (lista positiva, recusa de link, segredo e hook), primitiva que o relógio da AE3.2 vai chamar fora do sandbox (D7).

## Achados
- A1 (bloqueante) bin/forge_controle.py:37 · A recusa por código de fora só olha core.hooksPath e a pasta de hooks; core.fsmonitor (roda no status e no add), filter.<x>.clean (no add) e gpg.program com commit.gpgsign (no commit) executam comando da config e salvar segue (S1 a S3). O .git/config da pasta de controle é gravável no sandbox.
- A2 (recomendado) bin/forge_controle.py:89 · A trava abre .git/forge-controle.lock com open(..., "a"), que segue link: um link ali cria arquivo vazio no destino, fora da pasta de controle quando o relógio roda fora do sandbox. Abrir com O_NOFOLLOW e O_CREAT, como pede o desenho.
- A3 (recomendado) bin/forge_controle.py:21 · SEGREDO cobre só .env, .pem, .key, .p12, .pfx e id_<algoritmo>; docs/ é a pasta inteira e o push do D3 leva o commit ao remoto. Somar .netrc, credentials*, secrets*, *.kdbx, *.jks, *.keystore, *.p8 e o teste de cada um.

## Sondas
- S1 · repositório em $TMPDIR, `git config core.fsmonitor <script que grava marca>`, docs/a.md alterado, salvar(repo) · espera: nao-verificavel e nenhuma marca · obtido: ('salvo', sha) e 5 execuções do script
- S2 · mesmo repositório, `git config commit.gpgsign true` e `git config gpg.program <script que grava marca>`, docs/a.md alterado, salvar(repo) · espera: nao-verificavel sem rodar o script · obtido: ('erro', 'gpg failed to sign') e o script rodou
- S3 · mesmo repositório, `git config filter.z.clean <script que grava marca>` e `*.md filter=z` em .git/info/attributes, docs/a.md alterado, salvar(repo) · espera: nao-verificavel e nenhuma marca · obtido: ('salvo', sha) e 3 execuções do script

## Detalhe dos achados
**A1.** Evidência: `bin/forge_controle.py:35-47` (`_hook_ativo`) e a docstring em `:5-8`, que promete sair `nao-verificavel` quando "o commit rodaria código de fora". Sondas S1 a S3 rodadas sobre o head 98882c49 com o git 2.43 do ambiente. Teste de escrita (abertura em modo de acréscimo, sem gravar nada): `/root/.forge-contrib/.git/config` é gravável de dentro do sandbox; a pasta `.git/hooks` também, mas essa já é coberta. Caminho de ataque: um agente da sessão (por injeção num brief, pedido ou texto de PR) grava `core.fsmonitor`, um filtro `clean` ou `gpg.program` no `.git/config` da pasta de controle; o próximo `salvar` executa o comando. Na sessão, roda dentro do sandbox. Pelo relógio da AE3.2, que segundo o D7 roda fora da sessão, roda sem sandbox: é a fuga que a checagem de hook existe para fechar, por outra porta. Severidade: alta quando o relógio estiver ligado, média até lá; é bloqueante porque a garantia declarada falha com prova. Correção mínima: em `_hook_ativo`, ler a config efetiva (todas as origens, com includes: `git config --get-regexp`) e sair `nao-verificavel` quando houver qualquer uma destas chaves: `core.fsmonitor` com valor diferente de `false`; `filter.<nome>.clean`, `filter.<nome>.smudge` ou `filter.<nome>.process`; `commit.gpgsign` verdadeiro; `gpg.program`, `gpg.<formato>.program` ou `gpg.ssh.defaultkeycommand`. Sem trocar nem esvaziar a config (mesma regra do `core.hooksPath`, `R-VERIFY`). Um teste por chave, no molde de `test_hook_ativo_e_nao_verificavel_e_nao_roda`: o script não roda e não sai commit. A janela entre a checagem e o commit é residual aceitável: quem grava a config nessa janela já tinha o mesmo acesso antes dela. Esforço P. Dono: tech-lead (autor da E108.1).

**A2.** Evidência: `bin/forge_controle.py:89`. O `.git` da pasta de controle é gravável do sandbox, então o link pode ser plantado; o `open` em modo `a` só cria e não grava, por isso o dano se limita a um arquivo vazio onde o relógio puder escrever. Severidade baixa. Correção: `os.open(trava, os.O_WRONLY | os.O_CREAT | os.O_NOFOLLOW, 0o600)` e `nao-verificavel` no `ELOOP`, mais um teste com o link. Esforço P. Dono: tech-lead.

**A3.** Evidência: `bin/forge_controle.py:19-21`. O desenho põe a mitigação de segredo na lista positiva e no teto de tamanho; a lista ficou `docs/` inteira, mais larga que a do desenho (quadro, histórico, pedidos, briefs, retros, pareceres), e o filtro por nome é o único freio de conteúdo. Caminho: um arquivo de credencial salvo por engano em `docs/anexos/` entra no commit automático e o push do marco (D3) o publica. Severidade baixa. Correção: somar ao `SEGREDO` os nomes `.netrc`, `credentials*`, `secrets*` e as extensões `.kdbx`, `.jks`, `.keystore`, `.p8`, com um caso de teste por nome. Esforço P. Dono: tech-lead.

**Conferido e sem achado.** A lista positiva vale nos dois pontos (pathspec do `status` em `:74` e `_recusa` em `:52`); `add` e `commit --only` recebem só os nomes conferidos, com `--literal-pathspecs` (`:28`), e nada que já estava no índice entra no commit. O link é recusado em qualquer parte do caminho (`:57-64`) e o git grava link como texto, sem seguir. O ambiente do git sai sem as `GIT_*` herdadas (`:26`, inclusive `GIT_CONFIG_PARAMETERS`, o `-c` de fora). Nenhum push nem `--no-verify` no módulo; `test_nunca_faz_push` e `test_hook_ativo_e_nao_verificavel_e_nao_roda` cobrem os dois lados. A trava por `flock` não bloqueia (`:91`). Fora do escopo desta etapa e anotado para a AE3.2: o módulo grava na branch que estiver no HEAD, e a conferência da branch `controle` no projeto fica com ela (D3).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Rodados: `tests.test_forge_controle` (25 testes, OK) e as sondas S1 a S3 num repositório descartável em `$TMPDIR`. A suíte inteira fica para o CI do PR (o brief manda não rodar a suíte local). As ferramentas de SAST e de varredura de segredos não estão no PATH: lacuna registrada.
