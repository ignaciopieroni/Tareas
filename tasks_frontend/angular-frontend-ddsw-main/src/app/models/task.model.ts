import { Project } from "./project.model";
import { Team } from "./team.model";
import { User } from "./user.model";

/*
 * Modelo tarea, tiene los campos de lectura que retorna django y
 * de escritura preparados para enviar una nueva tarea.
 */
export class Task {
  id?: number;
  name!: string;
  description?: string;
  created_at?: string; // ISO string (Django devuelve datetime en formato ISO)
  expiration_datetime?: string;
  completed: boolean = false;

  project!: Project;

  // Campos 'Read-only'
  predecessors?: Task[];
  assigned_users?: User[];
  assigned_teams?: Team[];

  // Campos 'Write-only'
  predecessors_ids?: number[];
  users_ids?: number[];
  teams_ids?: number[];
}
