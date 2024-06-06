import { ComponentFixture, TestBed } from '@angular/core/testing';

import { LoginViewComponent } from './login-view.component';
import { RouterTestingModule } from '@angular/router/testing';
import { TranslateModule } from '@ngx-ajenti/core';
import { HttpClientTestingModule } from '@angular/common/http/testing';

describe('LoginViewComponent', () => {
  let component: LoginViewComponent;
  let fixture: ComponentFixture<LoginViewComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ LoginViewComponent ],
      imports: [
        HttpClientTestingModule,
        RouterTestingModule,
        TranslateModule.forRoot(),
      ],
    })
      .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(LoginViewComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
