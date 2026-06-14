import { Component, EventEmitter, Input, Output } from '@angular/core';
import { Project } from '../../../models/project.model';
import { CommonModule, DatePipe, NgClass } from '@angular/common';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { ToastrService } from 'ngx-toastr';
import { ProjectsService } from '../../../services/projectsService';
import { HttpErrorResponse } from '@angular/common/http';
import { UserDataService } from '../../../services/user-data-service';
import { ErrorParserService } from '../../../services/error-parser-service';
import { Task } from '../../../models/task.model';
import { TasksService } from '../../../services/tasksService';
import { Team, TeamMembership } from '../../../models/team.model';
import { OrganizationMembership } from '../../../models/organization.model';
import { TeamsService } from '../../../services/teamsService';
import { OrganizationsService } from '../../../services/organizationsService';

@Component({
  selector: 'app-task-editor-creator',
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './task-editor-creator.html',
  styleUrl: './task-editor-creator.css'
})
export class EditTask {
  @Input() task:Task|null = null; // Da una tarea vacia si se quiere crear una tarea, o una tarea ya creada cuando se quiere editar
  @Input() orgId?: number;
  @Input() proyId?: number;
  
  @Output() save = new EventEmitter<Task>();
  @Output() cancelled = new EventEmitter<void>();

  formulario:FormGroup = new FormGroup({});

  relateTasks: Task[] = [];
  relateTeams: Team[] = [];
  relateUsers: OrganizationMembership[] = [];


  newTask:boolean = false;

  constructor (private toastr:ToastrService, 
               private projectService:ProjectsService,
               private userDataService:UserDataService,
               private errorParserService:ErrorParserService,
               private tasksService:TasksService,
               private teamsService:TeamsService,
               private organizationService:OrganizationsService) {  }

  ngOnInit() {
    // Chequeo si se quiere crear una tarea o editar otra
    this.newTask = this.task?.name === undefined;

    // Campos usables en el formulario para el modelo de tarea
    this.formulario = new FormGroup({
      name: new FormControl(this.task?.name, [Validators.required, Validators.maxLength(32), Validators.minLength(4)]),
      description: new FormControl(this.task?.description, [Validators.required]),
      expiration_datetime:new FormControl(this.task?.expiration_datetime, [Validators.required]),

      // Campos no editables
      id:new FormControl(this.task?.id),
      created_at:new FormControl(this.task?.created_at),
      completed:new FormControl(this.task?.completed),
      project:new FormControl(this.task?.project),

      // El resto de campos de escritura, se manejan fuera de acá, pues no son HTML types
    });

    this.formulario.addControl('predecessors_ids', new FormControl([]));
    this.formulario.addControl('teams_ids', new FormControl([]));
    this.formulario.addControl('users_ids', new FormControl([]));

    // Obtenemos los posibles datos a usar de la organización
    if (this.orgId !== null && this.orgId !== undefined) {
      this.teamsService.getOrganizationTeams(this.orgId as number)
        .subscribe({
          next: v => {
            this.relateTeams = v;
          },
          error: e => {
            this.toastr.error(this.errorParserService.parseBackendError(e), "Error tratando de obtener los datos de los equipos disponibles");
          }
        });
      this.organizationService.getOrganizationUsers(this.orgId as number)
        .subscribe({
          next: v => {
            this.relateUsers = v;
          },
          error: e => {
            this.toastr.error(this.errorParserService.parseBackendError(e), "Error tratando de obtener los usuarios de la organización")
          }
        });
      this.tasksService.getOrganizationTasks(this.orgId as number, this.proyId as number)
        .subscribe({
          next: v => {
            this.relateTasks = v;
          },
          error: e => {
            this.toastr.error(this.errorParserService.parseBackendError(e), "Error tratando de obtener las tareas del proyecto")
          }
        });
    } else {
      this.tasksService.getPersonalTasks(this.proyId as number)
        .subscribe({
          next: v => {
            this.relateTasks = v;
          },
          error: e => {
            this.toastr.error(this.errorParserService.parseBackendError(e), "Error tratando de obtener las tareas relacionadas");
          }
        });
    }
  }


  submit() {
    if(this.formulario.invalid) {
      this.toastr.warning("Uno o varios campos no tienen el formato requerido", "No se cargará la tarea");
      return;
    }

    const tarea:Task = this.formulario.getRawValue();
    tarea.users_ids = this.formulario.value.users_ids;
    tarea.teams_ids = this.formulario.value.teams_ids;
    tarea.predecessors_ids = this.formulario.value.predecessors_ids;

    if (this.newTask) {
      // Nueva tarea organizacional
      if (this.orgId !== null && this.orgId != undefined) {
        this.tasksService.makeOrganizationTask(this.orgId, this.proyId as number, tarea)
          .subscribe({
            next: v => {
              this.save.emit(v)
            },
            error: e => {
              this.toastr.error(this.errorParserService.parseBackendError(e), "Error al crear una tarea organizacional");
            }
          });
      } 
      // Nueva tarea personal
      else {
        this.tasksService.makePersonalTask(this.proyId as number, tarea)
          .subscribe({
            next: v => {
              this.save.emit(v)
            },
            error: e => {
              this.toastr.error(this.errorParserService.parseBackendError(e), "Error al crear una tarea personal");
            }
          });
      }
    } else {
      // Edición de tarea organizacional
      if (this.orgId !== null && this.orgId != undefined) {
        this.tasksService.editOrganizationTask(this.orgId, this.proyId as number,tarea)
          .subscribe({
            next: v => {
              this.save.emit(v)
            },
            error: e => {
              this.toastr.error(this.errorParserService.parseBackendError(e), "Error al editar una tarea organizacional");
            }
          });
      } 
      // Edición de tarea personal
      else {
        this.tasksService.editPersonalTask(this.proyId as number, tarea)
          .subscribe({
            next: v => {
              this.save.emit(v)
            },
            error: e => {
              this.toastr.error(this.errorParserService.parseBackendError(e), "Error al editar una tarea personal");
            }
          });
      }
    }
  }
}
