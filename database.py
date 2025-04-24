import mysql.connector

import boto3
import os

def get_param(name):
    ssm = boto3.client('ssm', region_name='us-east-1')  # atau region sesuai EC2-mu
    response = ssm.get_parameter(Name=name, WithDecryption=True)
    return response['Parameter']['Value']




class SQL:
    def __init__(self):
        self.connection = self.create_connection()

    def create_connection(self):
        try:
            DB_HOST = get_param('/myapp/DB_HOST')
            DB_USER = get_param('/myapp/DB_USER')
            DB_PASSWORD = get_param('/myapp/DB_PASSWORD')
            DB_NAME = get_param('/myapp/DB_NAME')
            self.connection = mysql.connector.connect(
                host="rentaldb.cdm4ewgaio3j.us-east-1.rds.amazonaws.com",
                user="admin",
                password="FNDDatabase.1",
                database="car_rental"
            )
            print("Connection to database is successful")
            return self.connection

        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return None

    def execute_query(self, query, data=None):
        cursor = self.connection.cursor()
        try:
            if data:
                cursor.execute(query, data)
            else:
                cursor.execute(query)
            self.connection.commit()
            print("Query runs successfully")
        
        except mysql.connector.Error as err:
            print(f"Error: {err}")

        finally:
            cursor.close()

    def fetch_data(self, query, data=None):
        cursor = self.connection.cursor(dictionary=True)
        try:
            if data:
                cursor.execute(query, data)
            else:
                cursor.execute(query)
            result = cursor.fetchall()
            return result
        
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return None
        
        finally:
            cursor.close()

    # Bagian CRUD user
    def create_user(self, name, email, password, username, role="member"):
        query = """
        INSERT INTO user(name_user, email_user, password_user, username_user, role_user)
        VALUES
        (%s, %s, %s, %s, %s)
        """
        data = (name, email, password, username, role)
        self.execute_query(query, data)

    def get_all_users(self):
        query = "SELECT * FROM user"
        return self.fetch_data(query)

    def update_user(self, user_id, name=None, email=None, password=None, username=None, role=None):
        query = "UPDATE user SET "
        updates = []
        data = []

        if name:
            updates.append("name_user = %s")
            data.append(name)
        if email:
            updates.append("email_user = %s")
            data.append(email)
        if password:
            updates.append("password_user = %s")
            data.append(password)
        if username:
            updates.append("username_user = %s")
            data.append(username)
        if role:
            updates.append("role_user = %s")
            data.append(role)

        query += ", ".join(updates) + " WHERE ID_user = %s"
        data.append(user_id)
        self.execute_query(query, data)

    def delete_user(self, user_id):
        query = "DELETE FROM user WHERE ID_user = %s"
        data = (user_id,)
        self.execute_query(query, data)

    # Bagian CRUD car
    def create_car(self, model_id, license_plate, availability="available"):
        query = """
        INSERT INTO car (model_id, license_plate, availability)
        VALUES (%s, %s, %s)
        """
        data = (model_id, license_plate, availability)
        self.execute_query(query, data)

    def get_all_cars(self):
        query = "SELECT * FROM car"
        return self.fetch_data(query)

    # Bagian CRUD car_model
    def create_car_model(self, brand, year, model, price, image):
        query = """
        INSERT INTO car_model (brand_car, year_manufactured, model_car, price_car, image_car)
        VALUES (%s, %s, %s, %s, %s)
        """
        data = (brand, year, model, price, image)
        self.execute_query(query, data)

    def get_all_car_models(self):
        query = "SELECT * FROM car_model"
        return self.fetch_data(query)

    # Bagian CRUD rental
    def create_rental(self, user_id, car_id, rental_date, return_date, approval_status="pending"):
        query = """
        INSERT INTO rental (user_id, car_id, rental_date, return_date, approval_status)
        VALUES (%s, %s, %s, %s, %s)
        """
        data = (user_id, car_id, rental_date, return_date, approval_status)
        self.execute_query(query, data)

    def delete_rental(self, ID_rental):
        query = """
        DELETE FROM rental 
        WHERE ID_rental = %s
        """
        data = (ID_rental,)
        self.execute_query(query, data)

    def get_recent_rent(self, amount_car):
        query = """
        SELECT ID_rental, car_id FROM rental 
        ORDER BY ID_rental DESC 
        LIMIT %s
        """
        data = (amount_car, )
        return self.fetch_data(query, data)

    def get_all_rentals(self):
        query = "SELECT * FROM rental"
        return self.fetch_data(query)
    
    def update_status_rental(self, rental_id, status):
        query = """
        UPDATE rental 
        SET approval_status = %s 
        WHERE ID_rental = %s;
        """
        data = (status, rental_id, )
        self.execute_query(query, data)

    def is_username_taken(self, username):
        query = "SELECT COUNT(*) FROM user WHERE username_user = %s"
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, (username,))
            result = cursor.fetchone()
            return True if result[0] > 0 else False
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return False
        finally:
            cursor.close()

    def is_email_taken(self, email):
        query = "SELECT COUNT(*) FROM user WHERE email_user = %s"
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, (email,))
            result = cursor.fetchone()
            return True if result[0] > 0 else False
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return False
        finally:
            cursor.close()
