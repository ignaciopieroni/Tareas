import { Component } from '@angular/core';
import { ListInvitations } from '../list-invitations/list-invitations';
import { SendInvitations } from '../send-invitations/send-invitations';
import { UserDataService } from '../../../services/user-data-service';
import { User } from '../../../models/user.model';
import { OrganizationInvitation } from '../../../models/invitation.model';
import { Router } from '@angular/router';

@Component({
  selector: 'app-notifications',
  imports: [ListInvitations, SendInvitations],
  templateUrl: './notifications.html',
  styleUrl: './notifications.css'
})
export class Notifications {
  currentUser:User|null = null;
  mostrarPanel:boolean = false;

  listarNotificaciones:boolean = true;
  puedeInvitar:boolean = true;

  constructor(private userData:UserDataService, private router:Router) {  }

  ngOnInit() {
    this.userData.getOrganizationObject()
      .subscribe({
        next: (v) => {
          if (v.length < 1) {
            this.puedeInvitar = false;
            this.listarNotificaciones = true;
          } else {
            this.puedeInvitar = true;
            this.listarNotificaciones = false;
          }
        }
      });
  }

  toggleNotificationsPanel() {
    this.mostrarPanel = !this.mostrarPanel;
  }

  aceptoInvitacion() {
    window.location.reload();
  }
}
