import unittest
from database import Database


class TestOptions(unittest.TestCase):

    # Dropping #
    def test_drop_all(self):
        db = Database('data/Database.json', drop='*', use_warning=False)
        self.assertEqual(db.execute("SHOW TABLES;")[0][0], 'messages')

    def test_drop_one(self):
        db = Database('data/Database.json', drop=['messages'], use_warning=False)
        self.assertEqual(db.execute("SHOW TABLES;")[0][0], 'messages')

    def test_drop_warn(self):
        db = Database('data/DB_TABLES_ADD.json')
        self.assertEqual(2, len(db.execute("SHOW TABLES;")))
        del db

        print('Print n:')
        db = Database('data/Database.json', drop='*')
        self.assertEqual(2, len(db.execute("SHOW TABLES;")))

        print('Print y:')
        db = Database('data/Database.json', drop='*')
        self.assertEqual(1, len(db.execute("SHOW TABLES;")))
    # ----- #

    # Columns #
    def test_columns(self):
        # Add
        db = Database('data/DB_COLS_ADD.json')
        self.assertEqual('test_col', db.execute("DESCRIBE messages")[2][0])

        # Change
        db = Database('data/DB_COLS_CHANGE.json', update_cols=True)
        self.assertEqual('varchar(4)', db.execute("DESCRIBE messages")[2][1])

        # Remove
        db = Database('data/Database.json', remove_cols=True)
        cols = []
        for col in db.execute("DESCRIBE messages"):
            cols.append(col[0])
        self.assertEqual(['id', 'message', 'test_none'], cols)
    # ----- #

    # Check #
    def test_no_check(self):
        db = Database('data/DB_COLS_CHANGE.json')
        db.execute("DROP TABLE messages;")
        del db

        db = Database('data/DB_COLS_CHANGE.json', check=False)
        self.assertEqual(0, len(db.execute("SHOW TABLES;")))
    # ----- #


if __name__ == '__main__':
    unittest.main()
