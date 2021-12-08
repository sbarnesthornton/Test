I have fully tested that this program works on Python 3.8.10 (my home computer)
It also works on the lab machines as long as a virtual environment is used to install the required dependencies and the python program is allowed to read files in the same location as itself.

The python program implements my Encrypt-then-MAC operation designed in question 4 of the coursework.
It should be run using 'Python3 auth_encryption.py -h' to get instructions.

DEPENDENCIES:
PyCryptoDome (needs to be installed in a virtual environment using pip3 install pycryptodome)
base64 (installed by default on lab machines but can be installed using pip)
hashlib (installed by default on lab machines but can be installed using pip)
hmac (installed by default on lab machines but can be installed using pip)
argparse (installed by default on lab machines but can be installed using pip)
sys (installed by default on lab machines but can be installed using pip)