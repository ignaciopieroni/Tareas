import { Component } from '@angular/core';
import { Project } from '../../../models/project.model';
import { DatePipe } from '@angular/common';
import { EditProject } from '../edit-project/edit-project';
import { ToastrService } from 'ngx-toastr';
import { ProjectsService } from '../../../services/projectsService';
import { HttpErrorResponse } from '@angular/common/http';
import { UserDataService } from '../../../services/user-data-service';
import { RouterLink } from '@angular/router';
import { ErrorParserService } from '../../../services/error-parser-service';

@Component({
  selector: 'app-projects-list-organization',
  imports: [DatePipe, EditProject, RouterLink],
  templateUrl: './projects-list-organization.html',
  styleUrl: '../projects-list-personal/projects-list-personal.css',
  standalone:true
})
export class ProjectsListOrganization {
  projects:Project[] = [];
  editProjectId:number|null|undefined = null;
  organizationId:number = -1;

  constructor(private toastr:ToastrService, 
              private projectService:ProjectsService,
              private projectsService:ProjectsService,
              private userDataService:UserDataService,
              private errorParserService:ErrorParserService) { }

  ngOnInit() {
    this.userDataService.getOrganizationObject()
      .subscribe({
        next:(v) => {
          if (v.length < 1) return;

          this.organizationId = v[0].id as number;

          this.projectService.getOrganizationProjects(this.organizationId)
          .subscribe({
            next:(v) => {
              this.projects = v;
            },
            error:(e) => {
              this.toastr.error(this.errorParserService.parseBackendError(e), "Error al tratar de obtener los proyectos organizacionales!");
            }
          });
        },
        error:(e) => {
          this.toastr.error(this.errorParserService.parseBackendError(e), "Error al tratar de obtener el id de la organización de su organización");
        }
      });    
  }

  /* Atrapo el emmiter de 'edit-project' para mostrar el proyecto actualizado sin volver a consultar el back */
  onSave(updatedProject:Project) {
    let x;
    for(x = 0; x < this.projects.length; x++) {
      if (this.projects[x].id === updatedProject.id) { break; }
    }
    this.projects[x] = updatedProject;
    this.editProjectId = null;
  }
  deleteProject(project:Project) {
    this.projectService.removeOrganizationProject(this.organizationId, project.id as number)
      .subscribe({
        next: (v:any) => {
          this.toastr.success("Se eliminó correctamente el proyecto", "Éxito al eliminar el proyecto");
          this.projects.splice(this.projects.indexOf(project), 1);
        },
        error: (e) => {
          this.toastr.error(this.errorParserService.parseBackendError(e), "Error al tratar de eliminar el proyecto");
        }
      });
  }  
}
