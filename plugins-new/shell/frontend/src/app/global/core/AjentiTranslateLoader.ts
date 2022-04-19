import { HttpClient } from '@angular/common/http';
import { TranslateLoader } from '@ngx-ajenti/core';
import { Observable } from 'rxjs';
import { Provider } from '@angular/core';


/**
 * Translate loader which loads the translations of Ajenti.
 */
class Loader implements TranslateLoader {

  constructor(protected httpClient: HttpClient) {
  }

  /**
   * Factory method to create the loader.
   */
  public static create(httpClient: HttpClient) {
    return new Loader(httpClient);
  }

  /**
   * Gets the translations from the backend.
   *
   * @param lang The language code to get the translation for.
   *
   * @returns A key value pair for translations.
   */
  public getTranslation(lang: string): Observable<{ [key: string]: string }> {
    return this.httpClient
      .get<{ [key: string]: string }>(
        `/resources/all.locale.json?lang=${ lang }`,
        { responseType: 'json' },
      );
  }

}

export const AjentiTranslateLoader: Provider = {
  provide: TranslateLoader,
  useFactory: Loader.create,
  deps: [ HttpClient ],
};
