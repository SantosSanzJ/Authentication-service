https://github.com/SantosSanzJ/SSDD_Lab
# Resume
This is an implementation of an Authenticator service in python with the middleware ZeroIce.



# Notas:
En cuanto al pylint he desactivado los siguientes errores por las siguientes razones:
* Lineas extra, considero que no es un error añadir líneas en blanco y aumentar la facilidad de lectura.
* No snake_case, he usado snake_case todo lo que he podido, pero hay apratado que ICE, te obliga a ponerlo en cammel case.
* Argumentos no usados, Ice nos obliga a poner current aunque no lo usemos.
* Import mal realizado, no llego a entender el porqué de este error cuando el programa funciona a la perfección y se le acusa al IceFlix. De todas formas llego al 9 aun sin quitar esta excepción.
* El uso de return es inconsistente. Esto ocurre cuando en una rama creada por una decisión se hace un return y en otra no. Sin embargo, al parecer pylint no tiene en cuenta las excepciones, es decir, cuando hago saltar Unauthorized después de imprimir el mensaje de error, hago un return. Que teóricamente solo hay dos caminos posibles. return normal o excepción con return. Sin embargo, Pylint no lo detecta.

## Segundo Parcial:
* He eliminado el error E1101, porque no detectaba partes del código de Icestorm, cuando se ejecuta con perfección y es literalmente copiado y pegado de la wiki de SSDD.

iceflix/authenticator.py:235:24: E1101: Module 'IceStorm' has no 'TopicManagerPrx' member (no-member)

iceflix/authenticator.py:243:15: E1101: Module 'IceStorm' has no 'TopicExists' member (no-member)

iceflix/authenticator.py:254:15: E1101: Module 'IceStorm' has no 'TopicExists' member (no-member)


# Ejecución del programa
Necesitará instalar ZeroCIce, IceStorm y las herramientas de IceStorm.

Ejecutar ./run_service para ejecutar el authenticator.

Hay que tener en cuenta que necesitará un main para que no acabe a los 12 segundos.

Ejecutar ./run_icestorm para ejecutar el broker.
# Template project for ssdd-lab

This repository is a Python project template.
It contains the following files and directories:

- `configs` has several configuration files examples.
- `iceflix` is the main Python package.
  You should rename it to something meaninful for your project.
- `iceflix/__init__.py` is an empty file needed by Python to
  recognise the `iceflix` directory as a Python module.
- `iceflix/cli.py` contains several functions to handle the basic console entry points
  defined in `python.cfg`.
  The name of the submodule and the functions can be modified if you need.
- `iceflix/iceflix.ice` contains the Slice interface definition for the lab.
- `iceflix/main.py` has a minimal implementation of a service,
  without the service servant itself.
  Can be used as template for main or the other services.
- `pyproject.toml` defines the build system used in the project.
- `run_client` should be a script that can be run directly from the
  repository root directory. It should be able to run the IceFlix
  client.
- `run_service` should be a script that can be run directly from the
  repository root directory. It should be able to run all the services
  in background in order to test the whole system.
- `setup.cfg` is a Python distribution configuration file for Setuptools.
  It needs to be modified in order to adeccuate to the package name and
  console handler functions.
