/**
 * Defines the response of the identity controller.
 */
import { Identity } from './identity.model';
import { MachineInfo } from './machine-info.model';

export type IdentityResponse = {

  /**
   * Information of the user's identity.
   */
  identity: Identity;

  /**
   * Information of the server's machine.
   */
  machine: MachineInfo;

  /**
   * Defines the user's preferred color.
   */
  color?: string;

};
