import { Injectable } from '@angular/core';
import { RegisterPayload } from '../models/user.model';
import { Observable } from 'rxjs';
import { ApiGateway } from './api-gateway';

@Injectable({
  providedIn: 'root'
})
export class Auth {
  constructor(private apiGateway:ApiGateway) {  }

  register(user:RegisterPayload):Observable<any> {
    return this.apiGateway.post("auth/register/", user);
  }
  login(user:RegisterPayload):Observable<any> {
    return this.apiGateway.post("auth/token/", user);
  }
}
