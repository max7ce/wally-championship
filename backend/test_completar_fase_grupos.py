#!/usr/bin/env python3
"""
Script para completar automáticamente la fase de grupos
Genera resultados aleatorios para todos los 84 partidos
"""

import sys
import os
import random

# Añadir directorio actual al path para imports
sys.path.insert(0, os.path.dirname(__file__))

from database import execute_query


def completar_fase_grupos():
    """
    Completa todos los partidos de fase grupos con resultados aleatorios
    """
    print("=" * 60)
    print("🎲 COMPLETANDO FASE DE GRUPOS AUTOMÁTICAMENTE")
    print("=" * 60)
    
    # 1. Obtener todos los partidos de fase grupos
    partidos = execute_query(
        "SELECT id, equipo_local_id, equipo_visitante_id FROM partidos WHERE fase = 'grupos'"
    )
    
    if not partidos:
        print("❌ No se encontraron partidos de fase grupos")
        return
    
    print(f"\n📊 Total de partidos a completar: {len(partidos)}")
    
    # 2. Completar cada partido con resultado aleatorio
    completados = 0
    
    for i, partido in enumerate(partidos, 1):
        # Generar puntajes aleatorios (entre 15 y 25)
        puntos_local = random.randint(15, 25)
        puntos_visitante = random.randint(15, 25)
        
        # Evitar empates (en este torneo el punto de oro siempre define ganador)
        if puntos_local == puntos_visitante:
            if random.random() > 0.5:
                puntos_local += random.randint(1, 3)
            else:
                puntos_visitante += random.randint(1, 3)
        
        # Determinar si fue por puntos o por tiempo
        if puntos_local == 25 or puntos_visitante == 25:
            terminado_por = 'puntos'
        else:
            terminado_por = 'tiempo'
        
        # Insertar resultado
        try:
            execute_query(
                """
                INSERT INTO resultados (
                    partido_id, 
                    puntos_local, 
                    puntos_visitante, 
                    estado, 
                    terminado_por,
                    punto_de_oro,
                    tiempo_jugado
                )
                VALUES (%s, %s, %s, 'finalizado', %s, false, %s)
                ON CONFLICT (partido_id) DO UPDATE SET
                    puntos_local = %s,
                    puntos_visitante = %s,
                    estado = 'finalizado',
                    terminado_por = %s,
                    punto_de_oro = false,
                    tiempo_jugado = %s
                """,
                (
                    partido['id'], 
                    puntos_local, 
                    puntos_visitante, 
                    terminado_por,
                    random.randint(600, 840),  # Tiempo entre 10-14 minutos
                    puntos_local, 
                    puntos_visitante, 
                    terminado_por,
                    random.randint(600, 840)
                ),
                fetch=False
            )
            completados += 1
            
            # Mostrar progreso cada 10 partidos
            if i % 10 == 0:
                print(f"   Progreso: {i}/{len(partidos)} partidos completados ({i/len(partidos)*100:.0f}%)")
        
        except Exception as e:
            print(f"❌ Error en partido {partido['id']}: {e}")
    
    print(f"\n✅ {completados} partidos completados con resultados aleatorios")
    
    # 3. Mostrar tabla de posiciones
    print("\n" + "=" * 60)
    print("📊 TABLA DE POSICIONES FINAL")
    print("=" * 60)
    
    standings = execute_query("SELECT * FROM v_standings")
    
    print(f"\n{'Pos':<5} {'Equipo':<25} {'Pts':<6} {'SG':<5} {'SP':<5} {'Dif':<6}")
    print("-" * 60)
    
    for i, equipo in enumerate(standings, 1):
        clasificado = "🏆" if i <= 4 else "  "
        print(
            f"{clasificado} {i:<3} {equipo['nombre']:<25} "
            f"{equipo['puntos']:<6} {equipo['sets_ganados']:<5} "
            f"{equipo['sets_perdidos']:<5} {equipo['diferencia']:+6}"
        )
    
    print("\n" + "=" * 60)
    print("🏆 TOP 4 CLASIFICADOS A SEMIFINALES:")
    print("=" * 60)
    
    for i, equipo in enumerate(standings[:4], 1):
        print(f"   {i}°. {equipo['nombre']} - {equipo['puntos']} puntos")
    
    print("\n💡 Próximo paso:")
    print("   Ejecuta: curl -X POST http://localhost:8000/fase-final/generar-semifinales -u admin:admin123")
    print("   O desde el Panel Admin en la web")


def simular_algunos_wo(cantidad=2):
    """
    Simula algunos walkovers aleatorios (opcional)
    
    Args:
        cantidad: Número de WO a simular
    """
    print("\n" + "=" * 60)
    print(f"🚫 SIMULANDO {cantidad} WALKOVERS (WO)")
    print("=" * 60)
    
    # Obtener partidos sin resultado
    partidos = execute_query(
        """
        SELECT p.id, p.equipo_local_id, p.equipo_visitante_id,
               e1.nombre as equipo_local, e2.nombre as equipo_visitante
        FROM partidos p
        JOIN equipos e1 ON p.equipo_local_id = e1.id
        JOIN equipos e2 ON p.equipo_visitante_id = e2.id
        LEFT JOIN resultados r ON p.id = r.partido_id
        WHERE p.fase = 'grupos' AND r.id IS NULL
        LIMIT %s
        """,
        (cantidad,)
    )
    
    for partido in partidos:
        # Elegir equipo ausente al azar
        if random.random() > 0.5:
            equipo_ausente_id = partido['equipo_local_id']
            equipo_ausente_nombre = partido['equipo_local']
            puntos_local = 0
            puntos_visitante = 25
        else:
            equipo_ausente_id = partido['equipo_visitante_id']
            equipo_ausente_nombre = partido['equipo_visitante']
            puntos_local = 25
            puntos_visitante = 0
        
        # Registrar WO
        execute_query(
            """
            INSERT INTO resultados (
                partido_id, 
                puntos_local, 
                puntos_visitante, 
                estado, 
                terminado_por,
                es_walkover,
                equipo_ausente_id,
                tiempo_jugado
            )
            VALUES (%s, %s, %s, 'finalizado', 'walkover', true, %s, 0)
            """,
            (partido['id'], puntos_local, puntos_visitante, equipo_ausente_id),
            fetch=False
        )
        
        print(f"   🚫 WO registrado: {equipo_ausente_nombre} no se presentó")


def main():
    """Función principal"""
    print("\n¿Qué querés hacer?")
    print("1. Completar TODOS los 84 partidos automáticamente")
    print("2. Completar partidos + simular 2 Walkovers (WO)")
    print("3. Solo simular 2 Walkovers (para partidos ya creados)")
    print("4. Salir")
    
    opcion = input("\nIngresa opción (1-4): ").strip()
    
    if opcion == "1":
        completar_fase_grupos()
    elif opcion == "2":
        completar_fase_grupos()
        simular_algunos_wo(2)
        # Re-mostrar tabla con WO incluidos
        print("\n" + "=" * 60)
        print("📊 TABLA ACTUALIZADA (con WO)")
        print("=" * 60)
        standings = execute_query("SELECT * FROM v_standings")
        print(f"\n{'Pos':<5} {'Equipo':<25} {'Pts':<6} {'SG':<5} {'SP':<5} {'WO':<4} {'Dif':<6}")
        print("-" * 65)
        for i, equipo in enumerate(standings, 1):
            clasificado = "🏆" if i <= 4 else "  "
            print(
                f"{clasificado} {i:<3} {equipo['nombre']:<25} "
                f"{equipo['puntos']:<6} {equipo['sets_ganados']:<5} "
                f"{equipo['sets_perdidos']:<5} {equipo['walkovers']:<4} "
                f"{equipo['diferencia']:+6}"
            )
    elif opcion == "3":
        simular_algunos_wo(2)
    elif opcion == "4":
        print("👋 ¡Hasta luego!")
        return
    else:
        print("❌ Opción inválida")
        return


if __name__ == "__main__":
    main()
