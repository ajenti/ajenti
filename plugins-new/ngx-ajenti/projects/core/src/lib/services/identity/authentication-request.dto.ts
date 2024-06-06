import { AuthenticationModes } from './authentication.modes';


/**
 * Defines the request object to authenticate a user.
 */
export type AuthenticationRequest = {

  /**
   * The username of the user to authenticate.
   */
  username: string;

  /**
   * The password of the user to authenticate.
   */
  password: string;

  /**
   * The mode to user for authentication.
   */
  mode: AuthenticationModes;

};
