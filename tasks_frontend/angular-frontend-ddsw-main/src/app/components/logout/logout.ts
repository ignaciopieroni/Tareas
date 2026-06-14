import { Component } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-logout',
  imports: [],
  templateUrl: './logout.html'
})
export class Logout {
  constructor(private router:Router) {  }

  ngOnInit() {
    localStorage.removeItem("acc_tk");
    this.router.navigate(["/home"]);
  }
}
