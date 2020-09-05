import pytest
import config
from Recovery.Pages import page as page
assert pytest
assert config


# @pytest.fixture
# def booksfile():
#     booksfile = 'GoodReads/books-small.csv'
#     return booksfile


# @pytest.fixture
# def tagsfile():
#     tagsfile = 'GoodReads/tags.csv'
#     return tagsfile


# @pytest.fixture
# def booktagsfile():
#     booktagsfile = 'GoodReads/book_tags-small.csv'
#     return booktagsfile


# @pytest.fixture
# def catalog():
#     """
#     Llama la funcion de inicializacion del catalogo del modelo.
#     """
#     # catalog es utilizado para interactuar con el modelo
#     catalog = control.initCatalog()
#     assert catalog is not None
#     return catalog


# def test_load_movies(catalog, booksfile, tagsfile, booktagsfile):
#     control.loadData(catalog, booksfile, tagsfile, booktagsfile)
#     assert control is not None
#     assert control.booksSize(catalog) == 149
#     assert control.tagsSize(catalog) == 34252
#     books = control.getBooksYear(catalog, 2008)
#     assert lt.size(books) == 4
