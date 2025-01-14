from fake_headers import Headers

class FakeHeader:
    def generate():
        headers = Headers(headers=True).generate()

        return headers