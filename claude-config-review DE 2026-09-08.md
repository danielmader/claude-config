# Bewertung von Simon Blauths claude-config

Datum: 2026-09-08
Prüfer: Claude, auf dem Rechner von Daniel Mader
Umfang: alle Skills, Patches, cc.py, settings.json, CLAUDE.md; Prüfung mit Netzzugriff ausgeführt
Stand: auf diesem Rechner ist nichts installiert oder verändert

## Fazit

Das Paket ist gut gemacht und lohnt sich. Vor dem Installieren müssen aber ein paar Dinge geklärt werden.

## Was cc.py wirklich macht

Es synchronisiert nicht über git. Es hat drei getrennte Aufgaben:

- **vendor** holt die Skills aus fremden GitHub-Repos (superpowers, mattpocock, pstack, JuliusBrussee), kopiert sie unter Simons eigenen Namen nach `skills/`, wendet seine Patches an und merkt sich den Commit und eine Prüfsumme in `sources.tsv`.
- **install** kopiert `skills/`, `rules/`, `CLAUDE.md` und eine angepasste `settings.json` nach `~/.claude`. Reine Kopien, keine Symlinks, darum läuft es auch unter Windows.
- **check** meldet Abweichungen in drei Richtungen und ändert nichts. Es prüft: Repo hat lokale Änderungen oder ist hinter origin, installierte Dateien weichen vom Repo ab, ein fremdes Skill-Repo hat sich weiterbewegt. Läuft einmal am Tag beim Start von Claude Code.

Der Austausch zwischen Daniel und Simon läuft über normales git push und pull.

## Was gut ist

- **cc.py** ist sauber geschrieben: Dataclasses, Typannotationen, kleine Funktionen. Es ändert nie etwas von selbst. Das passt zu den Regeln in Daniels eigener CLAUDE.md.
- **Die Prüfung mit Netzzugriff** zeigt keine Abweichung. Alle 18 Skills sind auf dem aktuellen Stand ihrer Quelle.
- **Die Skills sind hochwertig.** Die Schreib-Skills (unslop, technical-writing, writing-for-agents) sind dicht und nützlich. systematic-debugging und verification-before-completion sind solide. Die schweren Skills (deslopify, prune-docs, improve-codebase-architecture) laufen nur auf Befehl und kosten sonst keinen Kontext.
- **Die zentrale CLAUDE.md** ist durchdacht. Besonders die Abschnitte "Probleme melden statt umgehen" und "keine unbelegten Behauptungen in Doku" sind Regeln, die in jedes Projekt gehören.

## Probleme, die vor dem Installieren gelöst werden müssen

1. **Install überschreibt Daniels eigene Konfiguration.** Seine `~/.claude/CLAUDE.md` (die Regeln zu find/xargs und git -C) und seine ganze Berechtigungsliste (die `git -C`-Formen, Windows-Lesepfade, pytest-Befehle, `switchModelsOnFlag`) stehen nirgends im Repo. Nur `model` und `effortLevel` überleben. Die Shell-Regeln vorher nach `~/.claude/rules/shell.md` verschieben. Diesen Ordner lässt install in Ruhe. Oder sie Simon für die gemeinsame CLAUDE.md vorschlagen, sie sind allgemein genug. Die README sagt selbst, dass es für settings.json keine lokale Überschreibung gibt. Das ist die echte Lücke, wenn zwei Leute ein Repo teilen.

2. **settings.json enthält Simons persönliche Vorlieben.** Sie verbietet `pwsh` und `powershell.exe`, was unter Windows stören kann, und `az`. Sie erzwingt Vollbild-TUI, schaltet das automatische Gedächtnis ab und entfernt den Co-Authored-By-Eintrag in Commits. Entscheiden, was davon gewollt ist.

3. **Die Zusammenarbeit ist noch nicht geregelt.** Daniels Klon zeigt direkt auf Simons GitHub-Repo. Jeder lokale Commit wird täglich als "nicht gepusht" gemeldet, und pushen ist nicht möglich. Entweder forken und Simons Repo als upstream eintragen, oder vereinbaren, dass nur gepullt wird.

4. **Die zentrale CLAUDE.md enthält Aussagen, die nur für Simon gelten.** Sie behauptet, GPG-Signieren sei eingerichtet. In Daniels git-Konfiguration ist es nicht eingerichtet. Sie erwähnt auch `glab` und Azure.

5. **Install mit dem System-Python ausführen.** Auf diesem Rechner zeigt `python3` auf `~/devel/.venv/bin/python3`. Der Hook-Befehl würde dann von diesem venv abhängen. Die `.claude/CLAUDE.md` des Repos warnt genau davor.

## Ermessensfragen

- **tdd ist streng.** "Kein Produktionscode ohne vorher fehlschlagenden Test. Code zuerst geschrieben? Löschen." Die Beispiele sind TypeScript und npm. Für PyQt-GUIs in beam_analyzer und ruby_array ist Test-zuerst bei Widgets oft unpraktisch. Der Skill erlaubt Ausnahmen auf Nachfrage, aber die CLAUDE.md schickt jede Implementierung dorthin. Das sollte mit Simon besprochen werden.
- **reflect hat lose Enden.** Es verweist auf `plugin-dev:skill-development` und `encode-lessons-in-structure`, die beide nicht mitgeliefert sind. Die Prüfung auf tote Verweise in cc.py erkennt diese Schreibweise nicht. Es braucht `node`, das auf diesem Rechner fehlt. Und es sagt, Backlog-Einträge würden "automatisch" in einen Tracker geschrieben. Das widerspricht der eigenen Regel des Repos, nie ungefragt auf Remotes zu schreiben.
- **Fremder Ballast wird mitinstalliert.** Die `agents/openai.yaml`-Dateien und die `test-pressure-*.md` in systematic-debugging sind Codex-Metadaten und Testdateien der Quelle. Harmlos und nicht im Kontext geladen, landen aber in `~/.claude/skills`.
- **cc.py hat keine Tests.** Das passt schlecht zu einer CLAUDE.md, die TDD vorschreibt.

## Nächste Schritte

Fork oder nur pullen entscheiden, und was mit den bestehenden Regeln passiert. Danach die Datei in `~/.claude/rules/` anlegen und install mit `/usr/bin/python3` ausführen.
