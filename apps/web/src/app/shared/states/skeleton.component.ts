import { Component } from '@angular/core';

@Component({
  selector: 'app-skeleton',
  standalone: true,
  template: `
    <div class="skeleton" role="status" aria-live="polite">
      <div class="bar wide"></div>
      <div class="grid">
        <div class="bar"></div>
        <div class="bar"></div>
        <div class="bar"></div>
      </div>
      <p>Carregando…</p>
    </div>
  `,
  styles: `
    .bar {
      height: 0.85rem;
      border-radius: 6px;
      background: linear-gradient(90deg, var(--surface-2), var(--surface-3), var(--surface-2));
      background-size: 200% 100%;
      animation: shimmer 1.4s linear infinite;
      margin-bottom: 0.6rem;
    }
    .wide {
      width: 40%;
      height: 1.2rem;
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 0.6rem;
    }
    p {
      color: var(--muted);
      font-size: 0.82rem;
    }
    @keyframes shimmer {
      to {
        background-position: -200% 0;
      }
    }
  `,
})
export class SkeletonComponent {}
