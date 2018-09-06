import time

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


    def get_every_from_user_info(self):
        c = self.conn.cursor()

        sql = "SELECT * FROM user_info"
        c.execute(sql)

        rows = c.fetchall()
        return rows

    def get_every_from_article(self):
        c = self.conn.cursor()

        sql = "SELECT * FROM ArticleTable"
        c.execute(sql)

        rows = c.fetchall()
        return rows

    def get_every_from_sentence_by_id(self, id):
        c = self.conn.cursor()

        sql = "SELECT * FROM SentenceTable WHERE ArticleTable_article_id= %s" % id
        c.execute(sql)

        rows = c.fetchall()
        return rows

    def get_original_from_sentence_by_id(self, id):
        c = self.conn.cursor()

        sql = "SELECT sent_original FROM SentenceTable WHERE sent_id = %s" % id
        c.execute(sql)

        row = c.fetchone()
        return row



    def update_converted_text(self, text, id):
        c = self.conn.cursor()


        if "'" in text:
            print('!!!!!!')
            text_replaced = text.replace("'", "''")
            print(text_replaced)
            sql = "UPDATE SentenceTable SET sent_converted = '%s' WHERE sent_id = %s" % (text_replaced, id)


        elif '"' in text:
            print('??????')
            text_replaced = text.replace('"', '""')
            print(text_replaced)
            sql = 'UPDATE SentenceTable SET sent_converted = "%s" WHERE sent_id = %s' % (text_replaced, id)


        else:
            sql = "UPDATE SentenceTable SET sent_converted = '%s' WHERE sent_id = %s" % (text, id)



        print(sql)

        c.execute(sql)
        self.conn.commit()

        print("Number of rows updated: %d" % c.rowcount)
        return