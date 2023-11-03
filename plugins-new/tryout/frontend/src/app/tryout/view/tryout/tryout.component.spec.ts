import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TryoutComponent } from './tryout.component';

describe('TryoutComponent', () => {
  let component: TryoutComponent;
  let fixture: ComponentFixture<TryoutComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ TryoutComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(TryoutComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
