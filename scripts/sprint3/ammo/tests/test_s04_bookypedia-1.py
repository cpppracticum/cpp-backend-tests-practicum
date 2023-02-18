import os
import random
import time
import types
import uuid

import pytest
import select
import subprocess

from typing import Callable, Optional, List
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
    return [f'{i+1} {book["title"]}, {book["publication_year"]}'.strip() for i, book in enumerate(books)]


def get_authors(db_name):
    with get_connection(db_name) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name FROM authors ORDER BY name;")
            return cur.fetchall()


def get_books(db_name):
    with get_connection(db_name) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, title, author_id, publication_year FROM books ORDER BY title;")
            return cur.fetchall()


def get_author_books(db_name, author_id):
    with get_connection(db_name) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, title, author_id, publication_year FROM books WHERE author_id=%s ORDER BY publication_year, title;", (author_id,))
            return [f'{i+1} {book["title"]}, {book["publication_year"]}'.strip() for i, book in enumerate(cur.fetchall())]


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

    def add_book(self, year: int, title: str, author_chooser: Optional[Callable] = None) -> Optional[str]:
        if author_chooser is None:
            author_chooser = Bookypedia.random_chooser

        self.process.write(f'AddBook {year} {title}')
        authors = self._wait_strings()[1:-1]
        if authors:
            number, self.chose = author_chooser(authors)
            self.process.write(f'{number}')
        else:
            self.process.write('')
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
    # os.environ['BOOKYPEDIA_DB_URL'] = db_connect
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


@pytest.mark.parametrize('db_name', ['empty_db', 'table_db', 'full_db'])
def test_add_book(db_name):
    with run_bookypedia(db_name) as bookypedia:
        bookypedia.add_author('author3')
        bookypedia.add_author('author2')
        bookypedia.add_author('author1')

        assert bookypedia.add_book(1111, 'Book1') is None
        assert bookypedia.add_book(222, 'Book2') is None
        assert bookypedia.add_book(33, 'Book3') is None


@pytest.mark.parametrize('db_name', ['empty_db', 'table_db', 'full_db'])
def test_show_author_books(db_name):
    with run_bookypedia(db_name) as bookypedia:
        bookypedia.show_books()
        authors = get_authors(db_name)
        for i in range(len(authors)):
            books = bookypedia.show_author_books(Bookypedia.index_chooser(i))
            assert books == get_author_books(db_name, authors[i]['id'])

        bookypedia.add_author('author3')
        bookypedia.add_author('author2')
        bookypedia.add_author('author1')

        bookypedia.add_book(1111, 'Title1', Bookypedia.index_chooser(0))
        bookypedia.add_book(222, 'Title2', Bookypedia.index_chooser(0))
        bookypedia.add_book(33, 'Title3', Bookypedia.index_chooser(1))

        authors = get_authors(db_name)
        for i in range(len(authors)):
            books = bookypedia.show_author_books(Bookypedia.index_chooser(i))
            assert books == get_author_books(db_name, authors[i]['id'])


@pytest.mark.parametrize('db_name', ['empty_db', 'table_db', 'full_db'])
def test_show_books(db_name):
    with run_bookypedia(db_name) as bookypedia:
        assert bookypedia.show_books() == books_to_str(get_books(db_name))

        bookypedia.add_author('author3')
        bookypedia.add_author('author2')
        bookypedia.add_author('author1')

        bookypedia.add_book(1111, 'Book1')
        bookypedia.add_book(222, 'Book2')
        bookypedia.add_book(33, 'Book3')

        assert bookypedia.show_books() == books_to_str(get_books(db_name))
#

@pytest.mark.parametrize('db_name', ['empty_db', 'table_db', 'full_db'])
def test_concurrency(db_name):
    with run_bookypedia(db_name) as bookypedia1:
        time.sleep(0.2)
        with run_bookypedia(db_name, reset_db=False) as bookypedia2:
            books = books_to_str(get_books(db_name))
            assert bookypedia1.show_books() == books
            assert bookypedia2.show_books() == books

            bookypedia1.add_author('AAAA')  # insert to top on list

            def create_chooser(index: int):
                def chooser(authors):
                    bookypedia2.add_author('A')  # insert to top on list
                    time.sleep(0.2)
                    return index+1, authors[index]
                return chooser

            bookypedia1.add_book(2022, '!Title', create_chooser(0))

            authors = get_authors(db_name)
            for i, author in enumerate(authors):
                if author['name'] == 'AAAA':
                    books = bookypedia1.show_author_books(Bookypedia.index_chooser(i))
                    assert books == ['1 !Title, 2022']
                if author['name'] == 'A':
                    books = bookypedia1.show_author_books(Bookypedia.index_chooser(i))
                    assert books == []


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
""")
    if db_name == 'full_db':
        with get_connection(db_name) as conn:
            with conn.cursor() as cur:
                query = f'INSERT INTO authors (id, name) VALUES (%s, %s);'
                author_ids = []
                for i in range(5):
                    _uuid = uuid.uuid4().hex
                    author_ids.append(_uuid)
                    cur.execute(query, (_uuid, f'author{i}'))
                query = f'INSERT INTO books (id, title, author_id, publication_year) VALUES (%s, %s, %s, %s);'
                for i in range(20):
                    cur.execute(query, (uuid.uuid4().hex, f'Title{i}', random.choice(author_ids), 1000+i))


if __name__ == '__main__':
    for name in ['empty_db', 'table_db', 'full_db']:
        drop_db(name)
        create_db(name)
