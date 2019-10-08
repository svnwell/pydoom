from pydoom import BaseModel, field


class Test(BaseModel, openex=True):
    name: str = ""
    size: int = field(10, lt=11, validator="vali_size")

    @classmethod
    def vali_size(cls, val):
        if val < 5:
            return True

        return False


if __name__ == "__main__":
    dic = {"name": "zhang", "size": 2, "favor": "test"}

    t = Test(**dic)
    print(t.json())
