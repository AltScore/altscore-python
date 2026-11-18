from altscore.borrower_central.utils import build_test_params, clean_dict
from altscore.utils import convert_to_dash_case, divide_in_chunks


def test_divide_in_chunks():
    assert list(divide_in_chunks([1, 2, 3, 4, 5], 2)) == [[1, 2], [3, 4], [5]]
    assert list(divide_in_chunks([], 3)) == []


def test_convert_to_dash_case():
    assert convert_to_dash_case("borrower_id") == "borrower-id"
    assert convert_to_dash_case("borrowerId") == "borrower-id"
    assert convert_to_dash_case("per_page") == "per-page"


def test_clean_dict_drops_only_none():
    assert clean_dict({"a": None, "b": 0, "c": "", "d": False}) == {"b": 0, "c": "", "d": False}


def test_build_test_params():
    assert build_test_params({"x": 1}) == {"x": 1, "include-tests": "true"}
    assert build_test_params({"x": 1}, include_tests=False) == {"x": 1}
    assert build_test_params({"x": 1}, test_only=True) == {"x": 1, "test-only": "true"}
