/**
 * Defines the response object to authenticate a user.
 */
export type AuthenticationResponse = {

  /**
   * Determines if the authentication was successful.
   */
  success: boolean;

  /**
   * Defines the error message if the authentication was not successful.
   */
  error: string;

};
