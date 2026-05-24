"""
Fixture Generator - Algoritmo inteligente para generar el fixture del campeonato
Restricciones:
1. Todos vs todos (28 partidos totales: 8 equipos × 7 enfrentamientos)
2. 3 canchas en paralelo
3. 2 días de competencia
4. Un equipo NO puede jugar en 2 canchas simultáneamente
5. Un equipo debe descansar MÍNIMO 1 slot entre sus partidos
"""
from datetime import time, timedelta
from typing import List, Dict, Tuple, Set
import random


def generate_round_robin_matches(num_teams: int = 8) -> List[Tuple[int, int]]:
    """
    Genera todos los enfrentamientos usando algoritmo Round-Robin
    
    Returns:
        Lista de tuplas (equipo_local, equipo_visitante)
    """
    teams = list(range(1, num_teams + 1))
    matches = []
    
    # Algoritmo Circle Method para Round-Robin
    # Fija el equipo 1 y rota los demás
    n = len(teams)
    
    for round_num in range(n - 1):
        for i in range(n // 2):
            home = teams[i]
            away = teams[n - 1 - i]
            matches.append((home, away))
        
        # Rotar equipos (excepto el primero)
        teams = [teams[0]] + [teams[-1]] + teams[1:-1]
    
    return matches


def generate_time_slots(start_time: str = "14:00", slot_duration: int = 15, 
                       num_slots_per_day: int = 14, num_days: int = 2,
                       num_courts: int = 3) -> List[Dict]:
    """
    Genera los slots de tiempo para todas las canchas
    
    Args:
        start_time: Hora de inicio (formato HH:MM)
        slot_duration: Duración en minutos de cada slot
        num_slots_per_day: Número de slots por día
        num_days: Número de días
        num_courts: Número de canchas
    
    Returns:
        Lista de diccionarios con info de cada slot
    """
    slots = []
    slot_id = 1
    
    hour, minute = map(int, start_time.split(":"))
    base_time = time(hour, minute)
    
    for day in range(1, num_days + 1):
        for slot_num in range(1, num_slots_per_day + 1):
            # Calcular hora de inicio para este slot
            delta = timedelta(minutes=(slot_num - 1) * slot_duration)
            slot_time = (
                timedelta(hours=base_time.hour, minutes=base_time.minute) + delta
            )
            slot_hour = slot_time.seconds // 3600
            slot_minute = (slot_time.seconds % 3600) // 60
            
            for court in range(1, num_courts + 1):
                slots.append({
                    'id': slot_id,
                    'dia': day,
                    'numero_slot': slot_num,
                    'hora_inicio': time(slot_hour, slot_minute),
                    'cancha': court
                })
                slot_id += 1
    
    return slots


def can_team_play_in_slot(team: int, slot_num: int, day: int, 
                          assignments: Dict, min_rest_slots: int = 1) -> bool:
    """
    Verifica si un equipo puede jugar en un slot específico
    
    Args:
        team: ID del equipo
        slot_num: Número de slot
        day: Día del torneo
        assignments: Diccionario de asignaciones actuales
        min_rest_slots: Número mínimo de slots de descanso
    
    Returns:
        True si el equipo puede jugar en ese slot
    """
    # Verificar si el equipo ya está jugando en este slot (en cualquier cancha)
    for (d, s, c), match in assignments.items():
        if d == day and s == slot_num:
            if team in match:
                return False
    
    # Verificar descanso mínimo
    for offset in range(1, min_rest_slots + 1):
        check_slot = slot_num - offset
        if check_slot > 0:
            for court in [1, 2, 3]:
                if (day, check_slot, court) in assignments:
                    if team in assignments[(day, check_slot, court)]:
                        return False
    
    return True


def assign_matches_to_slots(matches: List[Tuple[int, int]], 
                            slots: List[Dict]) -> List[Dict]:
    """
    Asigna partidos a slots respetando restricciones
    
    Returns:
        Lista de diccionarios con partido asignado a slot
    """
    # Agrupar slots por día y número de slot
    slots_by_time = {}
    for slot in slots:
        key = (slot['dia'], slot['numero_slot'])
        if key not in slots_by_time:
            slots_by_time[key] = []
        slots_by_time[key].append(slot)
    
    # Ordenar slots por día y número
    sorted_times = sorted(slots_by_time.keys())
    
    assignments = {}  # (dia, slot_num, cancha) -> (team1, team2)
    unassigned = list(matches)
    random.shuffle(unassigned)  # Aleatorizar para mejor distribución
    
    # Intentar asignar cada partido
    for day, slot_num in sorted_times:
        available_courts = slots_by_time[(day, slot_num)]
        
        for court_slot in available_courts:
            if not unassigned:
                break
            
            # Buscar un partido que pueda jugarse en este slot
            for i, (team1, team2) in enumerate(unassigned):
                if (can_team_play_in_slot(team1, slot_num, day, assignments) and
                    can_team_play_in_slot(team2, slot_num, day, assignments)):
                    
                    # Asignar partido
                    key = (day, slot_num, court_slot['cancha'])
                    assignments[key] = (team1, team2)
                    unassigned.pop(i)
                    break
    
    # Convertir assignments a lista de resultados
    result = []
    for (day, slot_num, court), (team1, team2) in assignments.items():
        # Encontrar el slot_id correspondiente
        slot_id = None
        for slot in slots:
            if (slot['dia'] == day and 
                slot['numero_slot'] == slot_num and 
                slot['cancha'] == court):
                slot_id = slot['id']
                break
        
        result.append({
            'slot_id': slot_id,
            'equipo_local': team1,
            'equipo_visitante': team2,
            'dia': day,
            'numero_slot': slot_num,
            'cancha': court
        })
    
    # Advertir si quedaron partidos sin asignar
    if unassigned:
        print(f"⚠️  ADVERTENCIA: {len(unassigned)} partidos no pudieron ser asignados")
        print(f"   Partidos sin asignar: {unassigned}")
    
    return result


def generate_fixture() -> Tuple[List[Dict], List[Dict]]:
    """
    Genera el fixture completo del campeonato
    
    Returns:
        Tupla de (slots, partidos_asignados)
    """
    print("🏐 Generando fixture del Campeonato de Wally...")
    
    # 1. Generar todos los enfrentamientos (todos vs todos)
    matches = generate_round_robin_matches(8)
    print(f"✅ Generados {len(matches)} partidos (todos vs todos)")
    
    # 2. Generar slots de tiempo
    slots = generate_time_slots()
    print(f"✅ Generados {len(slots)} slots de tiempo (2 días × 14 slots × 3 canchas)")
    
    # 3. Asignar partidos a slots con restricciones
    assigned_matches = assign_matches_to_slots(matches, slots)
    print(f"✅ Asignados {len(assigned_matches)} partidos a slots")
    
    # 4. Estadísticas
    total_slots_needed = len(matches) / 3  # 3 canchas en paralelo
    print(f"\n📊 Estadísticas:")
    print(f"   Total partidos: {len(matches)}")
    print(f"   Slots necesarios: {total_slots_needed:.1f}")
    print(f"   Slots disponibles: {len(slots) / 3:.1f} ({len(slots)} total)")
    print(f"   Utilización: {len(assigned_matches) / len(slots) * 100:.1f}%")
    
    return slots, assigned_matches


def validate_fixture(assigned_matches: List[Dict]):
    """
    Valida que el fixture cumple todas las restricciones
    """
    print("\n🔍 Validando fixture...")
    
    errors = []
    
    # Validar que ningún equipo juega dos veces en el mismo slot
    slot_teams = {}
    for match in assigned_matches:
        key = (match['dia'], match['numero_slot'])
        if key not in slot_teams:
            slot_teams[key] = set()
        
        team1, team2 = match['equipo_local'], match['equipo_visitante']
        
        if team1 in slot_teams[key]:
            errors.append(f"Equipo {team1} juega 2 veces en día {match['dia']}, slot {match['numero_slot']}")
        if team2 in slot_teams[key]:
            errors.append(f"Equipo {team2} juega 2 veces en día {match['dia']}, slot {match['numero_slot']}")
        
        slot_teams[key].add(team1)
        slot_teams[key].add(team2)
    
    # Validar descanso mínimo (1 slot)
    team_schedule = {}
    for match in sorted(assigned_matches, key=lambda x: (x['dia'], x['numero_slot'])):
        team1, team2 = match['equipo_local'], match['equipo_visitante']
        day, slot = match['dia'], match['numero_slot']
        
        for team in [team1, team2]:
            if team not in team_schedule:
                team_schedule[team] = []
            
            # Verificar último partido del equipo
            if team_schedule[team]:
                last_day, last_slot = team_schedule[team][-1]
                if day == last_day and slot - last_slot < 2:  # Menos de 1 slot de descanso
                    errors.append(
                        f"Equipo {team} no tiene descanso suficiente: "
                        f"slot {last_slot} → slot {slot} (día {day})"
                    )
            
            team_schedule[team].append((day, slot))
    
    if errors:
        print(f"❌ Se encontraron {len(errors)} errores:")
        for error in errors[:10]:  # Mostrar primeros 10
            print(f"   - {error}")
    else:
        print("✅ Fixture válido - todas las restricciones cumplidas")
    
    return len(errors) == 0
