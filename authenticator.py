import uuid
import json

with open("./files/users.json", "r") as f:
    users = json.load(f)
#podemos añadir una timestamp en el value del token, para saber si se ha caducado si es 30 o más.
#se genera un servicio unico con UUID, no se repitan en el mismo proceso
#Puedes tener un timer en otro
#current.adapter.addWithUUID
#usar tox
#integración continua yaml, travis, jenkins, github actions
#Fomrateo con githubs actions con Black
#token = (username, timestamp)
#si usa un token cuyo timestamp es 30 s posterior al time actual se vuelve inutil

auth_table = {} #Mapear token a nombre de usuario
admin_token = "123"


def refreshAuthorization(user, passwordhash): 
    '''Dado un usuario y su contraseña crea un token si son válidos.'''
    if user in users and users[user] == passwordhash:
        token = crear_token()
        auth_table.update({token:(user)})
        return token
    #else:
    #    raise iceflix.Unauthorized
    return ''

def isAuthorized(userToken): 
    '''Dado un token devuelves si existe.'''
    return userToken in auth_table

def whois(userToken): 
    '''Dado un Token te da un usuario válido.'''
    if userToken in auth_table:
        return auth_table[userToken]
    #else:
    #    raise iceflix.Unauthorized

def isAdmin(adminToken): 
    '''Dado un token devuelve si es Admin o no. Lo saco del config y hago una comparación simple.'''
    return admin_token == adminToken

def addUser(user,passwordhash,adminToken): 
    '''Dado un token admin y un usuario y contraseña metelos en la BBDD.'''
    if isAdmin(adminToken) and not user in users: #Temporary Unvaidable?
         users[user] = passwordhash
         with open("./files/users.json","w") as f:
            json.dump(users, f)
    #else:
     #   raise iceflix.Unauthorized

def removeUser(user, adminToken): 
    '''Dado un user y un token de admin elimina a un usuario de la BBDD.'''
    if isAdmin(adminToken) and user in users: #Temporary Unvaidable?
         del users[user]
         with open("./files/users.json","w") as f:
            json.dump(users, f)
    #else:
    #    raise iceflix.Unauthorized

def crear_token():
    return uuid.uuid4().hex[:6].upper()

def main():
    addUser("jajas","123","123")
    token = refreshAuthorization("jajas","123")
    print(whois(token))
    removeUser("jajas","123")

main()