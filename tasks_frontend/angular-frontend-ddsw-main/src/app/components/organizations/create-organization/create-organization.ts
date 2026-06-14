import { Component } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { ToastrService } from 'ngx-toastr';
import { OrganizationsService } from '../../../services/organizationsService';
import { HttpErrorResponse } from '@angular/common/http';
import { Router } from '@angular/router';
import { UserDataService } from '../../../services/user-data-service';
import { Organization } from '../../../models/organization.model';
import { ErrorParserService } from '../../../services/error-parser-service';

@Component({
  selector: 'app-create-organization',
  imports: [ReactiveFormsModule],
  templateUrl: './create-organization.html',
  styleUrl: './create-organization.css'
})

export class OrganizationForm {
  
  registerForm: FormGroup = new FormGroup({
    name: new FormControl("", Validators.required)
  });

  constructor(private toastr: ToastrService, 
              private organizationsService:OrganizationsService, 
              private router:Router,
              private errorParserService:ErrorParserService
  ){  }

  onSubmit() {
    if (this.registerForm.invalid) {
      this.toastr.warning("Cerciorese de que todos los campos requeridos estén completos y en el formato pedido.", "Error en los campos!");
      return;
    }

    const organization = this.registerForm.getRawValue() as Organization;
    
    this.organizationsService.makeOrganization(organization)
      .subscribe({
        next:(val) => {
          this.registerForm.reset();
          this.toastr.success("Organización creada correctamente", "Éxito al crear la organización");
          this.router.navigate(["/app"]);
        },
        error:(e) => {
          this.toastr.error(this.errorParserService.parseBackendError(e), "Error al crear la organización!");
        }
      })
  }
}