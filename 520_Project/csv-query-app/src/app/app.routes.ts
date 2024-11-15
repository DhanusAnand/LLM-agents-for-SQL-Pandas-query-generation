import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AuthComponent } from './pages/auth/auth.component';
import { FileUploadComponent } from './pages/file-upload/file-upload.component';
import { CsvRendererComponent } from './pages/csv-renderer/csv-renderer.component';
import { MainPageComponent } from './pages/main-page/main-page.component'; // Corrected the import path

export const routes: Routes = [
  { path: '', redirectTo: 'auth', pathMatch: 'full' },
  { path: 'auth', component: AuthComponent },
  { path: 'file-upload', component: FileUploadComponent },
  { path: 'csv-renderer', component: CsvRendererComponent },
  { path: 'main-page', component: MainPageComponent }, // Make sure this line is correct
];

