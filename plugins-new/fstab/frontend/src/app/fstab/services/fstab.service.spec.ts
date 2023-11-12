import { TestBed } from '@angular/core/testing';

import { FstabService } from './fstab.service';

describe('FstabService', () => {
  let service: FstabService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(FstabService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
