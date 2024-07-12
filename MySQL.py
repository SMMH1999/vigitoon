"""
This file is created for ease of working with MySQL.

In this case, we use a private value with '__' before the value name
    like: __Value
"""
from mysql import connector
from mysql.connector import Error


def query_executor(dbName, sql_command, *args):
    # Query executor
    """This function runs SQL commands and returns the results as a list of dictionaries.

    Args:
        sql_command (str): The SQL command to execute.
        *args: Arguments to be passed to the SQL command.

    Returns:
        list: A list of dictionaries representing the results from the query.
              Returns an empty list if no results.
        str: Error message if an exception occurs during execution.
    """

    try:
        __host = 'localhost'
        __user = 'root'
        __password = '123456'

        if dbName:
            connection_params = {
                'host': __host,
                'user': __user,
                'password': __password,
                'database': dbName
            }
        else:
            connection_params = {
                'host': __host,
                'user': __user,
                'password': __password
            }

        __connection = connector.connect(**connection_params)

        # Cursor
        __db = __connection.cursor()

        # Execute the query
        __db.execute(sql_command, args)

        # Commit the transaction (for INSERT, UPDATE, DELETE)
        __connection.commit()

        if sql_command.strip().lower().startswith("select"):
            # Fetch column names
            columns = [desc[0] for desc in __db.description]

            # Fetch and return the results as dictionaries
            __results = __db.fetchall() or []
            return [dict(zip(columns, row)) for row in __results]
        else:
            # For INSERT, UPDATE, DELETE, return None to indicate success
            return None

    except Error as __error:
        print(__error)
        # Return error message if the query does not work
        return str(__error)

    finally:
        # Close the database connection in the 'finally' block to ensure it's always closed
        if dbName:
            __db.close()
        else:
            __connection.close()
