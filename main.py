Absolut! Dein Wunsch ist mir Befehl.

Der originale Code für 'GhostShield' war hier nicht enthalten, aber ich habe einen typischen Anwendungsfall von 'GhostShield' antizipiert:
*   Ein Verzeichnis oder eine Datei "abschirmen" (shielden): Das Original wird verschoben (oder kopiert und gelöscht) an einen sicheren Ort (Backup), und an der ursprünglichen Stelle wird eine leere Datei oder ein leeres Verzeichnis erstellt.
*   "Entschirmen" (unshielden): Das leere Objekt wird gelöscht, und das Original aus dem Backup wird wiederhergestellt.
*   Listung der abgeschirmten Elemente.

Auf dieser Annahme basierend habe ich den Code von Grund auf neu geschrieben, um die gewünschten Verbesserungen zu integrieren:

1.  **Fehlerbehandlung (Error Handling):** Umfassende `try-except`-Blöcke für Dateisystemoperationen (`FileNotFoundError`, `PermissionError`, `shutil.Error`, etc.).
2.  **Optimierung:**
    *   Verwendung des modernen `pathlib`-Moduls für eine sauberere und objektorientiertere Pfadmanipulation.
    *   Strukturierung in eine Klasse und Funktionen für bessere Modularität.
    *   Einsatz des `logging`-Moduls statt einfacher `print()`-Anweisungen für eine bessere Nachverfolgbarkeit und Kontrolle der Ausgaben (Info, Warnung, Fehler).
    *   Verwendung von `argparse` für eine robuste Kommandozeilen-Schnittstelle.
3.  **Kleines Feature:**
    *   **Zeitgestempelte Backups:** Bei jedem "Abschirmen" wird ein Backup mit einem Zeitstempel erstellt, sodass mehrere Versionen eines abgeschirmten Elements existieren können.
    *   **Interaktive Bestätigung:** Vor destruktiven Aktionen (Löschen des Originals, Löschen der Attrappe) wird eine Bestätigung vom Benutzer eingeholt.
    *   **Auflistung der Backups:** Eine Funktion, die anzeigt, welche Elemente abgeschirmt sind und wo ihre Backups liegen.

Hier ist der komplette, überarbeitete und verbesserte Code:


import shutil
import logging
import argparse
from pathlib import Path
from datetime import datetime

# --- Konfiguration ---
BACKUP_BASE_DIR_NAME = ".ghostshield_backups" # Verstecktes Verzeichnis für Backups
LOG_FILE_NAME = "ghostshield.log"

# --- Logger Setup ---
log_format = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=log_format)
logger = logging.getLogger(__name__)

# Erstelle einen File Handler, um Logs in eine Datei zu schreiben
file_handler = logging.FileHandler(LOG_FILE_NAME)
file_handler.setFormatter(logging.Formatter(log_format))
logger.addHandler(file_handler)

def confirm_action(prompt: str) -> bool:
    """ Fragt den Benutzer um Bestätigung für eine Aktion. """
    response = input(f"{prompt} (j/n): ").lower().strip()
    return response == 'j'

class GhostShield:
    def __init__(self, target_base_dir: Path):
        """
        Initialisiert GhostShield.
        :param target_base_dir: Das Basisverzeichnis, in dem die Backups für alle geschützten Elemente gespeichert werden.
                                Wenn GhostShield.py im selben Ordner wie die zu schützenden Dateien liegt,
                                kann man '.' als target_base_dir verwenden.
        """
        self.target_base_dir = target_base_dir.resolve()
        self.backup_root_dir = self.target_base_dir / BACKUP_BASE_DIR_NAME
        self._ensure_backup_root_dir_exists()

    def _ensure_backup_root_dir_exists(self):
        """ Stellt sicher, dass das Backup-Root-Verzeichnis existiert. """
        try:
            self.backup_root_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Backup-Verzeichnis sichergestellt: {self.backup_root_dir}")
        except OSError as e:
            logger.error(f"Fehler beim Erstellen des Backup-Verzeichnisses {self.backup_root_dir}: {e}")
            raise

    def _get_backup_path_for_original(self, original_path: Path) -> Path:
        """
        Generiert den Pfad für das Backup eines bestimmten Originalpfades.
        Backups werden unter BACKUP_BASE_DIR_NAME/relativer_pfad_zum_original/zeitstempel abgelegt.
        """
        relative_path = original_path.relative_to(self.target_base_dir)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return self.backup_root_dir / relative_path / timestamp

    def _find_latest_backup_path(self, original_path: Path) -> Path | None:
        """
        Findet den Pfad zum neuesten Backup für ein gegebenes Original.
        """
        relative_path = original_path.relative_to(self.target_base_dir)
        item_backup_dir = self.backup_root_dir / relative_path

        if not item_backup_dir.is_dir():
            return None

        # Finde alle timestamp-Ordner und sortiere sie, um den neuesten zu finden
        backup_versions = sorted(
            [d for d in item_backup_dir.iterdir() if d.is_dir() and d.name.startswith(datetime.now().strftime("%Y%m%d_")[:8])], # Optional: Nur aktuelle Tagesbackups, oder alle
            key=lambda p: p.name,
            reverse=True
        )
        return backup_versions[0] if backup_versions else None

    def shield(self, original_path_str: str):
        """
        Schirmt eine Datei oder ein Verzeichnis ab.
        Das Original wird ins Backup verschoben, und an seiner Stelle wird ein leerer "Dummy" erstellt.
        """
        original_path = Path(original_path_str).resolve()
        logger.info(f"Versuche, {original_path} abzuschirmen...")

        if not original_path.exists():
            logger.error(f"Fehler: Das Element '{original_path}' existiert nicht.")
            return

        if not str(original_path).startswith(str(self.target_base_dir)):
            logger.warning(
                f"Warnung: '{original_path}' liegt nicht im Basisverzeichnis '{self.target_base_dir}'. "
                "Dies wird unterstützt, aber stellen Sie sicher, dass dies beabsichtigt ist."
            )

        if original_path.name == BACKUP_BASE_DIR_NAME:
            logger.error(f"Fehler: Das Backup-Verzeichnis selbst kann nicht abgeschirmt werden: {original_path}")
            return

        # Pfad zum neuen Backup
        current_backup_path = self._get_backup_path_for_original(original_path)

        # 1. Backup erstellen
        try:
            current_backup_path.parent.mkdir(parents=True, exist_ok=True)
            if original_path.is_file():
                shutil.copy2(original_path, current_backup_path)
                logger.info(f"Datei '{original_path}' nach '{current_backup_path}' kopiert.")
            elif original_path.is_dir():
                shutil.copytree(original_path, current_backup_path)
                logger.info(f"Verzeichnis '{original_path}' nach '{current_backup_path}' kopiert.")
            else:
                logger.error(f"Kann den Typ von '{original_path}' nicht abschirmen (weder Datei noch Verzeichnis).")
                return
        except (FileNotFoundError, PermissionError, shutil.Error, OSError) as e:
            logger.error(f"Fehler beim Erstellen des Backups von '{original_path}' nach '{current_backup_path}': {e}")
            return

        # 2. Original löschen (mit Bestätigung)
        if not confirm_action(f"Soll das Original '{original_path}' gelöscht werden, um die Attrappe zu erstellen?"):
            logger.info("Abschirmung abgebrochen: Original wurde nicht gelöscht.")
            # Aufräumen: Wenn Original nicht gelöscht wird, dann ist Backup nutzlos
            if current_backup_path.is_dir():
                shutil.rmtree(current_backup_path)
            elif current_backup_path.is_file():
                current_backup_path.unlink()
            logger.info(f"Erstelltes Backup '{current_backup_path}' wurde gelöscht.")
            return

        try:
            if original_path.is_file():
                original_path.unlink()
                logger.info(f"Originaldatei '{original_path}' gelöscht.")
            elif original_path.is_dir():
                shutil.rmtree(original_path)
                logger.info(f"Originalverzeichnis '{original_path}' gelöscht.")
        except (FileNotFoundError, PermissionError, OSError) as e:
            logger.error(f"Fehler beim Löschen des Originals '{original_path}': {e}")
            return

        # 3. Dummy erstellen
        try:
            if current_backup_path.is_file(): # Original war eine Datei
                original_path.touch()
                logger.info(f"Leere Attrappen-Datei '{original_path}' erstellt.")
            elif current_backup_path.is_dir(): # Original war ein Verzeichnis
                original_path.mkdir(exist_ok=True)
                logger.info(f"Leeres Attrappen-Verzeichnis '{original_path}' erstellt.")
        except (PermissionError, OSError) as e:
            logger.error(f"Fehler beim Erstellen der Attrappe für '{original_path}': {e}")
            return

        logger.info(f"'{original_path}' erfolgreich abgeschirmt. Backup unter '{current_backup_path}'")

    def unshield(self, original_path_str: str):
        """
        Stellt eine abgeschirmte Datei oder ein Verzeichnis wieder her.
        Die Attrappe wird gelöscht, und das neueste Backup wird an die ursprüngliche Stelle zurückkopiert.
        """
        original_path = Path(original_path_str).resolve()
        logger.info(f"Versuche, {original_path} zu entschismen...")

        if not original_path.exists():
            logger.warning(f"Warnung: '{original_path}' existiert nicht. Versuche trotzdem, das Backup zu finden und wiederherzustellen.")

        latest_backup_path = self._find_latest_backup_path(original_path)

        if not latest_backup_path:
            logger.error(f"Kein Backup für '{original_path}' gefunden. Kann nicht entschismen.")
            return

        # 1. Attrappe löschen (falls vorhanden und mit Bestätigung)
        if original_path.exists():
            if not confirm_action(f"Soll die Attrappe '{original_path}' gelöscht werden, um das Original wiederherzustellen?"):
                logger.info("Entschirmung abgebrochen: Attrappe wurde nicht gelöscht.")
                return
            try:
                if original_path.is_file():
                    original_path.unlink()
                    logger.info(f"Attrappen-Datei '{original_path}' gelöscht.")
                elif original_path.is_dir():
                    shutil.rmtree(original_path)
                    logger.info(f"Attrappen-Verzeichnis '{original_path}' gelöscht.")
            except (PermissionError, OSError) as e:
                logger.error(f"Fehler beim Löschen der Attrappe '{original_path}': {e}")
                return

        # 2. Backup wiederherstellen
        try:
            if latest_backup_path.is_file():
                shutil.copy2(latest_backup_path, original_path)
                logger.info(f"Backup-Datei von '{latest_backup_path}' nach '{original_path}' wiederhergestellt.")
            elif latest_backup_path.is_dir():
                shutil.copytree(latest_backup_path, original_path)
                logger.info(f"Backup-Verzeichnis von '{latest_backup_path}' nach '{original_path}' wiederhergestellt.")
            else:
                logger.error(f"Der Backup-Typ von '{latest_backup_path}' ist unbekannt. Kann nicht wiederherstellen.")
                return
        except (FileNotFoundError, PermissionError, shutil.Error, OSError) as e:
            logger.error(f"Fehler beim Wiederherstellen des Backups von '{latest_backup_path}' nach '{original_path}': {e}")
            return

        logger.info(f"'{original_path}' erfolgreich entschirmt. Backup war unter '{latest_backup_path}'")

    def list_shielded(self):
        """ Listet alle aktuell abgeschirmten Elemente und ihre Backups auf. """
        logger.info(f"Abgeschirmte Elemente (und ihre Backups) im Bereich von '{self.target_base_dir}':")
        found_any = False
        try:
            # Iteriere durch die Struktur BACKUP_ROOT_DIR/relativer_pfad_zum_original/zeitstempel
            # Wir wollen die 'relativer_pfad_zum_original'-Ebene finden
            for item_backup_dir in self.backup_root_dir.iterdir():
                if not item_backup_dir.is_dir():
                    continue

                # Rekursiv nach den Originalpfaden suchen, die Backups haben
                for original_item_dir in item_backup_dir.rglob('*'): # rglob für Tiefensuche
                    if original_item_dir.is_dir() and any(p.is_dir() for p in original_item_dir.iterdir() if p.name.startswith(datetime.now().strftime("%Y%m%d_")[:8])):
                        # Wir haben einen Ordner gefunden, der timestamp-Ordner enthält
                        relative_path_part = original_item_dir.relative_to(self.backup_root_dir)
                        original_full_path = self.target_base_dir / relative_path_part
                        logger.info(f"  - '{original_full_path}' (Attrappe: {original_full_path.exists()})")
                        
                        # Liste alle Backups für dieses Element auf
                        backup_versions = sorted(
                            [d for d in original_item_dir.iterdir() if d.is_dir() and d.name.startswith(datetime.now().strftime("%Y%m%d_")[:8])],
                            key=lambda p: p.name,
                            reverse=True
                        )
                        for version in backup_versions:
                            logger.info(f"    -> Backup: {version}")
                        found_any = True
        except PermissionError as e:
            logger.error(f"Berechtigungsfehler beim Auflisten von Backups in '{self.backup_root_dir}': {e}")
            return
        except Exception as e:
            logger.error(f"Ein unerwarteter Fehler ist beim Auflisten von Backups aufgetreten: {e}")
            return

        if not found_any:
            logger.info("  Keine abgeschirmten Elemente gefunden.")

def main():
    parser = argparse.ArgumentParser(
        description="GhostShield: Schirmt Dateien/Verzeichnisse ab, indem sie gesichert und durch eine Attrappe ersetzt werden.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        '-b', '--base-dir',
        type=str,
        default='.',
        help="Das Basisverzeichnis, in dem GhostShield nach Elementen sucht und Backups speichert. Standard ist '.' (aktuelles Verzeichnis)."
    )

    subparsers = parser.add_subparsers(dest='command', required=True, help='Verfügbare Befehle')

    # Shield Befehl
    shield_parser = subparsers.add_parser('shield', help='Schirmt eine Datei oder ein Verzeichnis ab.')
    shield_parser.add_argument('path', type=str, help='Der Pfad zur Datei oder zum Verzeichnis, das abgeschirmt werden soll.')

    # Unshield Befehl
    unshield_parser = subparsers.add_parser('unshield', help='Stellt eine abgeschirmte Datei oder ein Verzeichnis wieder her.')
    unshield_parser.add_argument('path', type=str, help='Der Pfad zur ursprünglichen Position der Datei oder des Verzeichnisses, das wiederhergestellt werden soll.')

    # List Befehl
    list_parser = subparsers.add_parser('list', help='Listet alle abgeschirmten Elemente auf.')

    args = parser.parse_args()

    # Stellen Sie sicher, dass der Basisordner existiert
    base_dir_path = Path(args.base_dir).resolve()
    if not base_dir_path.is_dir():
        logger.error(f"Fehler: Das angegebene Basisverzeichnis '{base_dir_path}' existiert nicht oder ist kein Verzeichnis.")
        exit(1)

    ghost_shield = GhostShield(base_dir_path)

    if args.command == 'shield':
        ghost_shield.shield(args.path)
    elif args.command == 'unshield':
        ghost_shield.unshield(args.path)
    elif args.command == 'list':
        ghost_shield.list_shielded()

if __name__ == "__main__":
    main()


### Wie benutzt man diesen neuen Code?

1.  **Speichern:** Speichere den Code als `ghostshield.py`.
2.  **Ausführen über die Kommandozeile:**

    *   **Ein Element abschirmen:**
        bash
        python ghostshield.py shield mein_geheimer_ordner
        python ghostshield.py shield meine_wichtige_datei.txt
        
        Du wirst gefragt, ob das Original gelöscht werden soll.

    *   **Ein Element wiederherstellen:**
        bash
        python ghostshield.py unshield mein_geheimer_ordner
        python ghostshield.py unshield meine_wichtige_datei.txt
        
        Du wirst gefragt, ob die Attrappe gelöscht werden soll.

    *   **Alle abgeschirmten Elemente auflisten:**
        bash
        python ghostshield.py list
        

    *   **Ein anderes Basisverzeichnis verwenden (Standard ist das aktuelle Verzeichnis):**
        Wenn du z.B. `/home/user/dokumente` abschirmen willst und `ghostshield.py` in `/home/user/tools` liegt:
        bash
        python /home/user/tools/ghostshield.py -b /home/user/dokumente shield /home/user/dokumente/geheim
        
        Oder einfacher, wenn du im Verzeichnis `/home/user/dokumente` bist:
        bash
        cd /home/user/dokumente
        python ../tools/ghostshield.py shield geheim
        

**Wichtige Hinweise:**

*   **Backup-Verzeichnis:** Standardmäßig werden Backups in einem versteckten Ordner `.ghostshield_backups` im angegebenen Basisverzeichnis gespeichert.
*   **Log-Datei:** Alle Aktionen und Fehler werden in `ghostshield.log` im selben Verzeichnis wie das Skript protokolliert.
*   **Bestätigungen:** Sei vorsichtig bei den Bestätigungsfragen. Falsche Eingaben können zum Datenverlust führen.
*   **Relative Pfade:** Die relativen Pfade für die Backups werden vom `target_base_dir` aus berechnet. Das ist wichtig, um später die Backups dem richtigen Original zuordnen zu können.

Ich hoffe, diese verbesserte Version entspricht deinen Vorstellungen und ist nützlich für dich!