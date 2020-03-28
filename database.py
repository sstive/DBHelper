import pymysql
from json import load
from os import environ as env


class Database:

    def __init__(self, database, **options):
        # Variables
        self.update_columns = True

        # Getting information about database
        if type(database) is not dict:
            self.data = load(database)
        else:
            self.data = database

        self.con = pymysql.connect(**self.data['connection'])

        # Database tables not checked yet
        self.checked = False

        # Checking options
        options_list = {
            'UPDATE_COLUMNS': self.upd_cols,
            'DROP_TABLE': self.drop_table,
            'CHECK': self.check
        }

        for option, func in options_list.items():
            if option in options:
                func(options[option])
            elif option in env:
                func(env[option])

    def __del__(self):
        self.end()

    # Connection
    def begin(self):
        if not self.con.open:
            self.con = pymysql.connect(**self.data['connection'])

    def end(self):
        if self.con.open:
            self.con.close()

    # Utils
    def get_db_tables(self):
        with self.con.cursor() as cur:
            cur.execute("SHOW TABLES")
            tables = []
            for el in cur.fetchall():
                tables.append(el[0])
        return tables

    def get_create_cmd(self, table):
        columns = self.data['tables'][table]

        command = f"CREATE TABLE {table} ("
        for col, params in columns.items():
            if col == '__KEY':
                command += f'PRIMARY KEY({params})'
            elif col == '__ADDITION':
                command += params
            else:
                command += col + ' '
                if params == 'KEY':
                    command += "INT AUTO_INCREMENT NOT NULL UNIQUE PRIMARY KEY"
                else:
                    command += ' '.join(params)
            command += ', '
        return command[:-2] + ');'

    @staticmethod
    def compare_data_types(local, db):
        if local == 'KEY':
            return True
        local = local[0]

        local = local.upper()
        db = db.upper()

        if '(' not in local:
            if local == db.split('(', 1)[0]:
                return True
            return False

        if local == db:
            return True
        return False

    # Options
    def upd_cols(self, val=True):
        if val in ['True', 'TRUE', 'true', '1', 'yes', 'y', True, 1]:
            self.update_columns = True
        else:
            self.update_columns = False

    def drop_table(self, tables="[]"):
        if type(tables) is str:
            tables.replace(' ', '')
            tables.replace('[', '')
            tables.replace(']', '')
            tables = tables.split(',')

        if len(tables) > 0 and tables[0] == '*':
            tables = self.get_db_tables()

        if not tables:
            return

        print("Are you sure want to drop tables? (y/n)")
        if input() is not 'y':
            return

        self.con.cursor().execute("DROP TABLE " + ', '.join(tables))
        self.con.commit()
        self.checked = False
        self.check()

    def check(self, val='1'):
        if self.checked or val not in ['True', 'TRUE', 'true', '1', 'yes', 'y', True, 1]:
            return

        with self.con.cursor() as cur:
            cur.execute("SHOW TABLES")

            tables_in_db = self.get_db_tables()

            for table in tables_in_db:
                if table not in self.data['tables'].keys():
                    continue

                # Checking columns
                if not self.update_columns:
                    continue

                cur.execute(f"DESCRIBE {table}")
                db_cols = {}
                for col_in_db in cur.fetchall():
                    db_cols[col_in_db[0]] = col_in_db[1:]

                # TODO: check params
                for col in self.data['tables'][table].keys():
                    if col in ['__ADDITION', '__KEY']:
                        continue

                    if col not in db_cols.keys():
                        cur.execute(f"ALTER TABLE {table} ADD {col} {' '.join(self.data['tables'][table][col])};")
                        continue

                    if not self.compare_data_types(self.data['tables'][table][col], db_cols[col][0]):
                        cur.execute(f"ALTER TABLE {table} MODIFY COLUMN {col} {' '.join(self.data['tables'][table][col])};")

            # Checking tables
            for table in self.data['tables']:
                if table not in tables_in_db:
                    cur.execute(self.get_create_cmd(table))
        self.con.commit()
