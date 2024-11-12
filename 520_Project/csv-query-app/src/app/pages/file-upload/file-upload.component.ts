import { Component } from '@angular/core';
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
export class FileUploadComponent {
chatQuery='';



chatMessages: ChatMessage[] = [
  { text: 'Hello, how can I help you today?', isUser: false },
  { text: 'I have a question about the sales data analysis function you provided.', isUser: true },
];

onChatSubmit() {
throw new Error('Method not implemented.');
}
  file: File | undefined;
  fileForm: FormGroup;
  fileData: any = null;
  queryResult: any = null;
  query = '';
chatbotResponse = '';

  constructor(private fb: FormBuilder, public service: BackendService, private http: HttpClient) {
    this.fileForm = this.fb.group({
      file: [null]
    });
  }

  onFileChange(event: any) {
    this.file = event.target.files[0];
    if (this.file) {
      console.log("file added");
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

  onSubmitQuery() {
    if (this.query) {
      // Here, you would send the query to the backend.
      console.log('Query submitted:', this.query);
      this.queryResult = `Results for query: ${this.query}`;
    }
  }
}
