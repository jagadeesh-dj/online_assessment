import mysql.connector
from powerbi_test_framework.utils.logger import get_logger

logger = get_logger(__name__)

def get_sql_value(query):
    logger.info(f"Executing SQL query: {query}")
    try:
        conn = mysql.connector.connect(
            host="powerbilocal.mysql.database.azure.com",
            database="healthcaredata",
            user="powerbilocal",
            password="Powerbi@1234"
        )
        cursor = conn.cursor()
        cursor.execute(query)
        value = cursor.fetchone()[0]
        conn.close()
        logger.info(f"Successfully executed query and got value: {value}")
        return value
    except Exception as e:
        logger.error(f"Error executing SQL query: {e}")
        raise


def get_sql_table(query):
    logger.info(f"Executing SQL query for table: {query}")
    try:
        conn = mysql.connector.connect(
            host="powerbilocal.mysql.database.azure.com",
            database="healthcaredata",
            user="powerbilocal",
            password="Powerbi@1234"
        )
        cursor = conn.cursor(dictionary=True)  # Get each row as a dict
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        logger.info(f"Successfully executed query and got {len(rows)} rows.")
        return rows
    except Exception as e:
        logger.error(f"Error executing SQL query for table: {e}")
        raise

# def get_mssql_connection(server, database, username=None, password=None, use_windows_auth=False):
#     logger.info(f"Attempting to connect to MS SQL Server: {server}/{database}")
#     try:
#         if use_windows_auth:
#             conn_str = (
#                 f"DRIVER={{ODBC Driver 17 for SQL Server}};"
#                 f"SERVER={server};"
#                 f"DATABASE={database};"
#                 f"Trusted_Connection=yes;"
#             )
#         else:
#             if not username or not password:
#                 raise ValueError("Username and password are required for SQL Server Authentication.")
#             conn_str = (
#                 f"DRIVER={{ODBC Driver 17 for SQL Server}};"
#                 f"SERVER={server};"
#                 f"DATABASE={database};"
#                 f"UID={username};"
#                 f"PWD={password};"
#             )
        
#         conn = pyodbc.connect(conn_str)
#         logger.info("Successfully connected to MS SQL Server.")
#         return conn
#     except pyodbc.Error as ex:
#         sqlstate = ex.args[0]
#         logger.error(f"Error connecting to MS SQL Server: {sqlstate} - {ex}")
#         raise
#     except Exception as e:
#         logger.error(f"An unexpected error occurred during MS SQL connection: {e}")
#         raise

# def get_mssql_value(query, server, database, username=None, password=None, use_windows_auth=False):
#     logger.info(f"Executing MS SQL query: {query}")
#     conn = None
#     cursor = None
#     try:
#         conn = get_mssql_connection(server, database, username, password, use_windows_auth)
#         cursor = conn.cursor()
#         cursor.execute(query)
#         value = cursor.fetchone()
#         if value:
#             value = value[0]
#         logger.info(f"Successfully executed MS SQL query and got value: {value}")
#         return value
#     except Exception as e:
#         logger.error(f"Error executing MS SQL query: {e}")
#         raise
#     finally:
#         if cursor:
#             cursor.close()
#         if conn:
#             conn.close()

# def get_mssql_table(query, server, database, username=None, password=None, use_windows_auth=False):
#     logger.info(f"Executing MS SQL query for table: {query}")
#     conn = None
#     cursor = None
#     try:
#         conn = get_mssql_connection(server, database, username, password, use_windows_auth)
#         cursor = conn.cursor()
        
#         # Fetch column names for dictionary conversion
#         cursor.execute(query)
#         columns = [column[0] for column in cursor.description]
        
#         rows = []
#         for row in cursor.fetchall():
#             rows.append(dict(zip(columns, row)))
            
#         logger.info(f"Successfully executed MS SQL query and got {len(rows)} rows.")
#         return rows
#     except Exception as e:
#         logger.error(f"Error executing MS SQL query for table: {e}")
#         raise
#     finally:
#         if cursor:
#             cursor.close()
#         if conn:
#             conn.close()



# # AZURE_SQL_CONNECTIONSTRING='Driver={ODBC Driver 18 for SQL Server};Server=tcp:devtestmssql.database.windows.net,1433;Database=testing;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30'


# # load_dotenv("config.env")
# # logger = logging.getLogger()
# # logger.setLevel(logging.DEBUG)

# # app = func.FunctionApp(http_auth_level=func.AuthLevel.ADMIN)

# # #ms sql connection
# # server = os.getenv('server')
# # database = os.getenv('database')

# # def get_connection():
# #     # return pymssql.connect(
# #     #     server=server,
# #     #     user=uid,
# #     #     password=password,
# #     #     database=database
# #     # )
# #     try:
# #         credential = identity.DefaultAzureCredential(exclude_interactive_browser_credential=False)
# #         token_bytes = credential.get_token("https://database.windows.net/.default").token.encode("UTF-16-LE")
# #         token_struct = struct.pack(f'<I{len(token_bytes)}s', len(token_bytes), token_bytes)
# #         SQL_COPT_SS_ACCESS_TOKEN = 1256  # This connection option is defined by microsoft in msodbcsql.h
# #         conn = pyodbc.connect(AZURE_SQL_CONNECTIONSTRING, attrs_before={SQL_COPT_SS_ACCESS_TOKEN: token_struct})
# #         print("connected")
# #         return conn
# #     except Exception as e:
# #         print(str(e))