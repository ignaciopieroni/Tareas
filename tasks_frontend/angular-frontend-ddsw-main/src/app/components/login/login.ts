import { Component } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { ToastrService } from 'ngx-toastr';
import { Auth } from '../../services/auth';
import { HttpErrorResponse } from '@angular/common/http';
import { RegisterPayload } from '../../models/user.model';
import { ErrorParserService } from '../../services/error-parser-service';

@Component({
  selector: 'app-login',
  imports: [ReactiveFormsModule],
  templateUrl: './login.html',
  styleUrl: '../register/register.css'
})
export class Log_in {
  formLogin = new FormGroup({
    username: new FormControl('', Validators.required),
    password: new FormControl('', [Validators.required, Validators.minLength(8)])
  });

  constructor(private authService:Auth, 
              private toastr:ToastrService, 
              private router:Router,
              private errorParserService:ErrorParserService) {  }

  onSubmit() {
    if (this.formLogin.invalid) {
      this.toastr.warning("Asegurate de completar todos los campos requeridos y cumplir el tipo de campo", "Formulario Inválido");
      return;
    }

    /* Parseo de datos para evitar conflictos de tipo undefiend */
    const data = this.formLogin.getRawValue() as RegisterPayload;

    this.authService.login(data)
      .subscribe({
        next: (response:any) => { 
          localStorage.setItem("acc_tk", response.access);
          this.router.navigate(["/app"]);
          this.toastr.success("Redirigiendo...", "Inicio de sesión exitoso!");
        },
        error:(e) => this.toastr.error(this.errorParserService.parseBackendError(e), "Error al inciar sesión!")
      });
  }
}