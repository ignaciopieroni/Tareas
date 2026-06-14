import { Routes } from '@angular/router';
import { Home } from './components/home/home';
import { Register } from './components/register/register';
import { Log_in } from './components/login/login';
import { MainPage } from './components/main-page/main-page';
import { AuthGuard } from './interceptors/auth-guard';
import { Logout } from './components/logout/logout';
import { RedirectIfAuthenticatedGuard } from './interceptors/redirect-if-authenticated';
import { ProjectForm } from './components/projects/project-form/project-form';
import { OrganizationForm } from './components/organizations/create-organization/create-organization';
import { ListPersonalProyectTasks } from './components/tasks/list-personal-proyect-tasks/list-personal-proyect-tasks';
import { ListOrganizationProyectTasks } from './components/tasks/list-organization-proyect-tasks/list-organization-proyect-tasks';
import { AdministrateOrgMain } from './components/administrate-organization/administrate-org-main/administrate-org-main';
import { AdministrateTeams } from './components/administrate-organization/administrate-teams/administrate-teams';

export const routes: Routes = [
    // Desde index hasta abajo
    {path:"", redirectTo:"home", pathMatch:"full"},

    // Página de inicio, se mostrará para los usuarios no logeados
    {path:"home", component:Home, canActivate:[RedirectIfAuthenticatedGuard]},
    {path:"register", component:Register, canActivate:[RedirectIfAuthenticatedGuard]},
    {path:"log_in", component:Log_in, canActivate:[RedirectIfAuthenticatedGuard]},
    
    // ---- COMPONENTES PROTEGIDOS (NECESITAMOS LOGGEARNOS) -----
    {path:"app", component:MainPage, canActivate:[AuthGuard]},
    
    {path:"logout", component:Logout, canActivate:[AuthGuard]},
    
    {path:"create_project", component:ProjectForm, canActivate:[AuthGuard]},
    
    {path:"create_organization", component: OrganizationForm, canActivate:[AuthGuard]},

    // Tareas personales
    {path:"tasks/:project_id", component:ListPersonalProyectTasks, canActivate:[AuthGuard]},

    // Tareas organizacionales
    {path:"tasks/:project_id/:organization_id", component:ListOrganizationProyectTasks, canActivate:[AuthGuard]},

    // Página principal para administrar una organización
    {path:"manageAdministration/:organization_id", component:AdministrateOrgMain, canActivate:[AuthGuard]}
];
