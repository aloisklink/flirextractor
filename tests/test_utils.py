from flirextractor.utils import split_dict


def test_split_dict():
    max_val = 100
    input_dict = {str(i): i for i in range(max_val)}
    even_dict = {str(i): i for i in range(0, max_val, 2)}
    odd_dict = {str(i): i for i in range(1, max_val, 2)}

    even_keys = filter(lambda x: 0 == int(x) % 2, input_dict.keys())
    assert split_dict(input_dict, even_keys) == (even_dict, odd_dict)
