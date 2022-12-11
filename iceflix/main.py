"""Module containing a template for a main service."""

import logging
import sys
import Ice

import IceFlix
from authenticator import AuthenticatorService

class Main(IceFlix.Main):
    """Servant for the IceFlix.Main interface.

    Disclaimer: this is demo code, it lacks of most of the needed methods
    for this interface. Use it with caution
    """

    def getAuthenticator(self, current):
        # TODO: implement
        Authenticator = AuthenticatorService()
        return Authenticator

    def getCatalog(self, current):
        # TODO: implement
        return None
    
    def newService(self, object, service_id, current):
        print("El servicio ha hecho newService")
        return
    
    def announce(self, object, service_id, current):
        print("El servicio se ha anunciado.")
        return


class MainApp(Ice.Application):
    """Example Ice.Application for a Main service."""

    def __init__(self):
        super().__init__()
        self.servant = Main()
        self.proxy = None
        self.adapter = None

    def run(self, args):
        """Run the application, adding the needed objects to the adapter."""
        logging.info("Running Main application")
        comm = self.communicator()
        self.adapter = comm.createObjectAdapter("MainAdapter")
        self.adapter.activate()
        #self.proxy = self.adapter.add(self.servant, comm.stringToIdentity("main1"))
        self.proxy = self.adapter.addWithUUID(self.servant)
        print(self.proxy, flush = False)
        self.shutdownOnInterrupt()
        comm.waitForShutdown()
        return 0
if __name__ == "__main__":
    MainApp = MainApp()
    sys.exit(MainApp.main(sys.argv))
