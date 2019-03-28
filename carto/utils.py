from io import RawIOBase

DEFAULT_CHUNK_SIZE = 8 * 1024  # 8 KB


class ResponseStream(RawIOBase):
    def __init__(self, response):
        self.it = response.iter_content(DEFAULT_CHUNK_SIZE)
        self.leftover = None

    def readable(self):
        return True

    def readinto(self, b):
        try:
            lenght = len(b)
            chunk = self.leftover or next(self.it)
            output, self.leftover = chunk[:lenght], chunk[lenght:]
            b[:len(output)] = output
            return len(output)
        except StopIteration:
            return 0
