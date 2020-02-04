from mysrc.IO.file_reader import myhost


def test_file():
    assert str(myhost("test/config.json")) == "postgresql+psycopg2://postgres:postgres@:5432/chargemap_test"

def test_fileerror_handling():
    assert str(myhost("tesgt/config.json")) == 'file error'