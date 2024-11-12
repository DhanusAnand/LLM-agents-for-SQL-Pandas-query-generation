import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import * as XLSX from 'xlsx';

@Component({
  selector: 'app-csv-renderer',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './csv-renderer.component.html',
  styleUrl: './csv-renderer.component.scss'
})
export class CsvRendererComponent {
  csvData: any[] = [];
  cols: any[] = [];
  fileToUpload: File | null = null;

  handleFileInput(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      const file = input.files[0];
      console.log("calling parse...");
      this.parseCSV(file); // call your parsing function with the selected file
    }
  }
  

  parseCSV(file: File) {
    const reader = new FileReader();
    reader.onload = (e: any) => {
      const data = e.target.result;
      const workbook = XLSX.read(data, { type: 'binary' });
      const sheetName = workbook.SheetNames[0];
      const sheet = workbook.Sheets[sheetName];
      this.csvData = XLSX.utils.sheet_to_json(sheet);
      console.log(this.csvData);
    };
    reader.readAsArrayBuffer(file);
  }
}
