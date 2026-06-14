import { RoleName } from './role.model';

/* Modelo de proyecto, con los campos según el serialzer */
export class Project {
  id?: number;
  organization?: number; // ID de la organización (null para proyectos personales)
  owner?: number;        // ID del usuario (solamente si es proyecto personal)
  name: string = '';
  description?: string;
  is_closed?: boolean;
  closed_at?: string; // ISO de date que retorna django
  created_at?: string;
}

/* Rol del usuario en el proyecto, no se escribe */
export class ProjectUserMembership {
  id?: number;
  project!: number; // ID del proyecto
  user!: number;    // ID del OrganizationMembership
  role!: RoleName;
  joined_at?: string;
}

/* Rol del equipo sobre el proyecto, no se escribe */
export class ProjectTeamMembership {
  id?: number;
  project!: number; // ID del proyecto
  team!: number;    // ID del equipo
  role!: RoleName;
  joined_at?: string;
}
