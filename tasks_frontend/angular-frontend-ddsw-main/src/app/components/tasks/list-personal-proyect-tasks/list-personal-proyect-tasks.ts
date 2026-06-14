import { Component } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { ToastrService } from 'ngx-toastr';
import { ErrorParserService } from '../../../services/error-parser-service';
import { ProjectsService } from '../../../services/projectsService';
import { TasksService } from '../../../services/tasksService';
import { Task } from '../../../models/task.model';
import { EditTask } from "../task-editor-creator/task-editor-creator";


@Component({
  selector: 'app-list-personal-proyect-tasks',
  imports: [EditTask],
  templateUrl: './list-personal-proyect-tasks.html',
  styleUrl: './list-personal-proyect-tasks.css',
  standalone:true
})
export class ListPersonalProyectTasks {
  project_id:number = -1;
  tasks:Task[] = [];
  editTaskId:number|null|undefined = null;

  showEditor = false;              // controla el *ngIf del editor
  editing: Task | null = null;     // tarea en edición (o null si es creación)

  constructor(private route: ActivatedRoute,
              private router:Router,
              private toastr:ToastrService,
              private errorParserService:ErrorParserService,
              private projectsService:ProjectsService,
              private tasksService: TasksService) {}

  ngOnInit() {
    const project_id = Number(this.route.snapshot.paramMap.get('project_id'));
    console.log(this.constructor.name);

    if ((!project_id || isNaN(Number(project_id)))) {
      this.router.navigate(['/app'])
    }
    this.project_id = Number(project_id);

    this.tasksService.getPersonalTasks(project_id).subscribe({
      next:(t) => {
        this.tasks = t;
      },
      error:(e) => {
        this.toastr.error(this.errorParserService.parseBackendError(e), "Erro al tratar de obtener las tareas personales!");
      }
    });
  }

  /* Atrapo el emmiter de 'editor-creator-task' para mostrar la tarea actualizada sin volver a consultar el back */
  onSave(updatedTask:Task) {
    window.location.reload();
  }

  deleteTask(task:Task) {
      this.tasksService.removePersonalTask(this.project_id, task.id as number)
        .subscribe({
          next: (v:any) => {
            this.toastr.success("Se eliminó correctamente la tarea", "Éxito al eliminar la tarea");
            this.tasks.splice(this.tasks.indexOf(task), 1);
          },
          error: (e) => {
            this.toastr.error(this.errorParserService.parseBackendError(e), "Error al tratar de eliminar la tarea");
          }
        });
    }  
  
  closeTasks(){
    for (const tarea of this.tasks){
      this.deleteTask(tarea);
    }
  }

  onCancelled() {
    this.showEditor = false;
    this.editing = null;
  }

  newTask() {
    if (this.editing === null) this.editing = new Task();
    else this.editing = null;
  }

}
