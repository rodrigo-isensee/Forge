"""E7 (TEMPO-B2): o `forge-check pr` da linha de comando só aprova com a linha `- <data> <hora>: entrega conferida <sha40>` do head no
`## Histórico` do pedido (falha fechada sem o pedido). Os testes que não tratam da conferência a gravam com `gravar_conferida`, no
pedido do HOME do teste (fora do repositório, onde o Jarvis do Forge o guarda), sobre o head da ref; os testes do E7 gravam a deles."""
import os
import subprocess
from pathlib import Path


def gravar_conferida(home, raiz, pedido, ref="HEAD"):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    r = subprocess.run(["git", "-C", str(raiz), "rev-parse", "--verify", "-q", f"{ref}^{{commit}}"], capture_output=True, text=True, env=env)
    if r.returncode:
        return
    arq = Path(home) / ".forge-contrib" / "docs" / "pedidos" / f"{pedido}.md"
    arq.parent.mkdir(parents=True, exist_ok=True)
    texto = arq.read_text(encoding="utf-8") if arq.is_file() else f"# {pedido}\n"
    texto = texto if texto.endswith("\n") else texto + "\n"
    texto += ("" if "\n## Histórico\n" in texto else "\n## Histórico\n") + f"- 2026-11-04 09:00: entrega conferida {r.stdout.strip()}\n"
    arq.write_text(texto, encoding="utf-8")
