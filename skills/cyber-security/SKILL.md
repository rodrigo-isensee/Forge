---
name: cyber-security
description: Revisão de cibersegurança e boas práticas de um sistema (checklists da stack do projeto, mais Docker e CI) - modelagem de ameaças, OWASP Top 10 e API Security Top 10, ASVS, cadeia de suprimentos, segredos, LGPD e endurecimento. Mantida pelo `security-engineer`. Use ao revisar o projeto, uma mudança sensível (autenticação, webhook quando houver, banco, CI, Docker, dados pessoais) ou uma dependência nova.
---

# Cibersegurança e boas práticas

## Postura
- Revisão **defensiva e estática**: ler código, configuração, migrações, workflows e documentação. **Não** explorar vulnerabilidade, **não** varrer sistemas externos, **não** copiar nem exibir segredo encontrado (cite só arquivo:linha e o tipo).
- Falso positivo é custo. Para cada achado, mostre um caminho realista de ataque (quem, de onde, o quê ganha). Sem caminho, é recomendação, não vulnerabilidade.
- Cada correção proposta deve ser proporcional: não inflar a arquitetura. Prefira configuração e remoção a mais código.

## Método
1. **Ativos e fronteiras de confiança:** dados pessoais, credenciais (integrações externas), o banco, webhooks (quando houver), o CI, o navegador. Desenhe o fluxo (Mermaid) e as fronteiras.
2. **Ameaças (STRIDE)** por fronteira; priorize por probabilidade × impacto.
3. **Checklists por camada** (abaixo), com evidência `arquivo:linha`.
4. **Severidade:** crítica (exploração remota sem autenticação ou vazamento de dado pessoal/segredo), alta, média, baixa, informativa. Para cada achado: evidência, caminho de ataque, correção mínima, esforço (P/M/G), dono (agente).
5. **Saída:** o parecer `docs/security/<pedido>.md` (modelo em `docs/security/_modelo.md`: resumo, achados, plano em cartões, riscos aceitos) e o modelo de ameaças em `docs/security/ameacas/<demanda>.md`. Atualizar, não duplicar. O parecer é portão quando há gatilho (`R-SEGURANCA`, que traz a lista).

## Checklists
**Da stack do projeto:** leia a stack no `CLAUDE.md` do projeto (seção "Stack") e aplique `${CLAUDE_PLUGIN_ROOT}/stacks/<stack>/seguranca.md` (API, front, banco e cadeia de suprimentos do gerenciador de pacotes). Stack sem esse arquivo: aplique OWASP Top 10 e API Security Top 10 às camadas que o projeto tem e registre a lacuna.
**SAST e varredura da stack:** regras de análise estática da linguagem, comando de auditoria do gerenciador de pacotes e endurecimento do framework web ficam na seção "SAST da stack" do `seguranca.md` da stack; o núcleo só manda aplicá-los.
**Docker/Compose:** imagens com versão fixa (idealmente digest), usuário não root, sistema de arquivos somente leitura quando possível, sem segredo na imagem nem no `Dockerfile`, portas expostas só em `127.0.0.1`, healthchecks, `.dockerignore`.
**GitHub Actions/CI:** `permissions:` mínimas por job, ações fixadas por SHA (ou revisadas via Dependabot), nenhuma `pull_request_target` com checkout de código de fork, segredos só onde necessário, cache sem envenenamento, proteção de branch e revisão obrigatória.
**Cadeia de suprimentos:** auditoria de dependências, lockfile versionado e instalação congelada, atualização automática (Dependabot), licenças permissivas, scripts de instalação revisados, pacotes recém-publicados ou com um mantenedor só; plugins de terceiros no Claude Code (código que executa na máquina: licença, auditoria, auto-update). Comandos exatos na `seguranca.md` da stack.
**Segredos e configuração:** `.env` fora do git, `.env.example` sem valores reais, varredura de histórico por segredos, configuração validada na partida, rotação possível.
**LGPD:** base legal e minimização; dado pessoal só onde a regra de negócio exige; acesso restrito e registrado; retenção; direito de eliminação viável com tabelas append-only (documentar a estratégia).
**Regras invioláveis do projeto como requisito de segurança:** trate cada regra do `CLAUDE.md` do projeto (ex.: restrições sobre dados pessoais, segregação de fontes) como requisito a verificar; credenciais só em `.env`.

## Ferramentas (só gratuitas, `R-CUSTO`)
`gitleaks` (segredos, com `--redact`), `osv-scanner` (dependências), Semgrep CE ou linter de segurança da linguagem (SAST, só com regras de licença compatível), `zizmor` e `actionlint` (workflows), `trivy` (imagens e IaC, no CI), Dependabot e secret scanning nativos (confira o custo em repositório privado). Análise avançada paga em repositório privado fica fora. O agente **não instala** ferramenta: usa a que já está no PATH e registra a lacuna no parecer; as varreduras rodam no CI do projeto (`devops-engineer`).

## Limites
Não altera código de produção: propõe o que mudar e o agente dono implementa; correção de segurança passa por code review e QA como qualquer outra (`R-REVIEW`, `R-QA`). Dúvida de regra de negócio ou de risco aceito vai ao usuário, com insumos.
