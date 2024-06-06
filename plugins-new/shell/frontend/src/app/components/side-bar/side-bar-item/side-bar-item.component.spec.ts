import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SideBarItemComponent } from './side-bar-item.component';
import { RouterTestingModule } from '@angular/router/testing';
import { TranslateModule } from '@ngx-ajenti/core';

describe('SideBarItemComponent', () => {
  let component: SideBarItemComponent;
  let fixture: ComponentFixture<SideBarItemComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ SideBarItemComponent ],
      imports: [
        RouterTestingModule,
        TranslateModule.forRoot(),
      ],
    })
      .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(SideBarItemComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
