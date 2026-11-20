"""BP3 S1 (v0478 E39.4): atalho durável. `scripts/jarvis` e `scripts/jarvis-forge`:
- AVISO: fora do tmux (sem o programa ou com --sem-tmux) só avisa numa linha e abre assim mesmo (D4);
- SUPERVISOR: dentro do tmux o atalho roda o claude e reabre (`--continue`) só em saída anormal (128 ou mais, fora 129 e 130),
  no máximo 3 reaberturas em 30 min, e registra cada queda em quedas.log (D1);
- CLAUDE-ATUAL: abre sempre o Claude Code mais novo entre o do instalador ($HOME/.local/bin/claude) e o primeiro do PATH, nunca o
  2.1.224 que o PATH do sistema traz na frente (D1 do dono).
Tudo com `claude`, `date` e `sleep` falsos no PATH: nenhuma sessão real, nenhuma API, relógio e espera controlados (AR-4: ambiente
montado do zero, sem TMUX, XDG_STATE_HOME nem PATH herdados)."""
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
UTEIS = ("bash", "env", "dirname", "basename", "python3", "grep", "sed", "sort", "head", "tail", "readlink", "mkdir", "timeout",
         "cat", "tr", "rm", "ln", "mktemp", "wc")
DATE_REAL = shutil.which("date") or "/usr/bin/date"


def claude_falso(nome, versao, extra=""):
    """Script `claude` de mentira: `--version` responde (ou cala, com versao=None); a execução vai para $LOG e sai com o
    próximo código de $CODIGOS (um por linha; acabando, 0)."""
    resposta = f'echo "{versao} (Claude Code)"' if versao else "true"
    return f"""#!/usr/bin/env bash
case "${{1:-}}" in
  --version) echo v >> "$VERSOES"; {resposta}; exit 0 ;;
  plugin) exit 0 ;;
esac
echo "{nome} $*" >> "$LOG"
{extra}
if [ -s "$CODIGOS" ]; then c="$(head -n 1 "$CODIGOS")"; sed -i 1d "$CODIGOS"; exit "$c"; fi
exit 0
"""


class Base(unittest.TestCase):
    script = "jarvis"
    rotulo = "proj"

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)
        self.home = self.tmp / "home"
        (self.home / ".local/bin").mkdir(parents=True)
        (self.home / "Forge").mkdir()
        self.projeto = self.home / "proj"
        self.projeto.mkdir()
        self.estado = self.tmp / "estado"
        self.log = self.tmp / "log"
        self.versoes = self.tmp / "versoes"
        self.codigos = self.tmp / "codigos"
        self.esperas = self.tmp / "esperas"
        self.relogio = self.tmp / "relogio"
        # cópia do script sem `.git` e sem `bin/` ao lado: nada de atualização de plugin nem de doutor no teste
        self.raiz = self.tmp / "raiz"
        (self.raiz / "scripts").mkdir(parents=True)
        for nome in ("jarvis", "jarvis-forge", "jarvis-comum.sh"):
            shutil.copy(RAIZ / "scripts" / nome, self.raiz / "scripts" / nome)
        # PATH do teste: fakes (date e sleep sempre) + as ferramentas comuns, sem tmux
        self.fakes = self.tmp / "fakes"
        self.fakes.mkdir()
        self.uteis = self.tmp / "uteis"
        self.uteis.mkdir()
        for nome in UTEIS:
            alvo = shutil.which(nome)
            if alvo:
                (self.uteis / nome).symlink_to(alvo)
        self.escrever(self.fakes / "sleep", f'#!/usr/bin/env bash\necho "$1" >> "{self.esperas}"\n')
        self.escrever(self.fakes / "date", f"""#!/usr/bin/env bash
if [ "${{1:-}}" = "+%s" ] && [ -e "{self.relogio}" ]; then
  read -r a p < "{self.relogio}"; echo $((a + p)) "$p" > "{self.relogio}"; echo "$a"
else exec {DATE_REAL} "$@"; fi
""")
        self.path_velho = self.tmp / "sistema"
        self.path_velho.mkdir()
        self.codigos.write_text("", encoding="utf-8")

    def escrever(self, caminho, texto):
        caminho.write_text(texto, encoding="utf-8")
        caminho.chmod(0o755)

    def velho(self, versao="2.1.224"):
        """O claude do sistema, primeiro do PATH."""
        self.escrever(self.path_velho / "claude", claude_falso("velho", versao))

    def novo(self, versao="2.1.329", extra=""):
        """O claude do instalador oficial."""
        self.escrever(self.home / ".local/bin/claude", claude_falso("novo", versao, extra))

    def saidas(self, *codigos):
        self.codigos.write_text("".join(f"{c}\n" for c in codigos), encoding="utf-8")

    def rodar(self, *args, tmux_dentro=False, **extra):
        env = {"HOME": str(self.home), "PATH": f"{self.fakes}:{self.path_velho}:{self.uteis}", "LOG": str(self.log),
               "VERSOES": str(self.versoes), "CODIGOS": str(self.codigos), "XDG_STATE_HOME": str(self.estado),
               "FORGE_ABERTURA_FEITA": "1", "LANG": "C.UTF-8"}
        if tmux_dentro:
            env["TMUX"] = "/tmp/tmux-falso,1,0"
        env.update(extra)
        argv = ["bash", str(self.raiz / "scripts" / self.script), *args]
        cwd = self.projeto
        if self.script == "jarvis-forge":
            argv.append("--dev")
            cwd = self.home / "Forge"
        return subprocess.run(argv, env=env, cwd=cwd, capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=60)

    def execucoes(self):
        return self.log.read_text(encoding="utf-8").splitlines() if self.log.exists() else []

    def quedas(self):
        arq = self.estado / "forge/quedas.log"
        return arq.read_text(encoding="utf-8").splitlines() if arq.exists() else []

    def consultas_de_versao(self):
        return len(self.versoes.read_text(encoding="utf-8").splitlines()) if self.versoes.exists() else 0


class Resolucao(Base):
    """CLAUDE-ATUAL: como o binário é resolvido."""

    def test_abre_o_do_instalador_e_nunca_o_velho_do_path(self):
        self.velho("2.1.224")
        self.novo("2.1.329")
        r = self.rodar("--sem-tmux")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual([e.split()[0] for e in self.execucoes()], ["novo"])
        self.assertIn("usando o Claude Code 2.1.329", r.stderr)

    def test_o_mais_novo_vence_mesmo_sendo_o_do_path(self):
        self.velho("2.1.400")
        self.novo("2.1.329")
        r = self.rodar("--sem-tmux")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual([e.split()[0] for e in self.execucoes()], ["velho"])
        self.assertNotIn("usando o Claude Code", r.stderr)

    def test_compara_como_numero_de_versao_nao_como_texto(self):
        self.velho("2.1.329")
        self.novo("2.1.99")
        self.rodar("--sem-tmux")
        self.assertEqual([e.split()[0] for e in self.execucoes()], ["velho"])

    def test_empate_fica_com_o_do_instalador(self):
        self.velho("2.1.329")
        self.novo("2.1.329")
        self.rodar("--sem-tmux")
        self.assertEqual([e.split()[0] for e in self.execucoes()], ["novo"])

    def test_um_candidato_so_nao_roda_version(self):
        self.velho("2.1.224")
        r = self.rodar("--sem-tmux")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.consultas_de_versao(), 0)
        self.assertEqual([e.split()[0] for e in self.execucoes()], ["velho"])

    def test_mesmo_arquivo_pelo_caminho_real_conta_uma_vez(self):
        self.velho("2.1.224")
        (self.home / ".local/bin/claude").symlink_to(self.path_velho / "claude")
        self.rodar("--sem-tmux")
        self.assertEqual(self.consultas_de_versao(), 0)

    def test_path_que_nao_responde_version_fica_como_sempre(self):
        self.velho(None)
        self.novo("2.1.329")
        r = self.rodar("--sem-tmux")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual([e.split()[0] for e in self.execucoes()], ["velho"])

    def test_sem_nenhum_claude_sai_127_com_aviso(self):
        r = self.rodar("--sem-tmux")
        self.assertEqual(r.returncode, 127)
        self.assertIn("claude não encontrado", r.stderr)

    def test_diretorio_do_instalador_chamado_claude_nao_conta(self):
        self.velho("2.1.224")
        (self.home / ".local/bin/claude").mkdir()
        r = self.rodar("--sem-tmux")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual([e.split()[0] for e in self.execucoes()], ["velho"])

    def test_dentro_do_tmux_a_resolucao_vale_na_primeira_abertura_tambem(self):
        self.velho("2.1.224")
        self.novo("2.1.329")
        r = self.rodar(tmux_dentro=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual([e.split()[0] for e in self.execucoes()], ["novo"])


class AvisoForaDoTmux(Base):
    """AVISO (D4): avisa, nunca bloqueia."""

    def test_sem_o_programa_tmux_avisa_e_abre(self):
        self.novo()
        r = self.rodar()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("tmux não instalado", r.stderr)
        self.assertIn("sudo apt-get install tmux", r.stderr)
        self.assertEqual(len(self.execucoes()), 1)

    def test_com_sem_tmux_avisa_e_abre(self):
        self.novo()
        r = self.rodar("--sem-tmux")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("sessão não durável (--sem-tmux)", r.stderr)
        self.assertNotIn("tmux não instalado", r.stderr)
        self.assertEqual(len(self.execucoes()), 1)

    def test_dentro_do_tmux_nao_avisa(self):
        self.novo()
        r = self.rodar(tmux_dentro=True)
        self.assertNotIn("não durável", r.stderr)

    def test_o_aviso_e_uma_linha_so(self):
        self.novo()
        r = self.rodar("--sem-tmux")
        self.assertEqual(sum("não durável" in linha for linha in r.stderr.splitlines()), 1)


class Supervisor(Base):
    """SUPERVISOR (D1): reabre só em saída anormal, teto de 3 em 30 min, quedas.log."""

    def setUp(self):
        super().setUp()
        self.novo()

    def test_saida_normal_nao_reabre(self):
        for codigo in (0, 1, 2, 64, 127):
            with self.subTest(codigo=codigo):
                self.log.unlink(missing_ok=True)
                self.saidas(codigo)
                r = self.rodar(tmux_dentro=True)
                self.assertEqual(r.returncode, codigo, r.stderr)
                self.assertEqual(len(self.execucoes()), 1)
        self.assertEqual(self.quedas(), [])

    def test_interrupcao_da_pessoa_e_terminal_fechado_nao_reabrem(self):
        for codigo in (129, 130, 143):  # 143: kill de propósito é parada, não queda (a parada de emergência tem de parar)
            with self.subTest(codigo=codigo):
                self.log.unlink(missing_ok=True)
                self.saidas(codigo)
                r = self.rodar(tmux_dentro=True)
                self.assertEqual(r.returncode, codigo, r.stderr)
                self.assertEqual(len(self.execucoes()), 1)
        self.assertEqual(self.quedas(), [])

    def test_saida_anormal_reabre_com_continue(self):
        for codigo in (128, 131, 137, 139, 255):
            with self.subTest(codigo=codigo):
                self.log.unlink(missing_ok=True)
                self.saidas(codigo, 0)
                r = self.rodar(tmux_dentro=True)
                self.assertEqual(r.returncode, 0, r.stderr)
                execs = self.execucoes()
                self.assertEqual(len(execs), 2, execs)
                self.assertIn("--continue", execs[1].split())
                self.assertIn(f"saída {codigo}", r.stderr)

    def test_reabertura_mantem_o_modo_automatico_e_o_resto_dos_argumentos(self):
        self.saidas(137, 0)
        self.rodar(tmux_dentro=True)
        primeira, segunda = self.execucoes()
        self.assertEqual(primeira.replace(" --continue", ""), segunda.replace(" --continue", ""))
        self.assertEqual(segunda.split().count("--continue"), 1, segunda)
        self.assertIn("--permission-mode auto", segunda)

    def test_reabertura_registra_em_quedas_log(self):
        self.saidas(137, 0)
        self.rodar(tmux_dentro=True)
        (linha,) = self.quedas()
        self.assertRegex(linha, rf"^\d{{4}}-\d\d-\d\dT\d\d:\d\d:\d\d[+-]\d{{4}} projeto={self.rotulo} saida=137 tentativa=1 acao=reabre$")

    def test_teto_tres_reaberturas_a_quarta_queda_para(self):
        self.saidas(*[137] * 10)
        r = self.rodar(tmux_dentro=True, FORGE_QUEDA_ESPERA="0")
        self.assertEqual(r.returncode, 137)
        self.assertEqual(len(self.execucoes()), 4)
        acoes = [re.search(r"tentativa=(\d+) acao=(\w+)", q).groups() for q in self.quedas()]
        self.assertEqual(acoes, [("1", "reabre"), ("2", "reabre"), ("3", "reabre"), ("3", "desiste")])
        self.assertIn("não reabro mais", r.stderr)
        self.assertIn("quedas.log", r.stderr)

    def test_tres_quedas_e_uma_saida_normal_nao_chegam_ao_teto(self):
        self.saidas(137, 137, 137, 0)
        r = self.rodar(tmux_dentro=True, FORGE_QUEDA_ESPERA="0")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(len(self.execucoes()), 4)
        self.assertNotIn("desiste", "".join(self.quedas()))

    def test_fora_da_janela_a_queda_velha_nao_conta(self):
        self.relogio.write_text("1000000 1000\n", encoding="utf-8")  # 1000 s entre quedas: só 2 cabem em 1800 s
        self.saidas(*[137] * 6, 0)
        r = self.rodar(tmux_dentro=True, FORGE_QUEDA_ESPERA="0")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(len(self.execucoes()), 7)
        self.assertNotIn("desiste", "".join(self.quedas()))

    def test_trinta_minutos_exatos_ja_passaram(self):
        self.relogio.write_text("1000000 600\n", encoding="utf-8")  # a 4.ª queda cai a 1800 s da 1.ª: a 1.ª já saiu da janela
        self.saidas(*[137] * 6, 0)
        r = self.rodar(tmux_dentro=True, FORGE_QUEDA_ESPERA="0")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(len(self.execucoes()), 7)

    def test_dentro_da_janela_conta(self):
        self.relogio.write_text("1000000 100\n", encoding="utf-8")
        self.saidas(*[137] * 6, 0)
        self.rodar(tmux_dentro=True, FORGE_QUEDA_ESPERA="0")
        self.assertEqual(len(self.execucoes()), 4)

    def test_janela_configuravel_so_com_numero(self):
        self.relogio.write_text("1000000 100\n", encoding="utf-8")
        self.saidas(*[137] * 10)
        self.rodar(tmux_dentro=True, FORGE_QUEDA_ESPERA="0", FORGE_QUEDA_JANELA="150")  # 2 quedas por janela: nunca chega a 3
        self.assertEqual(len(self.execucoes()), 11)
        for passo, corridas in (("500", 4), ("1000", 11)):  # inválido: volta a 1800 s (nem menor nem maior)
            with self.subTest(passo=passo):
                self.log.unlink()
                self.relogio.write_text(f"1000000 {passo}\n", encoding="utf-8")
                self.saidas(*[137] * 10)
                self.rodar(tmux_dentro=True, FORGE_QUEDA_ESPERA="0", FORGE_QUEDA_JANELA="abc")
                self.assertEqual(len(self.execucoes()), corridas)

    def test_janela_zero_nao_tira_o_teto_de_reaberturas(self):
        """Janela 0 (ou só zeros) deixaria nenhuma queda na conta: reabriria sem fim. Vale o padrão e o teto de 3 segura."""
        for valor in ("0", "00", "000"):
            with self.subTest(valor=valor):
                self.log.unlink(missing_ok=True)
                self.saidas(*[137] * 10)
                self.rodar(tmux_dentro=True, FORGE_QUEDA_ESPERA="0", FORGE_QUEDA_JANELA=valor)
                self.assertEqual(len(self.execucoes()), 4)

    def test_espera_padrao_dez_segundos_e_configuravel(self):
        self.saidas(137, 0)
        self.rodar(tmux_dentro=True)
        self.assertEqual(self.esperas.read_text().split(), ["10"])
        self.esperas.unlink()
        self.saidas(137, 0)
        self.rodar(tmux_dentro=True, FORGE_QUEDA_ESPERA="3")
        self.assertEqual(self.esperas.read_text().split(), ["3"])
        self.esperas.unlink()
        self.saidas(137, 0)
        self.rodar(tmux_dentro=True, FORGE_QUEDA_ESPERA="x; touch /tmp/nao")
        self.assertEqual(self.esperas.read_text().split(), ["10"])

    def test_sem_tmux_nao_supervisiona(self):
        self.saidas(137)
        r = self.rodar("--sem-tmux", tmux_dentro=True)
        self.assertEqual(r.returncode, 137)
        self.assertEqual(len(self.execucoes()), 1)
        self.assertEqual(self.quedas(), [])

    def test_quedas_log_so_com_data_projeto_saida_e_tentativa(self):
        self.escrever(self.home / ".local/bin/claude", claude_falso("novo", "2.1.329", 'echo "SEGREDO-NO-OUTPUT"'))
        self.saidas(137, 0)
        self.rodar(tmux_dentro=True)
        self.assertNotIn("SEGREDO", "".join(self.quedas()))

    def test_xdg_relativo_cai_na_pasta_padrao(self):
        self.saidas(137, 0)
        self.rodar(tmux_dentro=True, XDG_STATE_HOME="relativo")
        self.assertTrue((self.home / ".local/state/forge/quedas.log").is_file())
        self.assertFalse((self.projeto / "relativo").exists())

    def test_falha_ao_gravar_o_log_nao_impede_a_reabertura(self):
        (self.estado).write_text("arquivo no lugar da pasta", encoding="utf-8")
        self.saidas(137, 0)
        r = self.rodar(tmux_dentro=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(len(self.execucoes()), 2)

    def test_cada_reabertura_resolve_o_binario_de_novo(self):
        (self.home / ".local/bin/claude").unlink()
        self.escrever(self.tmp / "a", claude_falso("antes", "2.1.200", f'ln -sf "{self.tmp}/b" "$HOME/.local/bin/claude"'))
        self.escrever(self.tmp / "b", claude_falso("depois", "2.1.329"))
        (self.home / ".local/bin/claude").symlink_to(self.tmp / "a")
        self.saidas(137, 0)
        r = self.rodar(tmux_dentro=True, FORGE_QUEDA_ESPERA="0")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual([e.split()[0] for e in self.execucoes()], ["antes", "depois"])

    def test_reabre_com_o_atual_e_nunca_com_o_velho(self):
        self.velho("2.1.224")
        self.saidas(137, 137, 0)
        self.rodar(tmux_dentro=True, FORGE_QUEDA_ESPERA="0")
        self.assertEqual([e.split()[0] for e in self.execucoes()], ["novo"] * 3)


class ForgeResolucao(Resolucao):
    """O mesmo comportamento no `jarvis-forge` (modo --dev: cópia de trabalho, sem clone da cópia vigente)."""
    script = "jarvis-forge"
    rotulo = "Forge-dev"


class ForgeAviso(AvisoForaDoTmux):
    script = "jarvis-forge"
    rotulo = "Forge-dev"


class ForgeSupervisor(Supervisor):
    script = "jarvis-forge"
    rotulo = "Forge-dev"

    def test_xdg_relativo_cai_na_pasta_padrao(self):  # sobrescreve o do pai: o jarvis-forge já recusava XDG_STATE_HOME relativo, antes do laço
        r = self.rodar(tmux_dentro=True, XDG_STATE_HOME="relativo")
        self.assertEqual(r.returncode, 2)
        self.assertEqual(self.execucoes(), [])

    def test_reabertura_de_conversa_ja_existente_nao_duplica_continue(self):
        pasta = self.home / ".claude/projects" / str(self.home / "Forge").replace("/", "-")
        pasta.mkdir(parents=True)
        self.saidas(137, 0)
        self.rodar(tmux_dentro=True, FORGE_QUEDA_ESPERA="0")
        for e in self.execucoes():
            self.assertEqual(e.split().count("--continue"), 1, e)

    def test_sem_conversa_a_reabertura_poe_o_continue(self):
        self.saidas(137, 0)
        self.rodar(tmux_dentro=True, FORGE_QUEDA_ESPERA="0")
        primeira, segunda = self.execucoes()
        self.assertNotIn("--continue", primeira.split())
        self.assertIn("--continue", segunda.split())
        self.assertIn("projeto=Forge-dev", self.quedas()[0])


class ArquivoComum(unittest.TestCase):
    """O resolver e o supervisor vivem num arquivo só (scripts/jarvis-comum.sh); os dois atalhos o carregam e não o copiam."""

    FUNCOES = ("resolver_claude()", "registrar_queda()", "supervisionar()")

    def test_funcoes_so_no_arquivo_comum(self):
        comum = (RAIZ / "scripts" / "jarvis-comum.sh").read_text(encoding="utf-8")
        for f in self.FUNCOES:
            self.assertEqual(comum.count(f + " {"), 1, f)
        for nome in ("jarvis", "jarvis-forge"):
            texto = (RAIZ / "scripts" / nome).read_text(encoding="utf-8")
            with self.subTest(nome=nome):
                self.assertIn("jarvis-comum.sh", texto)
                for f in self.FUNCOES:
                    self.assertNotIn(f, texto, f"{nome} copia {f}")

    def test_os_dois_scripts_passam_pelo_supervisor_e_pelo_binario_resolvido(self):
        for nome in ("jarvis", "jarvis-forge"):
            texto = (RAIZ / "scripts" / nome).read_text(encoding="utf-8")
            with self.subTest(nome=nome):
                self.assertIn('supervisionar "${args[@]}"', texto)
                self.assertIn('exec "$claude_bin" "${args[@]}"', texto)
                self.assertNotRegex(texto, r"(?m)^\s*(exec )?claude \"\$\{args", "chamada direta ao claude do PATH")
                self.assertNotIn("\nif claude plugin list", texto)

    def test_readme_diz_como_encerrar_de_vez(self):
        readme = (RAIZ / "README.md").read_text(encoding="utf-8")
        self.assertIn("tmux kill-session -t jarvis-<projeto>", readme)
        self.assertIn("143", readme)


if __name__ == "__main__":
    unittest.main()
