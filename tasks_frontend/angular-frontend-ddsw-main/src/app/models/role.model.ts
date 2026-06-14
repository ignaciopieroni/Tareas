// Los enfoques que se aceptan unicamente de los roles son estos:
export type Scope = 'organization' | 'team' | 'project' | 'task';

// Y, los nombres de roles que se aceptan los siguientes
export type RoleName =
  | 'organization_admin'
  | 'organization_project_creator'
  | 'organization_team_creator'
  | 'organization_member'
  | 'team_admin'
  | 'team_member'
  | 'project_admin'
  | 'project_member'
  | 'task_assigned';

/* Clase Role, usada para cualquier scope que vimos ahí arriba */
export class Role {
    id?:number;
    name!:string;
    scope!:Scope;
    description?:string;
}