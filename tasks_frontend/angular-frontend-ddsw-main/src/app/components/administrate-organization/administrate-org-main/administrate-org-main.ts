import { Component } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { OrganizationsService } from '../../../services/organizationsService';
import { ToastrService } from 'ngx-toastr';
import { ErrorParserService } from '../../../services/error-parser-service';
import { OrganizationsMembersList } from '../organizations-members-list/organizations-members-list';
import { OrganizationMembership } from '../../../models/organization.model';
import { Team } from '../../../models/team.model';
import { TeamsService } from '../../../services/teamsService';
import { AdministrateTeams } from '../administrate-teams/administrate-teams';

@Component({
  selector: 'app-administrate-org-main',
  imports: [OrganizationsMembersList, AdministrateTeams],
  templateUrl: './administrate-org-main.html',
  styleUrl: './administrate-org-main.css'
})
export class AdministrateOrgMain {
  organizationId:number = -1;
  
  members:OrganizationMembership[] = [];
  
  showTeams:boolean = false;
  teams:Team[] = [];


  constructor (private route:ActivatedRoute,
               private router:Router,
               private organizationService:OrganizationsService,
               private toastr:ToastrService,
               private errorParser:ErrorParserService,
               private teamsService:TeamsService) {  }

  ngOnInit() {
    const idOrg = this.route.snapshot.paramMap.get("organization_id");
    
    if (!idOrg || isNaN(Number(idOrg))) {
      this.router.navigate(['/app']);
    }

    this.organizationId = Number(idOrg);

    this.organizationService.getOrganizationUsers(this.organizationId)
      .subscribe({
        next:(v) => {
          this.members = v;
        },
        error:(e) => {
          // Puede ser que se trate de un creador de equipos, no admin, por eso no se redirecciona acá
          this.showTeams = true;
        }
      });
    
    this.teamsService.getOrganizationTeams(this.organizationId)
      .subscribe({
        next:(v) => {
          this.teams =  v;
        },
        error: (e) => {
          this.errorParser.parseBackendError(e);
          this.router.navigate(['/app']);
        }
      });
  }

  deleteOrganization() {
    this.organizationService.deleteOrganization(this.organizationId)
      .subscribe({
        next:(v) => {
          this.toastr.success("La organización fue eliminada, ahora usted y sus integrantes dejan de pertenecer a esta.", "Éxito al borrar la organización!");
          this.router.navigate(['/app']);
        }, 
        error: (e) => {
          this.toastr.error(this.errorParser.parseBackendError(e), "Error al tratar de eliminar la organización!");
          this.router.navigate(['/app']);
        }
      });
  }

  crearEquipo() {
    const texto = window.prompt("Ingresá el nombre del nuevo equipo");
    if (texto !== null) {
      const equipo = new Team();
      equipo.name = texto;
      equipo.organization = this.organizationId;

      this.teamsService.makeOrganizationTeam(this.organizationId, equipo)
        .subscribe({
          next:(v) => {
            this.teams.push(v);
            this.toastr.success("Equipo creado", "Éxito al crear un nuevo equipo!");
          },
          error:(e) => {
            this.toastr.error(this.errorParser.parseBackendError(e), "Error al crear un equipo")
          }
        });
    }
  }
}
