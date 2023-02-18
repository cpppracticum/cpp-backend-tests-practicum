import os
import random
import time
import types
import uuid

import pytest
import select
import subprocess

from typing import Callable, Optional, List, Union, Dict
from dataclasses import dataclass
from contextlib import contextmanager

import psycopg2
from psycopg2.extras import DictCursor
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


random.seed(42)

# TODO: Replace all time.sleep


def get_connection(db_name):
    return psycopg2.connect(user=os.environ['POSTGRES_USER'],
                            password=os.environ['POSTGRES_PASSWORD'],
                            host=os.environ['POSTGRES_HOST'],
                            port=os.environ['POSTGRES_PORT'],
                            dbname=db_name,
                            cursor_factory=DictCursor,
                            )


def authors_to_str(authors):
    return [f'{i+1} {author["name"]}'.strip() for i, author in enumerate(authors)]


def books_to_str(books):
    return [f'{i+1} {book["title"]} by {book["name"]}, {book["publication_year"]}'.strip() for i, book in enumerate(books)]


def get_authors(db_name):
    query = "SELECT id, name FROM authors ORDER BY name;"
    with get_connection(db_name) as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            return cur.fetchall()


def get_books(db_name):
    query = """SELECT
    books.id AS book_id,
    title,
    author_id,
    authors.name AS name,
    publication_year
FROM books
INNER JOIN authors ON authors.id = author_id
ORDER BY title, name, publication_year
;"""
    with get_connection(db_name) as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            return cur.fetchall()


def get_author_books(db_name, author_id):
    query = """SELECT
    id,
    title,
    author_id,
    publication_year 
FROM books
WHERE author_id=%s
ORDER BY publication_year, title
;"""
    with get_connection(db_name) as conn:
        with conn.cursor() as cur:
            cur.execute(query, (author_id,))
            return [f'{i+1} {book["title"]}, {book["publication_year"]}'.strip() for i, book in enumerate(cur.fetchall())]


def get_book(db_name, title):
    query = """SELECT
    books.id AS book_id,
    title,
    name,
    publication_year,
    grouped_tags.tags
FROM books
INNER JOIN authors ON authors.id = author_id
INNER JOIN (
    SELECT
        book_id,
        STRING_AGG(tag, ', ') AS tags
    FROM tags
    GROUP BY tags.book_id
) AS grouped_tags
ON grouped_tags.book_id = books.id
WHERE title=%s
;"""
    with get_connection(db_name) as conn:
        with conn.cursor() as cur:
            cur.execute(query, (title,))
            return cur.fetchall()


@dataclass
class Bookypedia:
    process: subprocess.Popen
    db_name: str
    chose: Optional[str] = None

    @staticmethod
    def random_chooser(authors):
        index = random.randint(0, len(authors)-1)
        return index+1, authors[index]

    @staticmethod
    def index_chooser(index: int):
        def chooser(authors):
            return index+1, authors[index]
        return chooser

    def _wait_select(self, timeout=0.2):
        delta = timeout/100
        for _ in range(100):
            if select.select([self.process.stdout], [], [], 0.0)[0]:
                return True
            time.sleep(delta)
        return False

    def _wait_strings(self, timeout=0.2):
        res = list()
        if self._wait_select(timeout):
            delta = timeout/100
            for _ in range(100):
                line = self.process.read()
                if line:
                    res.append(line)
                time.sleep(delta)
        return res

    def add_author(self, author: Optional[str]) -> Optional[str]:
        if author:
            self.process.write(f'AddAuthor {author}')
        else:
            self.process.write(f'AddAuthor')
        if self._wait_select():
            return self.process.read()

    def show_authors(self) -> List[str]:
        self.process.write('ShowAuthors')
        return self._wait_strings()

    def _author(self, command, author_or_callback: Union[str, Callable]) -> Optional[str]:
        if isinstance(author_or_callback, str):
            self.process.write(f'{command} {author_or_callback}')
        else:
            self.process.write(command)
            authors = self._wait_strings()[1:-1]
            if authors:
                number, self.chose = author_or_callback(authors)
                self.process.write(f'{number}')
            else:
                self.process.write('')
                return None
        if self._wait_select():
            return self.process.read()

    def delete_author(self, author_or_callback: Union[str, Callable]) -> Optional[str]:
        return self._author('DeleteAuthor', author_or_callback)

    def edit_author(self, author_or_callback: Union[str, Callable], new_author: str) -> Optional[str]:
        _ = self._author('EditAuthor', author_or_callback)  # Enter new name:
        self.process.write(new_author)
        if self._wait_select():
            return self.process.read()

    def _book(self, command: str, book_or_callback: Union[str, Callable]) -> List[str]:
        if isinstance(book_or_callback, str):
            self.process.write(f'{command} {book_or_callback}')
            books = self._wait_strings()
            if books:
                if books[0].startswith('1'):
                    self.chose = books[0]
                    self.process.write('1')
                else:
                    return books
        else:
            self.process.write(command)
            books = self._wait_strings()[1:-1]
            if books:
                number, self.chose = book_or_callback(books)
                self.process.write(f'{number}')
        return self._wait_strings()

    def show_book(self, book_or_callback: Union[str, Callable]) -> List[str]:
        return self._book('ShowBook', book_or_callback)

    def delete_book(self, book_or_callback: Union[str, Callable]) -> List[str]:
        return self._book('DeleteBook', book_or_callback)

    def edit_book(self, book_or_callback: Union[str, Callable], new_info: Dict[str, str]) -> List[str]:
        mb_title = self._book('EditBook', book_or_callback)  # Enter new title
        if mb_title:
            if not mb_title[0].startswitn('Enter new title'):
                return mb_title[0]
        self.process.write(new_info['title'])
        _ = self.process.read()  # Enter publication year
        self.process.write(new_info['year'])
        _ = self.process.read()  # Enter tags
        self.process.write(new_info['tags'])

        if self._wait_select():
            return self.process.read()

    def add_book(self, year: int, title: str, author_or_callback: Union[str, Callable], add_author_answer: str = 'y') -> Optional[str]:
        self.process.write(f'AddBook {year} {title}')

        if isinstance(author_or_callback, str):
            self.process.write(author_or_callback)
            if self._wait_select():
                _ = self.process.read()  # y/n?
                self.process.write(add_author_answer)

        else:
            self.process.write('')
            authors = self._wait_strings()[1:-1]
            if authors:
                number, self.chose = author_or_callback(authors)
                self.process.write(f'{number}')
            else:
                self.process.write('')
                return None
            if self._wait_select():
                return self.process.read()

    def show_author_books(self, author_chooser: Optional[Callable] = None) -> List[str]:
        if author_chooser is None:
            author_chooser = Bookypedia.random_chooser
        self.process.write('ShowAuthorBooks')
        authors = self._wait_strings()[1:-1]
        if authors:
            number, self.chose = author_chooser(authors)
            self.process.write(f'{number}')
        else:
            self.process.write('')
        return self._wait_strings()

    def show_books(self) -> List[str]:
        self.process.write('ShowBooks')
        return self._wait_strings()


# @pytest.fixture(scope='function', params=['empty_db', 'table_db', 'full_db'])
# def bookypedia(request):
#     with run_bookypedia(request.param) as result:
#         yield result


@contextmanager
def run_bookypedia(db_name, terminate=True, reset_db=True):
    def _read(self):
        return self.stdout.readline().strip()

    def _write(self, message: str):
        self.stdin.write(f"{message.strip()}\n")
        self.stdin.flush()

    def _terminate(self):
        self.stdin.close()
        self.terminate()
        self.wait()

    try:
        if reset_db:
            drop_db(db_name)
            create_db(db_name)
    except Exception:
        pass

    db_connect = f"postgres://{os.environ['POSTGRES_USER']}:{os.environ['POSTGRES_PASSWORD']}@{os.environ['POSTGRES_HOST']}:{os.environ['POSTGRES_PORT']}/{db_name}"
    proc = subprocess.Popen(os.environ['DELIVERY_APP'].split(), text=True, env=dict(os.environ, BOOKYPEDIA_DB_URL=db_connect),
                            stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    os.set_blocking(proc.stdout.fileno(), False)
    proc.write = types.MethodType(_write, proc)
    proc.read = types.MethodType(_read, proc)
    proc.new_terminate = types.MethodType(_terminate, proc)

    try:
        yield Bookypedia(proc, db_name)
    finally:
        if terminate:
            proc.new_terminate()


@pytest.mark.parametrize('db_name', ['empty_db', 'table_db', 'full_db'])
def test_add_author(db_name):
    with run_bookypedia(db_name) as bookypedia:
        if db_name != 'full_db':
            assert bookypedia.add_author(None).startswith('Failed to add author')
            assert bookypedia.add_author('author2') is None
            assert bookypedia.add_author('author1') is None
            assert bookypedia.add_author('author2').startswith('Failed to add author')
        else:
            assert bookypedia.add_author(None).startswith('Failed to add author')
            assert bookypedia.add_author('author2').startswith('Failed to add author')
            assert bookypedia.add_author('author1').startswith('Failed to add author')
            assert bookypedia.add_author('author2').startswith('Failed to add author')


@pytest.mark.parametrize('db_name', ['empty_db', 'table_db', 'full_db'])
def test_show_authors(db_name):
    with run_bookypedia(db_name) as bookypedia:
        assert bookypedia.show_authors() == authors_to_str(get_authors(db_name))

        bookypedia.add_author('author3')
        bookypedia.add_author('author2')
        bookypedia.add_author('author1')

        assert bookypedia.show_authors() == authors_to_str(get_authors(db_name))


# @pytest.mark.parametrize('db_name', ['empty_db', 'table_db', 'full_db'])
# def test_add_book(db_name):
#     with run_bookypedia(db_name) as bookypedia:
#         bookypedia.add_author('author3')
#         bookypedia.add_author('author2')
#         bookypedia.add_author('author1')
#
#         assert bookypedia.add_book(1111, 'Book1') is None
#         assert bookypedia.add_book(222, 'Book2') is None
#         assert bookypedia.add_book(33, 'Book3') is None


# @pytest.mark.parametrize('db_name', ['empty_db', 'table_db', 'full_db'])
# def test_show_author_books(db_name):
#     with run_bookypedia(db_name) as bookypedia:
#         bookypedia.show_books()
#         authors = get_authors(db_name)
#         for i in range(len(authors)):
#             books = bookypedia.show_author_books(Bookypedia.index_chooser(i))
#             assert books == get_author_books(db_name, authors[i]['id'])
#
#         bookypedia.add_author('author3')
#         bookypedia.add_author('author2')
#         bookypedia.add_author('author1')
#
#         bookypedia.add_book(1111, 'Title1', Bookypedia.index_chooser(0))
#         bookypedia.add_book(222, 'Title2', Bookypedia.index_chooser(0))
#         bookypedia.add_book(33, 'Title3', Bookypedia.index_chooser(1))
#
#         authors = get_authors(db_name)
#         for i in range(len(authors)):
#             books = bookypedia.show_author_books(Bookypedia.index_chooser(i))
#             assert books == get_author_books(db_name, authors[i]['id'])


# @pytest.mark.parametrize('db_name', ['empty_db', 'table_db', 'full_db'])
# def test_show_books(db_name):
#     with run_bookypedia(db_name) as bookypedia:
#         assert bookypedia.show_books() == books_to_str(get_books(db_name))
#
#         bookypedia.add_author('author3')
#         bookypedia.add_author('author2')
#         bookypedia.add_author('author1')
#
#         bookypedia.add_book(1111, 'Book1')
#         bookypedia.add_book(222, 'Book2')
#         bookypedia.add_book(33, 'Book3')
#
#         assert bookypedia.show_books() == books_to_str(get_books(db_name))
#
#
# @pytest.mark.parametrize('db_name', ['empty_db', 'table_db', 'full_db'])
# def test_concurrency(db_name):
#     with run_bookypedia(db_name) as bookypedia1:
#         time.sleep(0.2)
#         with run_bookypedia(db_name, reset_db=False) as bookypedia2:
#             books = books_to_str(get_books(db_name))
#             assert bookypedia1.show_books() == books
#             assert bookypedia2.show_books() == books
#
#             bookypedia1.add_author('AAAA')  # insert to top on list
#
#             def create_chooser(index: int):
#                 def chooser(authors):
#                     bookypedia2.add_author('A')  # insert to top on list
#                     time.sleep(0.2)
#                     return index+1, authors[index]
#                 return chooser
#
#             bookypedia1.add_book(2022, '!Title', create_chooser(0))
#
#             authors = get_authors(db_name)
#             for i, author in enumerate(authors):
#                 if author['name'] == 'AAAA':
#                     books = bookypedia1.show_author_books(Bookypedia.index_chooser(i))
#                     assert books == ['1 !Title, 2022']
#                 if author['name'] == 'A':
#                     books = bookypedia1.show_author_books(Bookypedia.index_chooser(i))
#                     assert books == []


def drop_db(db_name):
    conn = get_connection(None)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    with conn.cursor() as cur:
        try:
            cur.execute(f'drop database {db_name};')
        except Exception as e:
            print(e)
    conn.close()


def create_db(db_name):
    conn = get_connection(None)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    with conn.cursor() as cur:
        cur.execute(f'create database {db_name};')
    conn.close()

    if db_name in {'table_db', 'full_db'}:
        with get_connection(db_name) as conn:
            with conn.cursor() as cur:
                cur.execute(
"""CREATE TABLE IF NOT EXISTS authors (
    id UUID CONSTRAINT firstindex PRIMARY KEY,
    name varchar(100) NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS books (
    id UUID PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    publication_year INT,
    author_id UUID,
    CONSTRAINT fk_authors
        FOREIGN KEY(author_id)
        REFERENCES authors(id)
);
CREATE TABLE IF NOT EXISTS tags (
    book_id UUID,
    tag varchar(30) NOT NULL,
    CONSTRAINT fk_books
        FOREIGN KEY(book_id)
        REFERENCES books(id)
);
""")

    insert_author = f'INSERT INTO authors (id, name) VALUES (%s, %s);'
    insert_book = f'INSERT INTO books (id, title, author_id, publication_year) VALUES (%s, %s, %s, %s);'
    insert_tag = f'INSERT INTO tags (book_id, tag) VALUES (%s, %s);'
    if db_name == 'full_db':
        with get_connection(db_name) as conn:
            with conn.cursor() as cur:

                author_ids = []
                for i in range(5):
                    _uuid = uuid.uuid4().hex
                    author_ids.append(_uuid)
                    cur.execute(insert_author, (_uuid, f'author{i}'))

                for i in range(20):
                    book_id = uuid.uuid4().hex
                    cur.execute(insert_book, (book_id, f'Title{i}', random.choice(author_ids), 1000+i))
                    for j in range(random.randint(0, 4)):
                        cur.execute(insert_tag, (book_id, f'tag{j}'))


if __name__ == '__main__':
    for name in ['empty_db', 'table_db', 'full_db']:
        drop_db(name)
        create_db(name)
