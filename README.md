# Reto Tecnico: Cifrado de Imagenes por Adveccion Caotica

## Contexto

En criptografia moderna, muchos cifrados se basan en **permutaciones**, **mezclado** y **alta sensibilidad a parametros**. En dinamica de fluidos existen flujos que presentan **mezcla caotica**, donde trayectorias de particulas cercanas divergen rapidamente en el tiempo.

En este reto van a explorar como un modelo de flujo 2D incompresible y dependiente del tiempo puede utilizarse como base para construir un **cifrado experimental de imagenes**.

> Este no es un cifrado industrial. Es un *toy cipher* disenado para aprender, experimentar y pensar.

### Caso de uso

Proteccion visual de imagenes (medicas, industriales, dashboards) donde:
- La estructura espacial es fuerte.
- La ofuscacion visual ya aporta valor.
- El scrambling puede combinarse con cifrado fuerte (AES, etc).

```
Imagen original  -->  Scrambling caotico  -->  Imagen irreconocible
                                                      |
                                               (opcional: AES / XOR)
```

---

## Objetivo

Implementar un sistema que:

1. Tome una imagen y una **llave** (conjunto de parametros).
2. Produzca una **imagen scrambled** visualmente irreconocible.
3. Pueda **recuperar la imagen original exactamente** usando la misma llave.
4. **Falle** al intentar recuperar con una llave ligeramente diferente.

---

## El Modelo Fisico: Double Gyre Flow

El Double Gyre es un flujo clasico en dinamica de fluidos que presenta mezcla caotica Lagrangiana. Es el motor de este cifrado.

### Dominio

El flujo vive en un rectangulo: `x` en `[0, 2]`, `y` en `[0, 1]`.

### Campo de velocidad

```
u(x, y, t) = -pi * A * sin(pi * f(x,t)) * cos(pi * y)

v(x, y, t) =  pi * A * cos(pi * f(x,t)) * sin(pi * y) * (df/dx)
```

donde:

```
f(x, t)  = a(t) * x^2 + b(t) * x

a(t)     = epsilon * sin(omega * t)
b(t)     = 1 - 2 * epsilon * sin(omega * t)

df/dx    = 2 * a(t) * x + b(t)
```

### Propiedades

- **Incompresible**: conserva area (no hay fuentes ni sumideros).
- **Dependiente del tiempo**: cuando `epsilon > 0`, los dos giros oscilan y generan mezcla.
- **Caotico**: particulas inicialmente cercanas terminan en posiciones muy lejanas despues de suficientes pasos.
- **Determinista**: dados los mismos parametros, el resultado es siempre el mismo.

### Parametros (la llave)

| Parametro  | Rol fisico                                      |
|------------|--------------------------------------------------|
| `A`        | Intensidad del flujo                             |
| `epsilon`  | Amplitud de la oscilacion temporal               |
| `omega`    | Frecuencia de la oscilacion temporal             |
| `dt`       | Paso de integracion (discretizacion temporal)    |
| `N`        | Numero de pasos de adveccion                     |

Valores sugeridos para empezar a experimentar:

```
A       = 0.25
epsilon = 0.25
omega   = 2 * pi
dt      = 0.1
N       = 20
```

---

## La Idea Central

Piensen en cada pixel de la imagen como una **particula** flotando en el flujo.

1. Cada pixel `(i, j)` tiene una posicion en el dominio continuo del Double Gyre.
2. El flujo **mueve** todas las particulas simultaneamente durante `N` pasos.
3. Las posiciones finales de las particulas definen **a donde va cada pixel**.
4. Eso es una **permutacion**: un reordenamiento de todos los pixeles.

Para **descifrar**, necesitan la operacion inversa de esa permutacion.

El caos del flujo garantiza que la permutacion resultante sea compleja y sensible a los parametros: cambiar un decimal en la llave produce una permutacion completamente diferente.

### Diagrama conceptual

```
Imagen (H x W pixeles)
        |
        v
Cada pixel -> particula en [0,2] x [0,1]
        |
        v
Adveccion: mover particulas N pasos con el campo de velocidad
        |
        v
Posiciones finales -> definir permutacion
        |
        v
Aplicar permutacion a los pixeles -> Imagen scrambled
```

---

## La Matematica que Necesitan

### Integracion temporal (Euler explicito)

Para mover una particula del paso `k` al paso `k+1`:

```
x_{k+1} = x_k + dt * u(x_k, y_k, t_k)
y_{k+1} = y_k + dt * v(x_k, y_k, t_k)
```

donde `t_k = k * dt`.

Esto se repite `N` veces para cada particula.

### Condiciones de frontera

Las particulas pueden salir del dominio `[0,2] x [0,1]` durante la adveccion. Necesitan decidir como manejar esto (periodicas, reflectivas, o clamp). La eleccion afecta la permutacion resultante.

### De posiciones a permutacion

Despues de la adveccion, tienen `H * W` particulas con posiciones finales `(x_f, y_f)`. Necesitan convertir eso en una **permutacion discreta**: una funcion biyectiva que mapee cada indice de pixel a otro indice de pixel, sin repeticiones.

Hay varias formas de hacerlo. Piensen en como pueden **ordenar** las posiciones finales para obtener un reordenamiento limpio y sin colisiones.

---

## Entregables

### 1. Codigo funcional

Que tome una imagen y una llave, y produzca:
- Imagen scrambled.
- Imagen recuperada (identica a la original).

La estructura del codigo, los nombres, la organizacion: es su decision.

### 2. Demo

Un script o notebook que se pueda ejecutar y muestre los resultados. Hay un archivo `demo/demo.py` como referencia de lo que esperamos ver.

### 3. Experimentos

Documenten al menos:

- **Scramble + recovery**: imagen original, scrambled y recuperada lado a lado.
- **Sensibilidad**: que pasa si cambian un solo parametro de la llave por un valor cercano?
- **Histograma**: como se ve el histograma de la imagen antes y despues del scrambling?
- **Observaciones**: que notaron? que aprendieron?

### 4. Tests

Escriban al menos un test que verifique que `descramble(scramble(img)) == img`.

---

## Setup

```bash
git clone <url-del-repo>
cd image-crypto-algorithm

python -m venv venv
source venv/bin/activate   # Linux/Mac
# venv\Scripts\activate    # Windows

pip install -r requirements.txt
```

Las dependencias base estan en `requirements.txt`. Si necesitan algo mas, agregenlo.

Coloquen imagenes de prueba en `images/`.

---

## Restricciones

- **Python**. Pueden usar `numpy`, `Pillow`, `matplotlib`, y lo que necesiten.
- El scrambling debe ser **determinista** y **reversible**.
- **No usar librerias de cifrado** para el scrambling (nada de AES, Fernet, etc). El punto es que ustedes construyan la permutacion desde el modelo fisico.
- Documenten lo que hagan. Codigo sin explicacion no cuenta.

---

## Referencias

- Shadden, Lekien & Marsden (2005). *Definition and properties of Lagrangian coherent structures from finite-time Lyapunov exponents in two-dimensional aperiodic flows.*
- Aref, H. (1984). *Stirring by chaotic advection.*
