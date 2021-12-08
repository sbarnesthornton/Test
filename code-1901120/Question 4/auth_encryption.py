from Crypto import Random
from Crypto.Cipher import AES
import base64
import hashlib
import hmac
import argparse
import sys


KEY_SIZE = 256


def error(s):
    """
    Prints error string to stderr and exits program cleanly
    :param s: error string to be printed
    :return: Nothing
    """
    print("Error: " + s, file=sys.stderr)
    exit(0)


def pad(s):
    """
    Pads string to be used in AES-CBC
    :param s: String to be padded
    :return: Padded string
    """
    return s + (AES.block_size - len(s) % AES.block_size) * chr(AES.block_size - len(s) % AES.block_size)


def unpad(s):
    """
    Removes padding from string encrypted using AES-CBC
    :param s: Padded string
    :return: String without padding
    """
    return s[:-ord(s[len(s) - 1:])]


def read_key(f):
    """
    Reads in key from a file generated by kgen()
    :param f: filename to read key from
    :return: Key for encryption and nonce
    """
    file = open(f, "rb")
    k = file.readline()
    k = k[:len(k) - 1]
    try:
        assert(len(base64.b64decode(k)) == int(KEY_SIZE/8))
    except AssertionError:
        error("Incorrect key formatting")
    n = file.readline()
    try:
        assert (len(base64.b64decode(n)) == int(AES.block_size))
    except AssertionError:
        error("Incorrect key formatting")
    file.close()
    return k, n


def write_key(f, k, n):
    """
    Writes key to a file in correct format
    :param f: Filename (minus .key)
    :param k: Encryption key
    :param n: Nonce
    :return: Nothing
    """
    file = open(f + ".key", "wb")
    file.write(base64.b64encode(k))
    file.write(bytes("\n".encode('utf-8')))
    file.write(base64.b64encode(n))
    file.close()


def hkdf(ik):
    """
    Derives two keys from one system key so that the authenticated encryption scheme can have one key
    Ensures that authentication and encryption key are independent so security is not affected
    :param ik: Randomly generated system key
    :return: Encryption key and authentication key
    """
    salt = bytes([0] * 32)
    prk = hmac.new(salt, ik, digestmod=hashlib.sha256).digest()
    t = b""
    okm = b""
    for i in range(2):
        t = hmac.new(prk, t + bytes([1 + i]), digestmod=hashlib.sha256).digest()
        okm += t
    return okm[:32], okm[32:]


def get_keys(ik):
    """
    Gets encryption and authentication key from hkdf function
    Checks resulting keys for formatting errors
    :param ik: System key
    :return: Encryption key and authentication key
    """
    ke, ka = hkdf(ik)
    try:
        assert (len(ke) == int(KEY_SIZE / 8))
        assert (len(ka) == int(KEY_SIZE / 8))
        assert (not (ka == ke))
    except AssertionError:
        error("Something went wrong in key generation, please try again")
    return ke, ka


def kgen():
    """
    Randomly generates an encryption and an authentication key
    :return: Key for encryption and key for authentication, both byte strings
    """
    # Researched the best random function to use as this is important to the security of the scheme
    # Found that urandom and PyCryptoDome each had +s and -s so used PyCryptoDome to limit dependencies
    ik = Random.get_random_bytes(int(KEY_SIZE/8))
    return ik


def enc(ke, ka, n, m):
    """
    Uses encrypt-then-mac method to encrypt a message
    :param ke: Encryption key
    :param ka: Authentication key
    :param n: Nonce
    :param m: Message to be encrypted
    :return: Concatenation of ciphertext and MAC tag
    """
    # Pads message for CBC encryption
    pad_m = pad(m)
    try:
        assert(len(pad_m) % AES.block_size == 0)
    except AssertionError:
        error("A problem occurred in padding for encryption, please try again")
    cipher = AES.new(ke, AES.MODE_CBC, n)
    c = cipher.encrypt(pad_m.encode('utf-8'))
    tag = hmac.new(ka, c, digestmod=hashlib.sha256)
    return c + tag.digest()


def dec(ke, ka, n, c):
    """
    Performs the decryption of an encrypt-then-mac scheme
    :param ke: Encryption key
    :param ka: Authentication key
    :param n: Nonce
    :param c: Ciphertext of form Ciphertext || Tag
    :return: Plaintext string or None if tag is not valid
    """
    # Uses list comprehension to separate tag and ciphertext
    t = c[len(c) - 32:]
    c = c[:len(c) - 32]
    tag = hmac.new(ka, c, digestmod=hashlib.sha256).digest()
    cipher = AES.new(ke, AES.MODE_CBC, n)
    # Ensures encryption is authenticated before decrypting the message
    if tag == t:
        plain_text = cipher.decrypt(c)
        plain_text = plain_text.decode('utf-8')
        return unpad(plain_text)
    else:
        return None


def test_string(s):
    """
    Tests the definition of the scheme: dec(enc(plaintext)) == plaintext
    :param s: Plaintext
    :return: Nothing
    """
    sk = kgen()
    n = Random.new().read(AES.block_size)
    ke, ka = get_keys(sk)
    c = enc(ke, ka, n, s)
    try:
        assert (dec(ke, ka, n, c) == s)
    except AssertionError:
        error("Encryption/decryption failed for plaintext " + s)


def test_unauth(s):
    """
    Tests that dec correctly identifies a forged tag
    :param s: Plaintext to simulate test
    :return: Nothing
    """
    sk = kgen()
    n = Random.new().read(AES.block_size)
    ke, ka = get_keys(sk)
    c = enc(ke, ka, n, s)
    # Changes tag to random string so that it shouldn't decrypt message
    c = c[:len(c) - 32] + Random.get_random_bytes(32)
    try:
        assert (dec(ke, ka, n, c) is None)
    except AssertionError:
        error("Program incorrectly authenticates an encrypted message")


def tests():
    """
    Runs tests to check that the scheme works as defined
    :return: Nothing
    """
    test_string("hello world")
    test_string("123456")
    test_string("")
    test_unauth("hello world")
    return "All tests passed"


parser = argparse.ArgumentParser(description='Nonce-based authenticated encryption system')
parser.add_argument('mode', type=str, help="Mode for scheme: enc to encrypt, dec to decrypt, kgen to generate key, test to run tests")
parser.add_argument('--plaintext', '-p', type=str, dest='plaintext', help='Plaintext to be encrypted')
parser.add_argument('--ciphertext', '-c', type=str, dest='ciphertext', help='File containing ciphertext: filename.txt')
parser.add_argument('--name', '-n', type=str, dest='key_name', help='Name for key file', default='keys')
parser.add_argument('--keys', '-k', type=str, dest='keys', help='File where the key and nonce are stored: filename.key')
args = parser.parse_args()

mode = args.mode
if mode == "enc":
    # Deals with incorrect input
    if args.plaintext is None:
        error("A plaintext is required to be encrypted")
    plaintext = args.plaintext
    if args.keys is None:
        error("Key file is required")
    system_key, nonce = read_key(args.keys)
    key_encrypt, key_auth = get_keys(base64.b64decode(system_key))
    cipher_text = enc(key_encrypt, key_auth, base64.b64decode(nonce), plaintext)
    file = open("ciphertext.txt", "wb")
    file.write(base64.b64encode(cipher_text))
    file.close()
    print("Ecnrypted message outputted to ciphertext.txt")

elif mode == "kgen":
    if args.key_name is None:
        error("File name for key is required")
    system_key = kgen()
    nonce = Random.new().read(AES.block_size)
    write_key(args.key_name, system_key, nonce)
    print("Key stored in " + args.key_name + ".key")

elif mode == "dec":
    if args.keys is None:
        error("Key file is required")
    system_key, nonce = read_key(args.keys)
    key_encrypt, key_auth = get_keys(base64.b64decode(system_key))
    if args.ciphertext is None:
        error("Ciphertext file is required")
    file = open(args.ciphertext, "rb")
    ciphertext = file.read()
    plaintext = dec(key_encrypt, key_auth, base64.b64decode(nonce), base64.b64decode(ciphertext))
    if plaintext is None:
        error("Encryption is unauthenticated, tag wasn't valid")
    else:
        print("Plaintext: " + plaintext)

elif mode == "test":
    print(tests())

else:
    error("Please select a mode from the list")
