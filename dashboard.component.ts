import { Component, OnInit } from '@angular/core';
import { ReactiveFormsModule } from '@angular/forms';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
declare var logout: any;

@Component({
  selector: 'app-dashboard',
  standalone: true,
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss'],
  imports: [ReactiveFormsModule, HttpClientModule, CommonModule]
})

// export class DashboardComponent {
//   files: any[] = [];
//   filteredFiles: any[] = [];
//   searchTerm: string = '';

//   constructor(private http: HttpClient) {
//     this.fetchFiles();
//   }

//   fetchFiles() {
//     this.http.get('http://localhost:5000/get-user-files').subscribe(
//       (response: any) => {
//         this.files = response.files;
//         this.filteredFiles = [...this.files]; // Initialize filtered files
//       },
//       (error) => {
//         console.error('Error fetching files:', error);
//         alert('Failed to fetch files. Please try again later.');
//       }
//     );
//   }

//   filterFiles() {
//     this.filteredFiles = this.files.filter((file) =>
//       file.fileName.toLowerCase().includes(this.searchTerm.toLowerCase())
//     );
//   }

//   uploadNewFile() {
//     alert('Upload new file functionality coming soon!');
//     // Redirect to file upload page or open a file upload dialog
//   }

//   logout() {
//     alert('Logging out...');
//     localStorage.removeItem('token'); // Clear stored token
//     // Redirect to login page
//     window.location.href = '/';
//   }
// }
export class DashboardComponent implements OnInit {
  userName: string = '';
  userFiles: { name: string; id: string }[] = [];

  constructor(private http: HttpClient, private router: Router) {}
  // userProfile: any;
  ngOnInit() {
  //   this.userProfile = JSON.parse(sessionStorage.getItem("loggedInUser") || "");
  //   this.userName = this.userProfile.name;
  //   if(this.userProfile == "")
  //   {
  //     this.fetchUserInfo();
  //   }
    this.fetchUserInfo();
    this.fetchUserFiles();
  }

  fetchUserInfo() {
    this.http.get('http://localhost:8000/dashboard').subscribe(
      (response: any) => {
        this.userName = response.name;
        console.log("Name++++>",response.name);
      },
      (error) => {
        alert('Failed to fetch user info. Please try again later.');
      }
    );
  }

  fetchUserFiles() {
    this.http.get('http://localhost:8000/get-users-files').subscribe(
      (response: any) => {
        this.userFiles = response.files;
        console.log("Resp+++>",response);
      },
      (error) => {
        alert('Failed to fetch user files. Please try again later.');
      }
    );
  }

  goToUploadPage() {
    this.router.navigate(['/main-page']);
  }

  openFile(file: { name: string; id: string }) {
    console.log('Open file:', file);
  }

  logout() {
    logout();
    sessionStorage.removeItem("loggedInUser");
    localStorage.removeItem('token');
    this.router.navigate(['/auth']).then(() => {
      window.location.reload();
    });
  }
}