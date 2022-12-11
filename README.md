# Notas:
En cuanto al pylint he desactivado los siguientes errores por las siguientes razones:
* Lineas extra, considero que no es un error añadir líneas en blanco y aumentar la facilidad de lectura.
* No snake_case, he usado snake_case todo lo que he podido, pero hay apratado que ICE, te obliga a ponerlo en cammel case.
* Argumentos no usados, Ice nos obliga a poner current aunque no lo usemos.
* Import mal realizado, no llego a entender el porqué de este error cuando el programa funciona a la perfección y se le acusa al IceFlix. De todas formas llego al 9 aun sin quitar esta excepción.
* El uso de return es inconsistente. Esto ocurre cuando en una rama creada por una decisión se hace un return y en otra no. Sin embargo, al parecer pylint no tiene en cuenta las excepciones, es decir, cuando hago saltar Unauthorized después de imprimir el mensaje de error, hago un return. Que teóricamente solo hay dos caminos posibles. return normal o excepción con return. Sin embargo, Pylint no lo detecta.

En cuanto al uso de run_service y de pip install -e para instalar el paquete local, para poder hacer iceflix-authenticator o iceflix-main. No he considerado que sea razonable usarlo, por la siguientes razones:
* run_service nunca va a ir bien, porque para authenticator necesito poner el proxy del main en el config. La única opción sería escribirlo desde main, sin embargo, al no ser mi responsabilidad no puedo hacerlo, porque puede que se pruebe con un main que no lo haga.
* Creo que para probar un microservicio instalando el paquete en local carece de sentido, porque la funcionalidad es incompleta y tiene dependencia con las demás. Creo que esto proviene de años pasados donde era en un grupo, todo lo que se necesitaba estaba y se sabía cómo se iba a comportar las demás, por lo tanto, poseía más sentido. Es decir, el programa estaba entero.

# Ejecucion del programa
Se ejecuta con los siguientes comandos desde la carpeta padre:

python3 iceflix/main.py --Ice.Config=./configs/main.config 

Se copia el proxy dado en el archivo de configuración del authenticator.

python3 iceflix/authenticator.py --Ice.Config=./configs/authenticator.config 
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
