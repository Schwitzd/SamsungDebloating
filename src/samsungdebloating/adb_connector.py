from typing import List, Dict, Tuple
from beaupy import select
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

    def _select_device(self) -> Dict[str, str]:
        while True:
            self.deviceslist = self._list_devices()

            if not self.deviceslist:
                try:
                    self.tui.print('No devices connected. Waiting for device...')
                    self.client.wait_for(state='device')
                    continue
                except adbutils.AdbTimeout as timeout:
                    self.tui.print('Timeout connecting to any devices')
                    raise SystemExit() from timeout
                except KeyboardInterrupt as ki:
                    self.tui.print('Aborted!')
                    raise SystemExit() from ki

            if len(self.deviceslist) == 1:
                return self.deviceslist[0]

            self.tui.print('Multiple devices connected, select one:')
            options = [
                f"{index + 1}. {device['model']} ({device['serial']})"
                for index, device in enumerate(self.deviceslist)
            ]
            selected_index = select(options, return_index=True)

            if selected_index is None:
                self.tui.print('No device selected, aborting.')
                raise SystemExit()

            return self.deviceslist[selected_index]

    def connect(self) -> Dict[str, str]:
        device = self._select_device()
        self.device = self.client.device(serial=device['serial'])
        return device

    def disconnect(self) -> None:
        self.client.server_kill()

    def list_apps(self) -> List[str]:
        if not self.device:
            self.tui.print('No device connected. Please connect a device first.')
            raise SystemExit()
        return self.device.list_packages()

    def remove_app(self, app_id: str) -> Tuple[bool, str]:
        if not self.device:
            self.tui.print('No device connected. Please connect a device first.')
            raise SystemExit()
        result = self.device.shell2(['pm', 'uninstall', '--user', '0', app_id])
        output = result.output.strip()
        if result.returncode != 0:
            return False, output or 'Unknown failure'
        return True, output or 'Success'
