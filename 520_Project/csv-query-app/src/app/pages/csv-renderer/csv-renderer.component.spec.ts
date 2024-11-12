import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CsvRendererComponent } from './csv-renderer.component';

describe('CsvRendererComponent', () => {
  let component: CsvRendererComponent;
  let fixture: ComponentFixture<CsvRendererComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CsvRendererComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CsvRendererComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
