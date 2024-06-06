export class InputValidator {


  public static ensureInputIsNumberArray(inputValue: any, requiredLength?: number) {
    this.ensureIsArray(inputValue, requiredLength);
    inputValue.every((value: any) => this.ensureIsNumber(value));
  }

  public static ensureInputIsStringArray(inputValue: any, requiredLength?: number) {
    this.ensureIsArray(inputValue, requiredLength);
    inputValue.every((value: any) => this.ensureIsString(value));
  }

  public static ensureIsArray(inputValue: any, requiredLength?: number) {
    if (!inputValue || !Array.isArray(inputValue)) {
      throw Error('Invalid input: ' + inputValue + 'is not an array!');
    }

    if (requiredLength && inputValue.length !== requiredLength) {
      throw Error('Invalid input: Array length' + inputValue.length
        + 'does not match the required length ' + requiredLength);
    }
  }

  public static ensureIsString(inputValue: any) {
    if (!inputValue || typeof inputValue !== 'string') {
      throw Error('Invalid input: ' + inputValue + 'is not a string!');
    }
  }

  public static ensureIsNumber(inputValue: any) {
    if (typeof inputValue !== 'number') {
      throw Error('Invalid input: ' + inputValue + 'is not a number!');
    }
  }
}
