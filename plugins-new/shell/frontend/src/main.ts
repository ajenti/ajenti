import { loadAllPluginsEntries } from 'plugin-list-loader';


Promise
  .all(loadAllPluginsEntries())
  .catch(err => console.error('Error loading remote entries', err))
  .then(() => import('./bootstrap'))
  .catch(err => console.error(err));
