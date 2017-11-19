# -*- coding: utf-8 -*-
"""连接MYSQL"""

import mysql.connector

from waimai import settings

cnx = mysql.connector.connect(
    user=settings.MYSQL_USER,
    password=settings.MYSQL_PASSWD,
    host=settings.MYSQL_HOST,
    database=settings.MYSQL_DBNAME
)

cur = cnx.cursor(buffered=True)
