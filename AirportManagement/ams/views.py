import os
from django.shortcuts import redirect, render
from numpy import require
from rest_framework.decorators import api_view
from rest_framework.response import Response
#from .db_extraction import DBConnection
from django.db import connections
import pandas as pd
from . import urls
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password



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


def login(request):
    # This function is called when 'login' is mentioned in url.
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username = username, password = password)
        if user is not None:
            auth.login(request, user)
            return redirect('home')
        else:
            messages.info(request, 'Invalid credentials')
            return redirect('login')
    else:
        return render(request, 'login.html')


def logout(request):
    # This function is called when 'logout' is mentioned in url.
    auth.logout(request)
    return redirect('login')
    
@api_view(['GET'])
@login_required(login_url='/login/')
def home(request):
    # This function is called when '' is mentioned in url.
    appdb_connection = DBConnection('default')
    count_query_unairworthy = "select count(*) from airplane where airworthy = 0"
    count_query_airworthy = "select count(*) from airplane where airworthy > 0"
    airworthy_count = appdb_connection.execute_count(count_query_airworthy)
    unairworthy_count = appdb_connection.execute_count(count_query_unairworthy)
    data = []
    label = []
    data.append(airworthy_count)
    label.append("Airworthy")
    data.append(unairworthy_count)
    label.append("Not Airworthy")

    return render(request, 'home.html', {
        'labels': label,
        'data': data,
    })

@login_required(login_url='/login/')
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
    
    header = ["e_name", "e_phonenumber", "e_city", "e_state", "e_country", "u_name"]

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
        query = """SELECT e_name, e_phonenumber, e_city, e_state, e_country, u_name from personal_details_union_view
        where LOWER(e_name) like '%{}%'
        or LOWER(e_phonenumber) like '%{}%' or LOWER(e_city) like '%{}%'
        or LOWER(e_state) like '%{}%' or LOWER(e_country) like '%{}%' or LOWER(u_name) like '%{}%' 
        limit {} offset {}""".format(search, search, search, search, search, search, length, start)
    else:
        sort_col = str(int(sort_col) + 1)
        query = """SELECT e_name, e_phonenumber, e_city, e_state, e_country, u_name from personal_details_union_view
        where LOWER(e_name) like '%{}%'
        or LOWER(e_phonenumber) like '%{}%' or LOWER(e_city) like '%{}%' or LOWER(u_name) like '%{}%' 
        or LOWER(e_state) like '%{}%' or LOWER(e_country) like '%{}%' order by {} {} 
        limit {} offset {}""".format(search, search, search, search, search, search, sort_col, sort_dir, length, start)

    count_query = "SELECT COUNT(*) FROM personal_details_union_view"
    filtered_count_query = """SELECT count(*) from personal_details_union_view
                            where LOWER(e_name) like '%{}%' or LOWER(u_name) like '%{}%' 
                            or LOWER(e_phonenumber) like '%{}%' or LOWER(e_city) like '%{}%'
                            or LOWER(e_state) like '%{}%' or LOWER(e_country) like '%{}%'
                            """.format(search, search, search, search, search, search)
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


@api_view(['GET'])
@login_required(login_url='/login/')
def medical_test(request):
    # This function is called when 'employeemanagement' is mentioned in url.
    return render(request, 'medical_test.html')



@api_view(['GET'])
def get_traffic_controller_details(request):

    header = ["e_ssn", "most_recent_exam", "safety"]

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


       
    print(request.user)
    query = """SELECT t.e_ssn,t.most_recent_exam,t.safety from traffic_controllers as t
    ,employee as e  where e.username like '%{}%' and e.e_ssn = t.e_ssn
    limit {} offset {}""".format(request.user, length, start)




    try:
        # Data extraction from DB
        appdb_connection = DBConnection('default')
        app_df = appdb_connection.read_table(query)
        total_count = 1
        filtered_count = 1

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


@api_view(['POST'])
def update_traffic_controller_details(request):
    """
    This function is called when 'updateemployeedetails' is mentioned in url.
    This request is made from ajax call from datatable under Edit button,
    to update employee details
    This function handles
    - parameter extraction
    - DB connection
    - DB record update
    """
    
    # Extracting params from url
    try:
        
        e_ssn = request.POST['e_ssn']
        tc_date = request.POST['most_recent_exam']
        test_results = request.POST.get('test_results')

        print(test_results)
        print(test_results)
        print(test_results)
        print(test_results)

        print("Extracted  {},{},{} using GET "
                     "request".format( e_ssn,tc_date,test_results))
    except Exception as e:
        print("Error occurred while parameter extraction."
                "Exception type:{}, Exception value:{} occurred while parameter "
                "extraction.".format(type(e), e))
        response = Response({"error": str(e)})
        response.status_code = 500 # To announce that the user isn't allowed to publish
        return response

    query = """UPDATE traffic_controllers 
                SET `e_ssn` = '{}',`most_recent_exam` = '{}',`safety` = '{}' 
                where  `e_ssn` = '{}'""".format(e_ssn, tc_date, test_results,e_ssn)
                                    
    print(query)
    try:
        appdb_connection = DBConnection('default')
        appdb_connection.execute_query(query)
        
    except Exception as e:
        print("Error occurred while saving data."
                "Exception type:{}, Exception value:{} while saving "
                "data.".format(type(e), e))
        response = Response({"error": str(e)})
        response.status_code = 500 # To announce that the user isn't allowed to publish
        return response
        
    return Response({'data': 'success'})


















@api_view(['GET'])
@login_required(login_url='/login/')
def admin_employee_management(request):
    # This function is called when 'employeemanagement' is mentioned in url.
    return render(request, 'employee_management.html')

@api_view(['GET'])
def get_employee_details(request):
    """
    This function is called when 'getemployeedetails' is mentioned in url.
    This request is made from ajax call from datatable under User directory,
    to render the dataTable and provide additional functionality like sorting, pagination
    This function handles
    - parameter extraction
    - DB connection
    - renders DataTable
    """
    header = ["e_ssn", "e_name", "e_phonenumber", "username", "e_street", "e_city", "e_state", "e_country", "e_pincode", "e_salary"]

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
        query = """SELECT e_ssn, e_name, e_phonenumber, username, e_street, e_city, e_state, e_country, e_pincode, e_salary from employee
        where LOWER(e_name) like '%{}%' or LOWER(e_ssn) like '%{}%' or LOWER(username) like '%{}%'
        or LOWER(e_phonenumber) like '%{}%' or LOWER(e_city) like '%{}%' or LOWER(e_street) like '%{}%'
        or LOWER(e_state) like '%{}%' or LOWER(e_country) like '%{}%' or LOWER(e_pincode) like '%{}%'
        or LOWER(e_salary) like '%{}%' limit {} offset {}""".format(search, search, search, search, search, search, search, search, search, search, length, start)
    else:
        sort_col = str(int(sort_col) + 1)
        query = """SELECT e_ssn, e_name, e_phonenumber, username, e_street, e_city, e_state, e_country, e_pincode, e_salary from employee
        where LOWER(e_name) like '%{}%' or LOWER(e_ssn) like '%{}%' or LOWER(username) like '%{}%'
        or LOWER(e_phonenumber) like '%{}%' or LOWER(e_city) like '%{}%' or LOWER(e_street) like '%{}%'
        or LOWER(e_state) like '%{}%' or LOWER(e_country) like '%{}%' or LOWER(e_pincode) like '%{}%'
        or LOWER(e_salary) like '%{}%' order by {} {}
        limit {} offset {}""".format(search, search, search, search, search, search, search, search, search, search, sort_col, sort_dir, length, start)

    count_query = "SELECT COUNT(*) FROM employee"
    filtered_count_query = """SELECT count(*) from employee
                            where LOWER(e_name) like '%{}%' or LOWER(e_ssn) like '%{}%' or LOWER(username) like '%{}%'
                            or LOWER(e_phonenumber) like '%{}%' or LOWER(e_city) like '%{}%' or LOWER(e_street) like '%{}%'
                            or LOWER(e_state) like '%{}%' or LOWER(e_country) like '%{}%' or LOWER(e_pincode) like '%{}%'
                            or LOWER(e_salary) like '%{}%'
                            """.format(search, search, search, search, search, search, search, search, search, search)
    #print(filtered_count_query)
    #print(count_query)
    #print(query)
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


@api_view(['POST'])
def insert_employee_details(request):
    """
    This function is called when 'insertemployeedetails' is mentioned in url.
    This request is made from ajax call from datatable under Add button,
    to add employee details
    This function handles
    - parameter extraction
    - DB connection
    - DB record creation
    """

    # Extracting params from url
    try:
        
        e_ssn = request.POST['e_ssn']
        e_name = request.POST['e_name']
        e_street = request.POST['e_street']
        e_city = request.POST['e_city']
        e_state = request.POST['e_state']
        e_country = request.POST['e_country']
        e_pincode = request.POST['e_pincode']
        e_phonenumber = request.POST['e_phonenumber']
        role = request.POST['role']
        e_salary = request.POST['e_salary']
        username = request.POST['username']
        password = request.POST['password']
        e_uid = request.POST['u_id']
        union_membership_number = request.POST['union_membership_number']


        print("Extracted  {},{},{},{},{},{},{},{},{},{},{},{},{} using GET "
                     "request".format( e_ssn, e_name, e_street, e_city, e_state, e_country, e_pincode, e_phonenumber,
                     e_salary, username, password, e_uid, union_membership_number))
    except Exception as e:
        print("Error occurred while parameter extraction."
                "Exception type:{}, Exception value:{} occurred while parameter "
                "extraction.".format(type(e), e))
        response = Response({"error": str(e)})
        response.status_code = 500 # To announce that the user isn't allowed to publish
        return response
        
    query = """INSERT INTO employee (`e_ssn`, `e_name`, `e_street`, `e_state`, `e_city`, `e_country`, 
                                    `e_pincode`, `e_phonenumber`, `e_salary`, `username`, `password`, 
                                    `u_id`, `union_membership_number`) 
                                    VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}',
                                     '{}', '{}', '{}')
                                    """.format(e_ssn, e_name, e_street, e_state, e_city, e_country,
                                    e_pincode, e_phonenumber, e_salary, username, password, e_uid, union_membership_number)
    
    table_name = ''                                    
    if role == "technician":
        table_name = "technicians"
    elif role == "traffic":
        table_name = "traffic_controllers"
    elif role == 'faa':
        table_name = 'faa_admin'
    
    query2 = "INSERT INTO " + table_name + "(e_ssn) VALUES('{}')".format(e_ssn)
    print(query2)
    try:
        appdb_connection = DBConnection('default')
        appdb_connection.execute_query(query)
        if role != "others":
            appdb_connection.execute_query(query2)

        # Storing the details in Django user object for authentication purpose
        user = User.objects.create_user(username=username, password = password, first_name = e_name)
        user.save()
    except Exception as e:
        print("Error occurred while saving data."
                "Exception type:{}, Exception value:{} while saving "
                "data.".format(type(e), e))
        response = Response({"error": str(e)})
        response.status_code = 500 # To announce that the user isn't allowed to publish
        return response    

    return Response({'data': 'success'})

@api_view(['POST'])
def update_employee_details(request):
    """
    This function is called when 'updateemployeedetails' is mentioned in url.
    This request is made from ajax call from datatable under Edit button,
    to update employee details
    This function handles
    - parameter extraction
    - DB connection
    - DB record update
    """

    # Extracting params from url
    try:
        
        e_ssn = request.POST['u_e_ssn']
        e_name = request.POST['u_e_name']
        e_street = request.POST['u_e_street']
        e_city = request.POST['u_e_city']
        e_state = request.POST['u_e_state']
        e_country = request.POST['u_e_country']
        e_pincode = request.POST['u_e_pincode']
        e_phonenumber = request.POST['u_e_phonenumber']
        e_salary = request.POST['u_e_salary']
        username = request.POST['u_username']
        #e_uid = request.POST['u_id']
        #union_membership_number = request.POST['union_membership_number']


        print("Extracted  {},{},{},{},{},{},{},{},{} using GET "
                     "request".format( e_ssn, e_name, e_street, e_city, e_state, e_country, e_pincode, e_phonenumber,
                     e_salary))
    except Exception as e:
        print("Error occurred while parameter extraction."
                "Exception type:{}, Exception value:{} occurred while parameter "
                "extraction.".format(type(e), e))
        response = Response({"error": str(e)})
        response.status_code = 500 # To announce that the user isn't allowed to publish
        return response

    query = """UPDATE employee 
                SET `e_ssn` = '{}', `e_name` = '{}', `e_street` = '{}', `e_state` = '{}',
                `e_city` = '{}', `e_country` = '{}', `e_pincode` = '{}', `e_phonenumber` = '{}',
                `e_salary` = '{}'
                where  `e_ssn` = '{}'""".format(e_ssn, e_name, e_street, e_state, e_city, e_country,
                e_pincode, e_phonenumber, e_salary, e_ssn)
                                    
    print(query)
    try:
        appdb_connection = DBConnection('default')
        appdb_connection.execute_query(query)

        #Update first name in the user model as it is the only details that we are storing
        User.objects.filter(username=username).update(first_name = e_name)
        

    except Exception as e:
        print("Error occurred while saving data."
                "Exception type:{}, Exception value:{} while saving "
                "data.".format(type(e), e))
        response = Response({"error": str(e)})
        response.status_code = 500 # To announce that the user isn't allowed to publish
        return response
        
    return Response({'data': 'success'})


@api_view(['POST'])
def delete_employee_details(request):
    """
    This function is called when 'deleteemployeedetails' is mentioned in url.
    This request is made from ajax call from datatable under Edit button,
    to delete employee details
    This function handles
    - parameter extraction
    - DB connection
    - DB record deletion
    """

    # Extracting params from url
    try:
        
        e_ssn = request.POST['d_e_ssn']
        username = request.POST['d_username']
        print("Extracted  {}, {} using POST "
                     "request".format( e_ssn,username))
    except Exception as e:
        print("Error occurred while parameter extraction."
                "Exception type:{}, Exception value:{} occurred while parameter "
                "extraction.".format(type(e), e))
        response = Response({"error": str(e)})
        response.status_code = 500 # To announce that the user isn't allowed to publish
        return response

    query = """DELETE from employee where `e_ssn` = '{}'
                """.format(e_ssn)
                                    
    print(query)
    try:
        appdb_connection = DBConnection('default')
        appdb_connection.execute_query(query)

        #deleting the record from User model
        User.objects.filter(username=username).delete()


    except Exception as e:
        print("Error occurred while saving data."
                "Exception type:{}, Exception value:{} while saving "
                "data.".format(type(e), e))
        response = Response({"error": str(e)})
        response.status_code = 500 # To announce that the user isn't allowed to publish
        return response
    
    return Response({'data': 'success'})


@api_view(['GET'])
@login_required(login_url='/login/')
def profile(request):
    # This function is called when 'profile' is mentioned in url.
    
    query = """SELECT e_ssn, e_name, e_phonenumber, username, password, e_street, e_city, e_state, e_country, e_pincode from employee
            where username = "{}" """.format(request.user.username)
    try:
        # Data extraction from DB
        appdb_connection = DBConnection('default')
        app_df = appdb_connection.read_table(query)
        context = app_df.to_dict('records')[0]
    except Exception as e:
        print("Error occurred while saving data."
                "Exception type:{}, Exception value:{} while extractng "
                "data.".format(type(e), e))
        response = Response({"error": str(e)})
        response.status_code = 500 
        return response
    finally:
        appdb_connection.close()
        print(context)
    return render(request, 'profile.html', context)


@api_view(['POST'])
def updateprofiledetails(request):
    """
    This function is called when 'updateprofiledetails' is mentioned in url.
    This request is made from ajax call from Profile page,
    to update personal details
    This function handles
    - parameter extraction
    - DB connection
    - DB record update
    """
    print("reached")

    # Extracting params from url
    try:
        
        e_ssn = request.POST['u_e_ssn']
        e_name = request.POST['u_e_name']
        e_street = request.POST['u_e_street']
        e_city = request.POST['u_e_city']
        e_state = request.POST['u_e_state']
        e_country = request.POST['u_e_country']
        e_pincode = request.POST['u_e_pincode']
        e_phonenumber = request.POST['u_e_phonenumber']
        username = request.POST['u_username']
        password = request.POST['u_password']

        print("Extracted  {},{},{},{},{},{},{},{} using GET "
                     "request".format( e_ssn, e_name, e_street, e_city, e_state, e_country, e_pincode, e_phonenumber))
    except Exception as e:
        print("Error occurred while parameter extraction."
                "Exception type:{}, Exception value:{} occurred while parameter "
                "extraction.".format(type(e), e))
        response = Response({"error": str(e)})
        response.status_code = 500 # To announce that the user isn't allowed to publish
        return response

    query = """UPDATE employee 
                SET  `e_name` = '{}', `e_street` = '{}', `e_state` = '{}',
                `e_city` = '{}', `e_country` = '{}', `e_pincode` = '{}', `e_phonenumber` = '{}',
                `password` = '{}'                
                where  `e_ssn` = '{}'""".format(e_name, e_street, e_state, e_city, e_country,
                e_pincode, e_phonenumber, password, e_ssn)
                                    
    print(query)
    try:
        appdb_connection = DBConnection('default')
        appdb_connection.execute_query(query)

        #Update first name and password in the user model as it is the only details that we are storing
        password=make_password(password,hasher='default')
        User.objects.filter(username=username).update(first_name = e_name, password = password)
        

    except Exception as e:
        print("Error occurred while saving data."
                "Exception type:{}, Exception value:{} while saving "
                "data.".format(type(e), e))
        response = Response({"error": str(e)})
        response.status_code = 500 # To announce that the user isn't allowed to publish
        return response
        
    return Response({'data': 'success'})