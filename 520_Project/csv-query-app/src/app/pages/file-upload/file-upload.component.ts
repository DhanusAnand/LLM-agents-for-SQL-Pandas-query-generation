import { Component } from '@angular/core';
import { FormBuilder, FormGroup } from '@angular/forms';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { log } from 'console';

interface ChatMessage {
  text: string;
  isUser: boolean;
}

@Component({
  selector: 'app-file-upload',
  templateUrl: './file-upload.component.html',
  styleUrls: ['./file-upload.component.scss'],
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule]
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
  fileForm: FormGroup;
  fileData: any = null;
  queryResult: any = null;
  query = '';
chatbotResponse = '';

  constructor(private fb: FormBuilder) {
    this.fileForm = this.fb.group({
      file: [null]
    });
  }

  onFileChange(event: any) {
    const file = event.target.files[0];
    if (file) {
      console.log("file added");
      this.fileForm.patchValue({ file });
      this.fileData = file;
    }
  }

  onSubmit() {
    if (this.query) {
      // Here, you would send the query to the backend.
      console.log('Query submitted:', this.query);
      this.queryResult = `Results for query: ${this.query}`;
    }
  }
}
