/**
 * Provides functionalities to restart the panel.
 */

import { MessageBoxService } from '../message-box/message-box.service';
import { Injectable, Type } from '@angular/core';

@Injectable({
  providedIn: 'platform',
})
export class RestartService {

  constructor(private mbs: MessageBoxService) {};

  public pageReload(): void {
    window.location.reload();
  };

  public restart(): void {
    const messageBox = this.mbs.show("Restart the panel ?", "Restart ?", undefined,undefined, "Yes", "No");

    messageBox.accepted = () => {
      this.forceRestart();
    };
  };

  public forceRestart(): void {
    console.warn("force restart");
    this.pageReload();
  };


  // this.forceRestart = () => {
  //    let msg = messagebox.show({progress: true, title: gettext('Restarting')});
  //    return $http.post('/api/core/restart-master').then(() => {
  //        return $timeout(() => {
  //            msg.close();
  //            messagebox.show({title: gettext('Restarted'), text: gettext('Please wait')});
  //            $timeout(() => {
  //                this.pageReload();
  //                return setTimeout(() => { // sometimes this is not enough
  //                    return this.pageReload();
  //                }, 5000);
  //            });
  //        }, 5000);
  //    }).catch((err) => {
  //        msg.close();
  //        notify.error(gettext('Could not restart'), err.message);
  //        return $q.reject(err);
  //    });
  // };

}
