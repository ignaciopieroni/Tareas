-- ============================================================
-- 1️⃣ Crear la base de datos desde la GUI de pgAdmin
--    Abre pgAdmin, haz clic derecho en "Databases" -> Create -> Database
--    Nombre: tasks_db
--    Owner: postgres (o tu superusuario)
--    Luego abre Query Tool sobre tasks_db para ejecutar este script.
-- ============================================================

-- ============================================================
-- 2️⃣ Crear role para la app
-- ============================================================
-- Crea el usuario/role backend_drf con contraseña
DO
$$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'backend_drf') THEN
        CREATE ROLE backend_drf LOGIN PASSWORD '1234';
    END IF;
END
$$;

-- Ajustes recomendados del role
ALTER ROLE backend_drf SET client_encoding TO 'utf8';
ALTER ROLE backend_drf SET default_transaction_isolation TO 'read committed';
ALTER ROLE backend_drf SET timezone TO 'America/Argentina/Buenos_Aires';

-- ============================================================
-- 3️⃣ Crear schema para la app
-- ============================================================
DO
$$
BEGIN
    IF NOT EXISTS (SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'tasks_app_schema') THEN
        CREATE SCHEMA tasks_app_schema AUTHORIZATION backend_drf;
    END IF;
END
$$;

-- ============================================================
-- 4️⃣ Dar todos los privilegios al role backend_drf
-- ============================================================
GRANT ALL PRIVILEGES ON SCHEMA tasks_app_schema TO backend_drf;

-- Opcional: dar permisos de conexión y uso de la DB
GRANT CONNECT ON DATABASE tasks_db TO backend_drf;
GRANT USAGE ON SCHEMA public TO backend_drf;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO backend_drf;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO backend_drf;

-- ============================================================
-- 5️⃣ Insertar roles iniciales en roles_role
-- ============================================================
-- scope puede ser 'organization', 'team' o 'project'

INSERT INTO tasks_app_schema.roles_role (name, scope, description)
VALUES
    -- Roles de organización
	('organization_admin', 'organization', 'Administrador de la organización, controla todo'),
	('organization_member', 'organization', 'Miembro de la organización'),
	('organization_project_creator', 'organization', 'Puede crear proyectos dentro de la organización'),
	('organization_team_creator', 'organization', 'Puede crear equipos dentro de la organización'),
    
    -- Roles de proyecto
    ('project_admin', 'project', 'Administrador del proyecto, controla miembros y configuración'),
	('project_member', 'project', 'Miembro del proyecto'),
	
    -- Roles de equipo
    ('team_admin', 'team', 'Administrador del equipo, controla miembros y tareas'),
	('team_member', 'team', 'Miembro del equipo'),

    -- Rol de tarea
    ('task_assigned', 'task', 'Rol asignado a usuarios/tareas para seguimiento de permisos')
ON CONFLICT (name, scope) DO NOTHING;


-- ============================================================
-- Fin del script
-- Ahora tu role backend_drf tiene un schema propio y permisos completos.
-- ============================================================
