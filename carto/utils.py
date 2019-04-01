from io import RawIOBase


class ResponseStream(RawIOBase):
    def __init__(self, response):
        self.it = response.iter_content(8 * 1024)
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
