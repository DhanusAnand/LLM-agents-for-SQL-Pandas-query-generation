import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import * as XLSX from 'xlsx';

@Component({
  selector: 'app-main-page',
  standalone: true,
  imports: [CommonModule, FormsModule], // Include FormsModule for ngModel
  templateUrl: './main-page.component.html',
  styleUrls: ['./main-page.component.scss'],
})
export class MainPageComponent {
  csvData: any[] = [];
  cols: string[] = [];

  // Right section properties
  queryType: string = 'pandas'; // Default selected option
  textToSend: string = '';
  queryResult: string = '';
  processedData: any[] = [];
  processedCols: string[] = [];

  handleFileInput(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      const file = input.files[0];
      this.parseFile(file);
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
        const maxRows = 50;
        const maxCols = 50;

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

  submitQuery(): void {
    // Process the query (stubbed for now)
    this.queryResult = `Query executed using ${this.queryType}: ${this.textToSend}`;

    // Mock processed data for demonstration
    this.processedCols = ['Column1', 'Column2', 'Column3'];
    this.processedData = [
      { Column1: 'Value 1', Column2: 'Value 2', Column3: 'Value 3' },
      { Column1: 'Value 4', Column2: 'Value 5', Column3: 'Value 6' },
    ];
  }
}
