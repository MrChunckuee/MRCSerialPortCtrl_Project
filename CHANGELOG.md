# MRCSerialPortCtrl Project

FileName:        MRCSerialPortCtrl.py <br>
Author:          Pedro Sánchez (@mrchunckuee_electronics) <br>
Blog:            http://mrchunckuee.blogspot.com/ <br>
Email:           mrchunckuee.electronics@gmail.com <br>
Description:     Firmware change history, bug fixes, and new version implementation.


## xx/xx/xxxx _vx.x.x_
Author:	Full Name
### Notes
-
### Added
- 
### Changed
- 
### Fixed
- 

<br>
<br>

***

## 12/09/2025 _v2.3.0_
Author:	Pedro Sánchez (@mrchunckuee_electronics)
### Added
- Checkbox to enable/disable hexadecimal data. An option has been added to select how to view the data: hexadecimal or ASCII.
- Option to clear the terminal. You can delete all received data with this button.
- The data sending option now includes a feature that sends data when the ENTER key is pressed.
- A small routine has been added at startup to test if the libraries are installed. If they are not, it will suggest how to install them.
### Changed
- Option to export to CSV or Excel. This feature was already implemented in a previous update, but in this version it has been unified to provide a single file with these capabilities.




<br>
<br>

***
## 12/09/2025 _v2.1.0_
Author:	Pedro Sánchez (@mrchunckuee_electronics)
### Changed
- La opción para exportar datos a un archivo Excel o CSV (he estado probando mas el CSV y ha trabajado de forma adecuada), debo aclarar que he decidido dejar estos cambios en archivos separados asi se puede usar el que mejor se ajuste a tu aplicación.
- Se agrego la sección de "Configuración de Archivo" en donde nos permite introducir el nombre de las columnas y seleccionar la ruta donde se almacenara el archivos (los pasos de siempre, seleccionar ubicación y nombre), es importante este paso para que los datos sean almacenados en el archivo adecuadamente.

<br>
<br>

***
## 12/09/2025 _v2.0.0_
Author:	Pedro Sánchez (@mrchunckuee_electronics)
### Changed
- Cambio de nombre del proyecto, paso se ser "serialPyInterface" a "MRC SerialPortCtrl".
- Se mejoro la vista del GUI y se dejo fijo para usarse en Windows.
- Se mejoro la opcion para conexion de puertos, anteriormente texteabas el puerto, ahora te permite seleccionar de la lista disponible.
- Se mejoro la forma de seleccion del Baud Rate. Igual te permite seleccionar de una lista de opciones.
- Se agrego la opcion de enviar datos. Actualmente solo puedes enviar datos en formato ASCII y por default se agrega '\n' al final de la cadena enviada.
- Se mejoro la opcion de visualizacion de datos, anteriormente se viualizaba en el Shell de Python. Actualmente ya se muestra en la GUI, ademas te muestra datos en formato ASCII y en formato Hexadecimal (estas opciones eran por que asi lo necesitaba).

<br>
<br>

***

## 01/06/2019 _v1.0.0_
Author:	Pedro Sánchez (@mrchunckuee_electronics)
### Notes
- Creacion del proyecto.
