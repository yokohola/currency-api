import os
import urllib.parse
from peewee import PostgresqlDatabase

os.environ["DATABASE_URL"] = "1"
print(os.environ.get("DATABASE_URL"))


# x = os.environ.get("DATABASE_URL")
#
# url = urllib.parse.urlparse(os.environ.get("DATABASE_URL"))
# db = PostgresqlDatabase(host=url.hostname, user=url.username, password=url.password, port=url.port,
#                             database=url.path[1:])