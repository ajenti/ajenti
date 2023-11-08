import { TestBed } from '@angular/core/testing';

import { BasicTemplateService } from './basicTemplate.service';

describe('FstabService', () => {
  let service: BasicTemplateService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(BasicTemplateService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
