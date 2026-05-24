#!/usr/bin/env python3
"""
Script de inicialización completa del sistema
Ejecuta todos los pasos necesarios para tener el sistema listo
"""

import sys
import os

# Añadir directorio actual al path para imports
sys.path.insert(0, os.path.dirname(__file__))

from database import init_db, create_default_users, execute_query, execute_many
from fixture_generator import generate_fixture, validate_fixture

def main():
    print("=" * 60)
    print("🏐 WALLY CHAMPIONSHIP - SETUP COMPLETO")
    print("=" * 60)
    
    # 1. Inicializar base de datos
    print("\n[1/4] Inicializando esquema de base de datos...")
    try:
        init_db()
        print("✅ Esquema creado exitosamente")
    except Exception as e:
        print(f"❌ Error creando esquema: {e}")
        return
    
    # 2. Crear usuarios por defecto
    print("\n[2/4] Creando usuarios por defecto...")
    try:
        create_default_users()
        print("✅ Usuarios creados:")
        print("   - cancha1 / cancha1")
        print("   - cancha2 / cancha2")
        print("   - cancha3 / cancha3")
        print("   - publico / publico")
        print("   - admin / admin123")
    except Exception as e:
        print(f"❌ Error creando usuarios: {e}")
        return
    
    # 3. Generar fixture
    print("\n[3/4] Generando fixture del campeonato...")
    try:
        slots, partidos = generate_fixture()
        
        # Validar fixture
        if not validate_fixture(partidos):
            print("⚠️  Advertencia: El fixture no pasó todas las validaciones")
            respuesta = input("¿Desea continuar de todos modos? (s/n): ")
            if respuesta.lower() != 's':
                return
        
        # Insertar slots
        slot_query = """
            INSERT INTO slots_tiempo (id, dia, numero_slot, hora_inicio, cancha)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """
        slot_params = [
            (s['id'], s['dia'], s['numero_slot'], s['hora_inicio'], s['cancha'])
            for s in slots
        ]
        execute_many(slot_query, slot_params)
        print(f"✅ Insertados {len(slots)} slots de tiempo")
        
        # Crear equipos genéricos
        for i in range(1, 9):
            execute_query(
                "INSERT INTO equipos (nombre, posicion) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                (f"EQ{i}", i),
                fetch=False
            )
        print("✅ Creados 8 equipos genéricos (EQ1-EQ8)")
        
        # Insertar partidos
        partido_query = """
            INSERT INTO partidos (slot_id, equipo_local_id, equipo_visitante_id)
            VALUES (%s, %s, %s)
        """
        partido_params = [
            (p['slot_id'], p['equipo_local'], p['equipo_visitante'])
            for p in partidos
        ]
        execute_many(partido_query, partido_params)
        print(f"✅ Insertados {len(partidos)} partidos en el fixture")
        
    except Exception as e:
        print(f"❌ Error generando fixture: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 4. Verificación final
    print("\n[4/4] Verificando instalación...")
    try:
        equipos = execute_query("SELECT COUNT(*) as total FROM equipos")
        partidos_count = execute_query("SELECT COUNT(*) as total FROM partidos")
        slots_count = execute_query("SELECT COUNT(*) as total FROM slots_tiempo")
        
        print(f"✅ Equipos: {equipos[0]['total']}")
        print(f"✅ Partidos: {partidos_count[0]['total']}")
        print(f"✅ Slots: {slots_count[0]['total']}")
        
    except Exception as e:
        print(f"⚠️  Advertencia en verificación: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 SETUP COMPLETADO EXITOSAMENTE")
    print("=" * 60)
    print("\nPróximos pasos:")
    print("1. Ejecutar backend: uvicorn main:app --reload")
    print("2. Ejecutar frontend: cd ../frontend && npm run dev")
    print("3. Login como 'admin' para realizar sorteo de equipos")
    print("\n¡El sistema está listo para usar! 🏐")

if __name__ == "__main__":
    main()
