import subprocess
import argparse
import sys

'''
IMPORTANT:
This program must be run with the coursework file 'cfb' in the same folder.
By default, it will attack the ciphertext in the question but it will also
decrypt any ciphertexts encrypted with the same fixed nonce.
'''


def error(string):
    """
    Prints an error to stderr and cleanly exits the program
    :param string: Error description
    :return: Nothing
    """
    print("Error: " + string, file=sys.stderr)
    exit(0)


def ascii_to_hex(string):
    """
    Converts an ASCII string to a hexadecimal encoding
    :param string: String to be encoded
    :return: Hexadecimal encoding
    """
    new = ""
    for c in string:
        new = new + format(ord(c), "x")
    try:
        assert(len(new) == len(string) * 2)
    except AssertionError:
        error("Problem converting ascii to hex")
    return new


def hex_to_ascii(string):
    """
        Converts a hexadecimal encoded string to ASCII characters
        :param string: Hexadecimal string
        :return: String of ASCII characters
        """
    new = ""
    for i in range(0, int(len(string)/2)):
        new = new + chr(int(string[2*i] + string[2*i + 1], 16))
    try:
        assert(len(new) == len(string)/2)
    except AssertionError:
        error("Problem converting hex to ascii")
    return new


def parse_cipher(c_string, enc_n):
    """
    Splits ciphertext into blocks
    Truncates nonce if ciphertext is smaller than a block
    :param c_string: Ciphertext
    :param enc_n: Encryption of nonce
    :return: Split ciphertext and correct length encrypted nonce
    """
    c = []
    for i in range(0, len(c_string), 32):
        c.append(c_string[i:i+32])
    if len(c[0]) < 32:
        enc_n = enc_n[:len(c[0])]
        try:
            assert(len(enc_n) == len(c[0]))
        except AssertionError:
            error("Program was not able to parse ciphertext correctly")
    return c, enc_n


def attack(c, enc_n):
    """
    Runs the attack as described in question 3(e)
    Uses subprocess to run encryption oracle
    :param c: Ciphertext
    :param enc_n: Encryption of nonce
    :return: Plaintext
    """
    p = []
    p.append(str(hex(int(c[0], 16) ^ int(enc_n,16)))[2:])
    for i in range (len(c) - 1):
        m = str(hex(int(c[i], 16) ^ int(enc_n, 16)))[2:] + "61" * 16
        enc_m = subprocess.run(["./cfb", "749c5b51a5785234", bytes.fromhex(m)], stdout=subprocess.PIPE, universal_newlines=True).stdout
        enc_ci = (str(hex(int(m[32:], 16) ^ int(enc_m[32:], 16)))[2:])
        # Ensures that the xor doesn't remove leading zeros
        while len(enc_ci) < 32:
            enc_ci = "0" + enc_ci
        if len(c[i+1]) < 32:
            enc_ci = enc_ci[:len(c[i+1])]
        p.append(str(hex(int(c[i+1],16)^int(enc_ci,16)))[2:])
    return ''.join(hex_to_ascii(s) for s in p)


def test_cipher(c_string,p_string, enc_n):
    """
    Tests that parse_cipher will deal with the inputted ciphertext correctly
    :param c_string: Ciphertext
    :param p_string: Plaintext
    :param enc_n: Encryption of nonce
    :return: Nothing
    """
    c = []
    c, enc_n = parse_cipher(c_string, enc_n)
    try:
        assert(attack(c, enc_n) == p_string)
    except AssertionError:
        error("Ciphertext " + c_string + " could not be decrypted correctly")


def tests(enc_n):
    """
    Runs tests on different test-cases
    :param enc_n: Encryption of nonce
    :return: Tests pass confirmation
    """
    test_cipher("d9d5fdaf3ec710ffcbedcc541a86579a2d75f8103c", "hello my name is jeff", enc_n)
    test_cipher("d9dfe6a728","howdy",enc_n)
    test_cipher("c0", "q", enc_n)
    test_cipher("edc8a2", "\\x3", enc_n)
    return "All tests pass"

p = []

# Encryption of nonce is hardcoded as this attack is applicable to one fixed nonce
pp = "62636365613531313038326331633233"
cp = "d3d3f2a630d24cb7dbbb9f5a4ec50cda"
enc_n = str(hex(int(pp, 16) ^ int(cp, 16)))[2:]

parser = argparse.ArgumentParser(description='Attacks AES256-CFB using fixed nonce: 749c5b51a5785234')
parser.add_argument('--ciphertext', '-c', type=str, dest='cipher', default="e5d8e3a634c710e792a3c65c1ad61e88dc0febbe5f5b07a2c3efae20bcacd3e0a76166fd28c4ca17dcbc1b6610c79c0944", help="Ciphertext to be decrypted in attack, must be encrypted using fixed nonce above (default: c_cfb given in coursework)")
parser.add_argument('--test', '-t', dest='run_tests', action='store_true', help="Flag to run tests, overrides all other flags")
parser.set_defaults(run_tests=False)
args = parser.parse_args()
c =[]
if not args.run_tests:
    c, enc_n = parse_cipher(args.cipher, enc_n)
    p = attack(c, enc_n)
    print(p)
else:
    print(tests(enc_n))

