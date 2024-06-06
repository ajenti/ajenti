export type PluginDto = {
  remoteEntry: string;
  remoteName: string;
  exposedModule: string;
  widgetComponents: string[];
  displayName: string;
  routePath: string;
  ngModuleName: string;
  themeComponent?: string;
};
