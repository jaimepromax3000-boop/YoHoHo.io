# YoHoHo.io en Scratch (`YoHoHo.sb3`)

Versión de **YoHoHo.io** (battle royale pirata) hecha solo con bloques de Scratch 3.
Se abre en Scratch (*Archivo → Cargar desde tu computadora*) o en TurboWarp (recomendado: lleva
guardada la configuración de 60 FPS).

## Cómo se juega (igual que el original)
- **Ratón**: te mueves hacia el cursor. **WASD / flechas**: también mueven.
- **Clic o ESPACIO**: ataque con espada. **Mantén pulsado** para cargar y suelta para hacer el *dash*.
- Recoge doblones para crecer, abre cofres, mata a los otros 79 piratas y quédate dentro del círculo seguro:
  el gas venenoso avanza y quita el 10 % de vida cada 3 s.
- **Characters**: elige entre los 35 personajes (se desbloquean con botín y subiendo de isla).
- Al terminar ganas botín y XP; con la XP subes de isla (Tortuga → Beach → Easter → Wreck → Aztec → Volcano → Village).

## Qué se ha portado del original (`yohoho.js`)
Mapas, tamaños y decorado de las 7 islas · 79 bots con la IA original (buscar monedas, huir de la tormenta, atacar al
que tienen cerca, cargar el dash, perseguir al jugador en islas altas) · stats de vida/daño por personaje y por isla ·
tamaño según monedas comidas (curva de Bézier, 10 escalones) · swing alterno de arma, knockback, choque de armas ·
cofres y monedas (50/25/5) · muerte: el botín cae al suelo · tormenta con los 8 pasos del original · minimapa, contador de
tormenta/jugadores/bajas, estela del dash, mascotas (9 tipos: siguen y curan al dueño, se compran y mejoran en
«Characters → Pets», a partir de la isla Beach; algunos bots también las llevan), mensajes "Double/Triple Kill…", "Size UP", pantalla final con rango, tiempo, XP y frase.

## Cómo está hecho
Un único sprite oculto (`Pirata`) simula y dibuja con la extensión **Lápiz** (`estampar`), igual que un motor 2D.
Todo el estado está en variables y listas de Scratch (una lista por atributo de jugador, monedas en una rejilla enlazada,
etc.) y la lógica está en unos 45 bloques personalizados «ejecutar sin refrescar pantalla».

## Diferencias respecto al original (limitaciones honestas)
- No hay anuncios ni login, ni guardado entre sesiones (Scratch no tiene almacenamiento local; el botín, la XP y las
  mascotas compradas duran hasta que cierras el proyecto).
- No se dibujan la cuadrícula tenue del suelo, la corona del líder ni las chispas del choque de armas.
- El suelo usa losetas de 2×2 unidades: el borde de arena es de 2 en vez de 1,5 unidades.
- La zona de golpe del arma es una cápsula (centro de la hoja + ancho) en vez del polígono exacto.
- El texto usa la fuente Nunito del juego, convertida en disfraces de resolución doble (solo ASCII).
- Todas las islas tienen 80 jugadores (tú y 79 bots); el original ajustaba el número al tamaño del mapa.

## Regenerar el proyecto
```
python3 scratch/build.py            # escribe scratch/YoHoHo.sb3
```
Requiere Python 3 con Pillow. `sb3lib.py` es un pequeño DSL que convierte bloques escritos en Python a `project.json`;
`assets.py` recorta los sprites de `img/spritesheet4-*.png`; `gamedata.py` contiene las tablas del juego.
