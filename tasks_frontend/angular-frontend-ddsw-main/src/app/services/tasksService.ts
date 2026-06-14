import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { Task } from '../models/task.model';
import { ApiGateway } from './api-gateway';

@Injectable({
  providedIn: 'root'
})
export class TasksService {
  constructor(private apiGateWay:ApiGateway) {  }

  // -------- Tareas personales --------------

  getPersonalTasks(project_id:number):Observable<Task[]> {
    return this.apiGateWay.get(`projects/${project_id}/tasks/`);
  }
  makePersonalTask(project_id:number, task:Task):Observable<Task> {
    return this.apiGateWay.post(`projects/${project_id}/tasks/`, task);
  }
  editPersonalTask(project_id:number, task:Task):Observable<Task> {
    return this.apiGateWay.patch(`projects/${project_id}/tasks/${task.id}/`, task);
  }
  removePersonalTask(project_id:number, task_id:number):Observable<any> {
    return this.apiGateWay.delete(`projects/${project_id}/tasks/${task_id}/`);
  }


  // -------- Tareas organizacionales --------------

  getOrganizationTasks(org_id:number, project_id:number):Observable<Task[]> {
    return this.apiGateWay.get(`organizations/${org_id}/projects/${project_id}/tasks/`);
  }
  makeOrganizationTask(org_id:number, project_id:number, task:Task):Observable<Task> {
    return this.apiGateWay.post(`organizations/${org_id}/projects/${project_id}/tasks/`, task);
  }
  editOrganizationTask(org_id:number, project_id:number, task:Task):Observable<Task> {
    return this.apiGateWay.patch(`organizations/${org_id}/projects/${project_id}/tasks/${task.id}/`, task);
  }
  removeOrganizationTask(org_id:number, project_id:number, task_id:number):Observable<any> {
    return this.apiGateWay.delete(`organizations/${org_id}/projects/${project_id}/tasks/${task_id}/`);
  }


  completePersonalTask(project_id:number, task_id:number) {
  return this.apiGateWay.post(`projects/${project_id}/tasks/${task_id}/complete/`, {});
  }

  completeOrganizationTask(org_id:number, project_id:number, task_id:number) {
  return this.apiGateWay.post(`organizations/${org_id}/projects/${project_id}/tasks/${task_id}/complete/`, {});
  }

}