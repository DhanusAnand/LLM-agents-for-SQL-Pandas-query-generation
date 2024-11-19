import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup } from '@angular/forms';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { log } from 'console';
import { BackendService } from '../../services/backend.service';
import { HttpClient, HttpClientModule } from '@angular/common/http';

interface ChatMessage {
  text: string;
  isUser: boolean;
}

@Component({
  selector: 'app-file-upload',
  templateUrl: './file-upload.component.html',
  styleUrls: ['./file-upload.component.scss'],
  standalone: true,
  providers:[BackendService],
  imports: [CommonModule, FormsModule, ReactiveFormsModule, HttpClientModule]
})
export class FileUploadComponent implements OnInit{
chatQuery='';
user_id="";
is_logged_in=false;
constructor(private fb: FormBuilder, public service: BackendService, private http: HttpClient) {
  this.fileForm = this.fb.group({
    file: [null]
  });
}
ngOnInit(): void {
  this.service.isLoggedIn().subscribe(
    (response:any) => {
      this.user_id = response.user_id;
      this.is_logged_in = true;
      console.log(this.user_id, this.is_logged_in);
    },
    (error) => {
      console.error('Access denied', error, this.is_logged_in);
    }
  );
}

chatMessages: ChatMessage[] = [
  { text: 'Hello, how can I help you today?', isUser: false },
  { text: 'I have a question about the sales data analysis function you provided.', isUser: true },
];

async onChatSubmit() {
// throw new Error('Method not implemented.');
this.query = this.chatQuery;
  await this.onSubmitQuery();
}
  file: File | undefined;
  fileForm: FormGroup;
  fileData: any = null;
  queryResult: any = null;
  query = '';
  chatbotResponse = '';
  isResultTable = false;
  data: any[] = [];  // To hold parsed table data
  headers: string[] = [];  // To hold table headers

  

  onFileChange(event: any) {
    this.file = event.target.files[0];
    if (this.file) {
      console.log("file added");
      console.log(this.file);
      // this.fileForm.patchValue({ this.file });
      // this.fileData = this.file;
    }

  }

  async uploadFile() {
    if (!this.file) return;

    try {
      const response = await this.service.getPresignedUploadUrl(this.file.name).toPromise();
      const presignedUrl = response?.url;

      console.log(presignedUrl);
      if (presignedUrl) {
        await this.service.uploadFileToS3(this.file, presignedUrl).toPromise();
        console.log('File uploaded successfully');
      }
    } catch (error) {
      console.error('Error uploading file', error);
    }
  }

  // async onSubmitQuery() {
  //   if (this.query) {
  //     // Here, you would send the query to the backend.
  //     console.log('Query submitted:', this.query);
  //     try {
  //       if (this.file){
  //     //     console.log("file name",this.file.name);
  //     //     const response = await this.service.getPandasQueryOutput(this.file.name,this.query,'default').toPromise();
  //     //     console.log(response);
  //     //     // this.queryResult = response.data?.result;
  //     //     // this.isResultTable = response.data?.is_table;
  //           const response = await this.service.getPandasQueryOutput(this.file.name, this.query, 'default').toPromise();
  //           const result = JSON.parse(response.result);

  //           // Get headers from object keys
  //           this.headers = Object.keys(result);

  //           // Convert object of arrays into array of rows
  //           const rows = Object.keys(result[this.headers[0]]);
  //           this.data = rows.map((rowId) => {
  //             let row = {};
  //             this.headers.forEach((header) => {
  //               row[header] = result[header][rowId];
  //             });
  //             return row;
  //           });
  //       }
  //       else{
  //         console.log("No file found!!");
  //       }
        
  //     } catch (error) {
  //       console.error('Error sending the query');
  //       console.log(error);
  //     }
      
  
  //     this.queryResult = `Results for query: ${this.query}`;
  //   }
  // }

  async onSubmitQuery() {
    if (this.query) {
      console.log('Query submitted:', this.query);
      try {
        if (this.file) {
          // Call the service and handle the response using subscribe
          this.service.getPandasQueryOutput(this.file.name, this.query, 'default').subscribe({
            next: (response: any) => {
              const result = JSON.parse(response['result']);
  
              // Get headers from object keys
              this.headers = Object.keys(result);
              this.isResultTable = response['is_table'];
  
              // Convert object of arrays into array of rows
              const rows = Object.keys(result[this.headers[0]]);
              this.data = rows.map((rowId) => {
                let row:any = {};
                this.headers.forEach((header) => {
                  row[header] = result[header][rowId];
                });
                return row;
              });
            },
            error: (error) => {
              console.error('Error sending the query', error);
            }
          });
        } else {
          console.log("No file found!!");
        }
      } catch (error) {
        console.error('Unexpected error in query submission', error);
      }
  
      this.queryResult = `Results for query: ${this.query}`;
    }
  }
  
}

