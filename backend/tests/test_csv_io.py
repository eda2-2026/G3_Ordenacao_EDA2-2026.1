from ordenacao.csv_io import criar_chave, criar_conversor, ler_csv, obter_indice_coluna


def test_ler_csv_ok(tmp_path):
    arquivo = tmp_path / "dados.csv"
    arquivo.write_text("nome,idade\nana,3\nbob,1\n", encoding="utf-8")

    cabecalho, linhas = ler_csv(str(arquivo))

    assert cabecalho == ["nome", "idade"]
    assert linhas == [["ana", "3"], ["bob", "1"]]


def test_ler_csv_vazio(tmp_path):
    arquivo = tmp_path / "vazio.csv"
    arquivo.write_text("", encoding="utf-8")

    try:
        ler_csv(str(arquivo))
    except ValueError as exc:
        assert "vazio" in str(exc)
    else:
        assert False, "Esperava ValueError para arquivo vazio"


def test_ler_csv_sem_dados(tmp_path):
    arquivo = tmp_path / "sem_dados.csv"
    arquivo.write_text("nome,idade\n", encoding="utf-8")

    try:
        ler_csv(str(arquivo))
    except ValueError as exc:
        assert "sem linhas" in str(exc)
    else:
        assert False, "Esperava ValueError para CSV sem dados"


def test_obter_indice_coluna_ok():
    cabecalho = ["nome", "idade"]
    assert obter_indice_coluna(cabecalho, "idade") == 1


def test_obter_indice_coluna_erro():
    cabecalho = ["nome", "idade"]
    try:
        obter_indice_coluna(cabecalho, "peso")
    except ValueError as exc:
        assert "Coluna nao encontrada" in str(exc)
    else:
        assert False, "Esperava ValueError para coluna inexistente"


def test_criar_conversor_ok():
    assert criar_conversor("str")("x") == "x"
    assert criar_conversor("int")("2") == 2
    assert criar_conversor("float")("2.5") == 2.5


def test_criar_conversor_invalido():
    try:
        criar_conversor("bool")
    except ValueError as exc:
        assert "Tipo de chave invalido" in str(exc)
    else:
        assert False, "Esperava ValueError para tipo invalido"


def test_criar_chave_ok():
    chave = criar_chave(1, tipo="int")
    assert chave(["ana", "3"]) == 3


def test_criar_chave_indice_invalido():
    chave = criar_chave(2, tipo="str")
    try:
        chave(["ana", "3"])
    except ValueError as exc:
        assert "Linha nao possui" in str(exc)
    else:
        assert False, "Esperava ValueError para indice invalido"


def test_criar_chave_conversao_invalida():
    chave = criar_chave(1, tipo="int")
    try:
        chave(["ana", "x"])
    except ValueError as exc:
        assert "converter" in str(exc)
    else:
        assert False, "Esperava ValueError para conversao invalida"
