import { RoleName } from './role.model';

// Organización, puede ser propia o que nos hayamos unido
export class Organization {
  id?: number;
  name: string = '';
  created_at?: string;
}

// Rol de un usuario en la organización
export class OrganizationMembership {
  id?: number;
  role?: number;
  role_name?: RoleName;
  
  user!: number; // ID del usuario
  user_email?: string;
  user_username?: string;
  
  joined_at?: string;
}