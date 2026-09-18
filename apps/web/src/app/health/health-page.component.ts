import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component, OnInit, inject } from '@angular/core';

export type HealthViewState = 'loading' | 'ok' | 'error';

@Component({
  selector: 'app-health-page',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './health-page.component.html',
  styleUrl: './health-page.component.scss',
})
export class HealthPageComponent implements OnInit {
  private readonly http = inject(HttpClient);
  state: HealthViewState = 'loading';
  specVersion = '';
  implementationVersion = '';
  errorMessage = '';

  ngOnInit(): void {
    this.http.get<{ specVersion: string; implementationVersion: string }>('/health').subscribe({
      next: (body) => {
        this.specVersion = body.specVersion;
        this.implementationVersion = body.implementationVersion;
        this.state = 'ok';
      },
      error: () => {
        this.errorMessage = 'Não foi possível obter a saúde da API local.';
        this.state = 'error';
      },
    });
  }
}
