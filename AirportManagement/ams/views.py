from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
#from .db_extraction import DBConnection
from django.db import connections
import pandas as pd

class DBConnection:
    """
    Class for database connection
    read_table - returns a dataFrame from query
    execute_query - executes a data manipulation query
    close - used to close the connection created
    execute_count - executes the query for selection and returns count of records
    """
    def __init__(self, connection_name):
        self.conn = connections[connection_name]

    def read_table(self, query):
        """executes the query and returns df"""
        return pd.read_sql(query, self.conn)

    def execute_query(self,query):
        """executes the query for insertion or stored procedure execution"""
        cur = self.conn.cursor()
        cur.execute(query)
        cur.close()
        self.conn.commit()

    def close(self):
        """closes the connection created"""
        self.conn.close()

    def execute_count(self, query):
        """executes the query for selection and returns count of records"""
        cursor = self.conn.cursor()
        data = cursor.execute(query)
        count = cursor.fetchone()[0]
        cursor.close()
        return count


@api_view(['GET'])
def user_directory(request):
    # This function is called when 'users' is mentioned in url.
    return render(request, 'user_directory.html')

@api_view(['GET'])
def get_user_details(request):
    """
    This function is called when 'getuserdetails' is mentioned in url.
    This request is made from ajax call from datatable under User directory,
    to render the dataTable and provide additional functionality like sorting, pagination
    This function handles
    - parameter extraction
    - DB connection
    - renders DataTable
    """
    
    header = ["e_name", "e_phonenumber", "e_city", "e_state", "e_country"]

    # Extracting params from url
    try:
        
        start = request.GET['start']
        length = request.GET['length']
        search = request.GET['search[value]']
        # Below parameters are available based on sorting activity(optional)
        sort_col = request.GET.get('order[0][column]')
        sort_dir = request.GET.get('order[0][dir]')
        pass

        print("Extracted start,length,search,"
                     "sort_col,sort_dir {},{},{},{},{} using GET "
                     "request".format( start, length, search, sort_col, sort_dir))
    except Exception as e:
        print("Error occurred while parameter extraction."
                "Exception type:{}, Exception value:{} occurred while parameter "
                "extraction.".format(type(e), e))
        raise

    # Extracting data from app DB
    search = search.lower().replace("'","''")

    if sort_col is None:
        query = """SELECT e_name, e_phonenumber, e_city, e_state, e_country from personal_details_view
        where LOWER(e_name) like '%{}%'
        or LOWER(e_phonenumber) like '%{}%' or LOWER(e_city) like '%{}%'
        or LOWER(e_state) like '%{}%' or LOWER(e_country) like '%{}%'
        limit {} offset {}""".format(search, search, search, search, search, length, start)
    else:
        sort_col = str(int(sort_col) + 1)
        query = """SELECT e_name, e_phonenumber, e_city, e_state, e_country from personal_details_view
        where LOWER(e_name) like '%{}%'
        or LOWER(e_phonenumber) like '%{}%' or LOWER(e_city) like '%{}%'
        or LOWER(e_state) like '%{}%' or LOWER(e_country) like '%{}%' order by {} {} 
        limit {} offset {}""".format(search, search, search, search, search, sort_col, sort_dir, length, start)

    count_query = "SELECT COUNT(*) FROM personal_details_view"
    filtered_count_query = """SELECT count(*) from personal_details_view
                            where LOWER(e_name) like '%{}%'
                            or LOWER(e_phonenumber) like '%{}%' or LOWER(e_city) like '%{}%'
                            or LOWER(e_state) like '%{}%' or LOWER(e_country) like '%{}%'
                            """.format(search, search, search, search, search)
    try:
        # Data extraction from DB
        appdb_connection = DBConnection('default')
        app_df = appdb_connection.read_table(query)
        total_count = appdb_connection.execute_count(count_query)
        filtered_count = appdb_connection.execute_count(filtered_count_query)

        # converting column name to lower case
        app_df.columns = [column.lower() for column in app_df.columns]
        datatable_json = []

        # Preparing dataTable records
        for i in range(app_df.shape[0]):
            temp_list = []
            for column_name in header:
                temp_list.append((app_df[column_name][i]))

            datatable_json.append(temp_list)

    except Exception as e:
        print("Error occurred while extracting data from application DB."
                      "Exception type:{}, Exception value:{} occurred while extracting data from application DB.".format(
            type(e), e))
        raise
    finally:
        appdb_connection.close()

    return Response({'recordsTotal': total_count, 'recordsFiltered': filtered_count, 'data': datatable_json})

