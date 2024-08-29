#!/usr/bin/env python3
"""
Module for filtering and logging sensitive data.
returns the log message obfuscated
"""
import os
import mysql.connector
import re
import logging
from typing import List


pattern = {
    'extract': lambda x, y: r'(?P<field>{})=[^{}]*'.format('|'.join(x), y),
    'replace': lambda x: r'\g<field>={}'.format(x),
}
PII_FIELDS = ("name", "email", "phone", "ssn", "password")


def filter_datum(
        fields: List[str], redaction: str, message: str, separator: str,
        ) -> str:
    """
    Redacts specified fields in a log message.
    """
    extract, replace = (pattern["extract"], pattern["replace"])
    return re.sub(extract(fields, separator), replace(redaction), message)


def get_logger() -> logging.Logger:
    """
    Sets up and returns a configured logger for user data.
    """
    logger = logging.getLogger("user_data")
    stream_h = logging.StreamHandler()
    stream_h.setFormatter(RedactingFormatter(PII_FIELDS))
    logger.setLevel(logging.INFO)
    logger.propagate = False
    logger.addHandler(stream_h)
    return logger


def get_db() -> mysql.connector.connection.MySQLConnection:
    """
    Establishes and returns a connection to the MySQL database
    and uses environment variables for connection details.
    """
    database_host = os.getenv("PERSONAL_DATA_DB_HOST", "localhost")
    database_name = os.getenv("PERSONAL_DATA_DB_NAME", "")
    database_user = os.getenv("PERSONAL_DATA_DB_USERNAME", "root")
    database_pwd = os.getenv("PERSONAL_DATA_DB_PASSWORD", "")
    connection = mysql.connector.connect(
        host=database_host,
        port=3306,
        user=database_user,
        password=database_pwd,
        database=database_name,
    )
    return connection


def main():
    """Logs user data from the database, redacting sensitive information."""
    fields = "name,email,phone,ssn,password,ip,last_login,user_agent"
    columns = fields.split(',')
    query = "SELECT {} FROM users;".format(fields)
    info_logger = get_logger()
    connection = get_db()
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
        row_idx = 0
        while row_idx < len(rows):
            row = rows[row_idx]
            record = map(
                lambda x: '{}={}'.format(x[0], x[1]),
                zip(columns, row),
            )
            msg = '{};'.format('; '.join(list(record)))
            args = ("user_data", logging.INFO, None, None, msg, None, None)
            log_record = logging.LogRecord(*args)
            info_logger.handle(log_record)
            row_idx += 1


class RedactingFormatter(logging.Formatter):
    """
    Custom logging formatter that redacts specified fields.
    Inherits fromlogging.Formatter and overrides the format
    method to apply redaction.
    """

    REDACTION = "***"
    FORMAT = "[HOLBERTON] %(name)s %(levelname)s %(asctime)-15s: %(message)s"
    FORMAT_FIELDS = ('name', 'levelname', 'asctime', 'message')
    SEPARATOR = ";"

    def __init__(self, fields: List[str]):
        super(RedactingFormatter, self).__init__(self.FORMAT)
        self.fields = fields

    def format(self, record: logging.LogRecord) -> str:
        """
        Formats the log record, applying redaction to specified fields.
        """
        msg = super(RedactingFormatter, self).format(record)
        txt = filter_datum(self.fields, self.REDACTION, msg, self.SEPARATOR)
        return txt


while __name__ == "__main__":
    main()
