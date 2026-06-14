import { Component } from '@angular/core';
import { FormGroup, FormControl, Validators, ReactiveFormsModule } from '@angular/forms';
import { ToastrService } from 'ngx-toastr';
import { RegisterPayload, User } from '../../models/user.model';
import { Auth } from '../../services/auth';
import { Router } from '@angular/router';
import { ErrorParserService } from '../../services/error-parser-service';

@Component({
  selector: 'app-register',
  imports: [ReactiveFormsModule],
  templateUrl: './register.html',
  styleUrl: './register.css'
})
export class Register {
  /* Propiedad que usará el template para validar y enviar al back */
  userForm = new FormGroup({
    username: new FormControl('', Validators.required),
    email: new FormControl('', [Validators.required, Validators.email]),
    password: new FormControl('', [Validators.required, Validators.minLength(8)])
  });

  constructor(private toastr: ToastrService, 
              private authService: Auth, 
              private router:Router,
              private errorParserService:ErrorParserService) {  }


  /* Método que se llama una vez que se 'submitea' algo */
  onSubmit():void {
    if (this.userForm.invalid) {
      this.toastr.warning("Completá todos los campos requeridos y asegurate que el email tenga formato válido!", "Formulario Inválido");
      return;
    }

    const user: RegisterPayload = this.userForm.getRawValue() as RegisterPayload;

    this.authService.register(user).subscribe({
      next: (response:any) => { 
        localStorage.setItem("acc_tk", response.access);
        this.router.navigate(["/app"]);
        this.toastr.success("Redirigiendo...", "Usuario Registrado!");
      },
      error: (e) => {
        this.toastr.error(this.errorParserService.parseBackendError(e), "Error al registrar el usuario!")
      }
    });
  }
}
