import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

const Base_URL = "http://localhost:8000";

@Injectable({
  providedIn: 'root'
})
 

export class BackendService {
  constructor(private http: HttpClient) {}

  
  // Method to request a pre-signed URL for uploading
  getPresignedUploadUrl(filename: string) {
    return this.http.get<{ url: string }>(Base_URL + `/generate-upload-url?filename=${filename}`);
  }

  // Method to request a pre-signed URL for downloading
  getPresignedDownloadUrl(filename: string) {
    return this.http.get<{ url: string }>(Base_URL + `/generate-download-url?filename=${filename}`);
  }

  // Method to upload file using the upload URL
  uploadFileToS3(file: File, presignedUrl: string) {
    const headers = { 'Content-Type': 'text/csv' };
    return this.http.put(presignedUrl, file, { headers });
  }

    // Method to ask query to the pandas llm
    getPandasQueryOutput(filekey: string, query: string, userid:string="default") {
      console.log("calling llm agent...");
      const data = {
        "file_key": filekey,
        "query": query
      };
      return this.http.post(Base_URL+`/get-pandas-query`,data);
    }

}
