"""Constants"""

import socket
import pkg_resources

HOST = socket.gethostname()
FQDN = socket.getfqdn()
APP_NAME = __package__
VERSION = pkg_resources.get_distribution(APP_NAME).version
