import uuid
import json
import Ice
import time
import IceFlix
import sys
#hay que ejecutarlo como si fuera
#pip install -e . install te crea 
#Ice.loadSlice('iceflix/iceflix.ice') ya lo haces al importar.

with open("../files/users.json", "r") as f:
    users = json.load(f)
#new service
#si te pide un usuario un token y luego te pide otro antes de 2 minutos, hay invalidar el segundo
#se genera un servicio unico con UUID, no se repitan en el mismo proceso
#Puedes tener un timer en otro hilo
#current.adapter.addWithUUID
#usar tox
#integración continua yaml, travis, jenkins, github actions
#Fomrateo con githubs actions con Black
#Pregunta: Cómo se podría solucionar un fallo de diseño?

auth_table = {} #Mapear token a nombre de usuario


#que hago con la excepcion temporary unaivalable?
#En el main tnego que crear authentiucator o authenticationService
#anounce?
#Las excepciones las controla el auth o el main?
class Authenticator(IceFlix.Authenticator):
    admin_token = ""

    def __init__(self, admin_token):
        self.admin_token = admin_token

    def refreshAuthorization(self,user, passwordhash, current = None): 
        '''Dado un usuario y su contraseña crea un token si son válidos.'''
        if user in users and users[user] == passwordhash:
            token = self.crear_token()
            auth_table.update({token:(user,time.time())})
            return token
        else:
            raise IceFlix.Unauthorized

    def isAuthorized(self,userToken, current = None): 
        '''Dado un token devuelves si existe.'''
        auth = False
        if userToken in auth_table and auth_table[userToken] + 120 > time.time():
            auth = True
        elif userToken in auth_table:
            del auth_table[userToken]
        return userToken in auth_table

    def whois(self, userToken, current = None): 
        '''Dado un Token te da un usuario válido.'''
        if userToken in auth_table:
            return auth_table[userToken][0]
        else:
            raise IceFlix.Unauthorized

    def isAdmin(self, adminToken, current = None): 
        '''Dado un token devuelve si es Admin o no. Lo saco del config y hago una comparación simple.'''
        return self.admin_token == adminToken

    def addUser(self, user,passwordhash,adminToken, current = None): 
        '''Dado un token admin y un usuario y contraseña metelos en la BBDD.'''
        if self.isAdmin(adminToken) and not user in users: #Temporary Unvaidable?
            users[user] = passwordhash
            with open("../files/users.json","w") as f:
                json.dump(users, f)
        else:
            raise IceFlix.Unauthorized

    def removeUser(self,user, adminToken, current = None): 
        '''Dado un user y un token de admin elimina a un usuario de la BBDD.'''
        if self.isAdmin(adminToken) and user in users: #Temporary Unvaidable?
            del users[user]
            with open("../files/users.json","w") as f:
                json.dump(users, f)
        else:
            raise IceFlix.Unauthorized

    def crear_token():
        return uuid.uuid4().hex[:6].upper()

class AuthenticatorService(Ice.Application):
    def run(self, argv):
        #como consigo el proxy de main?
        broker = self.communicator()
        properties = broker.getProperties()
        adminToken = properties.getProperty("AdminToken")
        #el adminToken lo meto por constructor?
        servant = Authenticator(adminToken)
        adapter = broker.createObjectAdapter("AuthenticatorAdapter")
        proxy = adapter.add(servant, broker.stringToIdentity("Authenticator1"))
        print(proxy, flush = False)
        adapter.activate()
        self.shutdownOnInterrupt()
        #tengo que guardarlo en algún sitio el objeto en main?
        broker.waitForShutdown()
        return 0

if __name__ == "__main__":
    AuthenticatorService = AuthenticatorService()
    sys.exit(AuthenticatorService.main(sys.argv))