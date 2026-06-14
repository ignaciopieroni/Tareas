// Usuario que envía Django al loggeo, sin contraseña por seguirdad
export class User {
  id!: number;
  username!: string;
  email!: string;
}

// Modelo para registrar el usuario este SI tiene password
export class RegisterPayload {
  username: string = '';
  email: string = '';
  password: string = '';
}