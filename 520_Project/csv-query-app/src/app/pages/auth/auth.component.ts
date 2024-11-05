import { Component } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import * as CryptoJS from 'crypto-js';

@Component({
  selector: 'app-auth',
  templateUrl: './auth.component.html',
  styleUrls: ['./auth.component.scss'],
  standalone: true,
  imports: [ReactiveFormsModule]
})
export class AuthComponent {
  authForm: FormGroup;

  constructor(private formBuilder: FormBuilder) {
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

  hashAndSendPassword() {
    const { email, password } = this.authForm.value;

    // Hash the password using CryptoJS
    const hashedPassword = CryptoJS.SHA256(password).toString(CryptoJS.enc.Hex);
    console.log(email, hashedPassword);
    // Send the email and hashed password to the backend
    this.sendToBackend(email, hashedPassword);
  }

  sendToBackend(email: string, hashedPassword: string) {
    // Implement logic to send the email and hashed password to the backend
    console.log('Sending to backend:', { email, hashedPassword });
  }
}

