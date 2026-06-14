import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { Project, ProjectTeamMembership, ProjectUserMembership } from '../models/project.model';
import { ApiGateway } from './api-gateway';

@Injectable({
  providedIn: 'root'
})
export class ProjectsService {
  constructor(private apiGateWay:ApiGateway) {  }

  // -------- Proyectos personales --------------

  getPersonalProjects():Observable<Project[]> {
    return this.apiGateWay.get("projects/");
  }
  makePersonalProject(project:Project):Observable<Project> {
    return this.apiGateWay.post("projects/", project);
  }
  editPersonalProject(project:Project):Observable<Project> {
    return this.apiGateWay.patch(`projects/${project.id}/`, project);
  }
  removePersonalProject(project_id:number):Observable<any> {
    return this.apiGateWay.delete(`projects/${project_id}/`);
  }


  // -------- Proyectos organizacionales --------------

  getOrganizationProjects(org_id:number):Observable<Project[]> {
    return this.apiGateWay.get(`organizations/${org_id}/projects/`);
  }
  makeOrganizationProject(org_id:number, project:Project):Observable<Project> {
    return this.apiGateWay.post(`organizations/${org_id}/projects/`, project);
  }
  editOrganizationProject(org_id:number, project:Project):Observable<Project> {
    return this.apiGateWay.patch(`organizations/${org_id}/projects/${project.id}/`, project);
  }
  removeOrganizationProject(org_id:number, project_id:number):Observable<any> {
    return this.apiGateWay.delete(`organizations/${org_id}/projects/${project_id}/`);
  }


  // ------- Alta y vista de usuarios y equipos en un proyecto ------- ♠


  listOrganizationProjectUsers(project:Project):Observable<ProjectUserMembership[]> {
    return this.apiGateWay.get(`organizations/${project.organization}/projects/${project.id}/members/`);
  }
  addUserOrganizationProject(org_id:number, projectUserMembership:ProjectUserMembership):Observable<any> {
    return this.apiGateWay.post(`organizations/${org_id}/projects/${projectUserMembership.project}>/members/`, projectUserMembership);
  }

  listOrganizationProjectTeams(project:Project):Observable<ProjectTeamMembership[]> {
    return this.apiGateWay.get(`organizations/${project.organization}/projects/${project.id}/teams/`);
  }
  addTeamOrganizationProject(org_id:number, projectTeamMembership:ProjectTeamMembership):Observable<any> {
    return this.apiGateWay.post(`organizations/${org_id}/projects/${projectTeamMembership.project}/teams/`, projectTeamMembership);
  }
}