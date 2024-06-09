from rich.console import Console
from beaupy import select_multiple
from .adb_connector import AdbConnector
from .bloatware_detector import BloatwareDetector

def main():
    # Initialize console and adb connector
    tui = Console()
    connector = AdbConnector(tui)
    detector = BloatwareDetector()

    # Connect to the device and get the softwares
    connector.connect()
    apps = connector.list_apps()


    # Uninstall Bloatware apps
    bloatware_detected = detector.compare_installed_apps(apps)
    tui.print('Select apps to remove:')
    try:
        selected_apps = select_multiple(bloatware_detected, pagination=True, page_size=20)
    except KeyboardInterrupt as ki:
        raise SystemExit() from ki

    tui.clear()
    for remove_app in selected_apps:
        connector.remove_app(detector.get_app_id(remove_app))
    tui.print('Succesfully unistalled the selected apps')

if __name__ == "__main__":
    main()
