import { Injectable } from '@angular/core';
import { CanActivate, Router } from '@angular/router';

@Injectable({
  providedIn: 'root'
})
export class RedirectIfAuthenticatedGuard implements CanActivate {
  constructor(private router: Router) {}

  canActivate(): boolean {
    const token = localStorage.getItem('acc_tk');

    if (!token) {
      return true;
    }

    /* Si se venció la sesión, se borra su información y se permite seguir navegando */
    const payload = JSON.parse(atob(token.split(".")[1]))
    const now = Math.floor(Date.now() / 1000);
    if (payload.exp && payload.exp < now) {
      localStorage.removeItem("acc_tk");
      return true;
    }
    
    this.router.navigate(['/app']); // redirige si ya está logueado
    return false; // evita que cargue la ruta pública
  }
}
