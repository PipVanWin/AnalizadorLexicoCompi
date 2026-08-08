// Ejemplo de codigo fuente en Kotlin
// Sistema simple de inventario y facturacion
// Usado como entrada de prueba para el analizador lexico

package com.umes.inventario

import kotlin.math.round

const val IVA: Float = 0.12f
const val NOMBRE_TIENDA: String = "Tienda UMES"

/*
 * Clase que representa un producto dentro del inventario
 * Contiene el nombre, precio unitario y cantidad disponible
 */
data class Producto(
    val nombre: String,
    val precio: Float,
    var cantidad: Int,
    val disponible: Boolean = true
)

class Inventario {
    private val productos = mutableListOf<Producto>()
    private var totalVentas: Float = 0.0f
    private var contadorFacturas: Int = 0

    fun agregarProducto(producto: Producto) {
        productos.add(producto)
    }

    fun buscarProducto(nombre: String): Producto? {
        for (p in productos) {
            if (p.nombre == nombre && p.disponible) {
                return p
            }
        }
        return null
    }

    fun venderProducto(nombre: String, cantidad: Int): Boolean {
        val producto = buscarProducto(nombre)
        if (producto == null || producto.cantidad < cantidad) {
            return false
        }
        producto.cantidad -= cantidad
        val subtotal = producto.precio * cantidad
        val impuesto = subtotal * IVA
        val total = subtotal + impuesto
        totalVentas += total
        contadorFacturas++
        return true
    }

    fun calcularDescuento(monto: Float, porcentaje: Int): Float {
        return when {
            porcentaje >= 50 -> monto * 0.5f
            porcentaje >= 25 -> monto * 0.75f
            porcentaje > 0 -> monto - (monto * porcentaje / 100)
            else -> monto
        }
    }

    fun reporteVentas(): String {
        val promedio = if (contadorFacturas > 0) totalVentas / contadorFacturas else 0.0f
        return "Ventas totales: $totalVentas, Facturas: $contadorFacturas, Promedio: $promedio"
    }

    fun productosAgotados(): List<String> {
        val agotados = mutableListOf<String>()
        var i = 0
        while (i < productos.size) {
            if (productos[i].cantidad == 0) {
                agotados.add(productos[i].nombre)
            }
            i++
        }
        return agotados
    }
}

fun main() {
    val inventario = Inventario()

    inventario.agregarProducto(Producto("Teclado", 150.50f, 20))
    inventario.agregarProducto(Producto("Mouse", 75.99f, 35))
    inventario.agregarProducto(Producto("Monitor", 899.0f, 10))
    inventario.agregarProducto(Producto("Cable HDMI", 45.25f, 0, false))

    println("Bienvenido a $NOMBRE_TIENDA")

    val exito = inventario.venderProducto("Teclado", 3)
    if (exito) {
        println("Venta realizada correctamente")
    } else {
        println("No se pudo completar la venta")
    }

    val descuento = inventario.calcularDescuento(500.0f, 30)
    println("Descuento aplicado: $descuento")

    val agotados = inventario.productosAgotados()
    for (item in agotados) {
        println("Producto agotado: $item")
    }

    println(inventario.reporteVentas())
}
