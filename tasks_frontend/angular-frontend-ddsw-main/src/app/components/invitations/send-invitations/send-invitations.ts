import { Component } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { ToastrService } from 'ngx-toastr';
import { InvitationsService } from '../../../services/notificationsService';
import { HttpErrorResponse } from '@angular/common/http';
import { UserDataService } from '../../../services/user-data-service';
import { ErrorParserService } from '../../../services/error-parser-service';

@Component({
  selector: 'app-send-invitations',
  imports: [ReactiveFormsModule],
  templateUrl: './send-invitations.html',
  styleUrl: './send-invitations.css'
})
export class SendInvitations {
  emailControl = new FormControl('', [Validators.required, Validators.email]);
  emails:string[] = [];

  organizationId:number = -1;

  constructor (private invitationsService:InvitationsService,
               private toastr:ToastrService,
               private userDataService:UserDataService,
               private errorParserService:ErrorParserService) {  }

  ngOnInit() {
    this.userDataService.getOrganizationObject()
      .subscribe({
        next: (v) => {
          if (v.length > 0) this.organizationId = v[0].id as number;
        },
        error: (e) => {
          this.toastr.error(this.errorParserService.parseBackendError(e), "Erorr al tratar de obtener el id de la organización C:'send-invitations'");
        }
      })
  }

  addEmail() {
    const email = this.emailControl.value?.trim();
    if (email && this.emailControl.valid && !this.emails.includes(email)) {
      this.emails.push(email);
      this.emailControl.reset();
    }
  }

  removeEmail(index:number) {
    this.emails.splice(index, 1);
  }

  sendEmails() {
    if (this.emails.length < 1) {
      this.toastr.warning("Asegurate de agregar un email antes de enviarlo", "No se enviará el email");
      return;
    }

    const emails = {"emails":this.emails};

    this.invitationsService.sendInvitation(emails, this.organizationId)
      .subscribe({
        next:(val) => {
          this.toastr.success("Invitaciones enviadas", "Éxito en el envio!");
          this.emails.length = 0;
          this.emailControl.reset();
        },
        error:(e) => {
          this.toastr.error(this.errorParserService.parseBackendError(e), "Error al enviar invitaciones!");
        }
      });
  }
}
