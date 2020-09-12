import os
import subprocess
import time

from utilities import CommandExecutionFailed


class MetamapServerManager(object):
    def __init__(self):
        self.__metamap_bin_path = os.path.join(os.environ.get('METAMAP_DIR'), 'bin')
        self.__servers_running = False

    def start_servers(self, wait_time: int = 60):
        if not self.__servers_running:
            print("Starting METAMAP servers")
            self._start_server('skrmedpostctl')
            self._start_server('wsdserverctl')
            time.sleep(wait_time)
            self.__servers_running = True
            print("METAMAP servers started")

    def stop_servers(self):
        if self.__servers_running:
            print("Stopping METAMAP servers")
            self._stop_server('skrmedpostctl')
            self._stop_server('wsdserverctl')
            self.__servers_running = False
            print("METAMAP servers stopped")

    def _start_server(self, server_name: str):
        self._run_server_command(server_name, 'start')

    def _stop_server(self, server_name: str):
        self._run_server_command(server_name, 'stop')

    def _run_server_command(self, server_name: str, command: str):
        try:
            subprocess.run([os.path.join(self.__metamap_bin_path, server_name), command])
        except subprocess.CalledProcessError as e:
            raise CommandExecutionFailed(e.output)
