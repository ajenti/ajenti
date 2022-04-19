import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SmartProgressComponent } from './smart-progress.component';

describe('SmartProgressComponent', () => {
  let component: SmartProgressComponent;
  let fixture: ComponentFixture<SmartProgressComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ SmartProgressComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(SmartProgressComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
