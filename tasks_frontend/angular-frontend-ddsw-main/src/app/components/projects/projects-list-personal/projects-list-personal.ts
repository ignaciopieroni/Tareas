import { Component } from '@angular/core';
import { Project } from '../../../models/project.model';
import { DatePipe } from '@angular/common';
import { EditProject } from '../edit-project/edit-project';
import { ToastrService } from 'ngx-toastr';
import { ProjectsService } from '../../../services/projectsService';
import { HttpErrorResponse } from '@angular/common/http';
import { ErrorParserService } from '../../../services/error-parser-service';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-projects-list-personal',
  imports: [DatePipe, EditProject, RouterLink],
  templateUrl: './projects-list-personal.html',
  styleUrl: './projects-list-personal.css',
  standalone:true
})
export class ProjectsListPersonal {
  projects:Project[] = [];
  editProjectId:number|null|undefined = null;

  constructor(private toastr:ToastrService, 
              private projectService:ProjectsService,
              private errorParserService:ErrorParserService) { }

  ngOnInit() {
    this.projectService.getPersonalProjects()
      .subscribe({
        next:(v) => {
          this.projects = v;
        },
        error:(e) => {
          this.toastr.error(this.errorParserService.parseBackendError(e), "Error al tratar de obtener los proyectos personales!");
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
    this.projectService.removePersonalProject(project.id as number)
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
