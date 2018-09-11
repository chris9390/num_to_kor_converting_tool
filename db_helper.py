import time
from flask_paginate import get_page_args, Pagination


class DB_Helper:
    def __init__(self, conn):
        self.conn = conn
        self.print_sql_len = 200

    def now(self):
        return time.strftime('%Y-%m-%d %H:%M:%S')

    def print_sql(self, sql):
        if len(sql) >= self.print_sql_len:
            sql_print = sql[:self.print_sql_len] + '...'
        else:
            sql_print = sql

        print("SQL:", sql_print)

    def generate_insert_key_values(self, values, without_date_fields=False):
        """
        SQL Insert 문에 필요한 key와 values를 생성
        :param values:
        :return:
        """
        insert_cols = ''
        insert_string = ''

        if not without_date_fields:
            values['created_at'] = self.now()
            values['updated_at'] = self.now()

        for key, value in values.items():
            if value is not None:
                insert_cols += '`%s`, ' % key
                insert_string += '\"%s\", ' % value

        insert_cols = insert_cols.strip()[:-1]
        insert_string = insert_string.strip()[:-1]

        return insert_cols, insert_string

    def generate_update_key_values(self, values):
        """
        SQL Update 문에 필요한 key와 values를 생성
        :param values:
        :return:
        """
        update_string = ''

        values['updated_at'] = self.now()

        for key, value in values.items():
            if value == None or len(str(value)) == 0:
                value = 'null'
                update_string += '`%s` = %s, ' % (key, value)
            else:
                update_string += '`%s` = \'%s\', ' % (key, value)

        update_string = update_string.strip()[:-1]

        return update_string

    #
    # 보험상품 테이블 관련 (Products)
    #
    def get_products(self):
        c = self.conn.cursor()
        c.execute("SELECT * FROM products")

        rows = c.fetchall()
        return rows

    def get_product(self, id):
        c = self.conn.cursor()
        c.execute("SELECT * FROM products WHERE id = %s" % id)

        row = c.fetchone()
        return row

    def insert_product(self, values):
        c = self.conn.cursor()

        insert_cols, insert_string = self.generate_insert_key_values(values)

        sql = "INSERT INTO products (%s) VALUES (%s)" % (insert_cols, insert_string)
        self.print_sql(sql)

        c.execute(sql)
        self.conn.commit()

        print("Number of rows inserted: %d" % c.rowcount)
        return

    def update_product(self, id, values):
        c = self.conn.cursor()

        update_string = self.generate_update_key_values(values)

        sql = "UPDATE products SET %s WHERE id = %s" % (update_string, id)
        self.print_sql(sql)

        c.execute(sql)
        self.conn.commit()

        print("Number of rows updated: %d" % c.rowcount)
        return

    def delete_product(self, id):
        c = self.conn.cursor()
        sql = "DELETE FROM products WHERE id = %s" % (id)

        c.execute(sql)
        self.conn.commit()

        print("Number of rows deleted: %d" % c.rowcount)
        return

    def get_questions_by_product_id(self, product_id, group_id=None, order_by=None):
        c = self.conn.cursor()
        sql = "SELECT * from product_questions as pq left join questions as q on pq.question_id = q.id where product_id = %s" % product_id

        where_clause = ''

        if group_id is not None:
            where_clause = ' and group_id = %s' % group_id

        if order_by:
            order_clause = ' ORDER BY `%s` %s' % (order_by[0], order_by[1])
        else:
            order_clause = ''

        sql += where_clause + order_clause

        c.execute(sql)
        rows = c.fetchall()
        return rows

    def get_questions_from_product(self, product_id, group_id=None):
        c = self.conn.cursor()
        sql = "SELECT * FROM questions as q left outer join (SELECT * FROM product_questions WHERE product_id = %s) as pq on q.id = pq.question_id"

        if group_id is None:
            where_clause = ' WHERE group_id is NULL OR group_id = ""'
            sql += where_clause

            c.execute(sql % (product_id))
        else:
            where_clause = ' WHERE group_id = %s'
            sql += where_clause

            c.execute(sql % (product_id, group_id))

        rows = c.fetchall()
        return rows






    # ===============================================================================================
    # ===============================================================================================
    # ===============================================================================================
    # ===============================================================================================
    # ===============================================================================================
    # ===============================================================================================




    def insert_new_text(self, dict):
        c = self.conn.cursor()

        sql = "INSERT INTO SentenceTable (sent_id, sent_original, sent_is_added, ArticleTable_article_id) " \
              "VALUES ('%s', '%s', '%s', '%s')" % (dict['sent_id'], dict['sent_original'], dict['sent_is_added'], dict['ArticleTable_article_id'])

        self.print_sql(sql)

        c.execute(sql)
        self.conn.commit()

        print("Number of rows inserted: %d" % c.rowcount)
        return

    # ===============================================================================================

    def select_every_rows_from_table(self, table_name):
        c = self.conn.cursor()

        sql = "SELECT * FROM %s" % table_name

        c.execute(sql)

        rows = c.fetchall()
        return rows



    def select_every_rows_from_sentence_by_id(self, id):
        c = self.conn.cursor()

        sql = "SELECT * FROM SentenceTable WHERE ArticleTable_article_id= %s" % id
        c.execute(sql)

        rows = c.fetchall()
        return rows

    def select_data_from_table_by_id(self, column_name, table_name, id):
        c = self.conn.cursor()

        if table_name == 'ArticleTable':
            sql = "SELECT %s as data FROM %s WHERE article_id = %s" % (column_name, table_name, id)
        elif table_name == 'SentenceTable':
            sql = "SELECT %s as data FROM %s WHERE sent_id = %s" % (column_name, table_name, id)

        c.execute(sql)

        row = c.fetchone()['data']
        return row



    def select_largest_sent_id(self):
        c = self.conn.cursor()

        sql = "SELECT sent_id as id FROM SentenceTable ORDER BY sent_id DESC LIMIT 1"

        c.execute(sql)

        row = c.fetchone()['id']
        return row


    def select_every_rows_including_text_from_table(self, table_name, text):
        c = self.conn.cursor()


        sql = "SELECT * FROM %s WHERE (sent_original LIKE '%%%s%%' AND sent_confirm = 0) OR " \
                                        "(sent_converted LIKE '%%%s%%' AND sent_confirm = 1)" % (table_name, text, text)

        c.execute(sql)

        rows = c.fetchall()
        return rows

    # ===============================================================================================

    def update_sent_converted(self, text, id):
        c = self.conn.cursor()


        if "'" in text:
            text_replaced = text.replace("'", "''")
            sql = "UPDATE SentenceTable SET sent_converted = '%s' WHERE sent_id = %s" % (text_replaced, id)


        elif '"' in text:
            text_replaced = text.replace('"', '""')
            sql = 'UPDATE SentenceTable SET sent_converted = "%s" WHERE sent_id = %s' % (text_replaced, id)


        else:
            sql = "UPDATE SentenceTable SET sent_converted = '%s' WHERE sent_id = %s" % (text, id)




        self.print_sql(sql)

        c.execute(sql)
        self.conn.commit()

        print("Number of rows updated: %d" % c.rowcount)
        return


    def update_sent_modified_date(self, id):
        c = self.conn.cursor()


        current = self.now()
        sql = "UPDATE SentenceTable SET sent_modified_date = '%s' WHERE sent_id = %s" % (current, id)

        self.print_sql(sql)

        c.execute(sql)
        self.conn.commit()

        print("Number of rows updated: %d" % c.rowcount)
        return



    def update_sent_confirm(self, id):
        c = self.conn.cursor()

        sql = "UPDATE SentenceTable SET sent_confirm = 1 WHERE sent_id = %s" % id

        self.print_sql(sql)

        c.execute(sql)
        self.conn.commit()

        print("Number of rows updated: %d" % c.rowcount)
        return



    def update_sent_ambiguity(self, id):
        c = self.conn.cursor()

        sql = "UPDATE SentenceTable SET sent_ambiguity = 1 WHERE sent_id = %s" % id

        self.print_sql(sql)

        c.execute(sql)
        self.conn.commit()

        print("Number of rows updated: %d" % c.rowcount)
        return



    def update_sent_converted_count(self, converted_count, id):
        c = self.conn.cursor()

        sql = "UPDATE SentenceTable SET sent_converted_count = %s WHERE sent_id = %s" % (converted_count, id)

        self.print_sql(sql)

        c.execute(sql)
        self.conn.commit()

        print("Number of rows updated: %d" % c.rowcount)
        return


    # ===============================================================================================


    def delete_sent_by_id(self, id):
        c = self.conn.cursor()
        sql = "DELETE FROM SentenceTable WHERE sent_id = %s" % (id)

        c.execute(sql)
        self.conn.commit()

        print("Number of rows deleted: %d" % c.rowcount)
        return

    # ===============================================================================================


    def call_board(self, page, per_page):

        c = self.conn.cursor()

        # 1페이지는 0부터 시작, 2페이지는 10부터 시작...
        limit_start = per_page * (page - 1)

        sql = "SELECT ST.* FROM SentenceTable as ST left join ArticleTable as AT on ST.sent_id = AT.article_id"
        sql += " LIMIT %s,%s" % (limit_start, per_page)

        c.execute(sql)

        rows = c.fetchall()
        return rows



    def call_board_search(self, page, per_page, text):

        c = self.conn.cursor()

        # 1페이지는 0부터 시작, 2페이지는 10부터 시작...
        limit_start = per_page * (page - 1)

        sql = "SELECT ST.* FROM SentenceTable as ST left join ArticleTable as AT on ST.sent_id = AT.article_id"
        sql += " WHERE (sent_original LIKE '%%%s%%' AND sent_confirm = 0) OR (sent_converted LIKE '%%%s%%' AND sent_confirm = 1)" % (text, text)
        sql += " LIMIT %s,%s" % (limit_start, per_page)

        c.execute(sql)

        rows = c.fetchall()
        return rows