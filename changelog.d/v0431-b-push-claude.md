### Corrigido
- **PUSH-DENTRO-DO-CLAUDE (P2):** a detecção `dentro_do_claude` ganha testes que a decidem no próprio processo, com ambiente e árvore de processos fixados, nos dois sentidos, e um teste que prova também no CI que um `claude` acima do processo do teste não muda a suíte; `docs/hooks.md` diz que o push de dentro do Claude Code não precisa mais do tmux. A guarda de produção não muda.
