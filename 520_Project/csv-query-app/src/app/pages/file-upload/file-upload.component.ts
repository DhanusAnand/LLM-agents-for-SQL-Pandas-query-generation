import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup } from '@angular/forms';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { BackendService } from '../../services/backend.service';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import * as XLSX from 'xlsx'; // Import XLSX for parsing Excel/CSV files



interface ChatMessage {
  text: string;
  isUser: boolean;
}

@Component({
  selector: 'app-file-upload',
  templateUrl: './file-upload.component.html',
  styleUrls: ['./file-upload.component.scss'],
  standalone: true,
  providers: [BackendService],
  imports: [CommonModule, FormsModule, ReactiveFormsModule, HttpClientModule],
})
export class FileUploadComponent implements OnInit {
  chatQuery = '';
  user_id = '';
  is_logged_in = false;

  // New properties for header dropdown functionality
  dropdownOpen = false;

  // Add chatMessages property
  chatMessages: ChatMessage[] = [];

  constructor(
    private fb: FormBuilder,
    public service: BackendService,
    private http: HttpClient
  ) {
    this.fileForm = this.fb.group({
      file: [null],
    });
  }

  ngOnInit(): void {
    this.service.isLoggedIn().subscribe(
      (response: any) => {
        this.user_id = response.user_id;
        this.is_logged_in = true;
        console.log(this.user_id, this.is_logged_in);
      },
      (error) => {
        console.error('Access denied', error, this.is_logged_in);
      }
    );
  }

  async onChatSubmit() {
    if (this.chatQuery.trim()) {
      // Add user message to chatMessages
      this.chatMessages.push({ text: this.chatQuery, isUser: true });

      // Simulate a bot response
      const botResponse = `Received your query: ${this.chatQuery}`;
      this.chatMessages.push({ text: botResponse, isUser: false });

      // Clear the chat input
      this.chatQuery = '';
    }

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
  data: any[] = []; // To hold parsed table data
  headers: string[] = []; // To hold table headers

  // New properties for CSV Preview
  csvData: any[] = [];
  cols: string[] = [];

  onFileChange(event: any) {
    this.file = event.target.files[0];
    if (this.file) {
      console.log('file added');
      console.log(this.file);
      // Process the file for CSV preview
      this.parseFile(this.file);
    }
  }

  parseFile(file: File): void {
    const reader = new FileReader();
    reader.onload = (e: any) => {
      const data = e.target.result;
      const workbook = XLSX.read(data, { type: 'binary' });
      const sheetName = workbook.SheetNames[0];
      const sheet = workbook.Sheets[sheetName];
      const jsonData = XLSX.utils.sheet_to_json<any[]>(sheet, { header: 1 });

      if (Array.isArray(jsonData)) {
        const maxRows = 50; // Limit rows to prevent rendering large files
        const maxCols = 50; // Limit columns to prevent rendering large files

        this.cols = jsonData[0]?.slice(0, maxCols) || [];
        this.csvData = jsonData.slice(1, maxRows).map((row: any[]) =>
          this.cols.reduce((acc: any, col: string, index: number) => {
            acc[col] = row[index] || '';
            return acc;
          }, {})
        );
      } else {
        console.error('Invalid data format');
      }
    };
    reader.readAsBinaryString(file);
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

  async onSubmitQuery() {
    if (this.query) {
      console.log('Query submitted:', this.query);
      try {
        if (this.file) {
          this.service.getPandasQueryOutput(this.file.name, this.query, 'default').subscribe({
            next: (response: any) => {
              const result = JSON.parse(response['result']);

              this.headers = Object.keys(result);
              this.isResultTable = response['is_table'];

              const rows = Object.keys(result[this.headers[0]]);
              this.data = rows.map((rowId) => {
                let row: any = {};
                this.headers.forEach((header) => {
                  row[header] = result[header][rowId];
                });
                return row;
              });
            },
            error: (error) => {
              console.error('Error sending the query', error);
            },
          });
        } else {
          console.log('No file found!!');
        }
      } catch (error) {
        console.error('Unexpected error in query submission', error);
      }

      this.queryResult = `Results for query: ${this.query}`;
    }
  }

  toggleDropdown() {
    this.dropdownOpen = !this.dropdownOpen;
  }

  logout() {
    console.log('Logging out...');
    // Add your logout logic here 
  }

  queryType: string = 'SQL'; // Default to 'Pandas'

}
