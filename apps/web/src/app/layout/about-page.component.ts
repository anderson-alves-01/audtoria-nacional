import { Component } from '@angular/core';
import { APP_IMPLEMENTATION_VERSION, APP_STATUS_LINE } from './navigation';

@Component({
  selector: 'app-about-page',
  standalone: true,
  template: `
    <section aria-labelledby="about-title">
      <h1 id="about-title">Sobre o SIRTA</h1>
      <p>
        Plataforma Municipal de Inteligência e Proteção da Receita Pública. Auditar. Acompanhar.
        Recuperar.
      </p>
      <p>Versão da interface {{ version }}. {{ statusLine }}.</p>
      <p>A interface recomenda e cita evidências. Não decide, não autua e não publica crédito.</p>
    </section>
  `,
  styles: `
    h1 {
      margin: 0 0 0.75rem;
      color: var(--primary-900);
    }
    p {
      margin: 0 0 0.6rem;
    }
  `,
})
export class AboutPageComponent {
  readonly version = APP_IMPLEMENTATION_VERSION;
  readonly statusLine = APP_STATUS_LINE;
}
