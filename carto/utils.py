class ResponseStream(io.RawIOBase):
    def __init__(self, response):
        self.it = response.iter_content(DEFAULT_CHUNK_SIZE)
        self.leftover = None

    def readable(self):
        return True

    def readinto(self, b):
        try:
            l = len(b)
            chunk = self.leftover or next(self.it)
            output, self.leftover = chunk[:l], chunk[l:]
            b[:len(output)] = output
            return len(output)
        except StopIteration:
            return 0
