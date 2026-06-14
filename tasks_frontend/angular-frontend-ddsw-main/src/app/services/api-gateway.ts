import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';


/*
 * Servicio que van a usar los otros servicios para aislarse
 * de la necesidad de conocer la URL del back-end, estos solamente,
 * deberán conocer la URI que usarán, el método y su contenido (si es necesario)
 */
@Injectable({
  providedIn: 'root'
})
export class ApiGateway {
  private baseUrl:string = "http://192.168.0.11:8000/api/v1/";

  constructor(private http:HttpClient) {  }

  get(endpoint:string):Observable<any> {
    return this.http.get(`${this.baseUrl + endpoint}`);
  }
  post(endpoint:string, data:any):Observable<any> {
    return this.http.post(`${this.baseUrl + endpoint}`, data);
  }
  patch(endpoint:string, data:any):Observable<any> {
    return this.http.patch(`${this.baseUrl + endpoint}`, data);
  }
  delete(endpoint:string):Observable<any> {
    return this.http.delete(`${this.baseUrl + endpoint}`);
  }
}