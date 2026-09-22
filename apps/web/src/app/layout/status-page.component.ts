import { Component, inject } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';

@Component({
  selector: 'app-status-page',
  standalone: true,
  imports: [RouterLink],
  template: `
    <section class="status" aria-labelledby="status-title">
      <p class="code">{{ code }}</p>
      <h1 id="status-title">{{ title }}</h1>
      <p>{{ message }}</p>
      <a routerLink="/executivo">Ir para a visão executiva</a>
    </section>
  `,
  styles: `
    .status {
      max-width: 40rem;
    }
    .code {
      margin: 0;
      color: var(--teal-600);
      font-weight: 700;
      letter-spacing: 0.04em;
    }
    h1 {
      margin: 0.25rem 0 0.5rem;
      color: var(--primary-900);
    }
  `,
})
export class StatusPageComponent {
  private readonly route = inject(ActivatedRoute);
  readonly code = String(this.route.snapshot.data['code'] || '404');
  readonly title = String(this.route.snapshot.data['title'] || 'Página não encontrada');
  readonly message = String(
    this.route.snapshot.data['message'] || 'O endereço não corresponde a um módulo do SIRTA.',
  );
}
