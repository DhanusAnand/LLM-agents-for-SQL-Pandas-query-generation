import { Component, OnInit} from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import * as CryptoJS from 'crypto-js';
import { BackendService } from '../../services/backend.service';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';

@Component({
  selector: 'app-auth',
  templateUrl: './auth.component.html',
  styleUrls: ['./auth.component.scss'],
  providers:[BackendService],
  standalone: true,
  imports: [ReactiveFormsModule, HttpClientModule, CommonModule]
})

export class AuthComponent implements OnInit{
  isSignup: boolean = false;
  authForm: FormGroup;
  signupForm: FormGroup;

  showErrorBox: boolean = false;
  showSuccessBox: boolean = false;
  errorMessage: string = '';

  constructor(private fb: FormBuilder, private http: HttpClient, private router: Router) {
    this.authForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(6)]]
    });

    this.signupForm = this.fb.group({
      firstName: ['', [Validators.required]],
      lastName: ['', [Validators.required]],
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(6)]]
    });
  }

  ngOnInit(): void {}

  toggleSignup() {
    this.isSignup = !this.isSignup;
  }
  
//   // onLogin() {
//   //   if (this.authForm.valid) {
//   //     const payload = this.authForm.value;
//   //     console.log("Payload++++>",payload);
//   //     this.http.post('http://localhost:8000/login', payload).subscribe(
//   //       (response: any) => {
//   //         alert('Login successful!');
//   //         localStorage.setItem('token', response.token); // Store the JWT token
//   //         // Redirect to dashboard or another page
//   //       },
//   //       (error) => {
//   //         console.error('Login failed:', error);
//   //         // alert('Invalid credentials. Please try again.');
//   //         this.errorMessage = error.error.message || 'Login failed';
//   //         this.showErrorBox = true;
//   //         this.resetAlertsAfterDelay();
//   //       }
//   //     );
//   //   }
//   // }

  onLogin() {
    if (this.authForm.valid) {
      const payload = this.authForm.value;
      console.log("Payload++++>", payload);
  
      this.http.post('http://localhost:8000/login', payload).subscribe(
        (response: any) => {
          this.showSuccessBox = true; // Show success alert
          this.resetAlertsAfterDelay();
          localStorage.setItem('token', response.token); // Store JWT token
          this.router.navigate(['/dashboard']); // Redirect to dashboard
        },
        (error) => {
          console.error('Login failed:', error);
          alert('Invalid credentials. Please try again.');
          this.errorMessage = error.error.message || 'Invalid credentials. Please try again.';
          this.showErrorBox = true; // Show error alert
          this.resetAlertsAfterDelay();
        }
      );
    }
  }

//   // onSignup() {
//   //   if (this.signupForm.valid) {
//   //     const payload = this.signupForm.value;
//   //     console.log("Payload++++>",payload);
//   //     this.http.post('http://localhost:8000/signup', payload).subscribe(
//   //       (response: any) => {
//   //         alert('Signup successful!');
//   //         this.toggleSignup(); // Switch to login form
//   //         console.log("Response++++>",response);
//   //       },
//   //       (error) => {
//   //         console.log("Error");
//   //         const errorMessage = error?.error?.error
//   //         console.error('Signup failed:', error);
//   //         alert(`Signup failed: ${errorMessage}`);
//   //       }
//   //     );
//   //   }
//   // }

  onSignup() {
    if (this.signupForm.valid) {
      const payload = this.signupForm.value;
      console.log("Payload++++>", payload);
  
      this.http.post('http://localhost:8000/signup', payload).subscribe(
        (response: any) => {
          this.showSuccessBox = true; 
          this.resetAlertsAfterDelay();
          this.toggleSignup(); 
          console.log("Response++++>", response);
        },
        (error) => {
          console.error('Signup failed:', error);
          this.showErrorBox = true; 

          const errorMessage = error?.error?.error
          alert(`Signup failed: ${errorMessage}`);

          this.resetAlertsAfterDelay();

        }
      );
    }
  }

  // onGoogleSignIn() {
  //   alert('Google Sign-In functionality coming soon!');
  // }

  resetAlerts(): void {
    this.showErrorBox = false;
    this.showSuccessBox = false;
    this.errorMessage = '';
  }
  resetAlertsAfterDelay(): void {
    setTimeout(() => {
      this.resetAlerts();
    }, 3000); 
  }
}