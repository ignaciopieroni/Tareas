import { HttpErrorResponse } from '@angular/common/http';
import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class ErrorParserService {
  parseBackendError(error: any): string {
    if (error instanceof HttpErrorResponse) {
      const status = error.status;
      const data = error.error;

      // Caso 1: Error interno del servidor
      if (status >= 500) {
        return 'Error interno del servidor. Intenta más tarde.';
      }

      // Caso 2: Error con 'detail'
      if (data?.detail) {
        return data.detail;
      }

      // Caso 3: Errores de validación del serializer
      if (typeof data === 'object') {
        const messages: string[] = [];

        for (const key in data) {
          const errores = data[key];
          if (Array.isArray(errores)) {
            errores.forEach((msg: string) => {
              messages.push(`${key}: ${msg}`);
            });
          }
        }

        if (messages.length > 0) {
          return messages.join('\n');
        }
      }

      // Fallback: mostrar mensaje genérico
      return 'Ocurrió un error inesperado.';
    }

    // Error no HTTP
    return 'Error desconocido.';
  }
}