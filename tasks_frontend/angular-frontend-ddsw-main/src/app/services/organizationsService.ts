import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { Organization, OrganizationMembership } from '../models/organization.model';
import { ApiGateway } from './api-gateway';
import { Role } from '../models/role.model';

@Injectable({
  providedIn: 'root'
})
export class OrganizationsService {
  constructor(private apiGateWay:ApiGateway) {  }

  getOrganizationRoles():Observable<Role[]> {
    return this.apiGateWay.get(`roles/`);
  }

  makeOrganization(organization: Organization):Observable<any> {
    return this.apiGateWay.post("organizations/", organization);
  }

  // Funciones exclusivas del admin de la organización

  editOrganization(organization: Organization):Observable<any> {
    return this.apiGateWay.patch(`organizations/${organization.id}/`, organization);
  }

  deleteOrganization(organization_id:number):Observable<any> {
    return this.apiGateWay.delete(`organizations/${organization_id}/`);
  }

  getOrganizationUsers(org_id:number):Observable<OrganizationMembership[]> {
    return this.apiGateWay.get(`organizations/${org_id}/members/`);
  }

  changeOrganizationUserRole(org_id:number, orgMemb:OrganizationMembership):Observable<OrganizationMembership> {
    return this.apiGateWay.patch(`organizations/${org_id}/members/${orgMemb.user}/`, orgMemb);
  }

  kickUserFromOrganization(org_id:number, usr_id:number):Observable<any> {
    return this.apiGateWay.delete(`organizations/${org_id}/members/${usr_id}/`);
  }
}