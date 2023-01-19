#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-
'''Servicio principal de IceFlix'''

import sys
import uuid
import random
from threading import Timer
import Ice
import IceStorm
import IceFlix



class ServiceAnnouncementsMain(IceFlix.Announcement):
    '''Implementa la interfaz ServiceAnnouncements para el servicio principal'''

    def __init__(self, main_servant):
        self._main_servant_ = main_servant

    @property
    def main_servant(self):
        '''Devuelve el sirviente al servicio principal que lo creó'''

        return self._main_servant_

    def announce (self, service, srv_id, current=None):
        '''Registra un servicio que mande un evento por el canal de announce'''

        #if srv_id in self.main_servant.known_services.keys():
        #    return

        if self.main_servant.id == srv_id:
            return

        if service.ice_isA('::IceFlix::Main'):
            print(f'\nNuevo servicio principal registrado: {srv_id}')
            self.main_servant.known_services[srv_id] = IceFlix.MainPrx.uncheckedCast(service)
        elif service.ice_isA('::IceFlix::Authenticator'):
            print(f'\nNuevo servicio de autenticación registrado: {srv_id}')
            self.main_servant.known_services[srv_id]=IceFlix.AuthenticatorPrx.uncheckedCast(service)
            self.main_servant.authenticators.append(IceFlix.AuthenticatorPrx.uncheckedCast(service))
            #self.main_servant.known_services[srv_id].refreshAuthorization("Xq","23")
            
        elif service.ice_isA('::IceFlix::MediaCatalog'):
            print(f'\nNuevo servicio de catálogo registrado: {srv_id}')


class MainI(IceFlix.Main):
    '''Sirviente del servicio principal'''
    authenticators = []
    known_services = {}
    id = str(uuid.uuid4())
    def __init__(self, admin_token):

        self.admin_token = admin_token

    def getAuthenticator(self, current=None):
        '''Retorna un proxy de autenticación si hay'''

        if len(self.services.authenticators) == 0:
            raise IceFlix.TemporaryUnavailable()

        selected_proxy = random.choice(list(self.services.authenticators))

        try:
            selected_proxy.ice_ping()
        except Ice.LocalException as local_ex:
            raise IceFlix.TemporaryUnavailable() from local_ex

        return IceFlix.AuthenticatorPrx.checkedCast(selected_proxy)

    def isAdmin (self, admin_token, current=None):
        '''Devuelve true si el token dado es el de administración'''

        return self._admin_token_ == admin_token


class MainService(Ice.Application):
    '''Clase del servicio principal'''

    def run(self, argv):
        '''Ejecuta el servicio principal'''

        broker = self.communicator()
        admin_token = "1234"

        adapter = broker.createObjectAdapterWithEndpoints('MainAdapter','tcp')
        

        service_implementation = MainI(admin_token)
        service_proxy = adapter.addWithUUID(service_implementation)

        if service_implementation.admin_token != admin_token:
            print('\n¡Token administrativo incorrecto!\n')
            return 0
        topic_manager = IceStorm.TopicManagerPrx.checkedCast(
            self.communicator().stringToProxy("IceStorm/TopicManager -t:tcp -h localhost -p 10000"),
        )
        if not topic_manager:
            raise RuntimeError("Invalid TopicManager proxy")

        try:
            service_ann_topic = topic_manager.create("Announcements")
        except IceStorm.TopicExists:
            service_ann_topic = topic_manager.retrieve("Announcements")


        service_ann_subscriber = ServiceAnnouncementsMain(service_implementation)
        service_ann_proxy = adapter.addWithUUID(service_ann_subscriber)
        service_ann_topic.subscribeAndGetPublisher({}, service_ann_proxy)
        service_ann_publisher = service_ann_topic.getPublisher()
        service_ann_proxy = IceFlix.AnnouncementPrx.uncheckedCast(service_ann_publisher)


        announce_timer(service_ann_proxy,service_proxy,service_implementation.id, True)

        adapter.activate()
        self.shutdownOnInterrupt()
        broker.waitForShutdown()
   
        service_ann_topic.unsubscribe(service_ann_proxy)

        return 0

    def get_admin_token(self, argv):
        '''Lee el token administrativo del fichero de configuración si no se ha introducido'''

        if len(argv) == 2:
            admin_token = argv[1]
        else:
            properties = self.communicator().getProperties()
            admin_token = properties.getProperty('AdminToken')

        return admin_token

def announce_timer(announce_publisher,proxy,id_servicio, primera_ejecuccion):
    '''Ejecuta el anunciamiento cada 8 segundos.'''
    my_timer = Timer(8.0,announce_timer,[announce_publisher,proxy,id_servicio,False])
    if not primera_ejecuccion:
        announce_publisher.announce(proxy,id_servicio)
    my_timer.start()
    return my_timer


if __name__ == "__main__":
    MainService = MainService()
    sys.exit(MainService.main(sys.argv))