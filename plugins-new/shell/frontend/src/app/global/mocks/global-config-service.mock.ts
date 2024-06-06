import { GlobalConstants } from '../extensions/Window';


export class GlobalConstantsServiceMock {

  /**
   * Gets the global constants.
   */
  public get constants(): GlobalConstants {
    return {
      urlPrefix: '',
      ajentiPlugins: {
        core: 'Core',
        dashboard: 'Dashboard',
      },
      initialConfigContent: {
        color: 'bluegrey',
        language: 'de',
        name: 'Test Box',
      },
      ajentiPlatform: 'centos',
      ajentiPlatformUnmapped: 'centos',
      ajentiVersion: '2.1.37',
    };
  }

}
