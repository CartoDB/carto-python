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
            length = len(b)
            chunk = self.leftover or next(self.it)
            output, self.leftover = chunk[:length], chunk[length:]
            b[:len(output)] = output
            return len(output)
        except StopIteration:
            return 0
