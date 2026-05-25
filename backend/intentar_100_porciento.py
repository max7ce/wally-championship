from fixture_generator import generate_fixture
from database import execute_many, execute_query

max_intentos = 20
mejor_resultado = 0
mejor_slots = []
mejor_partidos = []

print("🎯 Intentando conseguir 84/84 partidos...\n")

for intento in range(1, max_intentos + 1):
    slots, partidos = generate_fixture()
    
    if len(partidos) > mejor_resultado:
        mejor_resultado = len(partidos)
        mejor_slots = slots
        mejor_partidos = partidos
        print(f"✨ Intento {intento}: {len(partidos)}/84 partidos (NUEVO RÉCORD)")
        
        if len(partidos) == 84:
            print(f"\n🏆 ¡CONSEGUIDO! 84/84 en el intento {intento}")
            break
    else:
        print(f"   Intento {intento}: {len(partidos)}/84 partidos")

print(f"\n📊 Mejor resultado: {mejor_resultado}/84 partidos ({mejor_resultado/84*100:.1f}%)")

if mejor_resultado >= 80:
    print("\n💾 Guardando mejor resultado en base de datos...")
    
    # Limpiar
    execute_query("DELETE FROM resultados", fetch=False)
    execute_query("DELETE FROM partidos", fetch=False)
    execute_query("DELETE FROM slots_tiempo", fetch=False)
    execute_query("DELETE FROM equipos", fetch=False)
    
    # Crear equipos
    for i in range(1, 9):
        execute_query("INSERT INTO equipos (id, nombre, posicion) VALUES (%s, %s, %s)", (i, f"EQ{i}", i), fetch=False)
    
    # Insertar
    slot_query = "INSERT INTO slots_tiempo (id, dia, numero_slot, hora_inicio, cancha) VALUES (%s, %s, %s, %s, %s)"
    execute_many(slot_query, [(s['id'], s['dia'], s['numero_slot'], s['hora_inicio'], s['cancha']) for s in mejor_slots])
    
    partido_query = "INSERT INTO partidos (slot_id, equipo_local_id, equipo_visitante_id, ronda) VALUES (%s, %s, %s, %s)"
    execute_many(partido_query, [(p['slot_id'], p['equipo_local'], p['equipo_visitante'], p['ronda']) for p in mejor_partidos])
    
    print("✅ Guardado en base de datos")