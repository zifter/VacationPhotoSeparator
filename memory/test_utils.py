from paths import TEST_DATA_DIR
from utils import walk_in_folder

TEST_SOURCE_DIR = TEST_DATA_DIR.joinpath('test_source')
TEST_EMPTY_DIR = TEST_DATA_DIR.joinpath('empty_dir')


def test_walk_in_folder_empty_dir():
    result = list(walk_in_folder(TEST_EMPTY_DIR))
    assert result == []


def test_walk_in_folder_get_all():
    expected = sorted([
        TEST_SOURCE_DIR.joinpath('vacation/photo_2021-03-09_21-56-03.jpg'),
        TEST_SOURCE_DIR.joinpath('sort_me/Joke.jpg'),
        TEST_SOURCE_DIR.joinpath('sort_me/image.png'),
        TEST_SOURCE_DIR.joinpath('sort_me/1621918534125627841.webp'),
        TEST_SOURCE_DIR.joinpath('tmp/1099522_original.jpg'),
        TEST_SOURCE_DIR.joinpath('tmp/photo_2021-03-09_21-56-03.jpg'),
    ])

    result = sorted(walk_in_folder(TEST_SOURCE_DIR))

    assert len(result) == len(expected)
    for i in range(len(result)):
        assert result[i] == expected[i]


def test_walk_in_folder_get_all_with_filter():
    expected = sorted([
        TEST_SOURCE_DIR.joinpath('vacation/photo_2021-03-09_21-56-03.jpg'),
        TEST_SOURCE_DIR.joinpath('sort_me/Joke.jpg'),
        TEST_SOURCE_DIR.joinpath('sort_me/image.png'),
        TEST_SOURCE_DIR.joinpath('tmp/1099522_original.jpg'),
        TEST_SOURCE_DIR.joinpath('tmp/photo_2021-03-09_21-56-03.jpg'),
    ])

    result = sorted(walk_in_folder(TEST_SOURCE_DIR, ignore_ext={'.webp',}))

    assert len(result) == len(expected)
    for i in range(len(result)):
        assert result[i] == expected[i]
