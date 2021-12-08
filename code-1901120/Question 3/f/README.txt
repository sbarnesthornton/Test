I have fully tested that this program works on Python 3.8.10 (my home computer)
It also works on the lab machines running Python 3.6.8 as long as the cfb binary compiled for lab machines is included in the same folder.

The python program implements the attack in question 3(e)
It should be run using 'Python3 cfb_attack.py -h' to get instructions

DEPENDENCIES:
subprocess (Should be installed by default but if not: pip3 install subprocess)
argparse (Should be installed by default but if not: pip3 install subprocess)
sys (Should definitely be installed by default)

IMPORTANT:
The file must have the cfb coursework binary in the same file to work, if it is run in my code archive as submitted this should work fine. This binary is the one Francois uploaded to teams that works on my WSL ubuntu subsystem. This may have to be changed to the one in the original coursework files in order for it to work on the lab machines.