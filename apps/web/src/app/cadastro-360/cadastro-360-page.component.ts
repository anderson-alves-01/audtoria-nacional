import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component, OnInit, inject } from '@angular/core';

export type Cadastro360ViewState = 'loading' | 'empty' | 'ok' | 'error';

export interface MinimizationPolicyItem {
  field: string;
  policy: string;
  present: boolean;
}

@Component({
  selector: 'app-cadastro-360-page',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './cadastro-360-page.component.html',
  styleUrl: './cadastro-360-page.component.scss',
})
export class Cadastro360PageComponent implements OnInit {
  private readonly http = inject(HttpClient);
  state: Cadastro360ViewState = 'loading';
  disclaimer = '';
  version = '';
  piiPresent = false;
  territoryInvented = false;
  g0Status = '';
  minimizationPolicy: MinimizationPolicyItem[] = [];
  errorMessage = '';

  ngOnInit(): void {
    this.http
      .get<{
        version: string;
        piiPresent: boolean;
        territoryInvented: boolean;
        g0Status: string;
        minimizationPolicy: MinimizationPolicyItem[];
        subjects: unknown[];
        disclaimer: string;
      }>('/v1/cadastro-360')
      .subscribe({
        next: (body) => {
          this.disclaimer = body.disclaimer;
          this.version = body.version;
          this.piiPresent = body.piiPresent;
          this.territoryInvented = body.territoryInvented;
          this.g0Status = body.g0Status;
          this.minimizationPolicy = body.minimizationPolicy;
          this.state = body.subjects.length === 0 ? 'empty' : 'ok';
        },
        error: () => {
          this.errorMessage = 'Não foi possível carregar o Cadastro 360.';
          this.state = 'error';
        },
      });
  }
}
