import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { Organization, OrganizationMembership } from '../models/organization.model';
import { ApiGateway } from './api-gateway';
import { Team, TeamMembership } from '../models/team.model';

@Injectable({
  providedIn: 'root'
})
export class TeamsService {

  constructor (private apiGateWay:ApiGateway) {  }
  
  // ---- Métodos "globales" de los equipos de la organización ---------

  getOrganizationTeams(org_id:number):Observable<Team[]> {
    return this.apiGateWay.get(`organizations/${org_id}/teams/`);
  }

  makeOrganizationTeam(org_id:number, team:Team):Observable<Team> {
    return this.apiGateWay.post(`organizations/${org_id}/teams/`, team);
  }

  editOrganizationTeam(org_id:number, team:Team):Observable<Team> {
    return this.apiGateWay.patch(`organizations/${org_id}/teams/${team.id}/`, team);
  }

  removeOrganizationTeam(org_id:number, team_id:number):Observable<any> {
    return this.apiGateWay.delete(`organizations/${org_id}/teams/${team_id}/`);
  }


  // ---- Métodos específicos de cada equipo de la organización ---------
  
  getTeamMembers(org_id:number, team_id:number):Observable<TeamMembership[]> {
    return this.apiGateWay.get(`organizations/${org_id}/teams/${team_id}/memberships/`);
  }

  addTeamMember(org_id:number, team_id:number, user_organization_membership_id:number):Observable<TeamMembership> {
    return this.apiGateWay.post(`organizations/${org_id}/teams/${team_id}/memberships/`, {"user":user_organization_membership_id});
  }

  changeTeamRole(org_id:number, team_id:number, user_organization_membership_id:number, teamMemb:TeamMembership):Observable<TeamMembership> {
    return this.apiGateWay.patch(`organizations/${org_id}/teams/${team_id}/memberships/${user_organization_membership_id}/`, teamMemb);
  }

  removeUserFromTeam(org_id:number, team_id:number, user_organization_membership_id:number):Observable<any> {
    return this.apiGateWay.delete(`organizations/${org_id}/teams/${team_id}/memberships/${user_organization_membership_id}/`);
  }
}