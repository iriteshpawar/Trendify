import binascii
import os
import random


def generate_token(self, *args, **kwargs):

    length = random.randint(150, 256)

    return binascii.hexlify(os.urandom(256)).decode()[0:length]
