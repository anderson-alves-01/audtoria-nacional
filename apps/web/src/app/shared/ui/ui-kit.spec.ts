import { Component } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { FilterBarComponent } from './filter-bar.component';
import { KpiCardComponent, buildSparkPath } from './kpi-card.component';
import { TabsComponent } from './tabs.component';
import { ThemeService } from './theme.service';

@Component({
  standalone: true,
  imports: [TabsComponent, FilterBarComponent, KpiCardComponent],
  template: `
    <app-tabs [tabs]="tabs" [active]="active" (activeChange)="active = $event" />
    <app-filter-bar [chips]="chips" (removed)="removed = $event" />
    <app-kpi-card label="Valor" value="—" [spark]="[1, null, 3]" />
  `,
})
class HostComponent {
  tabs = [
    { id: 'a', label: 'Resumo' },
    { id: 'b', label: 'Detalhe', count: 4 },
  ];
  active = 'a';
  chips = [{ key: 'uf', label: 'Estado', value: 'Acre' }];
  removed = '';
}

describe('ui kit', () => {
  beforeEach(() => {
    localStorage.removeItem('sirta.theme');
    document.documentElement.removeAttribute('data-theme');
  });

  it('draws a sparkline only from real numbers and needs two points', () => {
    expect(buildSparkPath([1, null, 3])).toContain('M0.00');
    expect(buildSparkPath([5])).toBe('');
    expect(buildSparkPath([null, null])).toBe('');
  });

  it('moves between tabs with the arrow keys', () => {
    const fixture = TestBed.createComponent(HostComponent);
    fixture.detectChanges();
    const list = fixture.nativeElement.querySelector('[role=tablist]') as HTMLElement;
    list.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowRight', bubbles: true }));
    fixture.detectChanges();
    expect(fixture.componentInstance.active).toBe('b');
    const selected = fixture.nativeElement.querySelector('[aria-selected=true]') as HTMLElement;
    expect(selected.textContent).toContain('Detalhe');
  });

  it('removes a filter chip and keeps the label readable', () => {
    const fixture = TestBed.createComponent(HostComponent);
    fixture.detectChanges();
    const button = fixture.nativeElement.querySelector('.chip-x') as HTMLButtonElement;
    expect(button.getAttribute('aria-label')).toBe('Remover filtro Estado');
    button.click();
    expect(fixture.componentInstance.removed).toBe('uf');
  });

  it('keeps the theme in the page and in storage', () => {
    const themes = TestBed.inject(ThemeService);
    themes.set('light');
    expect(document.documentElement.getAttribute('data-theme')).toBe('light');
    expect(localStorage.getItem('sirta.theme')).toBe('light');
    themes.toggle();
    expect(themes.theme()).toBe('dark');
  });
});
