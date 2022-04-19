import { Pipe, PipeTransform } from '@angular/core';
import { TranslateService } from '@ngx-ajenti/core';

@Pipe({
  name: 'formatBytes',
})
export class FormatBytesPipe implements PipeTransform {

  constructor(private translateService: TranslateService) {
  }

  transform(value: number, precision?: number): string {

    if (isNaN(parseFloat(value.toString())) || !isFinite(value)) {
      return '-';
    }

    if (value === 0) {
      return this.translateService.instant('0 bytes');
    }

    if (typeof precision === 'undefined') {
      precision = 1;
    }

    let units = [
      'bytes',
      'KB',
      'MB',
      'GB',
      'TB',
      'PB',
    ];
    let number = Math.floor(Math.log(value) / Math.log(1024));

    let x = (value / Math.pow(1024, Math.floor(number)));
    if (number === 0) {
      x = Math.floor(x);
    } else {
      x = parseFloat(x.toFixed(precision));
    }

    const translatedUnit = this.translateService.instant(units[number]);
    return x + ' ' + translatedUnit;
  }
}
