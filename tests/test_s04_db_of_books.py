import os
import json
import time
import types
import pytest
import subprocess

from typing import Optional
from contextlib import contextmanager

import psycopg2
from psycopg2.extras import DictCursor
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def get_connection(db_name):
    return psycopg2.connect(user=os.environ['POSTGRES_USER'],
                            password=os.environ['POSTGRES_PASSWORD'],
                            host=os.environ['POSTGRES_HOST'],
                            port=os.environ['POSTGRES_PORT'],
                            dbname=db_name,
                            cursor_factory=DictCursor,
                            )


def drop_db(db_name):
    conn = get_connection(None)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    with conn.cursor() as cur:
        try:
            cur.execute(f'drop database {db_name};')
        except Exception as e:
            print(e)
    conn.close()


def get_last_added_book(db_name):
    with get_connection(db_name) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM books ORDER BY id DESC LIMIT 1;")
            return cur.fetchone()


def get_all_books(db_name):
    with get_connection(db_name) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM books ORDER BY year DESC, title, author, ISBN;")
            return cur.fetchall()


def check_exist_table(db_name, table_name):
    with get_connection(db_name) as conn:
        with conn.cursor() as cur:
            cur.execute("select exists(select * from information_schema.tables where table_name=%s)", (table_name,))
            return cur.fetchone()[0]


@contextmanager
def run_book_manager(db_name, terminate=True):
    def _read(self):
        return self.stdout.readline().strip()

    def _write(self, message: str):
        self.stdin.write(f"{message.strip()}\n")
        self.stdin.flush()

    def _terminate(self):
        self.stdin.close()
        self.terminate()
        self.wait(timeout=0.2)

    db_connect = f"postgres://{os.environ['POSTGRES_USER']}:{os.environ['POSTGRES_PASSWORD']}@{os.environ['POSTGRES_HOST']}:{os.environ['POSTGRES_PORT']}/{db_name}"
    proc = subprocess.Popen([os.environ['DELIVERY_APP'], db_connect], text=True,
                            stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    proc.write = types.MethodType(_write, proc)
    proc.read = types.MethodType(_read, proc)
    proc.new_terminate = types.MethodType(_terminate, proc)
    try:
        yield proc
    finally:
        if terminate:
            proc.new_terminate()


def create_add_book_command(title: str, author: str, year: int, isbn: Optional[str]) -> dict:
    return {
        "action": "add_book",
        "payload": {
            "title": title,
            "author": author,
            "year": year,
            "ISBN": isbn
        }
    }


def create_all_books_command() -> dict:
    return {
        "action": "all_books",
        "payload": {}
    }


def create_exit_command() -> dict:
    return {
        "action": "exit",
        "payload": {}
    }


def check_row(left, right, has_id=False):
    if has_id:
        assert left['id'] == right['id']
    assert left['title'] == right['title']
    assert left['author'] == right['author']
    assert left['year'] == right['year']
    if left['isbn']:
        if right['ISBN']:
            assert left['isbn'].strip() == right['ISBN'].strip()
        else:
            assert False
    else:
        assert left['isbn'] == right['ISBN']


def check_add_book(db_name, cmd):
    last = get_last_added_book(db_name)
    check_row(last, cmd)


def check_all_books(db_name, result):
    books = get_all_books(db_name)
    assert len(books) == len(result)
    for py_book, cpp_book in zip(books, result):
        check_row(py_book, cpp_book, has_id=True)


@pytest.mark.parametrize('db_name', ['table_db', 'empty_db', 'full_db'])
def test_exit(db_name):
    with run_book_manager(db_name) as book_manager:
        cmd = create_exit_command()

        book_manager.write(json.dumps(cmd))
        time.sleep(0.5)
        assert book_manager.poll() is not None


@pytest.mark.parametrize('db_name', ['table_db', 'empty_db', 'full_db'])
def test_all_books(db_name):
    with run_book_manager(db_name) as book_manager:
        cmd = create_all_books_command()

        book_manager.write(json.dumps(cmd))
        result = json.loads(book_manager.read())

        check_all_books(db_name, result)


@pytest.mark.parametrize('db_name', ['table_db', 'empty_db'])
def test_add_book(db_name):
    with run_book_manager(db_name) as book_manager:
        for i in range(50):
            isbn = f'{i}' if i % 2 == 0 else None
            cmd = create_add_book_command(f'book_{i}', f'author_{i}', 1000+i, isbn)

            book_manager.write(json.dumps(cmd))
            result = json.loads(book_manager.read())

            if result['result']:
                check_add_book(db_name, cmd['payload'])
            else:
                assert False


@pytest.mark.parametrize('db_name', ['table_db', 'empty_db', 'full_db'])
def test_inject(db_name):
    with run_book_manager(db_name) as book_manager:
        cmd = create_add_book_command('book', 'author', 1000, "111'); DROP TABLE books; --")
        book_manager.write(json.dumps(cmd))

        assert check_exist_table(db_name, 'books')

        cmd = create_add_book_command('book', "author', 1000, '111'); DROP TABLE books; --", 1000, '111')
        book_manager.write(json.dumps(cmd))

        assert check_exist_table(db_name, 'books')

        cmd = create_add_book_command("book', 'author', 1000, '111'); DROP TABLE books; --", 'author', 1000, '111')
        book_manager.write(json.dumps(cmd))

        assert check_exist_table(db_name, 'books')


def create_dbs():
    conn = get_connection(None)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    with conn.cursor() as cur:
        for name in ['empty_db', 'table_db', 'full_db']:
            cur.execute(f'create database {name};')
    conn.close()

    for name in ['table_db', 'full_db']:
        with get_connection(name) as conn:
            with conn.cursor() as cur:
                cur.execute("CREATE TABLE IF NOT EXISTS books (id SERIAL PRIMARY KEY, title varchar(100) NOT NULL, author varchar(100) NOT NULL, year integer NOT NULL, ISBN char(13) UNIQUE);")

    with get_connection('full_db') as conn:
        with conn.cursor() as cur:
            for i in range(50):
                isbn = f'{i}' if i % 2 == 0 else None
                query = f'INSERT INTO books (title, author, year, ISBN) VALUES (%s, %s, %s, %s);'
                cur.execute(query, (f'book_{i}', f'author_{i}', 1000+i, isbn))


if __name__ == '__main__':
    for name in ['empty_db', 'table_db', 'full_db']:
        drop_db(name)
    create_dbs()
