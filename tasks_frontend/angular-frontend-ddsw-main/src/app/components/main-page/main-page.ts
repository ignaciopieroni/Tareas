import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';
import { Notifications } from '../invitations/notifications/notifications';
import { ProjectsListOrganization } from '../projects/projects-list-organization/projects-list-organization';
import { ProjectsListPersonal } from '../projects/projects-list-personal/projects-list-personal';


@Component({
  selector: 'app-main-page',
  imports: [Notifications, RouterLink, ProjectsListOrganization, ProjectsListPersonal],
  templateUrl: './main-page.html',
  styleUrl: './main-page.css'
})
export class MainPage {  }