import { Component, HostListener } from '@angular/core';
import { LinkI } from '../../interfaces/navbar-link';
import { NavigationEnd, Router, RouterLink } from '@angular/router';
import { CommonModule } from '@angular/common';


@Component({
  selector: 'app-navbar',
  imports: [CommonModule, RouterLink],
  templateUrl: './navbar.html',
  styleUrl: './navbar.css'
})
export class NavbarComponent {
  currentRoute:string = ""; // Ruta luego de redirecciones
  navLinks:LinkI[] = []; // Links que se mostrará en el navbar (son dinámicos según la ruta)

  navbarVisible:boolean = true; // Este booleano se usa para esconder el navbar según si se scrrollea hacia abajo
  lastScrollTop:number = 0; // Cantidad de píxeles desplazados hacia arriba en el último scroll


  /* Links de las rutas sin acceso */
  public firstLinks:LinkI[] = [
    { label:"Inicio",        path:"home",     enabled:true, icon:"bi bi-house-fill" },
    { label:"Registro",      path:"register", enabled:true, icon:"bi bi-arrow-down-circle-fill" },
    { label:"Loggeo",        path:"log_in",    enabled:true, icon:"bi bi-arrow-right-circle" }
  ];
  /* Links de la página principal, luego del loggeo */
  public appLinks:LinkI[] = [
    { label:"Inicio",        path:"app",      enabled:true, icon:"bi bi-house-fill" },
    { label:"Cerrar Sesión", path:"logout",   enabled:true, icon:"bi bi-box-arrow-right" },
  ];
  

  constructor(private router:Router) {
    this.router.events.subscribe(event => {
      if (event instanceof NavigationEnd) {
        this.currentRoute = event.urlAfterRedirects;
        this.updateLinks();
      }
    });
  }

  updateLinks():void {
    const isAuth:boolean = ['/home', '/log_in', '/register'].some(path =>
      this.currentRoute.startsWith(path)
    );    
    this.navLinks = isAuth ? this.firstLinks : this.appLinks;
  }
  

  /* En este método detectamos si se scrollea hacia abajo o no
    el decorator sirve para auto-agregar y remover el event listener del scroll*/
  @HostListener("window:scroll", [])
  onScroll = (): void => {
    const currentScroll = window.pageYOffset || document.documentElement.scrollTop; // Según el componente que se renderiza abajo, el scroll es de la ventana o de todo el html
        
    if (currentScroll > this.lastScrollTop && currentScroll > 100) {
      this.navbarVisible = false;
    } else {
      this.navbarVisible = true;
    }

    this.lastScrollTop = currentScroll <= 0 ? 0 : currentScroll; // Si se scrolleo hacia abajo guardamos cuanto
  }
}