from typing import List, Tuple
from django.db import connection

def check_cycle_in_db(task_id: int, predecessors_ids: List[int]) -> Tuple[bool, List[int]]:
    """
    Comprueba si al asignar `predecessors_ids` como predecesoras de `task_id`
    se crearía un ciclo.

    Retorna (ok, offending_ids)
      - ok = True  => no se detectó ciclo
      - ok = False => offending_ids = lista de ids de `predecessors_ids` que
                      aparecen como sucesoras (directa/indirectamente) de task_id,
                      por lo que al agregarlas como predecesoras se formaría un ciclo.

    Implementación: recorre recursivamente las sucesoras de task_id (WITH RECURSIVE)
    y comprueba intersección con predecessors_ids.
    """
    if not predecessors_ids:
        return True, []

    # Normalizar a lista de ints (quita duplicados para mejor performance)
    preds = list(dict.fromkeys(int(x) for x in predecessors_ids))

    sql = """
        WITH RECURSIVE succ AS (
            SELECT successor_task_id
            FROM tasks_taskdependency
            WHERE predecessor_task_id = %s
          UNION
            SELECT td.successor_task_id
            FROM tasks_taskdependency td
            JOIN succ s ON td.predecessor_task_id = s.successor_task_id
        )
        SELECT DISTINCT successor_task_id
        FROM succ
        WHERE successor_task_id = ANY(%s);
    """

    with connection.cursor() as cur:
        # psycopg2 adapta la lista Python a array SQL para ANY(%s)
        cur.execute(sql, [task_id, preds])
        rows = cur.fetchall()

    # rows -> list of tuples like [(id,), (id,), ...]
    offending = [r[0] for r in rows] if rows else []

    if offending:
        return False, offending
    return True, []