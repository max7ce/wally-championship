from fixture_generator import generate_fixture, validate_fixture
from database import execute_many, execute_query

print("🔄 Regenerando fixture completo...\n")

# Limpiar
print("[1/5] Limpiando base de datos...")
execute_query("DELETE FROM resultados", fetch=False)
execute_query("DELETE FROM partidos", fetch=False)
execute_query("DELETE FROM slots_tiempo", fetch=False)
execute_query("DELETE FROM equipos", fetch=False)
print("✅ Base de datos limpia\n")

# Crear equipos
print("[2/5] Creando equipos...")
for i in range(1, 9):
    execute_query("INSERT INTO equipos (id, nombre, posicion) VALUES (%s, %s, %s)", (i, f"EQ{i}", i), fetch=False)
print("✅ 8 equipos creados\n")

# Generar fixture
print("[3/5] Generando fixture...")
slots, partidos = generate_fixture()
print()

# Validar
print("[4/5] Validando fixture...")
validate_fixture(partidos)
print("✅ Fixture validado\n")

# Insertar slots
print("[5/5] Insertando en base de datos...")
slot_query = "INSERT INTO slots_tiempo (id, dia, numero_slot, hora_inicio, cancha) VALUES (%s, %s, %s, %s, %s)"
execute_many(slot_query, [(s['id'], s['dia'], s['numero_slot'], s['hora_inicio'], s['cancha']) for s in slots])

# Insertar partidos
partido_query = "INSERT INTO partidos (slot_id, equipo_local_id, equipo_visitante_id, ronda) VALUES (%s, %s, %s, %s)"
execute_many(partido_query, [(p['slot_id'], p['equipo_local'], p['equipo_visitante'], p['ronda']) for p in partidos])

print("✅ Datos insertados\n")

print("=" * 60)
print("🎉 SETUP COMPLETO")
print("=" * 60)
print(f"   ✅ Equipos: 8")
print(f"   ✅ Slots: {len(slots)}")
print(f"   ✅ Partidos: {len(partidos)}/84 ({len(partidos)/84*100:.1f}%)")

if len(partidos) == 84:
    print("\n🏆 ¡TODOS LOS 84 PARTIDOS ASIGNADOS!")
else:
    print(f"\n⚠️  Faltan {84 - len(partidos)} partidos por asignar")

print("=" * 60)