from typing import Optional, List, Dict
from beaupy import select_multiple
import adbutils

class AdbConnector:
    def __init__(self, tui) -> None:
        self.tui = tui
        self.client = adbutils.AdbClient()
        self.deviceslist = self._list_devices()
        self.device = None

    def _list_devices(self) -> List[Dict[str, str]]:
        return [
            {'serial': device.serial, 'model': device.prop.model}
            for device in self.client.device_list()
        ]

    def _select_device(self) -> Optional[Dict[str, str]]:
        if not self.deviceslist:
            try:
                self.tui.print('No devices connected, waiting for device...')
                self.client.wait_for(state='device')
                return self._list_devices()
            except adbutils.AdbTimeout as timeout:
                self.tui.print('Timeout connecting to any devices')
                raise SystemExit() from timeout
            except KeyboardInterrupt as ki:
                self.tui.print('Aborted!')
                raise SystemExit() from ki

        elif len(self.deviceslist) == 1:
            return self.deviceslist
        else:
            self.tui.print('Multiple devices connected:')
            devices_model = [f"{device['model']}" for device in self.deviceslist]
            selected_device = select_multiple(devices_model, maximal_count=1)

            return [device for device in self.deviceslist if device['model'] == selected_device[0]]

    def connect(self) -> None:
        device = self._select_device()[0]
        self.tui.clear()
        if device:
            self.device = self.client.device(serial=device['serial'])
            self.tui.print(f"Successfully connected to device: {device['serial']}")
        else:
            self.disconnect()

    def disconnect(self) -> None:
        self.client.server_kill()

    def list_apps(self) -> List[str]:
        return self.device.list_packages()

    def remove_app(self, app_id) -> None:
        result = self.device.shell2(['pm', 'uninstall', '--user', '0', app_id])
        if result.returncode != 0:
            self.tui.print(f"Failed uninstalling app {app_id}")
            self.tui.print(result.output)
            raise SystemExit()
