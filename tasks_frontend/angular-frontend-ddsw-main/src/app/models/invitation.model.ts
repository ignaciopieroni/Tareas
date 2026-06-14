export class OrganizationInvitation {
  id?: number;
  
  inviter!: number; // ID del OrganizationMembership
  inviter_username?: string;
  inviter_email?: string;
  
  organization!: number; // ID de la organización
  
  email: string = ''; // Email del receptor, como es único en el sistema, la asignación se le da a este (por si no existe)

  created_at?: string; // ISO del date de django

  // Estados de la invitación (read_only)
  accepted: boolean = false;
  rejected: boolean = false;

  accepted_at?: string; // ISO de date por django
}
