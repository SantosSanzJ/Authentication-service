'''Programa pedido para el primera entrega parcial.'''
#pylint: disable=E0401
import sys
import time
import uuid
import json
from threading import Timer
import Ice
import IceFlix
#pylint: disable=C0103
#pylint: disable=C0303
#pylint: disable=W0613
#pylint: disable=R1710


with open("./files/users.json","r",encoding="utf-8") as file:
    users = json.load(file)

auth_table = {} #Mapear token a nombre de usuario y timestamp
class Authenticator(IceFlix.Authenticator):
    '''Sirvente que implementa el Autenticator.'''
    admin_token = ""
    def __init__(self, admin_token):
        self.admin_token = admin_token

    def refreshAuthorization(self,user:str, passwordhash:str, current = None): 
        '''Dado un usuario y su contraseña crea un token si son válidos.
        Si el usuario tiene un token anterior lo borra.'''
        try:
            if user in users and users[user] == passwordhash:

                token_antiguo = [token for token,list in auth_table.items() if user == list[0]]
                if not token_antiguo == []:
                    del auth_table[token_antiguo[0]]
            
                token = self.crear_token()
                auth_table.update({token:(user,time.time())})
                return token
            raise IceFlix.Unauthorized
        except IceFlix.Unauthorized:
            print("El usuario y la contraseña no es válido.")
            return None

    def isAuthorized(self,userToken:str, current = None): 
        '''Dado un token devuelves si existe.'''
        if userToken in auth_table and not auth_table[userToken][1] + 120 > time.time():
            del auth_table[userToken]
        return userToken in auth_table

    def whois(self, userToken:str, current = None): 
        '''Dado un Token te da un usuario válido.'''
        try:
            if userToken in auth_table:
                return auth_table[userToken][0]
            raise IceFlix.Unauthorized
        except IceFlix.Unauthorized:
            print("El token no existe.")
            return None

    def isAdmin(self, adminToken:str, current = None): 
        '''Dado un token devuelve si es Admin o no. Lo saco del config
        y hago una comparación simple.'''
        return self.admin_token == adminToken

    def addUser(self, user:str,passwordhash:str,adminToken:str, current = None): 
        '''Dado un token admin y un usuario y contraseña metelos en la BBDD.'''
        try:
            if self.isAdmin(adminToken) and not user in users:
                users[user] = passwordhash
                with open("./files/users.json","w",encoding="utf-8") as f:
                    json.dump(users, f)
            else:
                raise IceFlix.Unauthorized
        except IceFlix.Unauthorized:
            print("El token admin no es válido o ya existe el nombre dado.")
            return None

    def removeUser(self,user:str, adminToken:str, current = None): 
        '''Dado un user y un token de admin elimina a un usuario de la BBDD.'''
        try:
            if self.isAdmin(adminToken) and user in users: 
                del users[user]
                with open("./files/users.json","w", encoding="utf-8") as f:
                    json.dump(users, f)
            else:
                raise IceFlix.Unauthorized
        except IceFlix.Unauthorized:
            print("El token admin no es válido o no existe el usuario que se quiere eliminar.")
            return None
    def crear_token(self):
        '''Crea un token único.'''
        return uuid.uuid4().hex[:6].upper()


class AuthenticatorService(Ice.Application):
    '''Aplicación de Ice que se comunicará con el main, para pasarle
    referencia en newService o announce.'''
    id_servicio = uuid.uuid4().hex[:6].upper()
    def run(self, args):
        broker = self.communicator()
        properties = broker.getProperties()

        main_proxy = broker.propertyToProxy("Main.Proxy")
        main = IceFlix.MainPrx.checkedCast(main_proxy)

        admin_token = properties.getProperty("AdminToken")
        servant = Authenticator(admin_token)

        adapter = broker.createObjectAdapter("AuthenticatorAdapter")
        proxy = adapter.add(servant, broker.stringToIdentity("Authenticator1"))
        
        main.newService(proxy,self.id_servicio)
        announce_timer(main,proxy,self.id_servicio, True)
        
        adapter.activate()
        self.shutdownOnInterrupt()
        broker.waitForShutdown()
        return 0

def announce_timer(main,proxy,id_servicio,primera_ejecuccion):
    '''Ejecuta el anunciamiento cada 25 segundos.'''
    my_timer = Timer(25.0,announce_timer,[main,proxy,id_servicio,False])
    if not primera_ejecuccion:
        main.announce(proxy,id_servicio)
    my_timer.start()
    return my_timer

if __name__ == "__main__":
    AuthenticatorService = AuthenticatorService()
    sys.exit(AuthenticatorService.main(sys.argv))
