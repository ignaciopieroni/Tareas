import { Component, EventEmitter, Input, Output } from '@angular/core';
import { Team, TeamMembership } from '../../../models/team.model';
import { ToastrService } from 'ngx-toastr';
import { ErrorParserService } from '../../../services/error-parser-service';
import { TeamsService } from '../../../services/teamsService';
import { DatePipe } from '@angular/common';
import { Role, RoleName } from '../../../models/role.model';
import { OrganizationsService } from '../../../services/organizationsService';
import { OrganizationMembership } from '../../../models/organization.model';

@Component({
  selector: 'app-detailed-team-view',
  imports: [DatePipe],
  templateUrl: './detailed-team-view.html',
  styleUrl: './detailed-team-view.css'
})
export class DetailedTeamView {
  @Input() editTeam:Team = new Team();
  @Input() orgId:number = -1;
  @Output() goBack = new EventEmitter();

  teamMembers:TeamMembership[] = [];

  organizationMembers:OrganizationMembership[] = [];
  organizationMembersNotInTeam:OrganizationMembership[] = [];

  ORGANIZATION_ROLES: Role[] = [];
  showRoleOptions: { [userId: string]: boolean } = {};

  constructor(private toastr:ToastrService,
              private errorParser:ErrorParserService,
              private teamService:TeamsService,
              private organizationService:OrganizationsService) {  }

  ngOnInit() {
    this.teamService.getTeamMembers(this.editTeam.organization, this.editTeam.id)
      .subscribe({
        next:(v) => {
          this.teamMembers = v;

          for (let index = 0; index < this.organizationMembersNotInTeam.length; index++) {
            if (this.organizationMembers.find(x => x.id === this.organizationMembersNotInTeam[index].id) !== undefined) this.organizationMembersNotInTeam.splice(index, 1);
          }
        },
        error:(e) => {
          this.toastr.error(this.errorParser.parseBackendError(e), "Error tratando de obtener los miembros del equipo");
          this.goBack.emit();
        }
      });
    this.organizationService.getOrganizationRoles()
      .subscribe({
        next: (v) => {
          v.forEach(element => {if(element.scope === "team") this.ORGANIZATION_ROLES.push(element);});
        },
        error: e => {
          this.toastr.error(this.errorParser.parseBackendError(e), "Error tratando de obtener los roles del equipo");
        }
      });
    
    this.organizationService.getOrganizationUsers(this.orgId)
      .subscribe({
        next: v => {
          v.forEach(element => this.organizationMembers.push(element))

          this.organizationMembers.forEach(x => {
            if (this.teamMembers.find(y => y.user === x.id) === undefined) {
              this.organizationMembersNotInTeam.push(x);
            }
          });
        },
        error:(e)=> {
          this.toastr.error(this.errorParser.parseBackendError(e), "Error tratando de obtener los miembros de la organización")
        }
      });
  }

  formatedRole(role:String|undefined):string {
    if (!role) return '';
    return role
      .split('_')
      .map(w => w.charAt(0).toUpperCase() + w.slice(1))
      .join(' ');
  }
  toggleRoleOptions(member:number) {
    this.showRoleOptions[member] = !this.showRoleOptions[member];
  }

  changeUserRole(member:TeamMembership, newRole:Role) {
    let teamMember:TeamMembership = new TeamMembership();
    teamMember.id = member.id;
    teamMember.team = member.team;
    teamMember.user = member.user;
    teamMember.role = newRole.id as number;
    teamMember.joined_at = member.joined_at;

    this.teamService.changeTeamRole(this.orgId, teamMember.team, teamMember.user, teamMember)
      .subscribe({
        next:v => {
          this.teamMembers[this.teamMembers.indexOf(member)] = v;
          this.toastr.success(`Se cambió el rol a ${v.role}`, "Éxito al cambiar el rol");
        },
        error:e=> {
          this.toastr.error(this.errorParser.parseBackendError(e), "Error al tratar de cambiar el rol de un usuario del equipo");
        }
      });
  }

  kickUser(member:TeamMembership) {
    this.teamService.removeUserFromTeam(this.orgId, member.team, member.user)
      .subscribe({
        next:v => {
          this.teamMembers.splice(this.teamMembers.indexOf(member), 1);
          this.toastr.success(`Se eliminó al usuario id. ${member.user} del equipo ${member.team}`, "Éxito al expulsar");
          
          let kickedUser = this.organizationMembers.find(x => Number(x.id) === member.user ) as OrganizationMembership;

          this.organizationMembersNotInTeam.push(kickedUser);
        },
        error:e=> {
          this.toastr.error(this.errorParser.parseBackendError(e), "Error al tratar de eliminar al usuario del equipo");
        }
      });
  }
  
  getRoleName(roleId: number): string {
    return this.ORGANIZATION_ROLES.find(r => r.id === roleId)?.name || '';
  }

  userName(organizationMembershipId:number):string|undefined {
    const name = this.organizationMembers.find(x => x.id === organizationMembershipId);
    return name?.user_username;
  }

  addUserToTeam(user:OrganizationMembership) {
    this.teamService.addTeamMember(this.orgId, this.editTeam.id, user.id as number)
      .subscribe({
        next:(v) => {
          this.organizationMembersNotInTeam.splice(this.organizationMembersNotInTeam.indexOf(user), 1);
          this.teamMembers.push(v);
          this.toastr.success(`Usuario ${user.user_username} agregado al equipo`, "Éxito al agregando el usuario al equipo");
        },
        error: e => {
          this.toastr.error(this.errorParser.parseBackendError(e), "No se pudo agregar al usuario en el equipo");
        }
      });
  }
}
