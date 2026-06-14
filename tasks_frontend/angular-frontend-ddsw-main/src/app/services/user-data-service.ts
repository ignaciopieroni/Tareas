import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { User } from '../models/user.model';
import { ApiGateway } from './api-gateway';
import { Organization } from '../models/organization.model';


@Injectable({
  providedIn: 'root'
})
export class UserDataService {

  constructor(private apiGateway:ApiGateway) {  }

  // Acá solicitamos nuestros datos del usuario (modelo User)
  getUserObject():Observable<User> {
    return this.apiGateway.get("auth/me");
  }
  
  // Acá solicitamos la información de la lista de las organizaciones a las que
  // pertenece el usuario (para esta aplicación la lista tiene longitud 1 ó 0)
  getOrganizationObject():Observable<Organization[]> {
    return this.apiGateway.get("organizations/");
  }
}
