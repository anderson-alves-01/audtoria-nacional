import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component, OnInit, inject } from '@angular/core';

export type AuditRulesViewState = 'loading' | 'empty' | 'ok' | 'error';

export interface AuditRuleItemView {
  code: string;
  title: string;
  domain: string;
  status: string;
  binding: boolean;
  notes: string;
}

@Component({
  selector: 'app-audit-rules-page',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './audit-rules-page.component.html',
  styleUrl: './audit-rules-page.component.scss',
})
export class AuditRulesPageComponent implements OnInit {
  private readonly http = inject(HttpClient);
  state: AuditRulesViewState = 'loading';
  disclaimer = '';
  catalogVersion = '';
  items: AuditRuleItemView[] = [];
  errorMessage = '';

  ngOnInit(): void {
    this.http
      .get<{
        catalogVersion: string;
        binding: boolean;
        operational: boolean;
        homologated: boolean;
        commandsDisabled: boolean;
        createsTaxCredit: boolean;
        taxPotentialAsCredit: boolean;
        disclaimer: string;
        items: AuditRuleItemView[];
      }>('/v1/audit-rules')
      .subscribe({
        next: (body) => {
          this.disclaimer = body.disclaimer;
          this.catalogVersion = body.catalogVersion;
          this.items = body.items;
          this.state = body.items.length ? 'ok' : 'empty';
        },
        error: () => {
          this.errorMessage = 'Não foi possível carregar o catálogo de regras de auditoria.';
          this.state = 'error';
        },
      });
  }
}
