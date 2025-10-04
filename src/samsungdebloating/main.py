from typing import List

from rich.console import Console
from beaupy import Config, select_multiple

from .adb_connector import AdbConnector
from .bloatware_detector import BloatwareDetector


Config.raise_on_interrupt = True


def _uninstall_selected_apps(
    tui: Console,
    connector: AdbConnector,
    detector: BloatwareDetector,
    selected_apps: List[str],
) -> None:
    tui.clear()
    for app_name in selected_apps:
        app_id = detector.get_app_id(app_name)
        if not app_id:
            tui.print(f"Skipping {app_name}: package identifier not found.")
            continue
        success, raw_output = connector.remove_app(app_id)
        if success:
            tui.print(f"Uninstalled {app_name}")
        else:
            tui.print(
                f"Failed to uninstall {app_name} ({app_id}): {raw_output}"
            )
    tui.print('Finished processing selected apps.')


def main() -> None:
    tui = Console()
    connector = AdbConnector(tui)
    detector = BloatwareDetector()

    device_info = connector.connect()
    installed_apps = connector.list_apps()

    bloatware_detected = detector.compare_installed_apps(installed_apps)
    if not bloatware_detected:
        tui.print('No known bloatware detected on the device.')
        return

    connection_message = (
        f"Successfully connected to {device_info['model']} ({device_info['serial']})"
    )
    tui.clear()
    tui.print(connection_message)
    tui.print('Select apps to remove (press ESC to cancel):')
    try:
        selected_apps = select_multiple(
            bloatware_detected,
            pagination=True,
            page_size=20,
        )
    except KeyboardInterrupt:
        tui.print('Operation cancelled.')
        return

    if not selected_apps:
        tui.print('No apps selected. Nothing was uninstalled.')
        return

    _uninstall_selected_apps(tui, connector, detector, selected_apps)


if __name__ == "__main__":
    main()
