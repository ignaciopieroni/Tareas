import { Component, Input } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { OrganizationsService } from '../../../services/organizationsService';
import { ToastrService } from 'ngx-toastr';
import { ErrorParserService } from '../../../services/error-parser-service';
import { Team } from '../../../models/team.model';
import { DatePipe } from '@angular/common';
import { TeamsService } from '../../../services/teamsService';
import { DetailedTeamView } from '../detailed-team-view/detailed-team-view';

@Component({
  selector: 'app-administrate-teams',
  imports: [DatePipe, DetailedTeamView],
  templateUrl: './administrate-teams.html',
  styleUrl: '../organizations-members-list/organizations-members-list.css'
})
export class AdministrateTeams {
  @Input() organizationTeams:Team[] = [];
  @Input() organizationId:number = -1;

  detailTeam:Team|undefined = undefined;

  constructor (private toastr:ToastrService,
               private teamService:TeamsService,
               private parserError:ErrorParserService) {  }

  deleteTeam(team:Team) {
    this.teamService.removeOrganizationTeam(team.organization, team.id as number)
      .subscribe({
        next:(v) => {
          this.organizationTeams.splice(this.organizationTeams.indexOf(team), 1);
          this.toastr.success(`Equipo ${team.name} borrado`, "Se borró con éxito el equipo de la organización");
        },
        error: (e) => {
          this.toastr.error(this.parserError.parseBackendError(e), "Error al tratar de eliminar un equipo");
        }
      });
  }
}
