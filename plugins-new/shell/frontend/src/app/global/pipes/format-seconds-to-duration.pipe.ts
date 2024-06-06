import {Pipe, PipeTransform} from '@angular/core';

@Pipe({
  name: 'formatSecondsToDuration',
})
export class FormatSecondsToDurationPipe implements PipeTransform {

  transform(value: unknown, ...args: unknown[]): unknown {
    let seconds = 0;

    if (typeof value === 'string') {
      seconds = parseFloat(value);
    } else if (typeof value === 'number') {
      seconds = value;
    }

    if (seconds <= 0) {
      return '--:--:--';
    }

    const oneDayInSeconds = 60 * 60 * 24;
    const days = Math.floor(seconds / oneDayInSeconds);
    seconds -= days * oneDayInSeconds;

    const oneHourInSeconds = 60 * 60;
    const hours = Math.floor(seconds / oneHourInSeconds);
    seconds -= hours * oneHourInSeconds;

    const oneMinuteInSeconds = 60;
    const minutes = Math.floor(seconds / oneMinuteInSeconds);
    seconds -= minutes * oneMinuteInSeconds;
    seconds = Math.floor(seconds);

    let formattedDuration =
      this.convertNumberToTwoDigitString(hours)+":"
      +this.convertNumberToTwoDigitString(minutes)+":"
      +this.convertNumberToTwoDigitString(seconds);

    if (days > 0) {
      formattedDuration = `${days}d ` + formattedDuration;
    }

    return formattedDuration;
  }

  convertNumberToTwoDigitString(valueToConvert: number): string {
    let stringValue = ('00' + Math.floor(valueToConvert)).slice(-2);
    return stringValue;
  }
}
