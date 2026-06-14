import { Component } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Project } from '../../../models/project.model';
import { ToastrService } from 'ngx-toastr';
import { ProjectsService } from '../../../services/projectsService';
import { HttpErrorResponse } from '@angular/common/http';
import { Router } from '@angular/router';
import { UserDataService } from '../../../services/user-data-service';
import { ErrorParserService } from '../../../services/error-parser-service';

@Component({
  selector: 'app-project-form',
  imports: [ReactiveFormsModule],
  templateUrl: './project-form.html',
  styleUrl: './project-form.css'
})
export class ProjectForm {
  organizationId:number = -1;

  formulario:FormGroup = new FormGroup({
    name:new FormControl("", [Validators.required, Validators.maxLength(32)]),
    description:new FormControl("")
  });

  constructor(private toastr:ToastrService, 
              private projectsService:ProjectsService, 
              private router:Router, 
              private userData:UserDataService,
              private errorParserService:ErrorParserService) {  }


  ngOnInit() {
    this.userData.getOrganizationObject()
      .subscribe(v => {
        if (v.length > 0) this.organizationId = v[0].id as number;
      });
  }

  onSubmit() {
    if (this.formulario.invalid) {
      console.log(this.formulario.getRawValue());
      
      this.toastr.warning("Cerciorese de que todos los campos requeridos estén completos y en el formato pedido.", "Error en los campos!");
      return;
    }

    const proyecto = this.formulario.getRawValue() as Project;
    proyecto.created_at = new Date().toISOString().split('T')[0];

    const dropdown:HTMLSelectElement = document.getElementById("projectTipeSelector") as HTMLSelectElement;

    if (this.organizationId > 0 && dropdown.value == 'o') {
      this.projectsService.makeOrganizationProject(this.organizationId, proyecto)
      .subscribe({
        next:(val) => {
          this.formulario.reset();
          this.toastr.success("Proyecto creado correctamente", "Éxito al crear el proyecto");
          this.router.navigate(["/app"]);
        },
        error:(e) => {
          this.toastr.error(this.errorParserService.parseBackendError(e), "Error al crear el proyecto!");
        }
      });
    } else {
      this.projectsService.makePersonalProject(proyecto)
      .subscribe({
        next:(val) => {
          this.formulario.reset();
          this.toastr.success("Proyecto creado correctamente", "Éxito al crear el proyecto");
          this.router.navigate(["/app"]);
        },
        error:(e) => {
          this.toastr.error(this.errorParserService.parseBackendError(e), "Error al crear el proyecto!");
        }
      });
    }
    
  }
}
