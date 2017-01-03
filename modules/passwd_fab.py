# Import Fabric's API module#
import base64

from fabric.api import settings
from fabric.decorators import task
from passlib.handlers.pbkdf2 import pbkdf2_sha256


@task
def hashlib(password):
    """
Password hash func
    :param password: plaintext password to be hashed
    """
    with settings(warn_only=False):
        hash_pass = pbkdf2_sha256.encrypt(password, rounds=200000, salt_size=16)
        # plainpass = pbkdf2_sha256.decrypt(hash, rounds=200000, salt_size=16)
        return hash_pass


@task
def hash_verify(password, hash_password):
    """
Password hash verify func
    :param password: plaintext password to be hashed
    :param hash_password: password hash of the pass to be verified
    """
    with settings(warn_only=False):
        if pbkdf2_sha256.verify(password, hash_password):
            print "Correct Pass"
        else:
            print "Incorrect Pass"


@task
def base64_encode(password):
    """
Password base64 encode
    :param password: plaintext password to be hashed

    eg: [vagrant@server proton]$ fab -R local password_base64_encode:Testing!
    [localhost] Executing task 'password_base64_encode'
    VGVzdGluZyE=
    Done.

    """
    with settings(warn_only=False):
        password_base64 = base64.b64encode(password)
        print password_base64
        return str(password_base64)


@task
def base64_decode(password_base64):
    """
Password base64 decode
    :param password_base64: base64 encoded password

    eg: [vagrant@server proton]$ fab -R local password_base64_decode:"VGVzdGluZyE\="
    [localhost] Executing task 'password_base64_decode'
    Testing!
    Done.
    """
    with settings(warn_only=False):
        password = base64.b64decode(password_base64)
        # print password
        return str(password)
