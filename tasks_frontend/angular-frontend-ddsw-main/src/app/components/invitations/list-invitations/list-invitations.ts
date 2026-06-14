import { DatePipe } from '@angular/common';
import { Component, EventEmitter, Output } from '@angular/core';
import { ToastrService } from 'ngx-toastr';
import { InvitationsService } from '../../../services/notificationsService';
import { OrganizationInvitation } from '../../../models/invitation.model';
import { HttpErrorResponse } from '@angular/common/http';
import { ErrorParserService } from '../../../services/error-parser-service';

@Component({
  selector: 'app-list-invitations',
  imports: [DatePipe],
  templateUrl: './list-invitations.html',
  styleUrl: './list-invitations.css'
})
export class ListInvitations {
  invitations:OrganizationInvitation[] = [];

  constructor(private toastr:ToastrService, 
              private invitationsService:InvitationsService,
              private errrorParserService:ErrorParserService) {  }

  ngOnInit() {
    this.invitationsService.getInvitations()
      .subscribe({
        next: (data) => {
          this.invitations = [... data];
          
        },
        error: (data) => 
          this.toastr.error(this.errrorParserService.parseBackendError(data), 
            "Error de acceso de invitaciones!")
      })
  }

  rejectInvitation(invitation:OrganizationInvitation) {
    const action = {"action":"reject"};
    this.invitationsService.handleInvitation(action, invitation.id as number)
      .subscribe({
        next:(v) => {
          this.toastr.success("Se rechazó correctamente la invitación", "Éxito al rechazar!");
          // Buscamos la invitación de la lista y, la borramos de ahi
          const index:number = this.invitations.indexOf(invitation);
          this.invitations.splice(index, 1);
        },
        error:(e) => {
          this.toastr.error(this.errrorParserService.parseBackendError(e), "Error al rechazar invitación");
        }
      });
  }

  acceptInvitation(invitation:OrganizationInvitation) {
    const action = {"action":"accept"};
    this.invitationsService.handleInvitation(action, invitation.id as number)
      .subscribe({
        next: (v) => {
          this.toastr.success("Se aceptó correctamente la invitación", "Éxito al aceptar!");
          location.reload();
        },
        error: (e) => {
          this.toastr.error(this.errrorParserService.parseBackendError(e), "Error al aceptar invitación");
        }
      });
  }
}
