import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component, OnInit, inject } from '@angular/core';

export type MunicipalUploadsViewState = 'loading' | 'empty' | 'ok' | 'error';

export interface MunicipalUploadSlot {
  sourceId: string;
  layoutVersion: string;
  uploadEnabled: boolean;
  quarantineRequired: boolean;
  tenantScoped: boolean;
  samplePresent: boolean;
  status: string;
}

@Component({
  selector: 'app-municipal-uploads-page',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './municipal-uploads-page.component.html',
  styleUrl: './municipal-uploads-page.component.scss',
})
export class MunicipalUploadsPageComponent implements OnInit {
  private readonly http = inject(HttpClient);
  state: MunicipalUploadsViewState = 'loading';
  disclaimer = '';
  version = '';
  uploadEnabled = false;
  g0Status = '';
  slots: MunicipalUploadSlot[] = [];
  errorMessage = '';

  ngOnInit(): void {
    this.http
      .get<{
        version: string;
        uploadEnabled: boolean;
        g0Status: string;
        slots: MunicipalUploadSlot[];
        items: unknown[];
        disclaimer: string;
      }>('/v1/municipal-uploads')
      .subscribe({
        next: (body) => {
          this.disclaimer = body.disclaimer;
          this.version = body.version;
          this.uploadEnabled = body.uploadEnabled;
          this.g0Status = body.g0Status;
          this.slots = body.slots;
          this.state = body.items.length === 0 ? 'empty' : 'ok';
        },
        error: () => {
          this.errorMessage = 'Não foi possível carregar o upload municipal.';
          this.state = 'error';
        },
      });
  }
}
