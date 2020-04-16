from common import Hash

if __name__ == "__main__":
    b = Hash.b64("leon")
    assert b == 'bGVvbg=='
    assert Hash.b64_decode(b) == "leon"
    assert Hash.md5("leon") == "5c443b2003676fa5e8966030ce3a86ea"

