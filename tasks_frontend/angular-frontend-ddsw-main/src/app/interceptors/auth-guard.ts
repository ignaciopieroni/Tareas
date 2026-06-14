import { Injectable } from "@angular/core";
import { CanActivate, Router } from "@angular/router";
import { ToastrService } from "ngx-toastr";

/*
 * Middleware para 'proteger' rutas que requiren acceso
 */
@Injectable({ providedIn:"root" })
export class AuthGuard implements CanActivate {
    constructor(private router:Router, private toastr:ToastrService) {  }

    canActivate():boolean {
        const token = localStorage.getItem("acc_tk");
        
        /* No existe sesión */
        if (!token) {
            this.toastr.error("Iniciá sesión para poder acceder", "Ruta protegida!");
            this.router.navigate(["/home"]);
            return false;
        }

        // Esta parte es sacada de manual... Se asume codificación Windows64 y tipo de token con [1] info.
        const payload = JSON.parse(atob(token.split(".")[1]))
        const now = Math.floor(Date.now() / 1000);

        /* Sesión 'vencida' */
        if (payload.exp && payload.exp < now) {
            this.toastr.error("Tu sesión se venció", "Ruta protegida!");
            localStorage.removeItem("acc_tk");
            this.router.navigate(["/home"]);
            return false;
        }

        return true;
    }
}