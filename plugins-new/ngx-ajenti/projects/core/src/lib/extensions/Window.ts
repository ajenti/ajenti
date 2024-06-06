import { AjentiConfiguration } from '../services/config/ajenti-configuration.model';

export type GlobalConstants = {
  urlPrefix: string;
  ajentiPlugins: { [key: string]: string };
  initialConfigContent: AjentiConfiguration;
  ajentiPlatform: string;
  ajentiPlatformUnmapped: string;
  ajentiVersion: string;
  ajentiDevMode: boolean;
  ajentiBootstrapColor: string;
};

declare global {
  interface Window {
    globalConstants: GlobalConstants;
  }
}
