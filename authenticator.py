import mysql.connector
import uuid
#import json

#with open("/tmp/credentials.json")
#json.dump(users,storage_fil
#usuario contraseña
#json.load
#dumps, s
#el token admin no tiene usuario
#commit
#podemos añadir una timestamp en el value del token, para saber si se ha caducado si es 30 o más.
#se genera un servicio unico con UUID, no se repitan en el mismo proceso
#Puedes tener un timer en otro
#current.adapter.addWithUUID
#usar tox
#integración continua yaml, travis, jenkins, github actions
#Fomrateo con githubs actions con Black
#token = (username, timestamp)
#si usa un token cuyo timestamp es 30 s posterior al time actual se vuelve inutil

auth_table = {'123':"root"} #Mapear token a nombre de usuarios.
admin_token = "123"
conection = mysql.connector.connect(host='localhost',
                        database='authenticator',
                        user='root',
                        password='root',
                        auth_plugin='mysql_native_password'
                        )
mycursor = conection.cursor()

select_query = "SELECT COUNT(1) FROM users WHERE username = '%s' AND password = '%s'"
insert_query = "INSERT INTO users (Username,Password, IsAdmin) VALUES (%s, %s,%s)"
delete_query = "DELETE FROM users WHERE Username = %s"

def refreshAuthorization(user, passwordHash): 
    '''Dado un usuario y su contraseña crea un token si son válidos.'''
    mycursor.execute(select_query, (user,passwordHash)) #como creo token?
    if mycursor.fectchone()[0]:
        auth_table.update({crear_token():(user)})
    else:
        raise iceflix.Unauthorized
    return ''

def isAuthorized(userToken): 
    '''Dado un token devuelves si existe.'''
    return userToken in auth_table

def whois(userToken): 
    '''Dado un Token te da un usuario válido.'''
    if userToken in auth_table:
        return auth_table[userToken]
    else:
        raise iceflix.Unauthorized

def isAdmin(adminToken): 
    '''Dado un token devuelve si es Admin o no. Lo saco del config y hago una comparación simple.'''
    if admin_token == adminToken:
        return auth_table[adminToken][1]
    else:
        raise iceflix.Unauthorized

def addUser(user,passwordhash,adminToken): 
    '''Dado un token admin y un usuario y contraseña metelos en la BBDD.'''
    if isAdmin(adminToken): #Temporary Unvaidable?
        mycursor.execute(insert_query,(user,passwordhash,False)) #se pueden meter admins?
    else:
        raise iceflix.Unauthorized

def removeUser(user, adminToken): 
    '''Dado un user y un token de admin elimina a un usuario de la BBDD.'''
    print(delete_query,user)
    if isAdmin(adminToken): #Temporary Unvaidable?
        mycursor.execute(delete_query,user)
    else:
        raise iceflix.Unauthorized

def crear_token():
    return uuid.uuid4().hex[:6].upper()

def main():
    addUser("jajas","123","123")
    removeUser("root","123")

main()