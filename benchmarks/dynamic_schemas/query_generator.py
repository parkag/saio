import random
from data_generator import *


class BaseRandomTable(object):

    def __init__(self, table_name, ncols, datatypes):
        self.name = table_name
        self.ncols = ncols
        self.datatypes = datatypes
        self.columns = []

    def generate_columns(self):
        for i in xrange(self.ncols):
            datatype = random.choice(self.datatypes)
            column_name = "col_{num}".format(num=i)
            column = Column(column_name, datatype)
            self.columns.append(column)

    def sql(self):
        sql = "DROP TABLE IF EXISTS {table_name};\n".format(
            table_name=self.name)
        sql += """CREATE TABLE {table_name}(
                \r{columns_section}
            );
        """.format(
            table_name=self.name,
            columns_section=",\n".join([col.sql() for col in self.columns])
        )
        return sql


class Column(object):
    
    def __init__(self, name, datatype, constraints=[]):
        self.name = name
        self.datatype = datatype
        self.constraints = constraints

    def sql(self):
        sql = "{name} {datatype}".format(
            name=self.name,
            datatype=self.datatype,
        )
        if self.constraints:
            sql = "{sql} {constraints}".format(
                sql=sql,
                constraints=" ".join(self.constraints)
            )
        return sql


class RandomTableDataGenerator(object):

    def __init__(self, table, nrows=1):
        self.table = table
        self.nrows = nrows

    def sql(self):
        sql = """INSERT INTO {table_name}({column_names})
            VALUES
                {values_data};""".format(
                    table_name=self.table.name,
                    column_names=", ".join(
                        column.name for column in self.table.columns),
                    values_data=''
                )
        return sql


class RandomSchemaDataGenerator(object):

    def __init__(self, tables):
        pass


class RandomSchema(object):

    def __init__(self, ntables, data):
        self.ntables = ntables
        self.tables = []

    def generate_tables(self):
        for i in xrange(self.ntables):
            table_name = "table_{num}".format(num=i)
            ncols = random.randint(3, 10)
            table = BaseRandomTable(
                table_name, ncols=ncols, #datatypes=standard_datatypes)
                datatypes=['text'])
            # TODO: dynamic column distribution
            table.generate_columns()
            self.tables.append(table)

    def sql(self):
        sql = '--\n'
        sql += """DROP SCHEMA IF EXISTS test_view CASCADE;\n
            CREATE SCHEMA test_view;\n
            SET SEARCH_PATH = test_view, test_data;\n"""
        for table in self.tables:
            sql += table.sql()

        return sql


class RandomQuery(object):

    def __init__(self, schema, joins, left_joins, right_joins):
        self.schema = schema
        self.joins = joins
        self.left_joins = left_joins
        self.right_joins = right_joins
        self.already_joined = []

    def _get_from_section(self):
        from_section = '' + self.schema.tables[0].name
        
        self.already_joined.append(self.schema.tables[0])
        
        for i in xrange(self.joins):
            from_section += self._get_join_part("JOIN")
        for i in xrange(self.left_joins):
            from_section += self._get_join_part("LEFT JOIN")
        for i in xrange(self.right_joins):
            from_section += self._get_join_part("RIGHT JOIN")
        
        return from_section

    def _get_join_part(self, join_type):
        n_tables = len(self.schema.tables)
        table1 = self.schema.tables[0]
        table2 = random.choice(self.schema.tables)

        while table2 in self.already_joined:
            table2 = random.choice(self.schema.tables)

        join_part = " {join_type} {tab} ON {boolean_expression}\n".format(
            join_type=join_type,
            tab=table2.name,
            boolean_expression=self._get_boolean_expression(table1, table2)
        )
        self.already_joined.append(table2)
        return join_part

    def _get_boolean_expression(self, table1, table2):
        """extend this"""
        col1 = random.choice(table1.columns)
        col2 = random.choice(table2.columns)
        return "{table1}.{col1} = {table2}.{col2}".format(
            table1=table1.name,
            table2=table2.name,
            col1=col1.name,
            col2=col2.name
        )

    def sql(self):
        sql = """SELECT * FROM {from_section}
        """.format(from_section=self._get_from_section())
        return sql

    def explain_sql(self):
        sql = """ANALYZE;
        EXPLAIN (FORMAT JSON)""" + self.sql() + ";"
        return sql 


class RandomNestedQuery(RandomQuery):
    """Generated queries with subqueries"""

    def __init__(
        self, schema, joins, left_joins, right_joins, nest_level=1):
        RandomQuery.__init__(
            self, schema, joins, left_joins, right_joins)
        self.nest_level = nest_level

    def _get_join_part(self, join_type):
        n_tables = len(self.schema.tables)
        table1 = self.schema.tables[0]
        table2 = random.choice(self.schema.tables)

        if table2 in self.already_joined:
            join_part = """ {join_type} ({subquery}) AS {subquery_name} 
                ON TRUE\n""".format(
                join_type=join_type,
                subquery=self._get_subquery(),
                subquery_name='subquery_'+str(table1.name)+'_'+str(random.randint(1,1000))
            )
        else:
            join_part = RandomQuery._get_join_part(self, join_type)
        return join_part

    def _get_subquery(self):
        n_tables = len(self.schema.tables)
        if self.nest_level == 1:
            query = RandomQuery(self.schema, 2, 2, 2)
        else:
            query = RandomNestedQuery(self.schema, 2, 2, 2, self.nest_level-1)
        return query.sql()


