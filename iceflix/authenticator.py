#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-
'''Programa pedido para la entrega Ordinaria de IceFlix.'''

#pylint: disable=E0401
import os
import sys
import time
import uuid
import json
from threading import Timer
import Ice
import IceStorm
import IceFlix

#pylint: disable=E1101
#pylint: disable=C0103
#pylint: disable=C0303
#pylint: disable=W0613
#pylint: disable=R1710

with open("./files/users.json","r",encoding="utf-8") as file:
    users = json.load(file)

auth_table = {}
class Authenticator(IceFlix.Authenticator):
    '''Sirviente que implementa el Authenticator.'''
    admin_token = ""
    user_update_publisher = None
    dict_main = {}
    dict_auth = {}

    def __init__(self, admin_token,serviceId):
        self.admin_token = admin_token
        self.serviceId = serviceId

    def refreshAuthorization(self,user:str, passwordhash:str, current = None): 
        '''Dado un usuario y su contraseña crea un token si son válidos.
        Si el usuario tiene un token anterior lo borra.'''
        if user in users and users[user] == passwordhash:
            token_antiguo = [token for token,list in auth_table.items() if user == list[0]]
            if not token_antiguo == []:
                del auth_table[token_antiguo[0]]
                self.user_update_publisher.revokeToken(token_antiguo[0],self.serviceId)
            token = self.crear_token()
            auth_table.update({token:(user,time.time())})
            self.user_update_publisher.newToken(user, token,self.serviceId)
            return token
        raise IceFlix.Unauthorized()

    def isAuthorized(self,userToken:str, current = None): 
        '''Dado un token devuelves si existe.'''
        if userToken in auth_table and not auth_table[userToken][1] + 120 > time.time():
            del auth_table[userToken]
            self.user_update_publisher.revokeToken(userToken,self.serviceId)
        return userToken in auth_table

    def whois(self, userToken:str, current = None): 
        '''Dado un Token te da un usuario válido.'''
        if userToken in auth_table:
            return auth_table[userToken][0]
        raise IceFlix.Unauthorized()

    def isAdmin(self, adminToken:str, current = None): 
        '''Dado un token devuelve si es Admin o no. Lo saco del config
        y hago una comparación simple.'''
        return self.admin_token == adminToken

    def addUser(self, user:str,passwordhash:str,adminToken:str, current = None): 
        '''Dado un token admin y un usuario y contraseña metelos en la BBDD.'''
        if self.isAdmin(adminToken) and not user in users:
            users[user] = passwordhash
            self.user_update_publisher.newUser(user,passwordhash,self.serviceId)
            with open("./files/users.json","w",encoding="utf-8") as f:
                json.dump(users, f)
        else:
            raise IceFlix.Unauthorized()

    def removeUser(self,user:str, adminToken:str, current = None): 
        '''Dado un user y un token de admin elimina a un usuario de la BBDD.'''
        if self.isAdmin(adminToken) and user in users: 
            del users[user]
            self.user_update_publisher.removeUser(user,self.serviceId)
            with open("./files/users.json","w", encoding="utf-8") as f:
                json.dump(users, f)
        else:
            raise IceFlix.Unauthorized()
    
    def bulkUpdate(self,current = None):
        '''Metodo que consigue toda la información del servicio,
         para darsela al servicio que la llama.'''
        auth_data = IceFlix.AuthenticatorData()
        auth_data.adminToken = self.admin_token
        auth_data.currentUsers = users
        auth_data.activeTokens = auth_table
        return auth_data

    def crear_token(self):
        '''Crea un token único.'''
        return uuid.uuid4().hex[:6].upper()

    def remove_old_tokens(self):
        '''Se encargará de eliminar tokens antiguos.'''
        while True:
            if auth_table:
                timestamps = [timestamp for user, timestamp in auth_table.values()]
                next_timestamp = min(timestamps)
                index = timestamps.index(next_timestamp)
                time.sleep(120 - (time.time() - next_timestamp))
                token = list(auth_table.keys())[index]
                del auth_table[token]
                self.user_update_publisher.revokeToken(token,self.serviceId) 

class UserUpdate(IceFlix.UserUpdate):
    '''Implementa la interfaz UserUpdates que nos permitirá sincronizar
    los datos de los autenticadores.''' 
    def __init__(self, service_ID, servant):
        self.serviceID = service_ID
        self.servant = servant

    def newToken(self, user, token, serviceId, current = None):
        '''Recibe una actutalización de la BBDD de otro servicio y elimina el usuario.'''
        if serviceId == self.serviceID:
            return
        if not serviceId in self.servant.dict_auth.keys():
            print(f'La actualización newToken no ha sido realizada, servicio: {serviceId}')
            return
        else:
            auth_table.update({token:(user,time.time())})
            print(f'La actualización newToken ha sido realizada, servicio: {serviceId}')

    def revokeToken(self, token, serviceId, current = None):
        '''Recibe una actualización de la BBDD de otro servicio y elimina el usuario.'''
        if serviceId == self.serviceID:
            return
        if not serviceId in self.servant.dict_auth.keys():
            print(f'La actualización revokeToken no ha sido realizada, servicio: {serviceId}')
            return
        else:
            try:   
                del auth_table[token]
            except KeyError:
                print(f'La actualización revokeToken  no ha sido realizada por key error, servicio: {serviceId}')
            print(f'La actualización revokeToken ha sido realizada, servicio: {serviceId}')

    def newUser(self, user, passwordHash, serviceId, current = None):
        '''Recibe una actualización de la BBDD de otro servicio y añade el usuario.'''
        if serviceId == self.serviceID:
            return
        if not serviceId in self.servant.dict_auth.keys():
            print(f'La actualización newUser no ha sido realizada, servicio: {serviceId}')
            return
        else:
            users[user] = passwordHash
            print(f'La actualización newUser ha sido realizada, servicio: {serviceId}')
            with open("./files/users.json","w",encoding="utf-8") as f:
                json.dump(users, f)
        
    def removeUser(self, user, serviceId, current = None):
        '''Recibe una actutalización de la BBDD de otro servicio y elimina el usuario.'''
        if serviceId == self.serviceID:
            return
        if not serviceId in self.servant.dict_auth.keys():
            print(f'La actualización removeUser no ha sido realizada, servicio: {serviceId}')
            return
        else:
            del users[user]
            print(f'La actualización removeUser ha sido realizada, servicio: {serviceId}')
            with open("./files/users.json","w", encoding="utf-8") as f:
                json.dump(users, f)

class Announcement (IceFlix.Announcement):
    '''Implementa la interfaz Announcement que se encargará de realizar los anunciamientos.'''
    actualizado = False

    def __init__(self, serviceId, servant):
        self.serviceId = serviceId
        self.servant = servant

    def announce(self, service, serviceId, current = None):
        '''Obtendremos los anunciamientos de los demás servicios y los guardaremos 
        en sus diccionarios. Si existe alguno que no ha respondido a los 10s lo 
        quitamos de la lista.'''
        if self.serviceId == serviceId:
            print("AutoAnunciamiento")
            return
        
        if service.ice_isA('::IceFlix::Main'):
            self.servant.dict_main[serviceId] = (IceFlix.MainPrx.uncheckedCast(service),
             time.time())
            print(f'Se ha recibido un anunciamiento de un servicio Main con ID: {serviceId}')

        elif service.ice_isA('::IceFlix::Authenticator'):
            self.servant.dict_auth[serviceId] = (IceFlix.AuthenticatorPrx.uncheckedCast(service),
             time.time())
            print('Se ha recibido un anunciamiento de un servicio Authenticator,'
             + f'con ID: {serviceId}')

            if not self.actualizado:
                service = IceFlix.AuthenticatorPrx.uncheckedCast(service)
                auth_data = service.bulkUpdate()
                global users
                users = auth_data.currentUsers
                global auth_table
                auth_table = auth_data.activeTokens
                with open("./files/users.json","w",encoding="utf-8") as f:
                    json.dump(users, f)
                self.actualizado = True               
        else:
            print('Se ha recibido un anunciamiento de un servicio no relevante,'
             + f'con ID: {serviceId}')
    def first_execution(self):
        '''Se ejecutará si han pasado 12 segundos, es para definir al auth como primero.'''
        self.actualizado = True

class AuthenticatorService(Ice.Application):
    '''Aplicación de Ice que se comunicará con el main, para pasarle
    referencia en newService o announce.'''
    id_servicio = uuid.uuid4().hex[:6].upper()
    actualizado = False

    def run(self, args):
        broker = self.communicator()
        properties = broker.getProperties()
        
        admin_token = properties.getProperty("AdminToken")
        servant = Authenticator(admin_token, self.id_servicio)
        
        delete_old_tokens_timer = Timer(120.0, servant.remove_old_tokens,[])
        delete_old_tokens_timer.start()

        adapter = broker.createObjectAdapter("AuthenticatorAdapter")
        proxy = adapter.add(servant, broker.stringToIdentity("Authenticator1"))

        topic_manager = IceStorm.TopicManagerPrx.checkedCast(
            self.communicator().propertyToProxy("IceStorm.TopicManager"),
        )
        if not topic_manager:
            raise RuntimeError("Invalid TopicManager proxy")

        try:
            announce_topic = topic_manager.create("Announcements")
        except IceStorm.TopicExists:
            announce_topic = topic_manager.retrieve("Announcements")

        announce_subscriber = Announcement(self.id_servicio,servant)
        announce_proxy = adapter.addWithUUID(announce_subscriber)
        announce_topic.subscribeAndGetPublisher({}, announce_proxy)
        announce_publisher = announce_topic.getPublisher()
        announce_proxy = IceFlix.AnnouncementPrx.uncheckedCast(announce_publisher)

        try:
            user_update_topic = topic_manager.create("UserUpdates")
        except IceStorm.TopicExists:
            user_update_topic = topic_manager.retrieve("UserUpdates")
        
        user_update_subscriber = UserUpdate(self.id_servicio,servant)
        user_update_proxy = adapter.addWithUUID(user_update_subscriber)
        user_update_topic.subscribeAndGetPublisher({}, user_update_proxy)
        user_update_publisher = user_update_topic.getPublisher()
        user_update_proxy = IceFlix.UserUpdatePrx.uncheckedCast(user_update_publisher)

        servant.user_update_publisher = user_update_proxy

        announce_timer(announce_proxy,proxy,self.id_servicio, servant, True)
        
        check_main_exists_timer = Timer(12.0, self.check_main_exists,[servant])
        check_main_exists_timer.start()

        first_execution_timer = Timer(12.0, announce_subscriber.first_execution,[])
        first_execution_timer.start()

        adapter.activate() 
        self.shutdownOnInterrupt()
        broker.waitForShutdown()
        announce_topic.unsubscribe(announce_proxy)
        user_update_topic.unsubscribe(user_update_proxy)
        return 0

    def check_main_exists(self, servant):
        '''Si no existe algún main, el programa termina.'''
        if not servant.dict_main:
            print("Ningún main existe. Abortamos microservicio Authenticator.")
            self.communicator().shutdown()


def announce_timer(announce_publisher,proxy,id_servicio, servant, primera_ejecuccion):
    '''Ejecuta el anunciamiento cada 8 segundos.'''
    my_timer = Timer(8.0,announce_timer,[announce_publisher,proxy,id_servicio,servant,False])
    if not primera_ejecuccion:
        announce_publisher.announce(proxy,id_servicio)
        delete_old_services(servant.dict_main)
        delete_old_services(servant.dict_auth)
    my_timer.start()
    return my_timer

def delete_old_services(dictionary):
    '''Borraremos los servicios antiguos si no se han anunciado hace 10 segundos.'''
    for key, value in dictionary.copy().items():
        if time.time() - value[1] >= 10.0:
            del dictionary[key]


if __name__ == "__main__":
    AuthenticatorService = AuthenticatorService()
    os._exit(AuthenticatorService.main(sys.argv))
