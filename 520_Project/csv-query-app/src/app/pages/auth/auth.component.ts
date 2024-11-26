import { Component } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import * as CryptoJS from 'crypto-js';
import { BackendService } from '../../services/backend.service';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { Router } from '@angular/router';

@Component({
  selector: 'app-auth',
  templateUrl: './auth.component.html',
  styleUrls: ['./auth.component.scss'],
  providers:[BackendService],
  standalone: true,
  imports: [ReactiveFormsModule, HttpClientModule]
})
export class AuthComponent {
  authForm: FormGroup;

  constructor(private formBuilder: FormBuilder, public service: BackendService, private http: HttpClient, private route: Router) {
    this.authForm = this.formBuilder.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required]]
    });
  }

  onSubmit() {
    if (this.authForm.valid) {
      this.hashAndSendPassword();
    }
  }

  async hashAndSendPassword() {
    const { email, password } = this.authForm.value;

    // Hash the password using CryptoJS
    const hashedPassword = CryptoJS.SHA256(password).toString(CryptoJS.enc.Hex);
    console.log(email, hashedPassword);
    // Send the email and hashed password to the backend
    try {
      const response = await this.service.login(email, hashedPassword).toPromise();
      this.route.navigate(["file-upload"]);
    } catch (error) {
      console.error('Error logging in', error);
    }
  }
}

